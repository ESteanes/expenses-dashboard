import streamlit as st
import pandas as pd
import os
import altair as alt
from streamlit.delta_generator import DeltaGenerator


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
        sheet_name=["Spending", "Top_Table", "Middle Table", "Base Table", "Location"])
    
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
        .merge(hierarchy, on='Item')
        .merge(location, on='Location')
    )
    return df


@st.cache_data
def fetch_income_deduction_data():
    income_excel_path = os.getenv("EXCEL_PATH_INCOME")
    income_sheets = pd.read_excel(
        income_excel_path,
        sheet_name=["Income", "Deductions"]
    )
    income_data = remove_unnamed_columns(income_sheets['Income'])
    income_data["Financial Year"] = pd.to_datetime(income_data['Date']).apply(calculate_financial_year)

    deduction_data = remove_unnamed_columns(income_sheets['Deductions'])
    return income_data, deduction_data


def date_sidebar(st: DeltaGenerator, df: pd.DataFrame, date_key: str):
    minimum_date = df[date_key].min()
    maximum_date = df[date_key].max()
    start_date = st.sidebar.date_input(
        "Start Date",
        value=maximum_date - pd.DateOffset(months=1),
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