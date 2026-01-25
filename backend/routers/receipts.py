"""Receipt API endpoints."""
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response

from backend.services.receipt import get_receipt_service

router = APIRouter()


@router.get("/{receipt_ref}")
async def get_receipt(receipt_ref: str):
    """Get a receipt image."""
    service = get_receipt_service()
    try:
        content, file_type = service.get_receipt(receipt_ref)

        if file_type == service.PDF_TYPE:
            media_type = "application/pdf"
        else:
            # Determine image type from extension
            ext = receipt_ref.split(".")[-1].lower()
            media_type = f"image/{ext}" if ext in ["jpg", "jpeg", "png"] else "image/png"

        return Response(content=content, media_type=media_type)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{receipt_ref}/base64")
async def get_receipt_base64(receipt_ref: str):
    """Get receipt as base64-encoded images."""
    service = get_receipt_service()
    try:
        images = service.get_receipt_base64(receipt_ref)
        return {"images": images}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("")
async def upload_receipt(
    file: UploadFile = File(...),
    receipt_date: date = Form(...),
    existing_ref: Optional[str] = Form(None),
):
    """Upload a new receipt."""
    service = get_receipt_service()
    try:
        content = await file.read()
        ref = service.save_receipt(
            file_content=content,
            filename=file.filename,
            receipt_date=receipt_date,
            existing_ref=existing_ref,
        )
        return {"receipt_ref": ref}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{receipt_ref}/rotate")
async def rotate_receipt(receipt_ref: str, angle: int = 90):
    """Rotate a receipt image."""
    service = get_receipt_service()
    try:
        service.rotate_receipt(receipt_ref, angle)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{receipt_ref}")
async def delete_receipt(receipt_ref: str):
    """Delete a receipt."""
    service = get_receipt_service()
    deleted = service.delete_receipt(receipt_ref)
    return {"success": deleted}
