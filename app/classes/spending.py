from dataclasses import dataclass

import pandas as pd
import streamlit as st

from .datamanipulator import DataManipulator, FileType, TableName, remove_unnamed_columns

SPENDING_DATA_SCHEMA = [
    "Item",
    "Cost",
    "Quantity",
    "Measure",
    "Location",
    "Shop",
    "Details",
    "Tag",
    "Date",
    "Receipt Ref",
    "Receipt",
    "transactionId"
]


def save_data(df: pd.DataFrame, file_path: str, sheet_name: str):
    with pd.ExcelWriter(
            file_path,
            mode='a',
            if_sheet_exists='replace',
            engine='openpyxl',
            date_format="YYYY-MM-DD",
            datetime_format="YYYY-MM-DD"
    ) as writer:
        df.to_excel(
            writer,
            sheet_name=sheet_name,
        )


class SpendingData:
    def __init__(self, data_manipulator: DataManipulator, spending: pd.DataFrame = None, location: pd.DataFrame = None,
                 base_table: pd.DataFrame = None, middle_table: pd.DataFrame = None, top_table: pd.DataFrame = None):
        """Initialize with preloaded tables."""
        self.data_manipulator = data_manipulator
        self.spending = spending
        self.location = location
        self.base_table = base_table
        self.middle_table = middle_table
        self.top_table = top_table
        self.combined = pd.DataFrame()

    def combine(self):
        """Return the enriched spending data with all hierarchy tables merged."""
        hierarchy = (
            self.base_table
            .rename(columns={'All Items': 'Item'})
            .merge(self.middle_table, on="Sub Sub Category")
            .merge(self.top_table, on="Sub Category")
        )
        df = (
            self.spending
            .merge(hierarchy, on='Item', how='left')
            .merge(self.location, on='Location', how='left')
        )
        # Ensure specific columns are strings
        df['Details'] = df['Details'].astype(str)
        df['Tag'] = df['Tag'].astype(str)
        df['Measure'] = df['Measure'].astype(str)
        self.combined = df
        return self

    def save_spending(self):
        self.data_manipulator.save_backing_table(FileType.SPENDING, TableName.SPENDING, self.spending)

    def save_location(self):
        self.data_manipulator.save_backing_table(FileType.SPENDING, TableName.LOCATION, self.location)

    def save_hierarchy(self) -> None:
        self.save_top()
        self.save_middle()
        self.save_base()

    def save_top(self) -> None:
        self.data_manipulator.save_backing_table(FileType.SPENDING, TableName.TOP, self.top_table)

    def save_middle(self):
        self.data_manipulator.save_backing_table(FileType.SPENDING, TableName.MIDDLE, self.middle_table)

    def save_base(self):
        self.data_manipulator.save_backing_table(FileType.SPENDING, TableName.BASE, self.base_table)

    @st.cache_data
    def fetch_spending_data(_self):
        # Data ingest and basic prep hello
        fetched_data = _self.data_manipulator.fetch_backing_table(FileType.SPENDING)
        _self.spending = remove_unnamed_columns(fetched_data['Spending'])
        _self.location = (remove_unnamed_columns(fetched_data['Location']))
        _self.base_table = (remove_unnamed_columns(fetched_data['Base Table']))
        _self.middle_table = (remove_unnamed_columns(fetched_data['Middle Table']))
        _self.top_table = (remove_unnamed_columns(fetched_data['Top_Table']))
        return _self


@dataclass
class SpendingEntry:
    """Represents a spending entry."""
    item: str
    cost: float
    quantity: float
    measure: str
    location: str
    shop: str
    details: str
    tag: str
    date: pd.Timestamp
    receipt_ref: str
    receipt: str
    transaction_id: str

    @classmethod
    def from_dataframe(cls, row: pd.Series):
        """Creates a SpendingEntry from a DataFrame row (df.iloc[index])."""
        cls.item = row["Item"]
        cls.cost = row["Cost"]
        cls.quantity = row["Quantity"]
        cls.measure = row["Measure"]
        cls.location = row["Location"]
        cls.shop = row["Shop"]
        cls.details = row["Details"]
        cls.tag = row["Tag"]
        cls.date = pd.to_datetime(row["Date"])
        cls.receipt_ref = row["Receipt Ref"]
        cls.receipt = row["Receipt"]
        cls.transaction_id = row["transactionId"]
