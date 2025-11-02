"""
Authentication Schemas (Request/Response Models)
Define the shape of data for auth endpoints
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserSignup(BaseModel):
    """
    Request body for user signup
    
    Validation:
    - Email must be valid format
    - Name 2-50 characters
    - Password minimum 8 characters
    
    Example Request:
    POST /api/auth/signup
    {
      "email": "rohit@example.com",
      "name": "Rohit Prajapat",
      "password": "mypassword123"
    }
    """
    email: EmailStr  # Pydantic validates email format
    name: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=8)
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        """Custom validator - name can't be just spaces"""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('password')
    def password_strength(cls, v):
        """
        Optional: Add password strength requirements
        
        Uncomment to enforce:
        - At least one uppercase letter
        - At least one number
        """
        # if not any(char.isupper() for char in v):
        #     raise ValueError('Password must contain uppercase letter')
        # if not any(char.isdigit() for char in v):
        #     raise ValueError('Password must contain number')
        return v

class UserLogin(BaseModel):
    """
    Request body for user login
    
    Example Request:
    POST /api/auth/login
    {
      "email": "rohit@example.com",
      "password": "mypassword123"
    }
    """
    email: EmailStr
    password: str

class Token(BaseModel):
    """
    Response for successful login/signup
    
    Example Response:
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
    
    Frontend should store access_token and send in future requests:
    Authorization: Bearer <access_token>
    """
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """
    Internal model - decoded token payload
    Not sent to frontend
    """
    user_id: Optional[str] = None

class UserResponse(BaseModel):
    """
    User data returned to frontend
    
    IMPORTANT: Never return password_hash!
    
    Example Response:
    {
      "id": "507f1f77bcf86cd799439011",
      "email": "rohit@example.com",
      "name": "Rohit Prajapat",
      "plan": "free",
      "created_at": "2025-10-18T10:00:00Z",
      "usage": {
        "voice_minutes_used": 5,
        "comments_analyzed": 2
      },
      "limits": {
        "voice_minutes_per_month": 30,
        "comments_per_month": 20
      }
    }
    """
    id: str
    email: str
    name: str
    plan: str
    created_at: datetime
    
    usage: dict  # UsageStats as dict
    limits: dict  # UserLimits as dict
    
    class Config:
        # Allow conversion from ORM models
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }