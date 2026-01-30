"""Data manipulation service - handles Excel/Nextcloud storage."""
import os
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from typing import List, Dict

import pandas as pd
import requests
from filelock import FileLock, Timeout
from pandas import DataFrame
from requests.auth import HTTPBasicAuth


class FileType(Enum):
    SPENDING = "SPENDING"
    INCOME = "INCOME"
    RECEIPT = "RECEIPT"


class TableName(Enum):
    # Income file sheets
    INCOME = "Income"
    DEDUCTIONS = "Deductions"

    # Spending file sheets
    SPENDING = "Spending"
    TOP = "Top_Table"
    MIDDLE = "Middle Table"
    BASE = "Base Table"
    LOCATION = "Location"


class DataSource(Enum):
    NEXTCLOUD = "NEXTCLOUD"
    EXCEL = "EXCEL"


@dataclass(frozen=True)
class FileConfig:
    file_type: FileType
    tables: List[TableName]
    path: str


# Define all supported file configurations
FILE_CONFIGS = {
    FileType.INCOME: FileConfig(
        file_type=FileType.INCOME,
        tables=[TableName.INCOME, TableName.DEDUCTIONS],
        path=os.getenv("EXCEL_PATH_INCOME", default="/app/data/income.xlsx")
    ),
    FileType.SPENDING: FileConfig(
        file_type=FileType.SPENDING,
        tables=[
            TableName.SPENDING,
            TableName.TOP,
            TableName.MIDDLE,
            TableName.BASE,
            TableName.LOCATION,
        ],
        path=os.getenv("EXCEL_PATH_SPENDING", default="/app/data/spending.xlsx")
    ),
    FileType.RECEIPT: FileConfig(
        file_type=FileType.RECEIPT,
        tables=[],
        path=os.getenv("RECEIPT_PATH", default="/app/data/receipts")
    )
}


def remove_unnamed_columns(df: DataFrame) -> DataFrame:
    """Remove auto-generated unnamed columns from DataFrame."""
    return df.loc[:, ~df.columns.str.contains('^Unnamed')]


