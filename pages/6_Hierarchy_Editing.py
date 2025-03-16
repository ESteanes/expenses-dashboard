import streamlit as st

import classes.spending as spending

st.set_page_config(layout="wide")

spending_data = spending.SpendingData().fetch_spending_data()

col1, col2, col3 = st.columns(3)
sub_categories = spending_data.middle_table['Sub Category'].unique()
categories = spending_data.top_table.Category.dropna().unique()
base_categories = spending_data.base_table['Sub Sub Category'].unique()

selected_base_category = st.sidebar.multiselect("Base Category", options=base_categories)
selected_sub_category = st.sidebar.multiselect("Sub Category", options=sub_categories)
selected_category = st.sidebar.multiselect("Category", options=categories)

col1.title("Top table")
edited_top = col1.data_editor(
    (
        spending_data
        .top_table
        .loc[lambda df: df.Category.isin(selected_category) if selected_category else [True] * len(df)]
    ), num_rows="dynamic")
if col1.button("Save top table"):
    spending_data.top_table = edited_top
    spending_data.save_top()
    spending_data.fetch_spending_data.clear()
    st.rerun()

col2.title("Middle table")
edited_middle = col2.data_editor((
    spending_data
    .middle_table
    .loc[lambda df: df['Sub Category'].isin(selected_sub_category) if selected_sub_category else [True] * len(df)]
), num_rows="dynamic")
if col2.button("Save middle table"):
    spending_data.middle_table = edited_middle
    spending_data.save_middle()
    spending_data.fetch_spending_data.clear()
    st.rerun()

col3.title("Base table")
edited_base = col3.data_editor((
    spending_data
    .base_table
    .loc[lambda df: df['Sub Sub Category'].isin(selected_base_category) if selected_base_category else [True] * len(df)]
), num_rows="dynamic")
if col3.button("Save base table"):
    spending_data.base_table = edited_base
    spending_data.save_base()
    spending_data.fetch_spending_data.clear()
    st.rerun()
