from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from db.models import User, UserRole
from utils.hashing import verify_password
from utils.jwt import create_access_token


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Authenticate user with email and password
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    return user


def create_token_response(user: User) -> dict:
    """
    Create token response for authenticated user
    """
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role.value}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
