from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    CITIZEN = "CITIZEN"
    OFFICER_WATER = "OFFICER_WATER"
    OFFICER_ELECTRICITY = "OFFICER_ELECTRICITY"
    OFFICER_ROAD = "OFFICER_ROAD"
    OFFICER_SANITATION = "OFFICER_SANITATION"
    ADMIN = "ADMIN"


class ComplaintCategory(str, enum.Enum):
    WATER = "WATER"
    ELECTRICITY = "ELECTRICITY"
    ROAD = "ROAD"
    SANITATION = "SANITATION"
    GENERAL = "GENERAL"


class ComplaintStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class DocumentType(str, enum.Enum):
    AADHAAR = "AADHAAR"
    PAN = "PAN"
    VOTER_ID = "VOTER_ID"
    OTHER = "OTHER"


class CertificateType(str, enum.Enum):
    INCOME = "Income Certificate"
    DOMICILE = "Domicile Certificate"
    BIRTH = "Birth Certificate"
    CASTE = "Caste Certificate"


class CertificateStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_VERIFICATION = "UNDER_VERIFICATION"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CERTIFICATE_READY = "CERTIFICATE_READY"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    complaints = relationship("Complaint", back_populates="citizen", foreign_keys="Complaint.citizen_id")
    assigned_complaints = relationship("Complaint", back_populates="assigned_officer", foreign_keys="Complaint.assigned_officer_id")
    locker_documents = relationship("LockerDocument", back_populates="user")
    certificate_applications = relationship("CertificateApplication", back_populates="applicant")
    notifications = relationship("Notification", back_populates="user")
    complaint_comments = relationship("ComplaintComment", back_populates="officer")


class Complaint(Base):
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    place = Column(String(255), nullable=True)
    image_path = Column(String(500), nullable=True)
    category = Column(SQLEnum(ComplaintCategory), nullable=False)
    status = Column(SQLEnum(ComplaintStatus), default=ComplaintStatus.PENDING)
    assigned_officer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_proof = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    citizen = relationship("User", back_populates="complaints", foreign_keys=[citizen_id])
    assigned_officer = relationship("User", back_populates="assigned_complaints", foreign_keys=[assigned_officer_id])
    comments = relationship("ComplaintComment", back_populates="complaint")


class ComplaintComment(Base):
    __tablename__ = "complaint_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False)
    officer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    complaint = relationship("Complaint", back_populates="comments")
    officer = relationship("User", back_populates="complaint_comments")


class LockerDocument(Base):
    __tablename__ = "locker_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doc_type = Column(SQLEnum(DocumentType), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    extracted_text = Column(Text, nullable=True)
    verified = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="locker_documents")


class CertificateApplication(Base):
    __tablename__ = "certificate_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    certificate_type = Column(SQLEnum(CertificateType), nullable=False)
    status = Column(SQLEnum(CertificateStatus), default=CertificateStatus.SUBMITTED)
    
    # Application fields (flexible JSON-like storage)
    applicant_name = Column(String(255), nullable=False)
    father_name = Column(String(255), nullable=True)
    mother_name = Column(String(255), nullable=True)
    date_of_birth = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    purpose = Column(Text, nullable=True)
    additional_info = Column(Text, nullable=True)
    
    # Store full form data as JSON for flexibility
    form_data = Column(Text, nullable=True)  # JSON string of all form fields
    
    # Linked DigiLocker document IDs (comma-separated)
    locker_doc_ids = Column(String(500), nullable=True)
    
    # Certificate info
    certificate_pdf_path = Column(String(500), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    
    # Relationships
    applicant = relationship("User", back_populates="certificate_applications")
    documents = relationship("CertificateDocument", back_populates="application")
    comments = relationship("CertificateComment", back_populates="application", order_by="CertificateComment.created_at")


class CertificateDocument(Base):
    __tablename__ = "certificate_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("certificate_applications.id"), nullable=False)
    
    # Either uploaded file or reference to locker document
    file_path = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    locker_document_id = Column(Integer, ForeignKey("locker_documents.id"), nullable=True)
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    application = relationship("CertificateApplication", back_populates="documents")
    locker_document = relationship("LockerDocument")


class CertificateCommentAction(str, enum.Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NOTE = "NOTE"


class CertificateComment(Base):
    __tablename__ = "certificate_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("certificate_applications.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    action = Column(SQLEnum(CertificateCommentAction), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    application = relationship("CertificateApplication", back_populates="comments")
    admin = relationship("User")


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
