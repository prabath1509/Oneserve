from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from db.database import get_db
from db.models import CertificateApplication, CertificateDocument, CertificateComment, CertificateCommentAction, User, UserRole, CertificateStatus, Notification
from schemas.schemas import CertificateApplicationCreate, CertificateApplicationResponse, CertificateApprovalRequest, CertificateDetailResponse
from routers.auth import get_current_user, require_admin
from utils.files import save_upload_file, is_valid_document
from services.certificate_pdf import generate_certificate_pdf
import os

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.post("/apply", response_model=CertificateApplicationResponse)
async def apply_certificate(
    certificate_type: str = Form(...),
    applicant_name: str = Form(...),
    father_name: Optional[str] = Form(None),
    mother_name: Optional[str] = Form(None),
    date_of_birth: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    purpose: Optional[str] = Form(None),
    additional_info: Optional[str] = Form(None),
    locker_doc_ids: Optional[str] = Form(None),  # Comma-separated locker document IDs
    documents: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply for certificate"""
    import json
    
    # Prepare form data as JSON
    form_data = {
        "certificate_type": certificate_type,
        "applicant_name": applicant_name,
        "father_name": father_name,
        "mother_name": mother_name,
        "date_of_birth": date_of_birth,
        "address": address,
        "purpose": purpose,
        "additional_info": additional_info
    }
    
    # Create application
    application = CertificateApplication(
        applicant_id=current_user.id,
        certificate_type=certificate_type,
        applicant_name=applicant_name,
        father_name=father_name,
        mother_name=mother_name,
        date_of_birth=date_of_birth,
        address=address,
        purpose=purpose,
        additional_info=additional_info,
        form_data=json.dumps(form_data),
        locker_doc_ids=locker_doc_ids,
        status=CertificateStatus.SUBMITTED
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    # Link locker documents
    if locker_doc_ids:
        from db.models import LockerDocument
        doc_ids = [int(id.strip()) for id in locker_doc_ids.split(',') if id.strip()]
        for doc_id in doc_ids:
            # Verify ownership
            locker_doc = db.query(LockerDocument).filter(
                LockerDocument.id == doc_id,
                LockerDocument.user_id == current_user.id
            ).first()
            
            if locker_doc:
                cert_doc = CertificateDocument(
                    application_id=application.id,
                    locker_document_id=doc_id,
                    file_name=locker_doc.file_name
                )
                db.add(cert_doc)
    
    # Save uploaded documents
    if documents:
        for doc_file in documents:
            if doc_file and doc_file.filename:
                if not is_valid_document(doc_file.filename):
                    continue
                
                file_path, file_name = await save_upload_file(doc_file, "uploads/certificates")
                
                cert_doc = CertificateDocument(
                    application_id=application.id,
                    file_path=file_path,
                    file_name=file_name
                )
                db.add(cert_doc)
        
        db.commit()
    
    # Create notification
    notification = Notification(
        user_id=current_user.id,
        title="Certificate Application Submitted",
        message=f"Your application for {certificate_type} (ID: {application.id}) has been submitted and is under review."
    )
    db.add(notification)
    db.commit()
    
    db.refresh(application)
    return application


@router.get("/my", response_model=List[CertificateApplicationResponse])
def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's certificate applications"""
    applications = db.query(CertificateApplication).filter(
        CertificateApplication.applicant_id == current_user.id
    ).order_by(CertificateApplication.created_at.desc()).all()
    
    return applications


@router.get("/{application_id}", response_model=CertificateApplicationResponse)
def get_application_detail(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get certificate application details"""
    application = db.query(CertificateApplication).filter(
        CertificateApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check access rights
    if application.applicant_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return application


@router.get("/admin/pending", response_model=List[CertificateApplicationResponse])
def get_pending_applications(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get pending certificate applications (admin only)"""
    applications = db.query(CertificateApplication).filter(
        CertificateApplication.status.in_([
            CertificateStatus.SUBMITTED,
            CertificateStatus.UNDER_VERIFICATION
        ])
    ).order_by(CertificateApplication.created_at.desc()).all()
    
    return applications


@router.get("/admin/{application_id}", response_model=CertificateDetailResponse)
def get_application_for_admin_review(
    application_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get full certificate application details for admin review"""
    from db.models import LockerDocument
    
    application = db.query(CertificateApplication).filter(
        CertificateApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Preload all relationships including locker documents
    # The response model will automatically serialize relationships
    return application


@router.patch("/{application_id}/admin-approve")
async def admin_approve_application(
    application_id: int,
    comment: str = Form(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve certificate application with admin comment"""
    application = db.query(CertificateApplication).filter(
        CertificateApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application.status != CertificateStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve application with status {application.status}"
        )
    
    # Create comment record
    cert_comment = CertificateComment(
        application_id=application_id,
        admin_id=current_user.id,
        comment=comment,
        action=CertificateCommentAction.APPROVED
    )
    db.add(cert_comment)
    
    # Update application status
    application.status = CertificateStatus.APPROVED
    application.approved_at = datetime.utcnow()
    application.updated_at = datetime.utcnow()
    
    # Generate certificate PDF
    try:
        pdf_path = generate_certificate_pdf(
            certificate_id=application.id,
            certificate_type=application.certificate_type,
            applicant_name=application.applicant_name,
            father_name=application.father_name,
            date_of_birth=application.date_of_birth,
            address=application.address
        )
        
        application.certificate_pdf_path = pdf_path
        application.status = CertificateStatus.CERTIFICATE_READY
        
        db.commit()
        db.refresh(application)
        
        # Create notification
        notification = Notification(
            user_id=application.applicant_id,
            title="Certificate Approved!",
            message=f"Your {application.certificate_type} application has been approved. Your certificate is ready for download."
        )
        db.add(notification)
        db.commit()
        
        return {"success": True, "message": "Application approved and certificate generated"}
        
    except Exception as e:
        db.rollback()
        print(f"PDF generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating certificate PDF"
        )


@router.patch("/{application_id}/admin-reject")
async def admin_reject_application(
    application_id: int,
    comment: str = Form(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reject certificate application with admin comment"""
    application = db.query(CertificateApplication).filter(
        CertificateApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application.status != CertificateStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject application with status {application.status}"
        )
    
    # Create comment record
    cert_comment = CertificateComment(
        application_id=application_id,
        admin_id=current_user.id,
        comment=comment,
        action=CertificateCommentAction.REJECTED
    )
    db.add(cert_comment)
    
    # Update application status
    application.status = CertificateStatus.REJECTED
    application.rejection_reason = comment
    application.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(application)
    
    # Create notification
    notification = Notification(
        user_id=application.applicant_id,
        title="Certificate Application Rejected",
        message=f"Your {application.certificate_type} application has been rejected. Reason: {comment}"
    )
    db.add(notification)
    db.commit()
    
    return {"success": True, "message": "Application rejected"}


@router.post("/{application_id}/admin-note")
async def admin_add_note(
    application_id: int,
    comment: str = Form(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Add admin note to certificate application (doesn't change status)"""
    application = db.query(CertificateApplication).filter(
        CertificateApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Create note record
    cert_comment = CertificateComment(
        application_id=application_id,
        admin_id=current_user.id,
        comment=comment,
        action=CertificateCommentAction.NOTE
    )
    db.add(cert_comment)
    db.commit()
    
    return {"success": True, "message": "Note added"}


@router.patch("/{application_id}/approve", response_model=CertificateApplicationResponse)
def approve_application(
    application_id: int,
    approval_request: CertificateApprovalRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve or reject certificate application (admin only)"""
    application = db.query(CertificateApplication).filter(
        CertificateApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if approval_request.approved:
        # Approve application
        application.status = CertificateStatus.APPROVED
        application.approved_at = datetime.utcnow()
        application.updated_at = datetime.utcnow()
        
        # Generate certificate PDF
        try:
            pdf_path = generate_certificate_pdf(
                certificate_id=application.id,
                certificate_type=application.certificate_type,
                applicant_name=application.applicant_name,
                father_name=application.father_name,
                date_of_birth=application.date_of_birth,
                address=application.address
            )
            
            application.certificate_pdf_path = pdf_path
            application.status = CertificateStatus.CERTIFICATE_READY
            
            db.commit()
            db.refresh(application)
            
            # Create notification
            notification = Notification(
                user_id=application.applicant_id,
                title="Certificate Approved!",
                message=f"Your {application.certificate_type} application has been approved. Your certificate is ready for download."
            )
            db.add(notification)
            db.commit()
            
        except Exception as e:
            print(f"PDF generation error: {e}")
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating certificate PDF"
            )
    else:
        # Reject application
        application.status = CertificateStatus.REJECTED
        application.rejection_reason = approval_request.reason or "Application does not meet requirements"
        application.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(application)
        
        # Create notification
        notification = Notification(
            user_id=application.applicant_id,
            title="Certificate Application Rejected",
            message=f"Your {application.certificate_type} application has been rejected. Reason: {application.rejection_reason}"
        )
        db.add(notification)
        db.commit()
    
    return application


@router.patch("/{application_id}/reject", response_model=CertificateApplicationResponse)
def reject_application(
    application_id: int,
    reason: str = Form(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reject certificate application (admin only)"""
    application = db.query(CertificateApplication).filter(
        CertificateApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    application.status = CertificateStatus.REJECTED
    application.rejection_reason = reason
    application.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(application)
    
    # Create notification
    notification = Notification(
        user_id=application.applicant_id,
        title="Certificate Application Rejected",
        message=f"Your {application.certificate_type} application has been rejected. Reason: {reason}"
    )
    db.add(notification)
    db.commit()
    
    return application


@router.get("/{application_id}/download")
def download_certificate(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download approved certificate PDF"""
    application = db.query(CertificateApplication).filter(
        CertificateApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check access rights
    if application.applicant_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if application.status != CertificateStatus.CERTIFICATE_READY or not application.certificate_pdf_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificate not ready for download"
        )
    
    if not os.path.exists(application.certificate_pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate file not found on server"
        )
    
    return FileResponse(
        path=application.certificate_pdf_path,
        filename=f"certificate_{application.id}.pdf",
        media_type='application/pdf'
    )
