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


def initialise_sidebar(inputs: DeltaGenerator):
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
    return start_date, end_date


@st.dialog("Add expenses")
def add_expenses(existing_expenses: pd.DataFrame):
    with st.expander("Duplicate an existing expense entry"):
        prior_expenses_entry = st.dataframe(
            existing_expenses,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
    # Form fields
    if prior_expenses_entry.selection.rows:
        # Get the data for the selected row
        selected_row_data = existing_expenses.iloc[prior_expenses_entry.selection.rows[0]]
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
    else:
        # Default values if no row is selected
        item_value = ""
        cost_value = 0.0
        quantity_value = 0.0
        measure_value = ""
        location_value = ""
        shop_value = ""
        details_value = ""
        tag_value = ""
        date_value = pd.Timestamp.now()
        receipt_ref_value = ""
        receipt_value = ""
        transaction_id_value = ""

    # Form fields
    item = st.selectbox("Item", options=np.append(
        existing_expenses.Item.unique(),
        st.session_state.additional_items), placeholder=item_value)
    cost = st.number_input("Cost", min_value=0.0, format="%.2f", value=cost_value)
    quantity = st.number_input("Quantity", min_value=0.0, format="%.2f", value=quantity_value)
    measure = st.selectbox("Measure", options=np.append(
        existing_expenses.Measure.unique(),
        st.session_state.additional_items), placeholder=measure_value)
    location = st.selectbox("Location", options=np.append(
        existing_expenses.Location.unique(),
        st.session_state.additional_items), placeholder=location_value)
    shop = st.selectbox("Shop", options=np.append(
        existing_expenses.Shop.unique(),
        st.session_state.additional_items), placeholder=shop_value)
    details = st.text_area("Details", value=details_value)
    tag = st.selectbox("Location", options=np.append(
        existing_expenses.Tag.unique(),
        st.session_state.additional_items), placeholder=tag_value)
    date = st.date_input("Date", value=date_value, max_value=pd.Timestamp.today())

    ### Currently don't support adding receipts yet

    # receipt_ref = st.selectbox("Receipt Ref", options=np.append(
    #     existing_expenses['Receipt Ref'].unique(),
    #     st.session_state.additional_items), placeholder=receipt_ref_value)
    # receipt = st.selectbox("Receipt", options=np.append(
    #     existing_expenses['Receipt'].unique(),
    #     st.session_state.additional_items), placeholder=receipt_value)

    transaction_id = st.text_input("Employer", value=transaction_id_value)

    if st.button("Submit"):
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
            "Date": date,
            "Receipt Ref": "",
            "Receipt": "",
            "transactionId": transaction_id
        }
        edited_df = pd.concat(
            [existing_expenses, pd.DataFrame([new_row])],
            ignore_index=True
        )[utils.INCOME_DATA_SCHEMA]
        utils.save_data(
            edited_df,
            utils.SPENDING_PATH,
            utils.SPENDING_SHEET_NAME)
        utils.fetch_income_deduction_data.clear()
        st.rerun()


def render_transaction_input(inputs: DeltaGenerator):
    start_date, end_date = initialise_sidebar(inputs)
    transactions_data = utils.fetch_transaction_data(start_date, end_date)
    if transactions_data.empty:
        st.write("No transaction data fetched")
        return

    categorised_transactions = utils.fetch_spending_data()
    col1, col2 = st.sidebar.columns(2)
    if col1.button("Add Income Data"):
        add_expenses(categorised_transactions)
    # only show the uncategorised transactions
    uncategorised_transactions = transactions_data[
        ~transactions_data['transactionId'].isin(categorised_transactions['transactionId'])
    ]
    uncategorised_transactions = clean_transaction_data(uncategorised_transactions)

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
