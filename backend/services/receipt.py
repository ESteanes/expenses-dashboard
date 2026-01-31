"""Receipt handling service."""
import base64
import os
import uuid
from datetime import date
from io import BytesIO
from typing import Optional, List

from PIL import Image
from pdf2image import convert_from_bytes

from .datamanipulator import DataManipulator, DataSource


class ReceiptService:
    """Service for managing receipt images."""

    BASE_PATH = os.getenv("RECEIPT_PATH", "/app/data/receipts")
    PDF_TYPE = "application/pdf"
    IMAGE_TYPE = "image"

    def __init__(self, data_manipulator: DataManipulator):
        self.data_manipulator = data_manipulator
        self.datasource = self.data_manipulator.datasource

    def get_receipt_path(self, receipt_ref: str) -> str:
        """Get full path for a receipt reference."""
        try:
            date_part = receipt_ref.split("_")[0]
            dt = date.fromisoformat(date_part)
            sub_dir = dt.strftime("%Y/%m")
        except Exception:
            raise ValueError(f"Invalid filename format: {receipt_ref}")

        return os.path.join(self.BASE_PATH, sub_dir, receipt_ref)

    def get_receipt(self, receipt_ref: str) -> tuple[bytes, str]:
        """Get receipt file content and type."""
        file_path = self.get_receipt_path(receipt_ref)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Receipt not found: {file_path}")

        file_type = self._determine_type(receipt_ref)

        with open(file_path, "rb") as f:
            content = f.read()

        return content, file_type

    def get_receipt_as_images(self, receipt_ref: str) -> List[bytes]:
        """Get receipt as list of image bytes (handles PDFs)."""
        content, file_type = self.get_receipt(receipt_ref)

        if file_type == self.PDF_TYPE:
            # Convert PDF pages to images
            images = convert_from_bytes(content)
            result = []
            for img in images:
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                result.append(buffer.getvalue())
            return result
        else:
            return [content]

    def get_receipt_base64(self, receipt_ref: str) -> List[str]:
        """Get receipt as base64-encoded image strings."""
        images = self.get_receipt_as_images(receipt_ref)
        return [
            f"data:image/png;base64,{base64.b64encode(img).decode('utf-8')}"
            for img in images
        ]

    def save_receipt(
        self,
        file_content: bytes,
        filename: str,
        receipt_date: date,
        existing_ref: Optional[str] = None,
    ) -> str:
        """Save a receipt file and return its reference."""
        if self.datasource != DataSource.EXCEL:
            raise ValueError(f"Unsupported data source: {self.datasource}")

        # Create directory structure
        year_month = receipt_date.strftime("%Y/%m")
        save_dir = os.path.join(self.BASE_PATH, year_month)
        os.makedirs(save_dir, exist_ok=True)

        # Generate or use existing filename
        file_extension = filename.split(".")[-1].lower()

        if existing_ref:
            ref = existing_ref
        else:
            ref = f"{receipt_date.strftime('%Y-%m-%d')}_{uuid.uuid4()}.{file_extension}"

        file_path = os.path.join(save_dir, ref)

        # Save the file
        if file_extension == "pdf":
            with open(file_path, "wb") as f:
                f.write(file_content)
        elif file_extension in ["jpg", "jpeg", "png"]:
            img = Image.open(BytesIO(file_content))
            img.save(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

        return ref

    def rotate_receipt(self, receipt_ref: str, angle: int) -> str:
        """Rotate a receipt image and save it."""
        file_path = self.get_receipt_path(receipt_ref)
        file_type = self._determine_type(receipt_ref)

        if file_type == self.PDF_TYPE:
            raise ValueError("Cannot rotate PDF files")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Receipt not found: {file_path}")

        img = Image.open(file_path)
        rotated = img.rotate(angle, expand=True)
        rotated.save(file_path)

        return receipt_ref

    def delete_receipt(self, receipt_ref: str) -> bool:
        """Delete a receipt file."""
        file_path = self.get_receipt_path(receipt_ref)

        if os.path.exists(file_path):
            os.remove(file_path)
            return True

        return False

    def _determine_type(self, filename: str) -> str:
        """Determine file type from filename."""
        extension = filename.split(".")[-1].lower()
        if extension == "pdf":
            return self.PDF_TYPE
        return self.IMAGE_TYPE


