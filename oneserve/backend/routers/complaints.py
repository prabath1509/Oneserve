from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from db.database import get_db
from db.models import Complaint, User, UserRole, ComplaintStatus, ComplaintComment, Notification
from schemas.schemas import ComplaintCreate, ComplaintResponse, ComplaintDetailResponse, ComplaintStatusUpdate, ComplaintCommentCreate
from routers.auth import get_current_user
from utils.files import save_upload_file, is_valid_image
from services.image_classifier import predict_category
from services.complaint_assignment import assign_category_from_text, assign_officer_to_complaint

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post("/create", response_model=ComplaintResponse)
async def create_complaint(
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    place: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new complaint"""
    # Validate: at least one field must be provided
    if not title and not description and not image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of title, description, or image must be provided"
        )
    
    # Handle image upload and category detection
    image_path = None
    category = None
    
    if image:
        if not is_valid_image(image.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image format"
            )
        
        # Save image
        image_path, _ = await save_upload_file(image, "uploads/complaints")
        
        # Use image classifier to detect category
        try:
            category = predict_category(image_path)
        except Exception as e:
            print(f"Image classification failed: {e}")
            category = "GENERAL"
    
    # If no image, use text-based categorization
    if not category:
        category = assign_category_from_text(title or "", description or "")
    
    # Assign officer
    assigned_officer_id = assign_officer_to_complaint(db, category)
    
    # Create complaint
    complaint = Complaint(
        citizen_id=current_user.id,
        title=title,
        description=description,
        place=place,
        image_path=image_path,
        category=category,
        status=ComplaintStatus.PENDING,
        assigned_officer_id=assigned_officer_id
    )
    
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    
    # Create notification for citizen
    notification = Notification(
        user_id=current_user.id,
        title="Complaint Registered",
        message=f"Your complaint #{complaint.id} has been registered and assigned to {category} department."
    )
    db.add(notification)
    
    # Notify assigned officer if exists
    if assigned_officer_id:
        officer_notification = Notification(
            user_id=assigned_officer_id,
            title="New Complaint Assigned",
            message=f"New {category} complaint #{complaint.id} has been assigned to you."
        )
        db.add(officer_notification)
    
    db.commit()
    
    return complaint


@router.get("/my", response_model=List[ComplaintResponse])
def get_my_complaints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complaints created by current user"""
    complaints = db.query(Complaint).filter(
        Complaint.citizen_id == current_user.id
    ).order_by(Complaint.created_at.desc()).all()
    
    return complaints


@router.get("/assigned", response_model=List[ComplaintResponse])
def get_assigned_complaints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complaints assigned to current officer"""
    # Check if user is officer
    if current_user.role not in [
        UserRole.OFFICER_WATER,
        UserRole.OFFICER_ELECTRICITY,
        UserRole.OFFICER_ROAD,
        UserRole.OFFICER_SANITATION
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Officer access required"
        )
    
    complaints = db.query(Complaint).filter(
        Complaint.assigned_officer_id == current_user.id
    ).order_by(Complaint.created_at.desc()).all()
    
    return complaints


@router.get("/{complaint_id}", response_model=ComplaintDetailResponse)
def get_complaint_detail(
    complaint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complaint details"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Check access rights
    is_owner = complaint.citizen_id == current_user.id
    is_assigned_officer = complaint.assigned_officer_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN
    
    if not (is_owner or is_assigned_officer or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return complaint


@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
async def update_complaint_status(
    complaint_id: int,
    status: str = Form(...),  # Accept status as form field
    resolution_proof: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update complaint status (officer only)"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Check if user is assigned officer or admin
    if complaint.assigned_officer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only assigned officer can update status"
        )
    
    # Validate status
    try:
        new_status = ComplaintStatus(status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join([s.value for s in ComplaintStatus])}"
        )
    
    # Update status
    complaint.status = new_status
    complaint.updated_at = datetime.utcnow()
    
    if new_status == ComplaintStatus.RESOLVED:
        complaint.resolved_at = datetime.utcnow()
        
        # Handle resolution proof
        if resolution_proof:
            proof_path, _ = await save_upload_file(resolution_proof, "uploads/complaints")
            complaint.resolution_proof = proof_path
    
    db.commit()
    db.refresh(complaint)
    
    # Create notification for citizen
    status_messages = {
        ComplaintStatus.IN_PROGRESS: "Your complaint is now being processed.",
        ComplaintStatus.RESOLVED: "Your complaint has been resolved!",
        ComplaintStatus.REJECTED: "Your complaint has been reviewed."
    }
    
    if new_status in status_messages:
        notification = Notification(
            user_id=complaint.citizen_id,
            title=f"Complaint #{complaint.id} Status Updated",
            message=status_messages[new_status]
        )
        db.add(notification)
        db.commit()
    
    return complaint


@router.post("/{complaint_id}/comment", response_model=dict)
def add_complaint_comment(
    complaint_id: int,
    comment_data: ComplaintCommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add comment to complaint (officer only)"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Check if user is assigned officer or admin
    if complaint.assigned_officer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only assigned officer can add comments"
        )
    
    # Create comment
    comment = ComplaintComment(
        complaint_id=complaint_id,
        officer_id=current_user.id,
        comment=comment_data.comment
    )
    
    db.add(comment)
    db.commit()
    
    # Create notification for citizen
    notification = Notification(
        user_id=complaint.citizen_id,
        title=f"New Comment on Complaint #{complaint.id}",
        message=f"Officer has added a comment: {comment_data.comment[:50]}..."
    )
    db.add(notification)
    db.commit()
    
    return {"message": "Comment added successfully"}
