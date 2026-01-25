"""Pydantic schemas for income data."""
from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel, Field


TaxableType = Literal["Not-taxable", "Taxable", "Franked Dividends"]


class IncomeEntryBase(BaseModel):
    """Base schema for income entries."""
    gross_income: float = Field(..., alias="Gross Income")
    salary_sacrifice: float = Field(0.0, alias="Salary Sacrifice")
    tax: float = Field(0.0, alias="Tax")
    income: float = Field(..., alias="Income")
    date: datetime = Field(..., alias="Date")
    employer: str = Field(..., alias="Employer")
    description: str = Field(..., alias="Description")
    taxable: TaxableType = Field(..., alias="Taxable")
    received_in_bank_account: str = Field("Yes", alias="Received in bank account")
    comment: Optional[str] = Field(None, alias="Comment")

    class Config:
        populate_by_name = True


class IncomeEntryCreate(IncomeEntryBase):
    """Schema for creating an income entry."""
    pass


class IncomeEntry(IncomeEntryBase):
    """Full income entry with calculated fields."""
    financial_year: Optional[str] = Field(None, alias="Financial Year")
    taxable_income: Optional[float] = Field(None, alias="Taxable Income")

    class Config:
        populate_by_name = True


class IncomeFilters(BaseModel):
    """Filters for income queries."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    employers: Optional[List[str]] = None
    descriptions: Optional[List[str]] = None
    financial_years: Optional[List[str]] = None


class IncomeSummary(BaseModel):
    """Summary statistics for income."""
    total_gross: float
    total_tax: float
    total_net: float
    by_financial_year: dict
    by_employer: dict
