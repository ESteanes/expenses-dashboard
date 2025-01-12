import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
from streamlit.delta_generator import DeltaGenerator
import utils
import os


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
        # "Shop": st.column_config.SelectboxColumn(
        #     label="Shop",
        #     options=np.append(
        #         spending_data.Shop.dropna().unique(),
        #         st.session_state.additional_items),
        # ),
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
    utils.save_data(edited_df, os.getenv("EXCEL_PATH_SPENDING"), utils.SPENDING_SHEET_NAME)
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
def add_expenses(existing_income: pd.DataFrame):
    with st.expander("Duplicate an existing expense entry"):
        prior_income_entry = st.dataframe(
            existing_income,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
    # Form fields
    if prior_income_entry.selection.rows:
        # Get the data for the selected row
        selected_row_data = existing_income.iloc[prior_income_entry.selection.rows[0]]
        taxable_value = selected_row_data["Taxable"]
        gross_income_value = selected_row_data["Gross Income"]
        salary_sacrifice_value = selected_row_data["Salary Sacrifice"]
        tax_value = selected_row_data["Tax"]
        date_value = pd.to_datetime(selected_row_data["Date"])
        employer_value = selected_row_data["Employer"]
        description_value = selected_row_data["Description"]
        received_in_bank_value = selected_row_data["Received in bank account"]
        comment_value = selected_row_data["Comment"]
    else:
        # Default values if no row is selected
        taxable_value = utils.TAXABLE_OPTIONS[0]  # Default to first option
        gross_income_value = 0.0
        salary_sacrifice_value = 0.0
        tax_value = 0.0
        date_value = pd.Timestamp.today()
        employer_value = ""
        description_value = ""
        received_in_bank_value = "No"
        comment_value = ""

    # Form fields
    taxable = st.selectbox(
        "Taxable",
        options=utils.TAXABLE_OPTIONS)
    gross_income = st.number_input("Gross Income", min_value=0.0, format="%.2f", value=gross_income_value)
    salary_sacrifice = st.number_input("Salary Sacrifice", min_value=0.0, format="%.2f", value=salary_sacrifice_value)
    tax = st.number_input("Tax", min_value=0.0, format="%.2f", value=tax_value)
    # Dynamically calculate income based on the inputs
    income = gross_income - salary_sacrifice - tax
    st.number_input("Income", value=income, min_value=0.0, format="%.2f", disabled=True)
    date = st.date_input("Date", value=date_value, max_value=pd.Timestamp.today())
    employer = st.text_input("Employer", value=employer_value)
    description = st.text_input("Description", value=description_value)
    received_in_bank = st.radio(
        "Received in Bank Account?",
        options=["Yes", "No"],
        index=1
    )
    comment = st.text_area("Comment", value=comment_value)

    if st.button("Submit"):
        # Create a dictionary from the modal data
        new_row = {
            "Gross Income": gross_income,
            "Salary Sacrifice": salary_sacrifice,
            "Tax": tax,
            "Income": income,
            "Date": date,
            "Employer": employer,
            "Description": description,
            "Taxable": taxable,
            "Received in bank account": received_in_bank,
            "Comment": comment
        }
        edited_df = pd.concat(
                [existing_income, pd.DataFrame([new_row])],
                ignore_index=True
            )[utils.INCOME_DATA_SCHEMA]
        utils.save_data(
            edited_df,
            os.getenv("EXCEL_PATH_INCOME"),
            utils.INCOME_SHEET_NAME)
        utils.fetch_income_deduction_data.clear()
        st.rerun()


def render_transaction_input(inputs: DeltaGenerator):
    start_date, end_date = initialise_sidebar(inputs)
    transactions_data = utils.fetch_transaction_data(start_date, end_date)
    if transactions_data.empty:
        st.write("No transaction data fetched")
        return
    # inputs.dataframe(transactions_data)
    # inputs.write(transactions_data.columns)

    categorised_transactions = utils.fetch_spending_data()
    # only show the uncategorised transactions
    uncategorised_transactions = transactions_data[
        ~transactions_data['transactionId'].isin(categorised_transactions['transactionId'])
    ]
    uncategorised_transactions = clean_transaction_data(uncategorised_transactions)

    inputs.subheader("Uncategorised expenses")
    # inputs.write(uncategorised_transactions)
    # inputs.write(categorised_transactions)
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