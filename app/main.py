import streamlit as st
import pandas as pd
import classes.spending as spending
import utils

st.set_page_config(
    page_title="Manage Expenses",
    page_icon=":money:"
)


income, deductions = utils.fetch_income_deduction_data()
spending_data = spending.SpendingData().fetch_spending_data()

transaction_data = utils.fetch_transaction_data()
uncategorised_transactions = transaction_data[
        ~transaction_data['transactionId'].isin(spending_data.spending['transactionId'])
    ]
col1, col2, col3 = st.columns(3)
col1.metric("No. uncategorised transactions", len(uncategorised_transactions))
col1.metric("No. transactions from Up Bank", len(transaction_data))

col2.metric("Latest Transaction", spending_data.spending['Date'].max().strftime('%Y-%m-%d'), delta=-int(pd.Timedelta(pd.Timestamp.now() - spending_data.spending['Date'].max()).total_seconds()/(60*60*24)))
col2.metric("Number of transactions recorded:", len(spending_data.spending))

col3.metric("Number of incomes recorded", len(income))
col3.metric("Most recent income recorded", income['Date'].max().strftime("%Y-%m-%d"), delta=-int(pd.Timedelta(pd.Timestamp.now() - income['Date'].max()).total_seconds()/(60*60*24)))

st.divider()
a, b, c, d = st.columns(4)
a.metric("Rows in location table", len(spending_data.location))
b.metric("Rows in top table", len(spending_data.top_table))
c.metric("Rows in middle table", len(spending_data.middle_table))
d.metric("Rows in base table", len(spending_data.base_table))

st.divider()

st.write(f"Income path: `{utils.INCOME_PATH}`")
st.write(f"Spending path: `{spending.SPENDING_PATH}`")
