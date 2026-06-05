from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from db.database import get_db
from db.models import User, Complaint, CertificateApplication, LockerDocument, UserRole, ComplaintStatus, CertificateStatus
from schemas.schemas import CitizenDashboardStats, OfficerDashboardStats, AdminDashboardStats
from routers.auth import get_current_user, require_admin

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/citizen", response_model=CitizenDashboardStats)
def get_citizen_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get citizen dashboard statistics"""
    # Total complaints
    total_complaints = db.query(Complaint).filter(
        Complaint.citizen_id == current_user.id
    ).count()
    
    # Pending complaints
    pending_complaints = db.query(Complaint).filter(
        Complaint.citizen_id == current_user.id,
        Complaint.status == ComplaintStatus.PENDING
    ).count()
    
    # Resolved complaints
    resolved_complaints = db.query(Complaint).filter(
        Complaint.citizen_id == current_user.id,
        Complaint.status == ComplaintStatus.RESOLVED
    ).count()
    
    # Total applications
    total_applications = db.query(CertificateApplication).filter(
        CertificateApplication.applicant_id == current_user.id
    ).count()
    
    # Approved certificates
    approved_certificates = db.query(CertificateApplication).filter(
        CertificateApplication.applicant_id == current_user.id,
        CertificateApplication.status.in_([
            CertificateStatus.APPROVED,
            CertificateStatus.CERTIFICATE_READY
        ])
    ).count()
    
    # Complaints by category
    category_data = db.query(
        Complaint.category,
        func.count(Complaint.id)
    ).filter(
        Complaint.citizen_id == current_user.id
    ).group_by(Complaint.category).all()
    
    complaints_by_category = {cat.value: count for cat, count in category_data}
    
    # Complaints by status
    status_data = db.query(
        Complaint.status,
        func.count(Complaint.id)
    ).filter(
        Complaint.citizen_id == current_user.id
    ).group_by(Complaint.status).all()
    
    complaints_by_status = {stat.value: count for stat, count in status_data}
    
    # Monthly complaints (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_data = db.query(
        extract('month', Complaint.created_at).label('month'),
        func.count(Complaint.id).label('count')
    ).filter(
        Complaint.citizen_id == current_user.id,
        Complaint.created_at >= six_months_ago
    ).group_by('month').all()
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_complaints = [
        {"month": month_names[int(month) - 1], "count": count}
        for month, count in monthly_data
    ]
    
    return CitizenDashboardStats(
        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        resolved_complaints=resolved_complaints,
        total_applications=total_applications,
        approved_certificates=approved_certificates,
        complaints_by_category=complaints_by_category,
        complaints_by_status=complaints_by_status,
        monthly_complaints=monthly_complaints
    )


@router.get("/officer", response_model=OfficerDashboardStats)
def get_officer_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get officer dashboard statistics"""
    # Check if user is officer
    if current_user.role not in [
        UserRole.OFFICER_WATER,
        UserRole.OFFICER_ELECTRICITY,
        UserRole.OFFICER_ROAD,
        UserRole.OFFICER_SANITATION
    ]:
        raise HTTPException(status_code=403, detail="Officer access required")
    
    # Pending complaints
    pending_complaints = db.query(Complaint).filter(
        Complaint.assigned_officer_id == current_user.id,
        Complaint.status == ComplaintStatus.PENDING
    ).count()
    
    # In progress complaints
    in_progress_complaints = db.query(Complaint).filter(
        Complaint.assigned_officer_id == current_user.id,
        Complaint.status == ComplaintStatus.IN_PROGRESS
    ).count()
    
    # Resolved complaints
    resolved_complaints = db.query(Complaint).filter(
        Complaint.assigned_officer_id == current_user.id,
        Complaint.status == ComplaintStatus.RESOLVED
    ).count()
    
    # Average resolution time
    resolved = db.query(Complaint).filter(
        Complaint.assigned_officer_id == current_user.id,
        Complaint.status == ComplaintStatus.RESOLVED,
        Complaint.resolved_at.isnot(None)
    ).all()
    
    if resolved:
        total_time = sum([
            (c.resolved_at - c.created_at).total_seconds() / 3600  # hours
            for c in resolved
        ])
        avg_resolution_time = total_time / len(resolved)
    else:
        avg_resolution_time = 0.0
    
    # Monthly resolutions (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_data = db.query(
        extract('month', Complaint.resolved_at).label('month'),
        func.count(Complaint.id).label('count')
    ).filter(
        Complaint.assigned_officer_id == current_user.id,
        Complaint.status == ComplaintStatus.RESOLVED,
        Complaint.resolved_at >= six_months_ago
    ).group_by('month').all()
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_resolutions = [
        {"month": month_names[int(month) - 1], "count": count}
        for month, count in monthly_data
    ]
    
    # Category trend
    category_data = db.query(
        Complaint.category,
        func.count(Complaint.id)
    ).filter(
        Complaint.assigned_officer_id == current_user.id
    ).group_by(Complaint.category).all()
    
    category_trend = {cat.value: count for cat, count in category_data}
    
    return OfficerDashboardStats(
        pending_complaints=pending_complaints,
        in_progress_complaints=in_progress_complaints,
        resolved_complaints=resolved_complaints,
        avg_resolution_time=round(avg_resolution_time, 2),
        monthly_resolutions=monthly_resolutions,
        category_trend=category_trend
    )


