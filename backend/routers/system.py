"""System API endpoints."""
from datetime import datetime

from fastapi import APIRouter

from backend.services.datamanipulator import get_data_manipulator
from backend.services.spending import get_spending_service, invalidate_spending_cache
from backend.services.income import get_income_service, invalidate_income_cache

router = APIRouter()


@router.get("/status")
async def get_status():
    """Get system status and data source info."""
    dm = get_data_manipulator()
    spending_service = get_spending_service()
    income_service = get_income_service()

    # Get counts
    try:
        spending_count = len(spending_service.spending)
        location_count = len(spending_service.location)
        top_count = len(spending_service.top_table)
        middle_count = len(spending_service.middle_table)
        base_count = len(spending_service.base_table)
    except Exception:
        spending_count = 0
        location_count = 0
        top_count = 0
        middle_count = 0
        base_count = 0

    try:
        income_count = len(income_service.income)
    except Exception:
        income_count = 0

    # Get latest transaction date
    try:
        latest_spending = spending_service.spending['Date'].max()
        latest_spending_str = latest_spending.isoformat() if latest_spending else None
    except Exception:
        latest_spending_str = None

    try:
        latest_income = income_service.income['Date'].max()
        latest_income_str = latest_income.isoformat() if latest_income else None
    except Exception:
        latest_income_str = None

    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "data_source": dm.get_datasource(),
        "counts": {
            "spending": spending_count,
            "income": income_count,
            "locations": location_count,
            "categories": top_count,
            "sub_categories": middle_count,
            "items": base_count,
        },
        "latest_transactions": {
            "spending": latest_spending_str,
            "income": latest_income_str,
        }
    }


@router.post("/refresh")
async def refresh_data():
    """Clear all caches and force data refresh."""
    invalidate_spending_cache()
    invalidate_income_cache()

    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}
