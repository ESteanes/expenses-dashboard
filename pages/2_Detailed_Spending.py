import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import classes.spending as spending
import utils
from classes.receipt import Receipt
from classes.spending import SpendingData


def render_detailed_spending(
    detailed: DeltaGenerator,
    spending_data: SpendingData):
    filtered_dataframe = spending_data.combine().combined
    # Display some filters - date, tag etc.
    tags = filtered_dataframe["Tag"].unique()
    shops = filtered_dataframe["Shop"].dropna().unique()
    sub_categories = filtered_dataframe['Sub Category'].unique()
    categories = filtered_dataframe.Category.dropna().unique()
    detailed.sidebar.header("Filters")
    detailed.sidebar.button("Refresh Data", on_click=spending_data.fetch_spending_data.clear)
    start_date, end_date = utils.date_sidebar(detailed, filtered_dataframe, "Date")
    selected_tags = detailed.sidebar.multiselect("Tags", options=tags)
    selected_shops = detailed.sidebar.multiselect("Shops", options=shops)
    selected_sub_category = detailed.sidebar.multiselect("Sub Category", options=sub_categories)
    selected_category = detailed.sidebar.multiselect("Category", options=categories)

    filtered_dataframe = (
        filtered_dataframe
        .loc[lambda df: df.Date >= pd.to_datetime(start_date)]
        .loc[lambda df: df.Date <= pd.to_datetime(end_date)]
        .loc[lambda df: df.Tag.isin(selected_tags) if selected_tags else [True] * len(df)]
        .loc[lambda df: df.Shop.isin(selected_shops) if selected_shops else [True] * len(df)]
        .loc[lambda df: df['Sub Category'].isin(selected_sub_category) if selected_sub_category else [True] * len(df)]
        .loc[lambda df: df.Category.isin(selected_category) if selected_category else [True] * len(df)]
    )
    filtered_dataframe['Has Receipt'] = filtered_dataframe['Receipt Ref'].notna()
    # Header
    detailed.title("Detailed Spending Analysis")
    # Create columns for visualizations
    col1, col2 = detailed.columns(2)

    # Spending by Tag (Altair Bar Chart)
    with col1:
        col1.subheader("Spending by Tag")
        col1.altair_chart(
            utils.plot_bar_chart(
                filtered_dataframe,
                "Tag",
                "Cost",
                "Tag"
            ), use_container_width=True
        )

    # Spending by Shop (Altair Bar Chart)
    with col2:
        col2.subheader("Spending by Shop")
        col2.altair_chart(
            utils.plot_bar_chart(
                filtered_dataframe,
                "Shop", "Cost", "Shop"),
            use_container_width=True
        )

    # Spending by Category (Altair Bar Chart)
    with col1:
        col1.subheader("Spending Breakdown")
        sunburst_data = (
            filtered_dataframe.groupby(["Category", "Sub Category", "Sub Sub Category"])["Cost"]
            .sum()
            .reset_index()
        )
        sunburst_fig = px.sunburst(
            sunburst_data,
            path=["Category", "Sub Category", "Sub Sub Category"],
            values="Cost",
            color="Sub Category",
            color_discrete_sequence=px.colors.qualitative.Prism,
        )
        col1.plotly_chart(sunburst_fig, use_container_width=True)

    # Spending Map (if latitude and longitude are available)
    col2.subheader("Spending Map")
    map_data = filtered_dataframe[["Latitude", "Longitude", "Cost", "Tag"]].dropna(
        subset=['Latitude', 'Longitude']).rename(
        columns={"Latitude": "LAT", "Longitude": "LON"})
    col2.map(map_data, size='Cost')

    st.subheader("Line items")
    column_config = {
        "Date": st.column_config.DateColumn("Date", format="ddd DD-MM-YY"),
        "Details": st.column_config.TextColumn("Details", width="medium"),
        "Has Receipt": st.column_config.CheckboxColumn("Receipt",width="small",disabled=True)
    }
    column_order = ["Date", "Item", "Cost", "Shop", "Location", "Tag", "Details", "Sub Category", "Has Receipt"]
    transaction = detailed.dataframe(filtered_dataframe,
                                     selection_mode="single-row",
                                     on_select="rerun",
                                     hide_index=True,
                                     column_config=column_config,
                                     column_order=column_order,
                                     use_container_width=True
                                     )

    if transaction['selection']['rows']:
        transaction_data = filtered_dataframe.iloc[transaction['selection']['rows'][0]]
        if not type(transaction_data[
                        'Receipt Ref']).__name__ == "float":  # this means its null as the receipt reference should be a string
            selected_receipt = Receipt().set_path(transaction_data['Receipt Ref'])
            utils.display_image(selected_receipt)


st.set_page_config(layout="wide")
render_detailed_spending(st, spending.SpendingData().fetch_spending_data())
