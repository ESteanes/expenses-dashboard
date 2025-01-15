import numpy as np
import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import utils


def add_item():
    new_item = st.session_state.new_item_input.strip()  # Get input and strip whitespace
    if new_item and new_item not in st.session_state.additional_items:
        st.session_state.additional_items.append(new_item)  # Add item to the list
        st.session_state.new_item_input = ""  # Clear the input field


def refresh_all_the_data():
    utils.fetch_transaction_data.clear()
    utils.fetch_spending_data.clear()


def get_info(spending_data: pd.DataFrame):
    column_config = {
        "Item": st.column_config.SelectboxColumn(
            "Item",
            help="The item name of what was purchased. \n\nIf there is a new item that doesn't already exist, add it in the sidebar!",
            width="medium",
            options=np.append(
                spending_data.Item.unique(),
                st.session_state.additional_items),
            required=True,
        ),
        "Upbank Category": st.column_config.Column(
            label="Upbank Category",
            disabled=True
        ),
        "Cost": st.column_config.Column(
            label="Cost",
            disabled=True
        ),
        "Quantity": st.column_config.NumberColumn(
            label="Quantity",  # Ensures the field expects numeric input
            width="small"
        ),
        "Measure": st.column_config.SelectboxColumn(
            label="Measure",
            options=["g", "kg", "L", "mg", "lbs"],
            width="small"
        ),
        "Location": st.column_config.SelectboxColumn(
            label="Location",
            width="small",
            options=np.append(spending_data.Location.dropna().unique(),
                              st.session_state.additional_items),
            required=True,
        ),
        "Shop": st.column_config.Column(
            label="Shop"
        ),
        "Details": st.column_config.TextColumn(
            label="Details"
        ),
        "Tag": st.column_config.SelectboxColumn(
            label="Tag",
            options=np.append(
                spending_data.Tag.dropna().unique(),
                st.session_state.additional_items),
        ),
        "Date": st.column_config.DatetimeColumn(
            label="Date",
            required=True,
            format="YYYY-MM-DD",
            pinned=True
        ),
        "transactionId": st.column_config.Column(
            label="Transaction ID",
            disabled=True,
            width="small"
        )
    }
    column_order = [
        "Item",
        "Upbank Category",
        "Cost",
        "Location",
        "Upbank Text",
        "Shop",
        "Details",
        "Tag",
        "Quantity",
        "Measure",
        "Date",
        "transactionId"
    ]
    return column_config, column_order


def save_edited_values(edited_df: pd.DataFrame):
    utils.save_data(edited_df, utils.SPENDING_PATH, utils.SPENDING_SHEET_NAME)
    refresh_all_the_data()


