import streamlit as st
import pandas as pd
import classes.spending as spending
import utils

st.set_page_config(
    page_title="Manage Expenses",
    page_icon=":money:"
)
if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = None

income, deductions = utils.fetch_income_deduction_data()
spending_data = spending.SpendingData().fetch_spending_data()
st.session_state.last_refresh = pd.Timestamp.now()
transaction_data = utils.fetch_transaction_data()
uncategorised_transactions = transaction_data[
        ~transaction_data['transactionId'].isin(spending_data.spending['transactionId'])
    ]

st.metric("Last Refresh", st.session_state.last_refresh.strftime("%Y-%m-%d %H:%M:%S"))
col1, col2, col3 = st.columns(3, border=True)
col1.metric("No. uncategorised transactions", len(uncategorised_transactions))
col1.metric("No. transactions from Up Bank", len(transaction_data))

col2.metric(
    "Latest Transaction",
    f"{int(pd.Timedelta(pd.Timestamp.now() - spending_data.spending['Date'].max()).total_seconds()/(60*60*24))} days since",
    )
col2.metric("No. transactions recorded", len(spending_data.spending))

col3.metric(
      "Most recent income recorded",
      income['Date'].max().strftime("%Y-%m-%d")
    )
col3.metric("No. incomes recorded", len(income))

st.divider()
a, b, c, d = st.columns(4)
a.metric("Rows in location table", len(spending_data.location))
b.metric("Rows in top table", len(spending_data.top_table))
c.metric("Rows in middle table", len(spending_data.middle_table))
d.metric("Rows in base table", len(spending_data.base_table))

st.divider()

st.write(f"Income path: `{utils.INCOME_PATH}`")
st.write(f"Spending path: `{spending.SPENDING_PATH}`")


if st.button("Refresh Data", on_click=utils.refresh_all_the_data):
    st.session_state.last_refresh = pd.Timestamp.now()