class DataManipulator:
    """Handles data storage operations for Excel and Nextcloud."""

    def __init__(self):
        self.lock_dir = "locks"
        self.LOCK_TIMEOUT = 10
        self.receipt_share_id = os.getenv("NEXTCLOUD_RECEIPT_SHARE_ID")
        self.receipt_share_password = os.getenv("NEXTCLOUD_RECEIPT_SHARE_PASSWORD")
        self.spending_share_id = os.getenv("NEXTCLOUD_SPENDING_SHARE_ID")
        self.spending_share_password = os.getenv("NEXTCLOUD_SPENDING_SHARE_PASSWORD")
        self.income_share_id = os.getenv("NEXTCLOUD_INCOME_SHARE_ID")
        self.income_share_password = os.getenv("NEXTCLOUD_INCOME_SHARE_PASSWORD")
        self.nextcloud_url = os.getenv("NEXTCLOUD_BASE_URL")
        self.datasource = DataSource(os.getenv("DATASOURCE", default="EXCEL"))

    @staticmethod
    def fetch_data_from_excel(file_type: FileType) -> Dict[str, DataFrame]:
        """Fetch data from Excel file."""
        config = FILE_CONFIGS.get(file_type)
        return pd.read_excel(
            config.path,
            sheet_name=[x.value for x in config.tables]
        )

    def fetch_data_from_nextcloud(self, file_type: FileType) -> Dict[str, DataFrame]:
        """Fetch data from Nextcloud share."""
        share_id, share_password = self.get_nextcloud_share_id_password(file_type)
        response = requests.get(
            url=f"https://{self.nextcloud_url}/public.php/dav/files/{share_id}",
            auth=HTTPBasicAuth(username=share_id, password=share_password),
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        if response.status_code != 200:
            raise LookupError(f"Unable to fetch data from Nextcloud: {response.status_code}")
        return pd.read_excel(BytesIO(response.content))

    def get_nextcloud_share_id_password(self, file_type: FileType):
        """Get Nextcloud credentials for file type."""
        share_id = self.spending_share_id
        share_password = self.spending_share_password
        if file_type == FileType.INCOME:
            share_id = self.income_share_id
            share_password = self.income_share_password
        if file_type == FileType.RECEIPT:
            share_id = self.receipt_share_id
            share_password = self.receipt_share_password
        if share_id is None:
            raise ValueError("No nextcloud share specified")
        if share_password is None:
            raise ValueError("No nextcloud share password specified")
        if self.nextcloud_url is None:
            raise ValueError("No nextcloud url specified")
        return share_id, share_password

    def fetch_backing_table(self, file_type: FileType) -> Dict[str, DataFrame]:
        """Fetch data from configured data source."""
        if self.datasource == DataSource.NEXTCLOUD:
            return self.fetch_data_from_nextcloud(file_type=file_type)
        if self.datasource == DataSource.EXCEL:
            return self.fetch_data_from_excel(file_type=file_type)
        raise ValueError("Invalid datasource specified")

    def save_backing_table(
        self,
        file_type: FileType,
        table_name: TableName,
        dataframe: DataFrame = None
    ):
        """Save data to configured data source with file locking."""
        lock_path = self.get_lock_path(file_type, table_name)
        lock = FileLock(lock_path, timeout=10)
        try:
            with lock:
                if self.datasource == DataSource.NEXTCLOUD:
                    return self.save_table_to_nextcloud(
                        file_type=file_type,
                        table_name=table_name,
                        dataframe_to_save=dataframe
                    )
                if self.datasource == DataSource.EXCEL:
                    return self.save_table_to_excel(
                        file_type=file_type,
                        table_name=table_name,
                        df=dataframe
                    )
                raise ValueError("Invalid datasource specified")
        except Timeout:
            raise ValueError(
                f"Another user is currently saving {file_type}:{table_name}. Try again soon."
            )

    def fetch_income_table(self) -> Dict[str, DataFrame]:
        """Fetch income data."""
        return self.fetch_backing_table(FileType.INCOME)

    def fetch_spending_table(self) -> Dict[str, DataFrame]:
        """Fetch spending data."""
        return self.fetch_backing_table(FileType.SPENDING)

    def save_table_to_nextcloud(
        self,
        file_type: FileType,
        table_name: TableName,
        dataframe_to_save: DataFrame = None
    ):
        """Save table to Nextcloud share."""
        existing_dataframes = self.fetch_data_from_nextcloud(file_type)
        if table_name.value not in existing_dataframes.keys():
            raise LookupError(
                f"Table {table_name} does not exist in file: {existing_dataframes.keys()}"
            )
        existing_dataframes[table_name.value] = dataframe_to_save

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for sheet_name, df in existing_dataframes.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)
        binary_output = output.getvalue()
        share_id, share_password = self.get_nextcloud_share_id_password(file_type)
        response = requests.put(
            url=f"https://{self.nextcloud_url}/public.php/dav/files/{share_id}",
            auth=HTTPBasicAuth(username=share_id, password=share_password),
            headers={"X-Requested-With": "XMLHttpRequest"},
            data=binary_output
        )
        if response.status_code != 200:
            raise LookupError(f"Unable to save to Nextcloud: {response.status_code}")

    @staticmethod
    def save_table_to_excel(
        file_type: FileType,
        table_name: TableName,
        df: DataFrame = None
    ):
        """Save table to Excel file."""
        file_config = FILE_CONFIGS.get(file_type)
        file_path = file_config.path
        if file_path is None:
            raise ValueError("file_path was not set properly")
        if df is None:
            raise ValueError("Dataframe is empty")
        if table_name not in file_config.tables:
            raise ValueError(
                f"Invalid table name ({table_name}) for file ({file_type})"
            )
        with pd.ExcelWriter(
            file_path,
            mode='a',
            if_sheet_exists='replace',
            engine='openpyxl',
            date_format="YYYY-MM-DD",
            datetime_format="YYYY-MM-DD"
        ) as writer:
            df.to_excel(writer, sheet_name=table_name.value)

    def get_lock_path(self, file_type: FileType, table_name: TableName) -> str:
        """Get path for file lock."""
        os.makedirs(self.lock_dir, exist_ok=True)
        return os.path.join(self.lock_dir, f"{file_type.value}_{table_name.value}.lock")

    def get_datasource(self) -> str:
        """Get current data source name."""
        return self.datasource.value


