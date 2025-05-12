from io import StringIO

import pandas as pd
import requests
import streamlit as st

from app.utils import fetch_transaction_data, EXPENSE_MANAGER_URL


def get_data_manually() -> pd.DataFrame:
    start_date = pd.Timestamp.today() - pd.DateOffset(months=1)
    end_date = pd.Timestamp.today() + pd.DateOffset(days=1)
    csv_endpoint = "/api/v1/transactions/csv"
    params = {
        "startDate": f"{start_date.strftime('%Y-%m-%d')}T00:00:00.000Z",
        "endDate": f"{end_date.strftime('%Y-%m-%d')}T00:00:00.000Z",
        "numTransactions": 10000,
        "accountId": "a90b55ad-1bcb-4e75-b407-0e0e1e5c8a6d",
        # We need EFTPOS Deposit for BeemIt transactions as they are processed using EFTPOS
        # Direct credit is how some refunds appear
        # "transactionTypes": ['Payment', 'Purchase', 'Refund', 'EFTPOS Deposit', 'Direct Credit']
    }
    # Fetch the CSV data
    response = requests.get(EXPENSE_MANAGER_URL + csv_endpoint, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Convert CSV response to a pandas DataFrame
    csv_data = response.content.decode("utf-8")
    return pd.read_csv(StringIO(csv_data))


st.title("Debugging data fetching issues")
st.write("1. Check the regular data output from CSV Fetch")
st.dataframe(fetch_transaction_data())
st.write("2. Check fetching all transaction types for the past month manually")
st.dataframe(get_data_manually())
st.write("3. Look at the entire data (non-csv endpoint) and lets see what's changed")
