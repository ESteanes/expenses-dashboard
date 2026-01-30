"""Hierarchy API endpoints."""
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd

from backend.dependencies import SpendingServiceDep
from backend.services.datamanipulator import FileType, TableName

router = APIRouter()


class HierarchyBatchUpdate(BaseModel):
    """Batch update for hierarchy table."""
    entries: List[dict]


@router.get("/categories")
async def get_categories(service: SpendingServiceDep):
    """Get top-level categories (Top Table)."""
    return service.top_table.to_dict(orient='records')


@router.get("/subcategories")
async def get_subcategories(service: SpendingServiceDep):
    """Get sub-categories (Middle Table)."""
    return service.middle_table.to_dict(orient='records')


@router.get("/items")
async def get_items(service: SpendingServiceDep):
    """Get base items (Base Table)."""
    return service.base_table.to_dict(orient='records')


@router.get("/all")
async def get_all_hierarchy(service: SpendingServiceDep):
    """Get complete hierarchy data."""
    return {
        "categories": service.top_table.to_dict(orient='records'),
        "sub_categories": service.middle_table.to_dict(orient='records'),
        "items": service.base_table.to_dict(orient='records'),
    }


@router.put("/categories")
async def update_categories(service: SpendingServiceDep, update: HierarchyBatchUpdate):
    """Update categories (Top Table)."""
    try:
        service._top_table = pd.DataFrame(update.entries)
        service.data_manipulator.save_backing_table(
            FileType.SPENDING,
            TableName.TOP,
            service._top_table
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/subcategories")
async def update_subcategories(service: SpendingServiceDep, update: HierarchyBatchUpdate):
    """Update sub-categories (Middle Table)."""
    try:
        service._middle_table = pd.DataFrame(update.entries)
        service.data_manipulator.save_backing_table(
            FileType.SPENDING,
            TableName.MIDDLE,
            service._middle_table
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/items")
async def update_items(service: SpendingServiceDep, update: HierarchyBatchUpdate):
    """Update base items (Base Table)."""
    try:
        service._base_table = pd.DataFrame(update.entries)
        service.data_manipulator.save_backing_table(
            FileType.SPENDING,
            TableName.BASE,
            service._base_table
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
