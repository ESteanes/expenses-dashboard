import streamlit as st
import utils

st.set_page_config(
    page_title="Manage Expenses",
    page_icon=":money:"
)

st.write("""
This is the landing page
""")

utils.fetch_income_deduction_data()
utils.fetch_spending_data()
utils.fetch_transaction_data()