@router.get("/admin", response_model=AdminDashboardStats)
def get_admin_dashboard(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    # Total users
    total_users = db.query(User).count()
    
    # Total citizens
    total_citizens = db.query(User).filter(User.role == UserRole.CITIZEN).count()
    
    # Total officers
    total_officers = db.query(User).filter(
        User.role.in_([
            UserRole.OFFICER_WATER,
            UserRole.OFFICER_ELECTRICITY,
            UserRole.OFFICER_ROAD,
            UserRole.OFFICER_SANITATION
        ])
    ).count()
    
    # Pending certificate applications
    pending_certificate_applications = db.query(CertificateApplication).filter(
        CertificateApplication.status.in_([
            CertificateStatus.SUBMITTED,
            CertificateStatus.UNDER_VERIFICATION
        ])
    ).count()
    
    # Pending complaints
    pending_complaints = db.query(Complaint).filter(
        Complaint.status == ComplaintStatus.PENDING
    ).count()
    
    # Documents uploaded
    documents_uploaded = db.query(LockerDocument).count()
    
    # Applications trend (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_app_data = db.query(
        extract('month', CertificateApplication.created_at).label('month'),
        func.count(CertificateApplication.id).label('count')
    ).filter(
        CertificateApplication.created_at >= six_months_ago
    ).group_by('month').all()
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    applications_trend = [
        {"month": month_names[int(month) - 1], "count": count}
        for month, count in monthly_app_data
    ]
    
    # Complaint resolution performance
    total_comp = db.query(Complaint).count()
    resolved_comp = db.query(Complaint).filter(
        Complaint.status == ComplaintStatus.RESOLVED
    ).count()
    pending_comp = db.query(Complaint).filter(
        Complaint.status == ComplaintStatus.PENDING
    ).count()
    in_progress_comp = db.query(Complaint).filter(
        Complaint.status == ComplaintStatus.IN_PROGRESS
    ).count()
    
    complaint_performance = {
        "total": total_comp,
        "resolved": resolved_comp,
        "pending": pending_comp,
        "in_progress": in_progress_comp,
        "resolution_rate": round((resolved_comp / total_comp * 100) if total_comp > 0 else 0, 2)
    }
    
    return AdminDashboardStats(
        total_users=total_users,
        total_citizens=total_citizens,
        total_officers=total_officers,
        pending_certificate_applications=pending_certificate_applications,
        pending_complaints=pending_complaints,
        documents_uploaded=documents_uploaded,
        applications_trend=applications_trend,
        complaint_performance=complaint_performance
    )
