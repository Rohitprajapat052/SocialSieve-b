import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from config.settings import settings
from typing import Optional

class AuthService:
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt directly"""
        # Convert password to bytes
        password_bytes = password.encode('utf-8')
        
        # Truncate if too long (bcrypt limit is 72 bytes)
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password using bcrypt directly"""
        # Convert to bytes
        password_bytes = plain_password.encode('utf-8')
        
        # Truncate if too long
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Verify
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    
    @staticmethod
    def decode_access_token(token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            return payload.get("sub")
        except JWTError:
            return None