"""Income API endpoints."""
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from backend.dependencies import IncomeServiceDep
from backend.schemas.income import (
    IncomeEntry,
    IncomeEntryCreate,
    IncomeSummary,
)

router = APIRouter()


@router.get("", response_model=List[dict])
async def list_income(
    service: IncomeServiceDep,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    employers: Optional[List[str]] = Query(None),
    descriptions: Optional[List[str]] = Query(None),
    financial_years: Optional[List[str]] = Query(None),
):
    """Get list of income entries with optional filters."""
    return service.get_income_list(
        start_date=start_date,
        end_date=end_date,
        employers=employers,
        descriptions=descriptions,
        financial_years=financial_years,
    )


@router.get("/summary", response_model=IncomeSummary)
async def get_income_summary(
    service: IncomeServiceDep,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """Get income summary statistics."""
    return service.get_summary(start_date=start_date, end_date=end_date)


@router.get("/filters")
async def get_filter_options(service: IncomeServiceDep):
    """Get unique values for filter dropdowns."""
    return {
        "employers": service.get_unique_values("Employer"),
        "descriptions": service.get_unique_values("Description"),
        "financial_years": service.get_unique_values("Financial Year"),
    }


@router.get("/deductions", response_model=List[dict])
async def list_deductions(service: IncomeServiceDep):
    """Get list of deduction entries."""
    return service.deductions.to_dict(orient='records')


@router.post("", response_model=dict)
async def create_income_entry(service: IncomeServiceDep, entry: IncomeEntryCreate):
    """Create a new income entry."""
    try:
        return service.create_entry(entry.model_dump(by_alias=False))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{index}")
async def delete_income_entry(service: IncomeServiceDep, index: int):
    """Delete an income entry."""
    try:
        service.delete_entry(index)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
