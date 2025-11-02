"""
FastAPI Dependencies
Reusable functions for authentication and authorization
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import AuthService
from models.user import User
from typing import Optional

# Security scheme - expects "Authorization: Bearer <token>"
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get currently authenticated user from JWT token
    
    This is a FastAPI dependency - use it in route parameters
    
    Args:
        credentials: Extracted from Authorization header automatically
    
    Returns:
        User object if token valid
    
    Raises:
        HTTPException 401 if token invalid/expired
        HTTPException 404 if user not found
    
    Example Usage in Route:
        @app.get("/api/profile")
        async def get_profile(current_user: User = Depends(get_current_user)):
            # current_user is automatically populated!
            return {"email": current_user.email, "name": current_user.name}
    
    How it works:
    1. FastAPI extracts "Authorization: Bearer <token>" header
    2. HTTPBearer() parses it → credentials.credentials = token
    3. We decode token → get user_id
    4. Fetch user from database
    5. Return user object to route handler
    
    Flow:
    Request Header:
      Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
      
      ↓ HTTPBearer extracts token
      
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      
      ↓ AuthService.decode_access_token()
      
    user_id = "507f1f77bcf86cd799439011"
      
      ↓ User.get(user_id)
      
    user = User(email="rohit@example.com", ...)
      
      ↓ Return to route
      
    Route receives: current_user object ✅
    """
    
    # Extract token from credentials
    token = credentials.credentials
    
    # Decode token to get user_id
    user_id = AuthService.decode_access_token(token)
    
    if user_id is None:
        # Token invalid, expired, or tampered
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = await User.get(user_id)
    
    if user is None:
        # User was deleted but token still valid
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        # User account deactivated
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user

# Optional: Get current user without raising exception
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Get current user but don't raise exception if not authenticated
    
    Useful for routes that have different behavior for logged-in vs anonymous users
    
    Returns:
        User object if authenticated, None if not
    
    Example:
        @app.get("/api/content")
        async def get_content(user: Optional[User] = Depends(get_current_user_optional)):
            if user:
                # Show personalized content
                return {"message": f"Welcome back, {user.name}!"}
            else:
                # Show generic content
                return {"message": "Welcome, guest!"}
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None