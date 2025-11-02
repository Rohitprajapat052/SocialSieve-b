from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    mongodb_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080
    cloudinary_cloud_name: str = "placeholder"
    cloudinary_api_key: str = "placeholder"
    cloudinary_api_secret: str = "placeholder"
    groq_api_key: str 
    youtube_api_key: str = "placeholder"
    ollama_url: str = "http://localhost:11434"
    environment: str = "development"
    cors_origins: str = "http://localhost:5173,http://localhost:3000,https://social-sieve-nit-sri.vercel.app
"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
