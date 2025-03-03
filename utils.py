import base64
import math
import os
import uuid
from io import StringIO, BytesIO

import altair as alt
import pandas as pd
import requests
import streamlit as st
from PIL import Image
from streamlit.delta_generator import DeltaGenerator

SPENDING_SHEET_NAME = "Spending"
SPENDING_DATA_SCHEMA = [
    "Item",
    "Cost",
    "Quantity",
    "Measure",
    "Location",
    "Shop",
    "Details",
    "Tag",
    "Date",
    "Receipt Ref",
    "Receipt",
    "transactionId"
]
SPENDING_PATH = os.getenv("EXCEL_PATH_SPENDING", default="/app/data/spending.xlsx")

INCOME_SHEET_NAME = "Income"
INCOME_DATA_SCHEMA = [
    "Gross Income",
    "Salary Sacrifice",
    "Tax",
    "Income",
    "Date",
    "Employer",
    "Description",
    "Taxable",
    "Received in bank account",
    "Comment"
]
TAXABLE_OPTIONS = ["Not-taxable", "Taxable", "Franked Dividends"]
INCOME_PATH = os.getenv("EXCEL_PATH_INCOME", default="/app/data/income.xlsx")
EXPENSE_MANAGER_URL = os.getenv("EXPENSE_MANAGER_URL", default="http://localhost:8080")
RECEIPT_PATH = os.getenv("RECEIPT_PATH", default="/app/data/receipts")


def dataframe_in_list(df, key, list_items):
    if not list_items:
        return df[key].isin(list_items)
    return df


def remove_unnamed_columns(df):
    return df.loc[:, ~df.columns.str.contains('^Unnamed')]


def calculate_financial_year(date):
    # Adjust year based on whether the month is July or later
    if pd.isna(date):
        return None  # Handle missing dates
    year = date.year
    if date.month >= 7:
        return f"FY {year}/{year + 1}"
    else:
        return f"FY {year - 1}/{year}"


class SpendingData:
    def __init__(self, spending: pd.DataFrame, location: pd.DataFrame,
                 base_table: pd.DataFrame, middle_table: pd.DataFrame,
                 top_table: pd.DataFrame, ):
        """Initialize with preloaded tables."""
        self.spending = spending
        self.location = location
        self.base_table = base_table
        self.middle_table = middle_table
        self.top_table = top_table
        self.combined = pd.DataFrame()

    def combine(self):
        """Return the enriched spending data with all hierarchy tables merged."""
        hierarchy = (
            self.base_table
            .rename(columns={'All Items': 'Item'})
            .merge(self.middle_table, on="Sub Sub Category")
            .merge(self.top_table, on="Sub Category")
        )
        df = (
            self.spending
            .merge(hierarchy, on='Item', how='left')
            .merge(self.location, on='Location', how='left')
        )
        # Ensure specific columns are strings
        df['Details'] = df['Details'].astype(str)
        df['Tag'] = df['Tag'].astype(str)
        df['Measure'] = df['Measure'].astype(str)
        self.combined = df
        return self


@st.cache_data
def fetch_spending_data() -> SpendingData:
    # Data ingest and basic prep hello
    spending_data = pd.read_excel(
        SPENDING_PATH,
        sheet_name=[SPENDING_SHEET_NAME, "Top_Table", "Middle Table", "Base Table", "Location"])

    return SpendingData(
        spending=(remove_unnamed_columns(spending_data['Spending'])),
        top_table=(remove_unnamed_columns(spending_data['Top_Table'])),
        middle_table=(remove_unnamed_columns(spending_data['Middle Table'])),
        base_table=(remove_unnamed_columns(spending_data['Base Table'])),
        location=(remove_unnamed_columns(spending_data['Location']))
    )


