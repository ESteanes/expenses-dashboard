"""Hierarchy API endpoints."""
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.spending import get_spending_service

router = APIRouter()


class HierarchyBatchUpdate(BaseModel):
    """Batch update for hierarchy table."""
    entries: List[dict]


@router.get("/categories")
async def get_categories():
    """Get top-level categories (Top Table)."""
    service = get_spending_service()
    return service.top_table.to_dict(orient='records')


@router.get("/subcategories")
async def get_subcategories():
    """Get sub-categories (Middle Table)."""
    service = get_spending_service()
    return service.middle_table.to_dict(orient='records')


@router.get("/items")
async def get_items():
    """Get base items (Base Table)."""
    service = get_spending_service()
    return service.base_table.to_dict(orient='records')


@router.get("/all")
async def get_all_hierarchy():
    """Get complete hierarchy data."""
    service = get_spending_service()
    return {
        "categories": service.top_table.to_dict(orient='records'),
        "sub_categories": service.middle_table.to_dict(orient='records'),
        "items": service.base_table.to_dict(orient='records'),
    }


@router.put("/categories")
async def update_categories(update: HierarchyBatchUpdate):
    """Update categories (Top Table)."""
    service = get_spending_service()
    try:
        import pandas as pd
        service._top_table = pd.DataFrame(update.entries)
        service.data_manipulator.save_backing_table(
            service.data_manipulator.FileType.SPENDING,
            service.data_manipulator.TableName.TOP,
            service._top_table
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/subcategories")
async def update_subcategories(update: HierarchyBatchUpdate):
    """Update sub-categories (Middle Table)."""
    service = get_spending_service()
    try:
        import pandas as pd
        service._middle_table = pd.DataFrame(update.entries)
        service.data_manipulator.save_backing_table(
            service.data_manipulator.FileType.SPENDING,
            service.data_manipulator.TableName.MIDDLE,
            service._middle_table
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/items")
async def update_items(update: HierarchyBatchUpdate):
    """Update base items (Base Table)."""
    service = get_spending_service()
    try:
        import pandas as pd
        service._base_table = pd.DataFrame(update.entries)
        service.data_manipulator.save_backing_table(
            service.data_manipulator.FileType.SPENDING,
            service.data_manipulator.TableName.BASE,
            service._base_table
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
