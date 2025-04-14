import os
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from typing import List
from filelock import FileLock, Timeout

import pandas as pd
import requests
from pandas import DataFrame
from requests.auth import HTTPBasicAuth

SPENDING_FILE = "SPENDING"
INCOME_FILE = "INCOME"
SPENDING_SHEET_NAME = "Spending"
MIDDLE_TABLE = "Middle Table"
TOP_TABLE = "Top_Table"
BASE_TABLE = "Base Table"
LOCATION = "Location"
INCOME_SHEET_NAME = "Income"

FILENAME_SHEETS = {
    INCOME_FILE: [INCOME_SHEET_NAME, "Deductions"],
    SPENDING_FILE: [SPENDING_SHEET_NAME, TOP_TABLE, MIDDLE_TABLE, BASE_TABLE, LOCATION]
}
VALID_FILENAMES = [INCOME_FILE, SPENDING_FILE]

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

class DataManipulator:
    def __init__(self):
        self.lock_dir = "locks"
        self.LOCK_TIMEOUT = 10
        self.LOCK_PATH = None
        self.receipt_share_id = os.getenv("NEXTCLOUD_RECEIPT_SHARE_ID")
        self.receipt_share_password = os.getenv("NEXTCLOUD_RECEIPT_SHARE_PASSWORD")
        self.spending_share_id = os.getenv("NEXTCLOUD_SPENDING_SHARE_ID")
        self.spending_share_password = os.getenv("NEXTCLOUD_SPENDING_SHARE_PASSWORD")
        self.income_share_id = os.getenv("NEXTCLOUD_INCOME_SHARE_ID")
        self.income_share_password = os.getenv("NEXTCLOUD_INCOME_SHARE_PASSWORD")
        self.nextcloud_url = os.getenv("NEXTCLOUD_BASE_URL")
        self.nextcloud_upload_share_id = os.getenv("NEXTCLOUD")
        self.datasource = DataSource(os.getenv("DATASOURCE", default="EXCEL"))

    @staticmethod
    def fetch_data_from_excel(file_type: FileType) -> dict[str, DataFrame]:
        return pd.read_excel(
            FILE_CONFIGS.get(file_type).path,
            sheet_name=[x.value for x in FILE_CONFIGS.get(file_type).tables])


    def fetch_data_from_nextcloud(self, file_type: FileType) -> dict[str, DataFrame]:
        share_id, share_password = self.get_nextcloud_share_id_password(file_type)
        response = requests.request(
            method="GET",
            url=f"https://{self.nextcloud_url}/public.php/dav/files/{share_id}",
            auth=HTTPBasicAuth(
                username=share_id,
                password=share_password
            ),
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        if not response == "200":
            raise LookupError("Unable to fetch data from nextcloud")
        return pd.read_excel(BytesIO(response.content)) # Fetching all tables from Excel

    def get_nextcloud_share_id_password(self, file_type: FileType):
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
            raise ValueError("No nextcloud share password specified - only password protected shares are supported")
        if self.nextcloud_url is None:
            raise ValueError("No nextcloud url specified")
        return share_id, share_password

    def fetch_backing_table(self, file_type:FileType) -> dict[str, DataFrame]:
        if self.datasource == DataSource.NEXTCLOUD:
            return self.fetch_data_from_nextcloud(file_type=file_type)
        if self.datasource == DataSource.EXCEL:
            return self.fetch_data_from_excel(file_type=file_type)
        raise ValueError("Invalid datasource specified")

    def save_backing_table(self, file_type: FileType, table_name: TableName, dataframe: DataFrame = None):
        lock_path = self.get_lock_path(file_type, table_name)
        lock = FileLock(lock_path, timeout=10)
        try:
            with lock:
                if self.datasource == DataSource.NEXTCLOUD:
                    return self.save_table_to_nextcloud(file_type=file_type, table_name=table_name,
                                                        dataframe_to_save=dataframe)
                if self.datasource == DataSource.EXCEL:
                    return self.save_table_to_excel(file_type=file_type, table_name=table_name, df=dataframe)
                raise ValueError("Invalid datasource specified")
        except Timeout:
            raise ValueError(f"Another user is currently saving {file_type}:{table_name}. Try again soon.")



    def fetch_income_table(self):
        return self.fetch_backing_table(FileType.INCOME)

    def fetch_spending_table(self):
        return self.fetch_backing_table(FileType.SPENDING)

    def save_table_to_nextcloud(self, file_type: FileType, table_name: TableName, dataframe_to_save: DataFrame = None):
        existing_dataframes = self.fetch_data_from_nextcloud(file_type)
        if table_name.value not in existing_dataframes.keys():
            raise LookupError(f"desired table_name: {table_name} does not exist within file: {existing_dataframes.keys()}")
        existing_dataframes[table_name.value] = dataframe_to_save

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for sheet_name, df in existing_dataframes.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)
        binary_output = output.getvalue()
        share_id, share_password = self.get_nextcloud_share_id_password(file_type)
        response = requests.request(
            method="PUT",
            url=f"https://{self.nextcloud_url}/public.php/dav/files/{share_id}",
            auth=HTTPBasicAuth(
                username=share_id,
                password=share_password
            ),
            headers={"X-Requested-With": "XMLHttpRequest"},
            data=binary_output
        )
        if not response == "200":
            raise LookupError("Unable to fetch data from nextcloud")



    @staticmethod
    def save_table_to_excel(file_type: FileType, table_name: TableName, df: DataFrame = None):
        file_config = FILE_CONFIGS.get(file_type)
        file_path = file_config.path
        if file_path is None:
            raise ValueError("file_path was not set properly - not saving data to excel")
        if df is None:
            raise ValueError("Dataframe is empty - not saving data to excel")
        if table_name not in file_config.tables:
            raise ValueError(f"Invalid table name ({table_name}) supplied for the corresponding filename ({file_type})")
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
        # Clean or hash the file_type and table_name if needed
        os.makedirs(self.lock_dir, exist_ok=True)
        return os.path.join(self.lock_dir, f"{file_type.value}_{table_name.value}.lock")


def remove_unnamed_columns(df):
    return df.loc[:, ~df.columns.str.contains('^Unnamed')]
