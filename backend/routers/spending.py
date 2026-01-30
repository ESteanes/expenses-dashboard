"""Spending API endpoints."""
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from backend.dependencies import SpendingServiceDep
from backend.schemas.spending import (
    SpendingEntry,
    SpendingEntryCreate,
    SpendingEntryUpdate,
    SpendingSummary,
)

router = APIRouter()


@router.get("", response_model=List[dict])
async def list_spending(
    service: SpendingServiceDep,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    tags: Optional[List[str]] = Query(None),
    shops: Optional[List[str]] = Query(None),
    locations: Optional[List[str]] = Query(None),
    categories: Optional[List[str]] = Query(None),
    sub_categories: Optional[List[str]] = Query(None),
):
    """Get list of spending entries with optional filters."""
    return service.get_spending_list(
        start_date=start_date,
        end_date=end_date,
        tags=tags,
        shops=shops,
        locations=locations,
        categories=categories,
        sub_categories=sub_categories,
    )


@router.get("/combined", response_model=List[dict])
async def get_combined_spending(
    service: SpendingServiceDep,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """Get spending data with hierarchy and location merged."""
    return service.get_spending_list(start_date=start_date, end_date=end_date)


@router.get("/summary", response_model=SpendingSummary)
async def get_spending_summary(
    service: SpendingServiceDep,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """Get spending summary statistics."""
    return service.get_summary(start_date=start_date, end_date=end_date)


@router.get("/recent", response_model=SpendingSummary)
async def get_recent_spending(
    service: SpendingServiceDep,
    days: int = Query(30, ge=1, le=365),
):
    """Get spending summary for recent days."""
    return service.get_recent_spending(days=days)


@router.get("/filters")
async def get_filter_options(service: SpendingServiceDep):
    """Get unique values for filter dropdowns."""
    return {
        "tags": service.get_unique_values("Tag"),
        "shops": service.get_unique_values("Shop"),
        "locations": service.get_unique_values("Location"),
        "categories": service.get_unique_values("Category"),
        "sub_categories": service.get_unique_values("Sub Category"),
        "sub_sub_categories": service.get_unique_values("Sub Sub Category"),
    }


@router.get("/{index}", response_model=dict)
async def get_spending_entry(service: SpendingServiceDep, index: int):
    """Get a single spending entry by index."""
    entries = service.get_spending_list()
    if index >= len(entries):
        raise HTTPException(status_code=404, detail="Entry not found")
    return entries[index]


@router.post("", response_model=dict)
async def create_spending_entry(service: SpendingServiceDep, entry: SpendingEntryCreate):
    """Create a new spending entry."""
    try:
        return service.create_entry(entry.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{index}", response_model=dict)
async def update_spending_entry(
    service: SpendingServiceDep,
    index: int,
    entry: SpendingEntryUpdate,
):
    """Update an existing spending entry."""
    try:
        return service.update_entry(index, entry.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{index}")
async def delete_spending_entry(service: SpendingServiceDep, index: int):
    """Delete a spending entry."""
    try:
        service.delete_entry(index)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
