"""
Authentication Router
Handles user signup, login, and profile endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
from schemas.auth import UserSignup, UserLogin, Token, UserResponse
from models.user import User
from services.auth_service import AuthService
from utils.dependencies import get_current_user
from datetime import datetime

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup):
    """
    Create new user account
    
    Request Body:
    {
      "email": "rohit@example.com",
      "name": "Rohit Prajapat",
      "password": "mypassword123"
    }
    
    Response (201 Created):
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
    
    Errors:
    - 400: Email already exists
    - 422: Validation error (invalid email, short password, etc.)
    
    Flow:
    1. Check if email already exists
    2. Hash password
    3. Create user in database
    4. Generate JWT token
    5. Return token
    """
    
    # Check if user already exists
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password (NEVER store plain password!)
    password_hash = AuthService.hash_password(user_data.password)
    
    # Create user document
    user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=password_hash,
        plan="free",  # Default plan
        created_at=datetime.utcnow()
    )
    
    # Save to database
    await user.save()
    
    # Generate JWT token
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)}  # "sub" = subject (user_id)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login existing user
    
    Request Body:
    {
      "email": "rohit@example.com",
      "password": "mypassword123"
    }
    
    Response (200 OK):
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
    
    Errors:
    - 401: Invalid email or password
    
    Flow:
    1. Find user by email
    2. Verify password
    3. Generate JWT token
    4. Return token
    
    Security Note:
    We return same error for "user not found" and "wrong password"
    to prevent email enumeration attacks
    """
    
    # Find user by email
    user = await User.find_one(User.email == credentials.email)
    
    # Check if user exists and password is correct
    if not user or not AuthService.verify_password(
        credentials.password,
        user.password_hash
    ):
        # Generic error message (security best practice)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    # Generate JWT token
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile information
    
    Requires Authentication!
    
    Request:
    GET /api/auth/me
    Headers:
      Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    
    Response (200 OK):
    {
      "id": "507f1f77bcf86cd799439011",
      "email": "rohit@example.com",
      "name": "Rohit Prajapat",
      "plan": "free",
      "created_at": "2025-10-18T10:00:00Z",
      "usage": {
        "voice_minutes_used": 5,
        "comments_analyzed": 2,
        "last_reset": "2025-10-01T00:00:00Z"
      },
      "limits": {
        "voice_minutes_per_month": 30,
        "comments_per_month": 20
      }
    }
    
    Errors:
    - 401: Invalid or missing token
    - 404: User not found
    
    How it works:
    Depends(get_current_user) automatically:
    1. Extracts token from Authorization header
    2. Verifies token
    3. Fetches user from database
    4. Injects user object into function parameter
    
    If any step fails → 401 error automatically!
    """
    
    # Reset usage if new month (automatic)
    current_user.reset_usage_if_needed()
    await current_user.save()
    
    # Return user data
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        plan=current_user.plan,
        created_at=current_user.created_at,
        usage={
            "voice_minutes_used": current_user.usage.voice_minutes_used,
            "comments_analyzed": current_user.usage.comments_analyzed,
            "last_reset": current_user.usage.last_reset
        },
        limits={
            "voice_minutes_per_month": current_user.limits.voice_minutes_per_month,
            "comments_per_month": current_user.limits.comments_per_month
        }
    )

@router.post("/logout")
async def logout():
    """
    Logout user
    
    Note: JWT tokens are stateless, so we can't actually invalidate them server-side
    Frontend should delete the token from localStorage
    
    Request:
    POST /api/auth/logout
    
    Response (200 OK):
    {
      "message": "Successfully logged out"
    }
    
    Frontend Implementation:
    localStorage.removeItem("token");
    redirect("/login");
    """
    return {"message": "Successfully logged out"}