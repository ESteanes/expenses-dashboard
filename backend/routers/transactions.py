"""Transaction API endpoints - proxy to Expense Manager."""
from datetime import datetime
import os
from typing import Optional, List
from datetime import date
from io import StringIO

from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import requests

router = APIRouter()

EXPENSE_MANAGER_URL = os.getenv("EXPENSE_MANAGER_URL", "http://localhost:6123")
DEFAULT_ACCOUNT_ID = "a90b55ad-1bcb-4e75-b407-0e0e1e5c8a6d"
DEFAULT_TRANSACTION_TYPES = [
    'Payment', 'Purchase', 'Refund', 'EFTPOS Deposit',
    'Direct Credit', 'International ATM Cash Out', 'International Purchase'
]


def clean_transaction_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform transaction data."""
    clean = df.rename(columns={
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
    if 'Details' in clean.columns:
        clean['Details'] = clean['Details'].fillna('').astype(str)
    if 'Tag' in clean.columns:
        clean['Tag'] = clean['Tag'].fillna('').astype(str)
    return clean


@router.get("")
async def get_transactions(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    account_id: str = Query(DEFAULT_ACCOUNT_ID),
    transaction_types: Optional[List[str]] = Query(None),
):
    """Get transactions from Up Bank via Expense Manager."""
    if start_date is None:
        start_date = (pd.Timestamp.today() - pd.DateOffset(months=1)).date()
    if end_date is None:
        end_date = (pd.Timestamp.today() + pd.DateOffset(days=1)).date()
    if transaction_types is None:
        transaction_types = DEFAULT_TRANSACTION_TYPES

    params = {
        "startDate": f"{start_date.isoformat()}T00:00:00.000Z",
        "endDate": f"{end_date.isoformat()}T00:00:00.000Z",
        "numTransactions": 10000,
        "accountId": account_id,
        "transactionTypes": transaction_types,
    }

    try:
        response = requests.get(
            f"{EXPENSE_MANAGER_URL}/api/v1/transactions/csv",
            params=params,
        )
        response.raise_for_status()

        csv_data = response.content.decode("utf-8")
        df = pd.read_csv(StringIO(csv_data))
        df = clean_transaction_data(df)

        return df.to_dict(orient='records')
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error fetching from Expense Manager: {str(e)}"
        )


@router.get("/uncategorized")
async def get_uncategorized_transactions(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """Get transactions that haven't been categorized yet."""
    from backend.services.spending import get_spending_service

    # Get all transactions
    transactions = await get_transactions(start_date=start_date, end_date=end_date)

    # Get existing transaction IDs from spending
    service = get_spending_service()
    existing_ids = set(service.spending['transactionId'].dropna().unique())

    # Filter to uncategorized
    uncategorized = [
        t for t in transactions
        if t.get('transactionId') not in existing_ids
    ]

    return uncategorized


@router.get("/raw")
async def get_raw_transactions(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """Get raw transaction data without transformation (for debugging)."""
    if start_date is None:
        start_date = (pd.Timestamp.today() - pd.DateOffset(months=1)).date()
    if end_date is None:
        end_date = (pd.Timestamp.today() + pd.DateOffset(days=1)).date()

    params = {
        "startDate": f"{start_date.isoformat()}T00:00:00.000Z",
        "endDate": f"{end_date.isoformat()}T00:00:00.000Z",
        "numTransactions": 10000,
        "accountId": DEFAULT_ACCOUNT_ID,
        "transactionTypes": DEFAULT_TRANSACTION_TYPES,
    }

    try:
        response = requests.get(
            f"{EXPENSE_MANAGER_URL}/api/v1/transactions/csv",
            params=params,
        )
        response.raise_for_status()

        csv_data = response.content.decode("utf-8")
        df = pd.read_csv(StringIO(csv_data))

        return df.to_dict(orient='records')
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error fetching from Expense Manager: {str(e)}"
        )