def add_base64_column(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a column with base64-encoded images if 'Receipt Ref' exists."""
    df["Receipt Base64"] = df["Receipt Ref"].apply(
        lambda ref: image_to_base64(read_image(ref)) if pd.notna(ref) and ref else None
    )
    return df


@st.cache_data
def fetch_income_deduction_data():
    income_sheets = pd.read_excel(
        INCOME_PATH,
        sheet_name=["Income", "Deductions"]
    )
    income_data = remove_unnamed_columns(income_sheets['Income'])
    income_data.loc[:, ["Salary Sacrifice", "Tax"]] = income_data.loc[:,
                                                      ["Salary Sacrifice", "Tax"]
                                                      ].fillna(0)
    income_data.loc[:, "Financial Year"] = pd.to_datetime(
        income_data.loc[:, 'Date']).apply(calculate_financial_year)
    income_data.loc[:, 'Taxable Income'] = income_data.apply(
        lambda row: (
            row['Gross Income'] - row['Salary Sacrifice']
            if row['Taxable'] == 'Taxable' else
            row['Gross Income'] + row['Tax']
            if row['Taxable'] == 'Franked Dividends' else
            0
        ),
        axis=1
    )

    deduction_data = remove_unnamed_columns(income_sheets['Deductions'])
    deduction_data["Financial Year"] = pd.to_datetime(
        deduction_data['Date']
    ).apply(calculate_financial_year)
    return income_data, deduction_data


def date_sidebar(
    st: DeltaGenerator,
    df: pd.DataFrame,
    date_key: str,
    start_at_minimum=False
):
    minimum_date = df[date_key].min()
    maximum_date = df[date_key].max()
    start_date_initial_value = maximum_date - pd.DateOffset(months=1)
    if start_at_minimum:
        start_date_initial_value = minimum_date

    start_date = st.sidebar.date_input(
        "Start Date",
        value=start_date_initial_value,
        min_value=minimum_date,
        max_value=maximum_date)
    end_date = st.sidebar.date_input(
        "End Date",
        value=maximum_date,
        min_value=minimum_date,
        max_value=maximum_date)
    return start_date, end_date


def plot_bar_chart(dataframe, x_column, y_column, title, max_items=20):
    """Helper function to generate a bar chart with custom axis formatting."""
    chart_data = (
        dataframe.groupby(x_column)[y_column]
        .sum()
        .reset_index()
        .sort_values(by=y_column, ascending=False)
        .head(max_items)
    )
    select = alt.selection_point(name="select", on="click")
    highlight = alt.selection_point(name="highlight", on="pointerover", empty=False)
    stroke_width = (
        alt.when(select).then(alt.value(2, empty=False))
        .when(highlight).then(alt.value(1))
        .otherwise(alt.value(0))
    )
    return (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X(
                x_column,
                sort=None,
                title=title,
                axis=alt.Axis(labelAngle=-30, labelOverlap=False),
            ),
            y=alt.Y(
                y_column,
                title="Total Cost",
                axis=alt.Axis(labelExpr='"$" + datum.value'),
            ),
            fillOpacity=alt.when(select).then(alt.value(1)).otherwise(alt.value(0.3)),
            strokeWidth=stroke_width,
        ).configure_scale(bandPaddingInner=0.2).add_params(select, highlight)
    )


def format_income_table(dataframe: pd.DataFrame, column_names=(
    "Gross Income",
    "Salary Sacrifice",
    "Taxable Income",
    "Income",
    "Tax")):
    dataframe_formatted = dataframe.style.format(
        {columnname: '${:,.2f}' for columnname in column_names}
    )
    return dataframe_formatted


# Fetch the data from Upbank Client as a csv then read into a dataframe
@st.cache_data
def fetch_transaction_data(
    start_date=pd.Timestamp.today() - pd.DateOffset(months=1),
    end_date=pd.Timestamp.today() + pd.DateOffset(days=1)
):
    csv_endpoint = "/api/v1/transactions/csv"
    params = {
        "startDate": f"{start_date.strftime('%Y-%m-%d')}T00:00:00.000Z",
        "endDate": f"{end_date.strftime('%Y-%m-%d')}T00:00:00.000Z",
        "numTransactions": 10000,
        "accountId": "a90b55ad-1bcb-4e75-b407-0e0e1e5c8a6d",
        # We need EFTPOS Deposit for BeemIt transactions as they are processed using EFTPOS
        # Direct credit is how some refunds appear
        "transactionTypes": ['Payment', 'Purchase', 'Refund', 'EFTPOS Deposit', 'Direct Credit']
    }
    try:
        # Fetch the CSV data
        response = requests.get(EXPENSE_MANAGER_URL + csv_endpoint, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Convert CSV response to a pandas DataFrame
        csv_data = response.content.decode("utf-8")
        dataframe = pd.read_csv(StringIO(csv_data))
        return clean_transaction_data(dataframe)

    except requests.exceptions.RequestException as e:
        st.error(
            f"Please check that the service is running successfully at {EXPENSE_MANAGER_URL}.\n\n An error occurred while fetching the data: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame()


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


def save_data(df: pd.DataFrame, file_path: str, sheet_name: str):
    with pd.ExcelWriter(
        file_path,
        mode='a',
        if_sheet_exists='replace',
        engine='openpyxl',
        date_format="YYYY-MM-DD",
        datetime_format="YYYY-MM-DD"
    ) as writer:
        df.to_excel(
            writer,
            sheet_name=sheet_name,
        )


# Function to automatically rotate the image based on orientation
def rotate_image(image: Image.Image, manual_rotation_deg: int) -> Image.Image:
    if manual_rotation_deg != 0:
        return image.rotate(manual_rotation_deg, expand=True)
    return image


def save_image(image: Image, date: pd.Timestamp):
    sub_dir = date.strftime("%Y/%m")  # Organizes by Year/Month
    save_path = os.path.join(RECEIPT_PATH, sub_dir)

    os.makedirs(save_path, exist_ok=True)  # Ensure directory exists
    receipt_ref = f"{date.strftime('%Y-%m-%d')}_{uuid.uuid4()}.jpeg"

    file_path = os.path.join(save_path, receipt_ref)
    image.save(file_path)  # Assumes 'image' is a PIL Image or a file-like object with `.save()`

    return receipt_ref  # Return the saved file path for reference


def read_display_image(receipt_ref: str):
    image = read_image(receipt_ref)


def read_image(receipt_ref: str) -> Image:
    try:
        date_part = receipt_ref.split("_")[0]  # Extract the date part
        date = pd.Timestamp(date_part)  # Convert to Timestamp
        sub_dir = date.strftime("%Y/%m")  # Match save structure
    except Exception:
        raise ValueError(f"Invalid filename format: {receipt_ref}")
    file_path = os.path.join(RECEIPT_PATH, sub_dir, receipt_ref)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image not found: {file_path}")
    return Image.open(file_path)


def save_file(uploaded_file, date: pd.Timestamp, existing_file, manual_rotation_deg: int):
    """Save an uploaded file (image or PDF) in a structured directory format."""
    # Ensure the base directory exists
    os.makedirs(RECEIPT_PATH, exist_ok=True)

    # Extract year and month from the date
    save_dir = os.path.join(RECEIPT_PATH, date.strftime("%Y/%m"))
    os.makedirs(save_dir, exist_ok=True)

    # Get file extension and generate a unique filename
    file_extension = uploaded_file.name.split(".")[-1].lower()
    filename = f"{date.strftime('%Y-%m-%d')}_{uuid.uuid4()}.{file_extension}"
    if existing_file and not math.isnan(existing_file):
        filename = existing_file
    file_path = os.path.join(save_dir, filename)

    # Handle PDFs
    if file_extension == "pdf":
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    # Handle Images (JPG, JPEG, PNG)
    elif file_extension in ["jpg", "jpeg", "png"]:
        image = Image.open(uploaded_file)
        image = rotate_image(image, manual_rotation_deg)  # Ensure correct orientation
        image.save(file_path)

    else:
        raise ValueError("Unsupported file format")

    return filename  # Return the saved file path


def delete_file(receipt_reference: str):
    if not receipt_reference:
        return
    receipt_date = receipt_reference.split("_")[0]
    year = receipt_date.split("-")[0]
    month = receipt_date.split("-")[1]
    receipt_path = os.path.join(RECEIPT_PATH, year, month)
    receipt_file = os.path.join(receipt_path, receipt_reference)
    if os.path.exists(receipt_file):
        os.remove(receipt_file)
        return


def image_to_base64(image: Image) -> str:
    """Converts a PIL Image to a base64-encoded string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"
