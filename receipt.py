import base64
import os
import uuid
from io import BytesIO
from pathlib import Path
from typing import Optional

import pandas as pd
from PIL import Image


class Receipt:
    """A class to handle receipt image operations."""

    BASE_PATH = os.getenv("RECEIPT_PATH", "/app/data/receipts")

    def __init__(self):
        """Initialize the receipt with an optional reference."""
        self.receipt_ref: Optional[str] = None
        self.image: Optional[Image.Image] = None
        self.path = None

    def set_path(self, receipt_ref: str):
        try:
            date_part = receipt_ref.split("_")[0]  # Extract the date part
            date = pd.Timestamp(date_part)  # Convert to Timestamp
            sub_dir = date.strftime("%Y/%m")  # Match save structure
        except Exception:
            raise ValueError(f"Invalid filename format: {receipt_ref}")
        file_path = os.path.join(self.BASE_PATH, sub_dir, receipt_ref)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image not found: {file_path}")
        self.path = file_path
        self.receipt_ref = receipt_ref
        return self

    def read_image(self) -> Image.Image:
        """Reads the image from the file system."""
        self.image = Image.open(self.path)
        return self.image

    def rotate_image(self, angle: int) -> Image.Image:
        """Rotates the image by the given angle."""
        if self.image is None:
            raise ValueError("No image loaded. Read or provide an image first.")
        self.image = self.image.rotate(angle, expand=True)
        return self.image

    def save_image(self, image: Image.Image, image_date: pd.Timestamp) -> str:
        """Saves the image in the file system under a date-based structure.

        Args:
            image (Image.Image): The image to save.
            image_date (pd.Timestamp): The date associated with the receipt.

        Returns:
            str: The relative path where the image is saved.
        """
        if image is None:
            raise ValueError("No image provided to save.")

        # Create directory structure
        year_month: str = image_date.strftime("%Y-%m")
        save_path: Path = Path(self.BASE_PATH) / year_month
        save_path.mkdir(parents=True, exist_ok=True)

        # Generate a unique filename
        filename: str = f"{image_date.strftime('%Y-%m-%d')}_{uuid.uuid4()}.png"
        image_path: Path = save_path / filename

        # Save the image
        image.save(image_path)
        self.receipt_ref = str(Path(year_month) / filename)
        return self.receipt_ref

    def get_base64_image(self) -> Optional[str]:
        """Returns the image as a base64-encoded string."""
        if not self.path:
            raise ValueError("No Image has been loaded")
        buffered = BytesIO()
        self.read_image().save(buffered, format="PNG")
        encoded_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded_string}"
