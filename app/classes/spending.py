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
        # save_data(self.spending, SPENDING_PATH, SPENDING_SHEET_NAME)
        self.data_manipulator.save_backing_table(FileType.SPENDING, TableName.SPENDING, self.spending)

    def save_location(self):
        # save_data(self.location, SPENDING_PATH, LOCATION)
        self.data_manipulator.save_backing_table(FileType.SPENDING, TableName.LOCATION, self.location)

    def save_hierarchy(self) -> None:
        self.save_top()
        self.save_middle()
        self.save_base()

    def save_top(self) -> None:
        # save_data(self.top_table, SPENDING_PATH, TOP_TABLE)
        self.data_manipulator.save_backing_table(FileType.SPENDING, TableName.TOP, self.top_table)

    def save_middle(self):
        # save_data(self.middle_table, SPENDING_PATH, MIDDLE_TABLE)
        self.data_manipulator.save_backing_table(FileType.SPENDING, TableName.MIDDLE, self.middle_table)

    def save_base(self):
        # save_data(self.base_table, SPENDING_PATH, BASE_TABLE)
        self.data_manipulator.save_backing_table(FileType.SPENDING, TableName.BASE, self.base_table)

    @st.cache_data
    def fetch_spending_data(_self):
        # Data ingest and basic prep hello
        fetched_data = _self.data_manipulator.fetch_backing_table(FileType.SPENDING)
        _self.spending = remove_unnamed_columns(fetched_data['Spending'])
        _self.location=(remove_unnamed_columns(fetched_data['Location']))
        _self.base_table=(remove_unnamed_columns(fetched_data['Base Table']))
        _self.middle_table=(remove_unnamed_columns(fetched_data['Middle Table']))
        _self.top_table=(remove_unnamed_columns(fetched_data['Top_Table']))    # spending_data = pd.read_excel(
        #     SPENDING_PATH,
        #     sheet_name=[SPENDING_SHEET_NAME, TOP_TABLE, MIDDLE_TABLE, BASE_TABLE, LOCATION]
        #
        # return SpendingData(DataManipulator(),
        #                     spending=(remove_unnamed_columns(spending_data['Spending'])),
        #                     location=(remove_unnamed_columns(spending_data['Location'])),
        #                     base_table=(remove_unnamed_columns(spending_data['Base Table'])),
        #                     middle_table=(remove_unnamed_columns(spending_data['Middle Table'])),
        #                     top_table=(remove_unnamed_columns(spending_data['Top_Table'])))
        return _self
