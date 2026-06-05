from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from db.models import UserRole, ComplaintCategory, ComplaintStatus, DocumentType, CertificateType, CertificateStatus


# ============ Auth Schemas ============
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None


class OfficerCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    phone: Optional[str]
    address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# ============ Complaint Schemas ============
class ComplaintCreate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    place: Optional[str] = None
    
    @validator('title', 'description', 'place')
    def validate_at_least_one(cls, v, values):
        # Check if at least one field has value
        if not v and not values.get('title') and not values.get('description'):
            return v  # Let the validation happen after image check
        return v


class ComplaintResponse(BaseModel):
    id: int
    citizen_id: int
    title: Optional[str]
    description: Optional[str]
    place: Optional[str]
    image_path: Optional[str]
    category: ComplaintCategory
    status: ComplaintStatus
    assigned_officer_id: Optional[int]
    resolution_proof: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    citizen: UserResponse
    assigned_officer: Optional[UserResponse]
    
    class Config:
        from_attributes = True


class ComplaintStatusUpdate(BaseModel):
    status: ComplaintStatus


class ComplaintCommentCreate(BaseModel):
    comment: str


class ComplaintCommentResponse(BaseModel):
    id: int
    complaint_id: int
    officer_id: int
    comment: str
    created_at: datetime
    officer: UserResponse
    
    class Config:
        from_attributes = True


class ComplaintDetailResponse(ComplaintResponse):
    comments: List[ComplaintCommentResponse] = []
    
    class Config:
        from_attributes = True


# ============ Locker Schemas ============
class LockerDocumentResponse(BaseModel):
    id: int
    user_id: int
    doc_type: DocumentType
    file_path: str
    file_name: str
    extracted_text: Optional[str]
    verified: bool
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# ============ Certificate Schemas ============
class CertificateApplicationCreate(BaseModel):
    certificate_type: CertificateType
    applicant_name: str
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    purpose: Optional[str] = None
    additional_info: Optional[str] = None


class CertificateDocumentResponse(BaseModel):
    id: int
    file_path: Optional[str]
    file_name: Optional[str]
    locker_document_id: Optional[int]
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class CertificateApplicationResponse(BaseModel):
    id: int
    applicant_id: int
    certificate_type: CertificateType
    status: CertificateStatus
    applicant_name: str
    father_name: Optional[str]
    mother_name: Optional[str]
    date_of_birth: Optional[str]
    address: Optional[str]
    purpose: Optional[str]
    additional_info: Optional[str]
    form_data: Optional[str]  # JSON string of form data
    locker_doc_ids: Optional[str]  # Comma-separated locker doc IDs
    certificate_pdf_path: Optional[str]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime]
    applicant: UserResponse
    documents: List[CertificateDocumentResponse] = []
    
    class Config:
        from_attributes = True


class CertificateApprovalRequest(BaseModel):
    approved: bool
    reason: Optional[str] = None


class CertificateCommentResponse(BaseModel):
    id: int
    application_id: int
    admin_id: int
    comment: str
    action: str
    created_at: datetime
    admin: UserResponse
    
    class Config:
        from_attributes = True


class CertificateDetailResponse(BaseModel):
    id: int
    applicant_id: int
    certificate_type: CertificateType
    status: CertificateStatus
    applicant_name: str
    father_name: Optional[str]
    mother_name: Optional[str]
    date_of_birth: Optional[str]
    address: Optional[str]
    purpose: Optional[str]
    additional_info: Optional[str]
    form_data: Optional[str]
    locker_doc_ids: Optional[str]
    certificate_pdf_path: Optional[str]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime]
    applicant: UserResponse
    documents: List[CertificateDocumentResponse] = []
    comments: List[CertificateCommentResponse] = []
    
    class Config:
        from_attributes = True


# ============ Admin User Management Schemas ============
class UserCreateRequest(BaseModel):
    email: str
    full_name: str
    role: UserRole
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None


class UserUpdateRoleRequest(BaseModel):
    role: UserRole


class UserUpdateStatusRequest(BaseModel):
    is_active: bool


class UserResetPasswordRequest(BaseModel):
    new_password: str


class UserListResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    phone: Optional[str]
    
    class Config:
        from_attributes = True


# ============ Notification Schemas ============
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Dashboard Schemas ============
class CitizenDashboardStats(BaseModel):
    total_complaints: int
    pending_complaints: int
    resolved_complaints: int
    total_applications: int
    approved_certificates: int
    complaints_by_category: dict
    complaints_by_status: dict
    monthly_complaints: List[dict]


class OfficerDashboardStats(BaseModel):
    pending_complaints: int
    in_progress_complaints: int
    resolved_complaints: int
    avg_resolution_time: float
    monthly_resolutions: List[dict]
    category_trend: dict


class AdminDashboardStats(BaseModel):
    total_users: int
    total_citizens: int
    total_officers: int
    pending_certificate_applications: int
    pending_complaints: int
    documents_uploaded: int
    applications_trend: List[dict]
    complaint_performance: dict
