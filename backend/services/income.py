"""Income data service."""
from typing import Optional, Dict, List
from datetime import datetime

import pandas as pd
from pandas import DataFrame

from .datamanipulator import (
    DataManipulator,
    FileType,
    TableName,
    remove_unnamed_columns,
)


def calculate_financial_year(dt: datetime) -> Optional[str]:
    """Calculate Australian financial year from date."""
    if pd.isna(dt):
        return None
    year = dt.year
    if dt.month >= 7:
        return f"FY {year}/{year + 1}"
    else:
        return f"FY {year - 1}/{year}"


class IncomeService:
    """Service for managing income data."""

    def __init__(self, data_manipulator: DataManipulator):
        self.data_manipulator = data_manipulator
        self._income: Optional[DataFrame] = None
        self._deductions: Optional[DataFrame] = None

    def fetch_all(self) -> "IncomeService":
        """Fetch all income data from storage."""
        fetched_data = self.data_manipulator.fetch_backing_table(FileType.INCOME)
        self._income = remove_unnamed_columns(fetched_data['Income'])
        self._deductions = remove_unnamed_columns(fetched_data['Deductions'])

        # Process income data
        self._income[["Salary Sacrifice", "Tax"]] = self._income[
            ["Salary Sacrifice", "Tax"]
        ].fillna(0)

        # Calculate financial year
        self._income["Financial Year"] = pd.to_datetime(
            self._income["Date"]
        ).apply(lambda d: calculate_financial_year(d.date()) if pd.notna(d) else None)

        # Calculate taxable income
        self._income["Taxable Income"] = self._income.apply(
            lambda row: (
                row["Gross Income"] - row["Salary Sacrifice"]
                if row["Taxable"] == "Taxable"
                else row["Gross Income"] + row["Tax"]
                if row["Taxable"] == "Franked Dividends"
                else 0
            ),
            axis=1
        )

        # Process deductions
        self._deductions["Financial Year"] = pd.to_datetime(
            self._deductions["Date"]
        ).apply(lambda d: calculate_financial_year(d.date()) if pd.notna(d) else None)

        return self

    @property
    def income(self) -> DataFrame:
        if self._income is None:
            self.fetch_all()
        return self._income

    @property
    def deductions(self) -> DataFrame:
        if self._deductions is None:
            self.fetch_all()
        return self._deductions

    def get_income_list(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        employers: Optional[List[str]] = None,
        descriptions: Optional[List[str]] = None,
        financial_years: Optional[List[str]] = None,
    ) -> List[Dict]:
        """Get filtered income entries."""
        df = self.income.copy()

        # Apply filters
        if start_date:
            df = df[pd.to_datetime(df['Date']) >= pd.Timestamp(start_date)]
        if end_date:
            df = df[pd.to_datetime(df['Date']) <= pd.Timestamp(end_date)]
        if employers:
            df = df[df['Employer'].isin(employers)]
        if descriptions:
            df = df[df['Description'].isin(descriptions)]
        if financial_years:
            df = df[df['Financial Year'].isin(financial_years)]

        return df.to_dict(orient='records')

    def get_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """Get income summary statistics."""
        df = self.income.copy()

        if start_date:
            df = df[pd.to_datetime(df['Date']) >= pd.Timestamp(start_date)]
        if end_date:
            df = df[pd.to_datetime(df['Date']) <= pd.Timestamp(end_date)]

        # Aggregations
        by_financial_year = df.groupby('Financial Year').agg({
            'Gross Income': 'sum',
            'Tax': 'sum',
            'Income': 'sum',
            'Taxable Income': 'sum',
        }).to_dict(orient='index')

        by_employer = df.groupby('Employer').agg({
            'Gross Income': 'sum',
            'Income': 'sum',
        }).to_dict(orient='index')

        return {
            "total_gross": float(df['Gross Income'].sum()),
            "total_tax": float(df['Tax'].sum()),
            "total_net": float(df['Income'].sum()),
            "by_financial_year": by_financial_year,
            "by_employer": by_employer,
        }

    def create_entry(self, entry_data: Dict) -> Dict:
        """Create a new income entry."""
        df = self.income.copy()

        new_row = pd.DataFrame([{
            "Gross Income": entry_data.get("gross_income"),
            "Salary Sacrifice": entry_data.get("salary_sacrifice", 0),
            "Tax": entry_data.get("tax", 0),
            "Income": entry_data.get("income"),
            "Date": pd.Timestamp(entry_data.get("date")),
            "Employer": entry_data.get("employer"),
            "Description": entry_data.get("description"),
            "Taxable": entry_data.get("taxable"),
            "Received in bank account": entry_data.get("received_in_bank_account", "Yes"),
            "Comment": entry_data.get("comment"),
        }])

        # Calculate derived fields
        dt = new_row.iloc[0]["Date"]
        new_row["Financial Year"] = calculate_financial_year(dt.date())

        taxable = new_row.iloc[0]["Taxable"]
        gross = new_row.iloc[0]["Gross Income"]
        sacrifice = new_row.iloc[0]["Salary Sacrifice"]
        tax = new_row.iloc[0]["Tax"]

        if taxable == "Taxable":
            new_row["Taxable Income"] = gross - sacrifice
        elif taxable == "Franked Dividends":
            new_row["Taxable Income"] = gross + tax
        else:
            new_row["Taxable Income"] = 0

        self._income = pd.concat([df, new_row], ignore_index=True)
        self.save_income()

        return new_row.to_dict(orient='records')[0]

    def delete_entry(self, index: int) -> bool:
        """Delete an income entry."""
        df = self.income.copy()

        if index >= len(df):
            raise ValueError(f"Invalid index: {index}")

        self._income = df.drop(index).reset_index(drop=True)
        self.save_income()

        return True

    def save_income(self):
        """Save income table to storage."""
        # Remove calculated columns before saving
        save_df = self._income.drop(columns=["Financial Year", "Taxable Income"], errors='ignore')
        self.data_manipulator.save_backing_table(
            FileType.INCOME,
            TableName.INCOME,
            save_df
        )

    def get_unique_values(self, column: str) -> List[str]:
        """Get unique values for a column."""
        df = self.income
        if column not in df.columns:
            return []
        return df[column].dropna().unique().tolist()

    def invalidate_cache(self):
        """Clear cached data to force refresh."""
        self._income = None
        self._deductions = None


