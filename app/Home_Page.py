import pandas as pd
import streamlit as st

import app.classes.spending as spending
import app.utils as utils
from app.classes.datamanipulator import DataManipulator, DataSource, FILE_CONFIGS, FileType

st.set_page_config(
    page_title="Manage Expenses",
    page_icon=":money:"
)
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = None

mydf = pd.read_excel(
    FILE_CONFIGS.get(FileType.SPENDING).path,
    sheet_name=[x.value for x in FILE_CONFIGS.get(FileType.SPENDING).tables])

income, deductions = utils.fetch_income_deduction_data()
data_manipulator = DataManipulator()
spending_data = spending.SpendingData(data_manipulator).fetch_spending_data()
st.session_state.last_refresh = pd.Timestamp.now()
transaction_data = utils.fetch_transaction_data()
uncategorised_transactions = transaction_data[
    ~transaction_data['transactionId'].isin(spending_data.spending['transactionId'])
]

st.metric(
    "Last Refresh",
    f"{st.session_state.last_refresh.strftime('%Y/%m/%d %H:%M:%S')} - {int(pd.Timedelta(pd.Timestamp.now() - st.session_state.last_refresh).total_seconds() / (60 * 60))} hours ago")
col1, col2, col3 = st.columns(3, border=True)
col1.metric("No. uncategorised transactions", len(uncategorised_transactions))
col1.metric("No. transactions from Up Bank", len(transaction_data))

col2.metric(
    "Latest Transaction",
    f"{int(pd.Timedelta(pd.Timestamp.now() - spending_data.spending['Date'].max()).total_seconds() / (60 * 60 * 24))} days since",
)
col2.metric("No. transactions recorded", len(spending_data.spending))

col3.metric(
    "Most recent income recorded",
    income['Date'].max().strftime("%Y/%m/%d")
)
col3.metric("No. incomes recorded", len(income))

st.divider()
a, b, c, d = st.columns(4)
a.metric("Rows in location table", len(spending_data.location))
b.metric("Rows in top table", len(spending_data.top_table))
c.metric("Rows in middle table", len(spending_data.middle_table))
d.metric("Rows in base table", len(spending_data.base_table))

st.divider()
st.write(f"Data source: {data_manipulator.datasource.value}")
if data_manipulator.datasource == DataSource.EXCEL:
    st.write(f"Income path: `{FILE_CONFIGS.get(FileType.INCOME).path}`")
    st.write(f"Spending path: `{FILE_CONFIGS.get(FileType.SPENDING).path}`")

if data_manipulator.datasource == DataSource.NEXTCLOUD:
    st.write(f"Nextcloud Income ShareId: {data_manipulator.income_share_id}")
    st.write(f"Nextcloud Spending ShareId: {data_manipulator.spending_share_id}")

st.divider()
st.write(f"Fetching up bank transactions from: {utils.EXPENSE_MANAGER_URL}")
if st.button("Refresh Data", on_click=utils.refresh_all_the_data):
    st.session_state.last_refresh = pd.Timestamp.now()