@st.dialog("Add expenses")
def add_expenses(categorised_transactions: pd.DataFrame):
    sorted_df = categorised_transactions.sort_values(by=['Date'], ascending=False)
    with st.expander("Duplicate an existing expense entry"):
        prior_expenses_entry = st.dataframe(
            sorted_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
    # Form fields
    if prior_expenses_entry.selection.rows:
        new_row = handle_selection_and_prefill(prior_expenses_entry, sorted_df)
    else:
        new_row = handle_selection_and_prefill(None, sorted_df)
    if st.button("Submit"):
        edited_df = pd.concat(
            [categorised_transactions, pd.DataFrame([new_row])],
            ignore_index=True
        )[utils.SPENDING_DATA_SCHEMA]
        save_reset(edited_df)


@st.dialog("Delete expenses")
def delete_expenses(categorised_transactions: pd.DataFrame):
    sorted_df = categorised_transactions.sort_values(by=['Date'], ascending=False)
    prior_expenses_entry = st.dataframe(
        sorted_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )
    if prior_expenses_entry.selection.rows:
        index_label = sorted_df.index[prior_expenses_entry.selection.rows[0]]
        edited_df = (
            sorted_df
            .drop(index=index_label)
            [utils.SPENDING_DATA_SCHEMA]
            .sort_values(by=["Date"])
            .reset_index()
        )
        if st.button("Delete Transaction"):
            save_reset(edited_df)


def unique_items_and_index(series: pd.Series, value):
    unique_series = series.drop_duplicates().reset_index(drop=True)
    if value:
        index = int(unique_series[unique_series == value].index[0])
    else:
        index = 0
    return unique_series, index


@st.dialog("Edit expenses")
def edit_expenses(categorised_transactions: pd.DataFrame):
    sorted_df = categorised_transactions.sort_values(by=['Date'], ascending=False)
    prior_expenses_entry = st.dataframe(
        sorted_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    if prior_expenses_entry.selection.rows:
        # Get the data for the selected row
        new_row = handle_selection_and_prefill(prior_expenses_entry, sorted_df)
        if st.button("Edit transaction"):
            sorted_df.iloc[prior_expenses_entry.selection.rows[0]] = new_row
            edited_df = sorted_df[utils.SPENDING_DATA_SCHEMA].sort_values(by=["Date"]).reset_index()
            save_reset(edited_df)


def save_reset(edited_df):
    utils.save_data(
        edited_df,
        utils.SPENDING_PATH,
        utils.SPENDING_SHEET_NAME)
    utils.fetch_spending_data.clear()
    st.rerun()


def handle_selection_and_prefill(prior_expenses_entry, sorted_df: pd.DataFrame):
    item_value = None
    cost_value = None
    quantity_value = None
    measure_value = None
    location_value = None
    shop_value = None
    details_value = None
    tag_value = None
    date_value = None
    receipt_ref_value = None
    receipt_value = None
    transaction_id_value = None
    if prior_expenses_entry:
        selected_row_data = sorted_df.iloc[prior_expenses_entry.selection.rows[0]]
        item_value = selected_row_data["Item"]
        cost_value = selected_row_data["Cost"]
        quantity_value = selected_row_data["Quantity"]
        measure_value = selected_row_data["Measure"]
        location_value = selected_row_data["Location"]
        shop_value = selected_row_data["Shop"]
        details_value = selected_row_data["Details"]
        tag_value = selected_row_data["Tag"]
        date_value = selected_row_data["Date"]
        receipt_ref_value = selected_row_data["Receipt Ref"]
        receipt_value = selected_row_data["Receipt"]
        transaction_id_value = selected_row_data["transactionId"]
    item_unique, item_index = unique_items_and_index(sorted_df.Item, item_value)
    item = st.selectbox("Item", options=np.append(
        item_unique,
        st.session_state.additional_items), index=item_index)
    cost = st.number_input("Cost", min_value=-90000.0, format="%.2f", value=cost_value)
    quantity = st.number_input("Quantity", min_value=0.0, format="%.2f", value=quantity_value)
    measure_unique, measure_index = unique_items_and_index(sorted_df.Measure, measure_value)
    measure = st.selectbox("Measure", options=np.append(
        measure_unique,
        st.session_state.additional_items), index=measure_index)
    location_unique, location_index = unique_items_and_index(sorted_df.Location, location_value)
    location = st.selectbox("Location", options=np.append(
        location_unique,
        st.session_state.additional_items), index=location_index)
    shop_unique, shop_index = unique_items_and_index(sorted_df.Shop, shop_value)
    shop = st.selectbox("Shop", options=np.append(
        shop_unique,
        st.session_state.additional_items), index=shop_index)
    details = st.text_area("Details", value=details_value)
    tag_unique, tag_index = unique_items_and_index(sorted_df.Tag, tag_value)
    tag = st.selectbox("Location", options=np.append(
        tag_unique,
        st.session_state.additional_items), index=tag_index)
    date = st.date_input("Date", value=date_value, max_value=pd.Timestamp.today() + pd.DateOffset(months=2))
    # Create a dictionary from the modal data
    new_row = {
        "Item": item,
        "Cost": cost,
        "Quantity": quantity,
        "Measure": measure,
        "Location": location,
        "Shop": shop,
        "Details": details,
        "Tag": tag,
        "Date": pd.Timestamp(date),
        "Receipt Ref": "",
        "Receipt": "",
        "transactionId": transaction_id_value
    }
    return new_row


def initialise_sidebar(inputs: DeltaGenerator, categorised_transactions: pd.DataFrame):
    inputs.sidebar.button("Refresh Data", on_click=refresh_all_the_data)
    if "additional_items" not in st.session_state:
        st.session_state.additional_items = []

    maximum_date = pd.Timestamp.today()
    start_date = inputs.sidebar.date_input(
        "**Start Date**",
        value=maximum_date - pd.DateOffset(months=1),
        max_value=maximum_date)
    end_date = inputs.sidebar.date_input(
        "**End Date**",
        value=maximum_date,
        max_value=maximum_date)
    inputs.sidebar.subheader("Add new items here")
    inputs.sidebar.text_input("New Item Name", on_change=add_item, key='new_item_input')
    if inputs.session_state.additional_items:
        inputs.sidebar.write("Addtional item names:")
        inputs.sidebar.write(inputs.session_state.additional_items)
    inputs.title("Categorise Expenses from Upbank or Add Expenses")
    col1, col2, col3 = st.sidebar.columns(3)
    if col1.button("Add"):
        add_expenses(categorised_transactions)
    if col2.button("Edit"):
        edit_expenses(categorised_transactions)
    if col3.button("Remove"):
        delete_expenses(categorised_transactions)
    return start_date, end_date


def render_transaction_input(inputs: DeltaGenerator):
    categorised_transactions = utils.fetch_spending_data()
    start_date, end_date = initialise_sidebar(inputs, categorised_transactions)
    transactions_data = utils.fetch_transaction_data(start_date, end_date)
    if transactions_data.empty:
        st.write("No transaction data fetched")
        return
    # only show the uncategorised transactions
    uncategorised_transactions = transactions_data[
        ~transactions_data['transactionId'].isin(categorised_transactions['transactionId'])
    ]

    inputs.subheader("Uncategorised expenses")
    column_config, column_order = get_info(categorised_transactions)
    edited_transactions = inputs.data_editor(
        uncategorised_transactions.style.format(
            {"Cost": '${:,.2f}'}
        ),
        column_config=column_config,
        column_order=column_order,
        hide_index=True
    )
    inputs.button(
        "Click this to save data",
        args=[
            pd.concat(
                [
                    categorised_transactions,
                    edited_transactions[
                        ~edited_transactions['Item'].isna() &
                        ~edited_transactions['Location'].isna()]
                ],
                ignore_index=True
            )[utils.SPENDING_DATA_SCHEMA]],
        on_click=save_edited_values)


# We need to have some sort of way to
st.set_page_config(layout="wide")
render_transaction_input(st)
