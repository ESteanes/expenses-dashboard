import streamlit as st
import pandas as pd
import altair as alt
import os


def dataframe_in_list(df, key, list_items):
    if not list_items:
        return df[key].isin(list_items)
    return df


def remove_unnamed_columns(df):
    return df.loc[:, ~df.columns.str.contains('^Unnamed')]


# Data ingest and basic prep
location_excel_path = os.getenv("EXCEL_PATH_LOCATION")
spending_excel_path = os.getenv("EXCEL_PATH_SPENDING")
df = remove_unnamed_columns(pd.read_excel(spending_excel_path))
top_table = remove_unnamed_columns(pd.read_excel(spending_excel_path, sheet_name="Top_Table", header=1))
middle_table = remove_unnamed_columns(pd.read_excel(spending_excel_path, sheet_name="Middle Table", header=1))
base_table = remove_unnamed_columns(pd.read_excel(spending_excel_path, sheet_name="Base Table", header=2))
hierarchy = base_table.rename(columns={'All Items': 'Item'}).merge(middle_table, on="Sub Sub Category").merge(top_table, on="Sub Category")
location = remove_unnamed_columns(pd.read_excel(location_excel_path, sheet_name="Location", header=1))
df = (
    df
    .merge(hierarchy, on='Item')
    .merge(location, on='Location')
)

# Display some filters - date, tag etc.
tags = df["Tag"].unique()
minimum_date = df["Date"].min()
maximum_date = df["Date"].max()
shops = df["Shop"].dropna().unique()
sub_categories = df['Sub Category'].unique()
categories = top_table.Category.dropna().unique()
st.sidebar.header("Filters")
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

st.write("""
# Expenditure Dashboard
""")
recent, detailed, income = st.tabs(["Last 30 days spending", "Detailed Spending", "Income"])


selected_tags = st.sidebar.multiselect("Tags", options=tags)
selected_shops = st.sidebar.multiselect("Shops", options=shops)
selected_sub_category = st.sidebar.multiselect("Sub Category", options=sub_categories)
selected_category = st.sidebar.multiselect("Category", options=categories)
st.write(f"Selected start and end dates: {start_date}, {end_date}")
st.write(f"Selected tags: {selected_tags}")
# Display some metrics: Total expenditure, biggest purchase etc.
filtered_dataframe = (
    df
    .loc[lambda df: df.Date > pd.to_datetime(start_date)]
    .loc[lambda df: df.Date < pd.to_datetime(end_date)]
    .loc[lambda df: df.Tag.isin(selected_tags) if selected_tags else [True] * len(df)]
    .loc[lambda df: df.Shop.isin(selected_shops) if selected_shops else [True] * len(df)]
    .loc[lambda df: df['Sub Category'].isin(selected_sub_category) if selected_sub_category else [True] * len(df)]
    .loc[lambda df: df.Category.isin(selected_category) if selected_category else [True] * len(df)]
    
)
st.write("Column Headers: " + " ".join(filtered_dataframe.columns))
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


st.subheader("Summary Table")
st.dataframe(filtered_dataframe.astype(str))
