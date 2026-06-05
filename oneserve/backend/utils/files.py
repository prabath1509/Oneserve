import os
import shutil
from datetime import datetime
from fastapi import UploadFile
from typing import Tuple


async def save_upload_file(upload_file: UploadFile, folder: str) -> Tuple[str, str]:
    """
    Save uploaded file to specified folder
    Returns: (file_path, file_name)
    """
    # Create folder if not exists
    os.makedirs(folder, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(upload_file.filename)[1]
    file_name = f"{timestamp}_{upload_file.filename}"
    file_path = os.path.join(folder, file_name)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return file_path, file_name


def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return os.path.splitext(filename)[1].lower()


def is_valid_image(filename: str) -> bool:
    """Check if file is a valid image"""
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    return get_file_extension(filename) in valid_extensions


def is_valid_document(filename: str) -> bool:
    """Check if file is a valid document"""
    valid_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}
    return get_file_extension(filename) in valid_extensions
