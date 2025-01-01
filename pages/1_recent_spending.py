import streamlit as st
import altair as alt
import pandas as pd
from streamlit.delta_generator import DeltaGenerator
import utils

def render_recent_spending(
    recent: DeltaGenerator,
    filtered_dataframe: pd.DataFrame):
    recent.header("Past 30 Days Expenditures")
    recent.write('''
    The goal of this page is to provide a simple overview of the past 30 days.
    
    It is intended to be very minimal and at a glance.
    ''')
    recent.sidebar.button("Refresh Data", on_click=utils.fetch_spending_data.clear)
    
    recent.metric("Total Cost", f"${round(filtered_dataframe.Cost.sum(),2)}")
    metrics = recent.container()
    metric_col1, metric_col2, metric_col3 = metrics.columns(3)
    metric_col1.metric("Discretionary", f"${round(filtered_dataframe.loc[lambda df: df.Category == 'Wants'].Cost.sum(),2)}")
    metric_col2.metric("Miscellaneous", f"${round(filtered_dataframe.loc[lambda df: df['Sub Category'] == 'Miscellaneous'].Cost.sum(),2)}")
    metric_col3.metric("Necessary", f"${round(filtered_dataframe.loc[lambda df: df.Category == 'Week by Week'].Cost.sum(),2)}")
    recent.bar_chart(
        filtered_dataframe,
        x="Date",
        y="Cost",
        x_label="Date of Purchase",
        y_label="Cost of Purchase",
        color="Sub Category"
    )

    # Cost by Tag
    recent.subheader("Cost by Tag")
    cost_by_tag = filtered_dataframe.groupby("Tag")["Cost"].sum().reset_index().sort_values(by="Cost", ascending=False).head(20)
    recent.altair_chart(alt.Chart(cost_by_tag).mark_bar().encode(
        x=alt.X('Tag', sort=None, title="Tag"),
        y=alt.Y('Cost', title="Total Cost"),
        color="Tag"
    ), use_container_width=True)

    # Cost by Shop
    recent.subheader("Cost by Shop")
    cost_by_shop = filtered_dataframe.groupby("Shop")["Cost"].sum().reset_index().sort_values(by="Cost", ascending=False).head(20)
    recent.altair_chart(alt.Chart(cost_by_shop).mark_bar().encode(
        x=alt.X('Shop', sort=None, title="Shop"),
        y=alt.Y('Cost', title="Total Cost")
    ), use_container_width=True)

    # Cost by Location
    recent.subheader("Cost by Location")
    cost_by_location = filtered_dataframe.groupby("Location")["Cost"].sum().reset_index().sort_values(by="Cost", ascending=False).head(20)
    recent.altair_chart(alt.Chart(cost_by_location).mark_bar().encode(
        x=alt.X('Location', sort=None, title="Location"),
        y=alt.Y('Cost', title="Total Cost")
    ), use_container_width=True)

render_recent_spending(st, utils.fetch_spending_data().loc[lambda df: df.Date > pd.Timestamp.now() - pd.DateOffset(months=1)])