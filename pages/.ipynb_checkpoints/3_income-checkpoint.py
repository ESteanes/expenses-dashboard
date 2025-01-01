import streamlit as st
import altair as alt
import pandas as pd
from streamlit.delta_generator import DeltaGenerator
import plotly.express as px
import utils


def variable_income_aggregation(
        income: DeltaGenerator,
        income_data: pd.DataFrame):
    # Gross Income Over Time
    income.subheader("Gross Income Over Time with Breakdown")
    time_aggregation = income.selectbox(
        "Aggregate by:",
        options=["Day", "Week", "Month", "Year"],
        index=2  # Default to "Month"
    )
    # Apply the selected aggregation
    if time_aggregation == "Day":
        income_data["Period"] = income_data["Date"]
    elif time_aggregation == "Week":
        income_data["Period"] = income_data["Date"].dt.to_period("W").apply(lambda r: r.start_time)
    elif time_aggregation == "Month":
        income_data["Period"] = income_data["Date"].dt.to_period("M").apply(lambda r: r.start_time)
    elif time_aggregation == "Year":
        income_data["Period"] = income_data["Date"].dt.to_period("Y").apply(lambda r: r.start_time)

    # Aggregate gross income
    gross_income_by_period = (
        income_data.groupby("Period")["Gross Income"]
        .sum()
        .reset_index()
        .sort_values("Period")
    )

    # Aggregate breakdown by category (if available)
    if "Description" in income_data.columns:
        breakdown_by_period = (
            income_data.groupby(["Period", "Description"])["Gross Income"]
            .sum()
            .reset_index()
        )
    else:
        breakdown_by_period = income_data.groupby("Period")["Gross Income"].sum().reset_index()

    y_axis = alt.Y("Gross Income:Q", title="Gross Income ($)", axis=alt.Axis(labelExpr='"$" + datum.value'))

    # Stacked bar chart for breakdown
    bar_chart = alt.Chart(breakdown_by_period).mark_bar().encode(
        x=alt.X("Period:T", title="Period"),
        y=y_axis,
        color=alt.Color("Description:N", title="Income Description"),
        tooltip=["Period:T", "Description:N", "Gross Income:Q"]
    ).properties(
        title=f"Gross Income and Breakdown ({time_aggregation})"
    )
    # Display the layered chart
    income.altair_chart(bar_chart, use_container_width=True)


def render_income(
        income: DeltaGenerator,
        income_data: pd.DataFrame,
        deductions_data: pd.DataFrame):

    income.sidebar.button("Refresh Data", on_click=utils.fetch_income_deduction_data.clear)
    # income.write(income_data.columns.astype(str))

    employers = income_data.Employer.unique()
    income_descriptions = income_data.Description.unique()
    selected_employers = income.sidebar.multiselect("Employer", options=employers)
    selected_descriptions = income.sidebar.multiselect("Income Description", options=income_descriptions)
    start_date, end_date = utils.date_sidebar(income, income_data, "Date")

    income_data = (
        income_data
        .loc[lambda df: df.Date >= pd.to_datetime(start_date)]
        .loc[lambda df: df.Date <= pd.to_datetime(end_date)]
        .loc[lambda df:
             df.Employer.isin(selected_employers)
             if selected_employers else [True] * len(df)]
    )
    filtered_deduction = (
        deductions_data
        .loc[lambda df: df.Date > pd.to_datetime(start_date)]
        .loc[lambda df: df.Date < pd.to_datetime(end_date)]
    )
    # Filter historical and projected data
    today = pd.Timestamp.today()
    historical_data = income_data[income_data["Date"] <= today]
    future_data = income_data[income_data["Date"] > today]

    # Display the data table
    income.subheader("Income Data")
    income.dataframe(income_data, hide_index=True)

    variable_income_aggregation(income, income_data)

    # Income Breakdown by Financial Year
    income.subheader("Income Breakdown by Financial Year")
    income_by_year = (
        historical_data.groupby("Financial Year")[["Gross Income", "Tax", "Income"]]
        .sum()
        .reset_index()
        .sort_values("Gross Income", ascending=False)
    )
    bar_chart = alt.Chart(income_by_year).mark_bar().encode(
        x=alt.X("Financial Year:N", title="Financial Year"),
        y=alt.Y("Gross Income:Q", title="Gross Income ($)", axis=alt.Axis(labelExpr='"$" + datum.value')),
        color=alt.Color("Financial Year:N", legend=None),
        tooltip=["Financial Year:N", "Gross Income:Q", "Tax:Q", "Income:Q"]
    ).properties(title="Income Breakdown by Financial Year")
    income.altair_chart(bar_chart, use_container_width=True)

    # Tax Impact
    income.subheader("Tax Impact on Gross Income")
    tax_impact_data = historical_data.groupby("Date")[["Gross Income", "Tax"]].sum().reset_index()
    tax_chart = alt.Chart(tax_impact_data).transform_fold(
        fold=["Gross Income", "Tax"],
        as_=["Category", "Value"]
    ).mark_area().encode(
        x=alt.X("Date:T", title="Date"),
        y=alt.Y("Value:Q", title="Amount ($)", axis=alt.Axis(labelExpr='"$" + datum.value')),
        color="Category:N",
        tooltip=["Date:T", "Category:N", "Value:Q"]
    ).properties(title="Tax and Gross Income Over Time")
    income.altair_chart(tax_chart, use_container_width=True)

    # Income Projections
    income.subheader("Projected Income")
    recent_months = historical_data[historical_data["Date"] > today - pd.DateOffset(months=6)]
    avg_monthly_income = recent_months["Income"].mean()
    projection_data = pd.DataFrame({
        "Date": pd.date_range(today + pd.DateOffset(days=1), periods=12, freq="ME"),
        "Projected Income": avg_monthly_income
    })
    projection_chart = alt.Chart(projection_data).mark_line(point=True).encode(
        x=alt.X("Date:T", title="Date"),
        y=alt.Y("Projected Income:Q", title="Projected Income ($)", axis=alt.Axis(labelExpr='"$" + datum.value')),
        tooltip=["Date:T", "Projected Income:Q"]
    ).properties(title="Projected Monthly Income for Next 12 Months")
    income.altair_chart(projection_chart, use_container_width=True)

    # Employer Contributions
    income.subheader("Income by Employer")
    income_by_employer = (
        historical_data.groupby(["Employer", "Description"])["Gross Income"]
        .sum()
        .reset_index()
        .sort_values("Gross Income", ascending=False)
    )
    sunburst = px.sunburst(income_by_employer, path=["Employer", "Description"], values="Gross Income")
    income.plotly_chart(sunburst, use_container_width=True)
    # Summary Statistics
    income.subheader("Summary Statistics")
    summary_stats = historical_data[["Gross Income", "Tax", "Income"]].sum().to_frame(name="Total")
    summary_stats.loc["Net Income"] = summary_stats.loc["Gross Income"] - summary_stats.loc["Tax"]
    income.table(summary_stats)
    
st.set_page_config(layout="wide")
income_data, deductions_data = utils.fetch_income_deduction_data()
render_income(st, income_data, deductions_data)

st.dataframe(income_data, hide_index=True)
    