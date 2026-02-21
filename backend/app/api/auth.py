"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import timedelta

from app.database import get_db
from app.models.db_models import User, Organization, SubscriptionPlan
from app.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    org_name: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str
    org_id: str
    org_name: str


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user and organization"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create organization
    org = Organization(
        org_name=user_data.org_name,
        subscription_plan=SubscriptionPlan.BASIC
    )
    db.add(org)
    db.flush()
    
    # Create user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        org_id=org.org_id,
        role="compliance_admin"  # First user is admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": str(user.user_id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "org_id": str(user.org_id)
        }
    }


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": str(user.user_id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "org_id": str(user.org_id)
        }
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get current user info"""
    org = db.query(Organization).filter(Organization.org_id == current_user.org_id).first()
    
    return {
        "user_id": str(current_user.user_id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "org_id": str(current_user.org_id),
        "org_name": org.org_name if org else ""
    }
