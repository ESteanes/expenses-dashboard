import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import utils


def render_detailed_spending(
    detailed: DeltaGenerator,
    filtered_dataframe: pd.DataFrame):
    # Display some filters - date, tag etc.
    tags = filtered_dataframe["Tag"].unique()
    shops = filtered_dataframe["Shop"].dropna().unique()
    sub_categories = filtered_dataframe['Sub Category'].unique()
    categories = filtered_dataframe.Category.dropna().unique()
    detailed.sidebar.header("Filters")
    detailed.sidebar.button("Refresh Data", on_click=utils.fetch_spending_data.clear)
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
    detailed.dataframe(filtered_dataframe)


st.set_page_config(layout="wide")
render_detailed_spending(st, utils.fetch_spending_data())
