from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from db.database import get_db
from db.models import LockerDocument, User, DocumentType
from schemas.schemas import LockerDocumentResponse
from routers.auth import get_current_user
from utils.files import save_upload_file, is_valid_document
from services.ocr_service import extract_text_from_image, extract_text_from_pdf, detect_document_type, validate_aadhaar, validate_pan, validate_voter_id
import os

router = APIRouter(prefix="/locker", tags=["DigiLocker"])


@router.post("/upload", response_model=LockerDocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),  # User-selected document type
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload document to locker with type validation"""
    # Validate file
    if not is_valid_document(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document format. Supported: PDF, JPG, PNG, DOC, DOCX"
        )
    
    # Save file
    file_path, file_name = await save_upload_file(file, "uploads/locker")
    
    # Extract text using OCR and validate based on selected type
    extracted_text = ""
    verified = False
    
    # Determine file type and extract text
    file_lower = file.filename.lower()
    if file_lower.endswith(('.jpg', '.jpeg', '.png')):
        try:
            extracted_text = extract_text_from_image(file_path)
            print("extracted_text:", extracted_text)
        except Exception as e:
            print(f"Image OCR error: {e}")
            extracted_text = f"OCR failed: {str(e)}"
    elif file_lower.endswith('.pdf'):
        try:
            extracted_text = extract_text_from_pdf(file_path)
        except Exception as e:
            print(f"PDF extraction error: {e}")
            extracted_text = f"PDF extraction failed: {str(e)}"
    
    # Validate based on user-selected document type
    if extracted_text and len(extracted_text) > 10:
        try:
            if doc_type == "AADHAAR":
                is_valid = validate_aadhaar(extracted_text)
                print(f"Aadhaar validation result: {is_valid}")
                if not is_valid:
                    # Delete uploaded file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Aadhaar document. Unable to validate Aadhaar number (12 digits). Please upload correct Aadhaar card."
                    )
                verified = True
            elif doc_type == "PAN":
                is_valid = validate_pan(extracted_text)
                print(f"PAN validation result: {is_valid}")
                if not is_valid:
                    # Delete uploaded file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid PAN document. Unable to validate PAN format (e.g., ABCDE1234F). Please upload correct PAN card."
                    )
                verified = True
            elif doc_type == "VOTER_ID":
                is_valid = validate_voter_id(extracted_text)
                print(f"Voter ID validation result: {is_valid}")
                if not is_valid:
                    # Delete uploaded file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Voter ID document. Unable to validate Voter ID. Please upload correct Election/Voter ID card."
                    )
                verified = True
        except HTTPException:
            # Re-raise validation errors
            raise
        except Exception as e:
            print(f"Validation error: {e}")
            # For OTHER type or validation errors, still allow upload but mark as unverified
            pass
    else:
        print(f"Text extraction insufficient for validation: {extracted_text[:100] if extracted_text else 'None'}")
        # For PDFs and other docs
        extracted_text = f"Document uploaded: {file_name}"
    
    # Create locker document
    document = LockerDocument(
        user_id=current_user.id,
        doc_type=doc_type,
        file_path=file_path,
        file_name=file_name,
        extracted_text=extracted_text,
        verified=verified
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document


@router.get("/list", response_model=List[LockerDocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents in user's locker"""
    documents = db.query(LockerDocument).filter(
        LockerDocument.user_id == current_user.id
    ).order_by(LockerDocument.uploaded_at.desc()).all()
    
    return documents


@router.get("/download/{document_id}")
def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download document from locker"""
    document = db.query(LockerDocument).filter(
        LockerDocument.id == document_id,
        LockerDocument.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    return FileResponse(
        path=document.file_path,
        filename=document.file_name,
        media_type='application/octet-stream'
    )
