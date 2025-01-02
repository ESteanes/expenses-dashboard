import streamlit as st
import utils

st.write("""
This is the landing page
""")

utils.fetch_income_deduction_data()
utils.fetch_spending_data()