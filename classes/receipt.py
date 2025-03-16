import base64
import math
import os
import uuid
from io import BytesIO
from typing import Optional, List

import pandas as pd
from PIL import Image
from pdf2image import convert_from_bytes
from streamlit.runtime.uploaded_file_manager import UploadedFile


class Receipt:
    """A class to handle receipt image operations."""

    BASE_PATH = os.getenv("RECEIPT_PATH", "/app/data/receipts")
    PDF_TYPE = "application/pdf"
    IMAGE_TYPE = "image"

    def __init__(self):
        """Initialize the receipt with an optional reference."""
        self.reference: Optional[str] = None
        self.filename: str = ""
        self.type: str = ""
        self.data: bytes = None
        self.image: Optional[Image.Image] = None
        self.path = None

    def set_uploaded_file(self, uploaded_file: UploadedFile):
        self.filename = uploaded_file.name
        self.type = uploaded_file.type 
        
        if self.type == Receipt.PDF_TYPE:
            self.data = uploaded_file.read()
            return
        
        self.data = uploaded_file
        self.image = Image.open(self.data)
        return

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
        self.reference = receipt_ref
        self.type = self.determine_type_from_filename(receipt_ref)
        return self

    def read_image(self) -> List[Image.Image]:
        # Reads image stored in class if present.
        if self.image:
            return [self.image]
        """Reads the image from the file system."""
        if self.type != "application/pdf":
            self.image = Image.open(self.path)
            return [self.image]

        return convert_from_bytes(self.data)

    def rotate_image(self, angle: int) -> Image.Image:
        """Rotates the image by the given angle."""
        if self.image is None:
            raise ValueError("No image loaded. Read or provide an image first.")
        self.image = self.image.rotate(angle, expand=True)
        return self.image

    def rotate_clockwise(self):
        if not self.type == Receipt.PDF_TYPE: 
            self.rotate_image(-90)

    def rotate_anti_clockwise(self):
        if not self.type == Receipt.PDF_TYPE: 
            self.rotate_image(90)

    def save_image(self, image_date: pd.Timestamp, existing_file_name: Optional[str | float]) -> str:
        if self.data is None:
            raise ValueError("No image provided to save.")

        # Create directory structure
        year_month: str = image_date.strftime("%Y/%m")
        save_dir: str = os.path.join(self.BASE_PATH, year_month)
        os.makedirs(save_dir, exist_ok=True)

        # Generate a unique filename
        file_extension = self.filename.split(".")[-1].lower()
        filename: str = f"{image_date.strftime('%Y-%m-%d')}_{uuid.uuid4()}.{file_extension}"
        if existing_file_name and not math.isnan(existing_file_name):
            filename = existing_file_name
        image_path: str = os.path.join(save_dir, filename)

        # Save the image
        if file_extension == "pdf":  # Handle PDFs
            with open(image_path, "wb") as f:
                f.write(self.data)
        elif file_extension in ["jpg", "jpeg", "png"]:  # Handle Images (JPG, JPEG, PNG)
            self.image.save(image_path)
        else:
            raise ValueError("Unsupported file format")

        self.path = os.path.join(year_month, filename)
        return filename

    def delete_image(self) -> str:
        if self.path is None:
            return "No path was specified"
        if os.path.isfile(self.path):
            os.remove(self.path)
            return "Receipt deleted successfully"
        return f"Receipt does not exist at specified path: {self.path}"

    def get_base64_image(self) -> List[str]:
        """Returns the image as a base64-encoded string."""
        if not self.path:
            raise ValueError("No Image has been loaded")
        buffered = BytesIO()
        base64_images = []
        for image in self.read_image():
            image.save(buffered, format="PNG")
            encoded_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
            base64_images += f"data:image/png;base64,{encoded_string}"
        return base64_images

    def read_from_path(self):
        with open(self.path, "rb") as f:
            self.data = f.read()
        return self


    def get_type(self):
        return self.type
    
    def determine_type_from_filename(self, filename: str) -> str:
        extension = filename.split(".")[-1].lower()
        if extension == "pdf":
            return self.PDF_TYPE
        return self.IMAGE_TYPE
