"""Spending data service."""
from typing import Optional, Dict, List
from datetime import datetime

import pandas as pd
from pandas import DataFrame

from .datamanipulator import (
    DataManipulator,
    FileType,
    TableName,
    remove_unnamed_columns,
    get_data_manipulator,
)

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


class SpendingService:
    """Service for managing spending data."""

    def __init__(self, data_manipulator: DataManipulator = None):
        self.data_manipulator = data_manipulator or get_data_manipulator()
        self._spending: Optional[DataFrame] = None
        self._location: Optional[DataFrame] = None
        self._base_table: Optional[DataFrame] = None
        self._middle_table: Optional[DataFrame] = None
        self._top_table: Optional[DataFrame] = None
        self._combined: Optional[DataFrame] = None

    def fetch_all(self) -> "SpendingService":
        """Fetch all spending data from storage."""
        fetched_data = self.data_manipulator.fetch_backing_table(FileType.SPENDING)
        self._spending = remove_unnamed_columns(fetched_data['Spending'])
        self._location = remove_unnamed_columns(fetched_data['Location'])
        self._base_table = remove_unnamed_columns(fetched_data['Base Table'])
        self._middle_table = remove_unnamed_columns(fetched_data['Middle Table'])
        self._top_table = remove_unnamed_columns(fetched_data['Top_Table'])
        return self

    @property
    def spending(self) -> DataFrame:
        if self._spending is None:
            self.fetch_all()
        return self._spending

    @property
    def location(self) -> DataFrame:
        if self._location is None:
            self.fetch_all()
        return self._location

    @property
    def base_table(self) -> DataFrame:
        if self._base_table is None:
            self.fetch_all()
        return self._base_table

    @property
    def middle_table(self) -> DataFrame:
        if self._middle_table is None:
            self.fetch_all()
        return self._middle_table

    @property
    def top_table(self) -> DataFrame:
        if self._top_table is None:
            self.fetch_all()
        return self._top_table

    def get_combined(self) -> DataFrame:
        """Get spending data with hierarchy and location merged."""
        if self._combined is not None:
            return self._combined

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
        self._combined = df
        return self._combined

    def get_spending_list(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        shops: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None,
    ) -> List[Dict]:
        """Get filtered spending entries."""
        df = self.get_combined()

        # Apply filters
        if start_date:
            df = df[df['Date'] >= pd.Timestamp(start_date)]
        if end_date:
            df = df[df['Date'] <= pd.Timestamp(end_date)]
        if tags:
            df = df[df['Tag'].isin(tags)]
        if shops:
            df = df[df['Shop'].isin(shops)]
        if locations:
            df = df[df['Location'].isin(locations)]
        if categories:
            df = df[df['Category'].isin(categories)]
        if sub_categories:
            df = df[df['Sub Category'].isin(sub_categories)]

        return df.to_dict(orient='records')

    def get_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """Get spending summary statistics."""
        df = self.get_combined()

        if start_date:
            df = df[df['Date'] >= pd.Timestamp(start_date)]
        if end_date:
            df = df[df['Date'] <= pd.Timestamp(end_date)]

        # Count uncategorized (items without category)
        uncategorized = df[df['Category'].isna()].shape[0]

        # Aggregations
        by_category = df.groupby('Category')['Cost'].sum().to_dict()
        by_shop = df.groupby('Shop')['Cost'].sum().to_dict()
        by_tag = df.groupby('Tag')['Cost'].sum().to_dict()

        return {
            "total_cost": float(df['Cost'].sum()),
            "transaction_count": len(df),
            "latest_transaction_date": df['Date'].max().isoformat() if len(df) > 0 else None,
            "uncategorized_count": uncategorized,
            "by_category": by_category,
            "by_shop": by_shop,
            "by_tag": by_tag,
        }

    def get_recent_spending(self, days: int = 30) -> Dict:
        """Get spending summary for recent days."""
        end_date = pd.Timestamp.today()
        start_date = end_date - pd.DateOffset(days=days)
        return self.get_summary(start_date=start_date.date(), end_date=end_date.date())

    def create_entry(self, entry_data: Dict) -> Dict:
        """Create a new spending entry."""
        df = self.spending.copy()

        # Create new row
        new_row = pd.DataFrame([{
            "Item": entry_data.get("item"),
            "Cost": entry_data.get("cost"),
            "Quantity": entry_data.get("quantity"),
            "Measure": entry_data.get("measure"),
            "Location": entry_data.get("location"),
            "Shop": entry_data.get("shop"),
            "Details": entry_data.get("details"),
            "Tag": entry_data.get("tag"),
            "Date": pd.Timestamp(entry_data.get("date")),
            "Receipt Ref": entry_data.get("receipt_ref"),
            "Receipt": entry_data.get("receipt"),
            "transactionId": entry_data.get("transaction_id"),
        }])

        self._spending = pd.concat([df, new_row], ignore_index=True)
        self._combined = None  # Invalidate cache
        self.save_spending()

        return new_row.to_dict(orient='records')[0]

    def update_entry(self, index: int, entry_data: Dict) -> Dict:
        """Update an existing spending entry."""
        df = self.spending.copy()

        if index >= len(df):
            raise ValueError(f"Invalid index: {index}")

        for key, value in entry_data.items():
            col_map = {
                "item": "Item",
                "cost": "Cost",
                "quantity": "Quantity",
                "measure": "Measure",
                "location": "Location",
                "shop": "Shop",
                "details": "Details",
                "tag": "Tag",
                "date": "Date",
                "receipt_ref": "Receipt Ref",
            }
            if key in col_map and value is not None:
                col = col_map[key]
                if col == "Date":
                    value = pd.Timestamp(value)
                df.at[index, col] = value

        self._spending = df
        self._combined = None  # Invalidate cache
        self.save_spending()

        return df.iloc[index].to_dict()

    def delete_entry(self, index: int) -> bool:
        """Delete a spending entry."""
        df = self.spending.copy()

        if index >= len(df):
            raise ValueError(f"Invalid index: {index}")

        self._spending = df.drop(index).reset_index(drop=True)
        self._combined = None  # Invalidate cache
        self.save_spending()

        return True

    def save_spending(self):
        """Save spending table to storage."""
        self.data_manipulator.save_backing_table(
            FileType.SPENDING,
            TableName.SPENDING,
            self._spending
        )

    def save_location(self):
        """Save location table to storage."""
        self.data_manipulator.save_backing_table(
            FileType.SPENDING,
            TableName.LOCATION,
            self._location
        )

    def save_hierarchy(self):
        """Save all hierarchy tables."""
        self.data_manipulator.save_backing_table(
            FileType.SPENDING,
            TableName.TOP,
            self._top_table
        )
        self.data_manipulator.save_backing_table(
            FileType.SPENDING,
            TableName.MIDDLE,
            self._middle_table
        )
        self.data_manipulator.save_backing_table(
            FileType.SPENDING,
            TableName.BASE,
            self._base_table
        )

    def get_unique_values(self, column: str) -> List[str]:
        """Get unique values for a column."""
        df = self.get_combined()
        if column not in df.columns:
            return []
        return df[column].dropna().unique().tolist()

    def invalidate_cache(self):
        """Clear cached data to force refresh."""
        self._spending = None
        self._location = None
        self._base_table = None
        self._middle_table = None
        self._top_table = None
        self._combined = None


# Service instance cache
_spending_service: Optional[SpendingService] = None


def get_spending_service() -> SpendingService:
    """Get or create spending service instance."""
    global _spending_service
    if _spending_service is None:
        _spending_service = SpendingService()
    return _spending_service


def invalidate_spending_cache():
    """Invalidate spending service cache."""
    global _spending_service
    if _spending_service:
        _spending_service.invalidate_cache()
