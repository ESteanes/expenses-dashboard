"""Pydantic schemas for spending data."""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class SpendingEntryBase(BaseModel):
    """Base schema for spending entries."""
    item: str = Field(..., description="Item name")
    cost: float = Field(..., description="Cost of the item")
    quantity: Optional[float] = Field(None, description="Quantity purchased")
    measure: Optional[str] = Field(None, description="Unit of measure")
    location: Optional[str] = Field(None, description="Purchase location")
    shop: Optional[str] = Field(None, description="Shop/retailer name")
    details: Optional[str] = Field(None, description="Additional details")
    tag: Optional[str] = Field(None, description="Custom tag")
    date: datetime = Field(..., description="Transaction date")


class SpendingEntryCreate(SpendingEntryBase):
    """Schema for creating a spending entry."""
    receipt_ref: Optional[str] = Field(None, description="Receipt reference")
    transaction_id: Optional[str] = Field(None, description="Bank transaction ID")


class SpendingEntryUpdate(BaseModel):
    """Schema for updating a spending entry."""
    item: Optional[str] = None
    cost: Optional[float] = None
    quantity: Optional[float] = None
    measure: Optional[str] = None
    location: Optional[str] = None
    shop: Optional[str] = None
    details: Optional[str] = None
    tag: Optional[str] = None
    date: Optional[datetime] = None
    receipt_ref: Optional[str] = None


class SpendingEntry(SpendingEntryBase):
    """Full spending entry with all fields."""
    receipt_ref: Optional[str] = None
    receipt: Optional[str] = None
    transaction_id: Optional[str] = Field(None, alias="transactionId")

    # Hierarchy fields (from combined data)
    sub_sub_category: Optional[str] = Field(None, alias="Sub Sub Category")
    sub_category: Optional[str] = Field(None, alias="Sub Category")
    category: Optional[str] = Field(None, alias="Category")

    # Location fields
    latitude: Optional[float] = Field(None, alias="Latitude")
    longitude: Optional[float] = Field(None, alias="Longitude")

    class Config:
        populate_by_name = True


class SpendingFilters(BaseModel):
    """Filters for spending queries."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    shops: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    sub_categories: Optional[List[str]] = None


class SpendingSummary(BaseModel):
    """Summary statistics for spending."""
    total_cost: float
    transaction_count: int
    latest_transaction_date: Optional[datetime] = None
    uncategorized_count: int
    by_category: dict
    by_shop: dict
    by_tag: dict
