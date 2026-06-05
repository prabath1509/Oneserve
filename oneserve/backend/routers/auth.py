from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User, UserRole
from schemas.schemas import UserCreate, OfficerCreate, UserLogin, TokenResponse
from utils.hashing import hash_password
from services.auth_service import authenticate_user, create_token_response
from utils.jwt import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/register", response_model=TokenResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new citizen"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
        role=UserRole.CITIZEN,
        phone=user_data.phone,
        address=user_data.address
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Return token
    return create_token_response(new_user)


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = authenticate_user(db, credentials.email, credentials.password)
    return create_token_response(user)


@router.get("/me", response_model=dict)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "phone": current_user.phone,
        "address": current_user.address
    }


@router.post("/create-officer", response_model=dict)
def create_officer(
    officer_data: OfficerCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create officer account (admin only)"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == officer_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role
    if officer_data.role not in [
        UserRole.OFFICER_WATER,
        UserRole.OFFICER_ELECTRICITY,
        UserRole.OFFICER_ROAD,
        UserRole.OFFICER_SANITATION,
        UserRole.ADMIN
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid officer role"
        )
    
    # Create officer
    new_officer = User(
        email=officer_data.email,
        full_name=officer_data.full_name,
        password_hash=hash_password(officer_data.password),
        role=officer_data.role,
        phone=officer_data.phone
    )
    
    db.add(new_officer)
    db.commit()
    db.refresh(new_officer)
    
    return {
        "message": "Officer created successfully",
        "officer": {
            "id": new_officer.id,
            "email": new_officer.email,
            "full_name": new_officer.full_name,
            "role": new_officer.role
        }
    }
