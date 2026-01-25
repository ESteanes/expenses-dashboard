"""Pydantic schemas for hierarchy data."""
from typing import List, Optional

from pydantic import BaseModel, Field


class CategoryEntry(BaseModel):
    """Top-level category."""
    sub_category: str = Field(..., alias="Sub Category")
    category: str = Field(..., alias="Category")

    class Config:
        populate_by_name = True


class SubCategoryEntry(BaseModel):
    """Middle-level sub-category."""
    sub_sub_category: str = Field(..., alias="Sub Sub Category")
    sub_category: str = Field(..., alias="Sub Category")

    class Config:
        populate_by_name = True


class ItemEntry(BaseModel):
    """Base-level item."""
    all_items: str = Field(..., alias="All Items")
    sub_sub_category: str = Field(..., alias="Sub Sub Category")

    class Config:
        populate_by_name = True


class HierarchyUpdate(BaseModel):
    """Batch update for hierarchy tables."""
    entries: List[dict]


class HierarchyData(BaseModel):
    """Complete hierarchy data."""
    categories: List[CategoryEntry]
    sub_categories: List[SubCategoryEntry]
    items: List[ItemEntry]
