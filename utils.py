import os
from dataclasses import dataclass
from io import StringIO
from typing import List

import altair as alt
import pandas as pd
import requests
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

INCOME_SHEET_NAME = "Income"
INCOME_DATA_SCHEMA = [
    "Gross Income",
    "Salary Sacrifice",
    "Tax",
    "Income",
    "Date",
    "Employer",
    "Description",
    "Taxable",
    "Received in bank account",
    "Comment"
]
YES_NO_OPTIONS = ["Yes", "No"]


@dataclass
class IncomeEntry:
    """Represents an income entry."""
    gross_income: float
    salary_sacrifice: float
    tax: float
    income: float
    date: pd.Timestamp
    employer: str
    description: str
    taxable: str
    received_in_bank_account: str
    comment: str

    @classmethod
    def from_Series(self, row: pd.Series):
        """Creates an IncomeEntry from a DataFrame row (df.iloc[index])."""
        self.gross_income = row["Gross Income"]
        self.salary_sacrifice = row["Salary Sacrifice"]
        self.tax = row["Tax"]
        self.income = row["Income"]
        self.date = pd.to_datetime(row["Date"])
        self.employer = row["Employer"]
        self.description = row["Description"]
        self.taxable = row["Taxable"]
        self.received_in_bank_account = row["Received in bank account"]
        self.comment = row["Comment"]
        return self

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([{
            "Gross Income": self.gross_income,
            "Salary Sacrifice": self.salary_sacrifice,
            "Tax": self.tax,
            "Income": self.income,
            "Date": self.date,
            "Employer": self.employer,
            "Description": self.description,
            "Taxable": self.taxable,
            "Received in bank account": self.received_in_bank_account,
            "Comment": self.comment,
        }])

    @classmethod
    def builder(self):
        return IncomeEntryBuilder()


class IncomeEntryBuilder:
    def __init__(self):
        self._data = {}

    def gross_income(self, value: float):
        self._data["gross_income"] = value
        return self

    def salary_sacrifice(self, value: float):
        self._data["salary_sacrifice"] = value
        return self

    def tax(self, value: float):
        self._data["tax"] = value
        return self

    def income(self, value: float):
        self._data["income"] = value
        return self

    def date(self, value: pd.Timestamp):
        self._data["date"] = value
        return self

    def employer(self, value: str):
        self._data["employer"] = value
        return self

    def description(self, value: str):
        self._data["description"] = value
        return self

    def taxable(self, value: int):
        self._data["taxable"] = value
        return self

    def received_in_bank_account(self, value: bool):
        self._data["received_in_bank_account"] = value
        return self

    def comment(self, value: str):
        self._data["comment"] = value
        return self

    def build(self) -> IncomeEntry:
        return IncomeEntry(**self._data)


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
    def from_dataframe(self, row: pd.Series):
        """Creates a SpendingEntry from a DataFrame row (df.iloc[index])."""
        self.item = row["Item"]
        self.cost = row["Cost"]
        self.quantity = row["Quantity"]
        self.measure = row["Measure"]
        self.location = row["Location"]
        self.shop = row["Shop"]
        self.details = row["Details"]
        self.tag = row["Tag"]
        self.date = pd.to_datetime(row["Date"])
        self.receipt_ref = row["Receipt Ref"]
        self.receipt = row["Receipt"]
        self.transaction_id = row["transactionId"]


TAXABLE_OPTIONS = ["Not-taxable", "Taxable", "Franked Dividends"]
INCOME_PATH = os.getenv("EXCEL_PATH_INCOME", default="/app/data/income.xlsx")
EXPENSE_MANAGER_URL = os.getenv("EXPENSE_MANAGER_URL", default="http://localhost:8080")
RECEIPT_PATH = os.getenv("RECEIPT_PATH", default="/app/data/receipts")


def remove_unnamed_columns(df):
    return df.loc[:, ~df.columns.str.contains('^Unnamed')]


def calculate_financial_year(date):
    # Adjust year based on whether the month is July or later
    if pd.isna(date):
        return None  # Handle missing dates
    year = date.year
    if date.month >= 7:
        return f"FY {year}/{year + 1}"
    else:
        return f"FY {year - 1}/{year}"


@st.cache_data
def fetch_income_deduction_data():
    income_sheets = pd.read_excel(
        INCOME_PATH,
        sheet_name=["Income", "Deductions"]
    )
    income_data = remove_unnamed_columns(income_sheets['Income'])
    income_data.loc[:, ["Salary Sacrifice", "Tax"]] = income_data.loc[:,
                                                      ["Salary Sacrifice", "Tax"]
                                                      ].fillna(0)
    income_data.loc[:, "Financial Year"] = pd.to_datetime(
        income_data.loc[:, 'Date']).apply(calculate_financial_year)
    income_data.loc[:, 'Taxable Income'] = income_data.apply(
        lambda row: (
            row['Gross Income'] - row['Salary Sacrifice']
            if row['Taxable'] == 'Taxable' else
            row['Gross Income'] + row['Tax']
            if row['Taxable'] == 'Franked Dividends' else
            0
        ),
        axis=1
    )

    deduction_data = remove_unnamed_columns(income_sheets['Deductions'])
    deduction_data["Financial Year"] = pd.to_datetime(
        deduction_data['Date']
    ).apply(calculate_financial_year)
    return income_data, deduction_data


