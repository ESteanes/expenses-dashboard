import streamlit as st
import pandas as pd
import os
import altair as alt
from streamlit.delta_generator import DeltaGenerator
from datetime import datetime
import requests
from io import StringIO


SPENDING_SHEET_NAME = "Spending"
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


def dataframe_in_list(df, key, list_items):
    if not list_items:
        return df[key].isin(list_items)
    return df


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
def fetch_spending_data():
    # Data ingest and basic prep hello
    spending_excel_path = os.getenv("EXCEL_PATH_SPENDING")
    spending_data = pd.read_excel(
        spending_excel_path,
        sheet_name=[SPENDING_SHEET_NAME, "Top_Table", "Middle Table", "Base Table", "Location"])
    
    df = remove_unnamed_columns(spending_data['Spending'])
    top_table = remove_unnamed_columns(spending_data['Top_Table'])
    middle_table = remove_unnamed_columns(spending_data['Middle Table'])
    base_table = remove_unnamed_columns(spending_data['Base Table'])
    location = remove_unnamed_columns(spending_data['Location'])
    
    hierarchy = (
        base_table
        .rename(columns={'All Items': 'Item'})
        .merge(middle_table, on="Sub Sub Category")
        .merge(top_table, on="Sub Category")
    )
    df = (
        df
        .merge(hierarchy, on='Item', how='left')
        .merge(location, on='Location', how='left')
    )
    df['Details'] = df['Details'].astype(str)
    return df


@st.cache_data
def fetch_income_deduction_data():
    income_excel_path = os.getenv("EXCEL_PATH_INCOME")
    income_sheets = pd.read_excel(
        income_excel_path,
        sheet_name=["Income", "Deductions"]
    )
    income_data = remove_unnamed_columns(income_sheets['Income'])
    income_data[["Salary Sacrifice", "Tax"]] = income_data[["Salary Sacrifice", "Tax"]].fillna(0)
    income_data["Financial Year"] = pd.to_datetime(income_data['Date']).apply(calculate_financial_year)
    income_data['Taxable Income'] = income_data.apply(
        lambda row: (
            row['Gross Income'] - row['Salary Sacrifice']
            if row['Taxable'] == 1 else
            row['Gross Income'] + row['Tax'])
        if row['Taxable'] == 2
        else 0,
        axis=1
    )

    deduction_data = remove_unnamed_columns(income_sheets['Deductions'])
    deduction_data["Financial Year"] = pd.to_datetime(deduction_data['Date']).apply(calculate_financial_year)
    return income_data, deduction_data


def date_sidebar(st: DeltaGenerator, df: pd.DataFrame, date_key: str, start_at_minimum=False):
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


def format_income_table(dataframe: pd.DataFrame, column_names=[
        "Gross Income",
        "Salary Sacrifice",
        "Taxable Income",
        "Income",
        "Tax"]):
    dataframe_formatted = dataframe.style.format(
            {columnname: '${:,.2f}' for columnname in column_names}
        )
    return dataframe_formatted


# Fetch the data from Upbank Client as a csv then read into a dataframe
@st.cache_data
def fetch_transaction_data(start_date=pd.Timestamp.today() - pd.DateOffset(months=1), end_date=pd.Timestamp.today()):
    transactions_uri = "http://localhost:8080"
    csv_endpoint = "/api/v1/transactions/csv"
    params = {
        "startDate": f"{start_date}T00:00:00.000Z",
        "endDate": f"{end_date}T00:00:00.000Z",
        "numTransactions": 10000,
        "accountId": "a90b55ad-1bcb-4e75-b407-0e0e1e5c8a6d",
        "transactionTypes": ['Payment', 'Purchase', 'Refund']
    }
    try:
        # Fetch the CSV data
        response = requests.get(transactions_uri + csv_endpoint, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Convert CSV response to a pandas DataFrame
        csv_data = response.content.decode("utf-8")
        dataframe = pd.read_csv(StringIO(csv_data))
        return dataframe

    except requests.exceptions.RequestException as e:
        st.error(f"Please check that the service is running successfully at {transactions_uri}.\n\n An error occurred while fetching the data: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame()


def save_data(df: pd.DataFrame):
    with pd.ExcelWriter(
        os.getenv("EXCEL_PATH_SPENDING"),
        mode='a',
        if_sheet_exists='replace',
        engine='openpyxl',
        date_format="YYYY-MM-DD",
        datetime_format="YYYY-MM-DD"
    ) as writer:
        df.to_excel(
            writer,
            sheet_name=SPENDING_SHEET_NAME,
        )