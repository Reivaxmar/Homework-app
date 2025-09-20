from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import requests
import logging

from ..models.database import get_db
from ..models.user import User
from ..auth import get_current_user, get_current_user_optional, create_access_token
from .. import schemas
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

class GoogleTokenRequest(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None

class LoginRequest(BaseModel):
    email: str
    full_name: str
    google_access_token: Optional[str] = None
    google_refresh_token: Optional[str] = None

class LoginResponse(BaseModel):
    user: schemas.User
    access_token: str
    token_type: str
    message: str

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Simple login endpoint - creates or updates user"""
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if user:
            # Update existing user
            user.full_name = login_data.full_name
            if login_data.google_access_token:
                user.google_access_token = login_data.google_access_token
                user.google_refresh_token = login_data.google_refresh_token
        else:
            # Create new user
            user = User(
                email=login_data.email,
                full_name=login_data.full_name,
                avatar_url=None,
                supabase_user_id=f"user_{login_data.email}",  # Simple ID for now
                google_access_token=login_data.google_access_token,
                google_refresh_token=login_data.google_refresh_token
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return LoginResponse(
            user=schemas.User.from_orm(user),
            access_token=access_token,
            token_type="bearer",
            message="Login successful"
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/google/callback")
async def google_auth_callback(
    token_data: GoogleTokenRequest,
    supabase_user_id: str,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback and create/update user"""
    try:
        # Get user info from Google
        response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {token_data.access_token}"}
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )
        
        google_user = response.json()
        
        # Check if user exists
        user = db.query(User).filter(
            User.supabase_user_id == supabase_user_id
        ).first()
        
        if user:
            # Update existing user
            user.email = google_user.get("email")
            user.full_name = google_user.get("name", user.full_name)
            user.avatar_url = google_user.get("picture")
            user.google_access_token = token_data.access_token
            user.google_refresh_token = token_data.refresh_token
            if token_data.expires_in:
                from datetime import datetime, timedelta
                user.google_token_expiry = datetime.utcnow() + timedelta(seconds=token_data.expires_in)
        else:
            # Create new user
            user = User(
                email=google_user.get("email"),
                full_name=google_user.get("name", ""),
                avatar_url=google_user.get("picture"),
                supabase_user_id=supabase_user_id,
                google_access_token=token_data.access_token,
                google_refresh_token=token_data.refresh_token
            )
            if token_data.expires_in:
                from datetime import datetime, timedelta
                user.google_token_expiry = datetime.utcnow() + timedelta(seconds=token_data.expires_in)
            
            db.add(user)
        
        db.commit()
        db.refresh(user)
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return LoginResponse(
            user=schemas.User.from_orm(user),
            access_token=access_token,
            token_type="bearer",  
            message="Authentication successful"
        )
        
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@router.get("/me", response_model=schemas.User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=schemas.User)
async def update_current_user(
    user_update: schemas.UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user