def date_sidebar(
    st: DeltaGenerator,
    df: pd.DataFrame,
    date_key: str,
    start_at_minimum=False
):
    minimum_date = df[date_key].min()
    maximum_date = df[date_key].max()
    start_date_initial_value = maximum_date - pd.DateOffset(months=1)
    if start_at_minimum:
        start_date_initial_value = minimum_date

    start_date = st.sidebar.date_input(
        "Start Date",
        value=start_date_initial_value,
        min_value=minimum_date,
        max_value=maximum_date)
    end_date = st.sidebar.date_input(
        "End Date",
        value=maximum_date,
        min_value=minimum_date,
        max_value=maximum_date)
    return start_date, end_date


def plot_bar_chart(dataframe, x_column, y_column, title, max_items=20):
    """Helper function to generate a bar chart with custom axis formatting."""
    chart_data = (
        dataframe.groupby(x_column)[y_column]
        .sum()
        .reset_index()
        .sort_values(by=y_column, ascending=False)
        .head(max_items)
    )
    select = alt.selection_point(name="select", on="click")
    highlight = alt.selection_point(name="highlight", on="pointerover", empty=False)
    stroke_width = (
        alt.when(select).then(alt.value(2, empty=False))
        .when(highlight).then(alt.value(1))
        .otherwise(alt.value(0))
    )
    return (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X(
                x_column,
                sort=None,
                title=title,
                axis=alt.Axis(labelAngle=-30, labelOverlap=False),
            ),
            y=alt.Y(
                y_column,
                title="Total Cost",
                axis=alt.Axis(labelExpr='"$" + datum.value'),
            ),
            fillOpacity=alt.when(select).then(alt.value(1)).otherwise(alt.value(0.3)),
            strokeWidth=stroke_width,
        ).configure_scale(bandPaddingInner=0.2).add_params(select, highlight)
    )


def format_income_table(dataframe: pd.DataFrame, column_names=(
    "Gross Income",
    "Salary Sacrifice",
    "Taxable Income",
    "Income",
    "Tax")):
    dataframe_formatted = dataframe.style.format(
        {columnname: '${:,.2f}' for columnname in column_names}
    )
    return dataframe_formatted


# Fetch the data from Upbank Client as a csv then read into a dataframe
@st.cache_data
def fetch_transaction_data(
    start_date=pd.Timestamp.today() - pd.DateOffset(months=1),
    end_date=pd.Timestamp.today() + pd.DateOffset(days=1)
):
    csv_endpoint = "/api/v1/transactions/csv"
    params = {
        "startDate": f"{start_date.strftime('%Y-%m-%d')}T00:00:00.000Z",
        "endDate": f"{end_date.strftime('%Y-%m-%d')}T00:00:00.000Z",
        "numTransactions": 10000,
        "accountId": "a90b55ad-1bcb-4e75-b407-0e0e1e5c8a6d",
        # We need EFTPOS Deposit for BeemIt transactions as they are processed using EFTPOS
        # Direct credit is how some refunds appear
        "transactionTypes": ['Payment', 'Purchase', 'Refund', 'EFTPOS Deposit', 'Direct Credit']
    }
    try:
        # Fetch the CSV data
        response = requests.get(EXPENSE_MANAGER_URL + csv_endpoint, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Convert CSV response to a pandas DataFrame
        csv_data = response.content.decode("utf-8")
        dataframe = pd.read_csv(StringIO(csv_data))
        return clean_transaction_data(dataframe)

    except requests.exceptions.RequestException as e:
        st.error(
            f"Please check that the service is running successfully at {EXPENSE_MANAGER_URL}.\n\n An error occurred while fetching the data: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame()


def clean_transaction_data(transaction_data: pd.DataFrame):
    clean = transaction_data.rename(columns={
        "Category": "Upbank Category",
        "empty": "Quantity",
        "Empty": "Measure",
        "rawText": "Upbank Text",
        "description": "Shop",
        "empty_1": "Details",
        "empty_2": "Tag",
        "createdAt": "Date"
    })
    clean['Cost'] = clean['Cost'] * -1
    clean['Item'] = pd.Series(dtype='str')
    clean['Location'] = pd.Series(dtype='str')
    clean['Date'] = pd.to_datetime(clean['Date'])
    clean['Details'] = clean['Details'].dropna().astype(str)
    clean['Tag'] = clean['Tag'].dropna().astype(str)
    return clean


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


def find_index_in_list(list: List[str], search_value: str) -> int:
    for i, val in enumerate(list):
        if val == search_value:
            return i
    return 0
