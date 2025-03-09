import os

import pandas as pd
import streamlit as st

from utils import remove_unnamed_columns

SPENDING_SHEET_NAME = "Spending"
MIDDLE_TABLE = "Middle Table"
TOP_TABLE = "Top_Table"
BASE_TABLE = "Base Table"
LOCATION = "Location"
SPENDING_PATH = os.getenv("EXCEL_PATH_SPENDING", default="/app/data/spending.xlsx")
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
    def __init__(self, spending: pd.DataFrame = None, location: pd.DataFrame = None,
                 base_table: pd.DataFrame = None, middle_table: pd.DataFrame = None,
                 top_table: pd.DataFrame = None):
        """Initialize with preloaded tables."""
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
        save_data(self.spending, SPENDING_PATH, SPENDING_SHEET_NAME)

    def save_location(self):
        save_data(self.location, SPENDING_PATH, LOCATION)

    def save_hierarchy(self) -> None:
        self.save_top()
        self.save_middle()
        self.save_base()

    def save_top(self) -> None:
        save_data(self.top_table, SPENDING_PATH, TOP_TABLE)

    def save_middle(self):
        save_data(self.middle_table, SPENDING_PATH, MIDDLE_TABLE)

    def save_base(self):
        save_data(self.base_table, SPENDING_PATH, BASE_TABLE)

    @st.cache_data
    def fetch_spending_data(_self):
        # Data ingest and basic prep hello
        spending_data = pd.read_excel(
            SPENDING_PATH,
            sheet_name=[SPENDING_SHEET_NAME, TOP_TABLE, MIDDLE_TABLE, BASE_TABLE, LOCATION])

        return SpendingData(
            spending=(remove_unnamed_columns(spending_data['Spending'])),
            top_table=(remove_unnamed_columns(spending_data['Top_Table'])),
            middle_table=(remove_unnamed_columns(spending_data['Middle Table'])),
            base_table=(remove_unnamed_columns(spending_data['Base Table'])),
            location=(remove_unnamed_columns(spending_data['Location']))
        )
