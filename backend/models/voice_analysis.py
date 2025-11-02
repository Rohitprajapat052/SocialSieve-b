from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import List, Optional
from bson import ObjectId

class VoiceAnalysis(Document):
    user_id: Indexed(str)
    file_name: str
    audio_url: str
    duration_seconds: int
    file_size_bytes: int
    transcript: str
    summary: str
    action_items: List[str] = []
    sentiment: Optional[str] = None
    language: str = "en-US"
    created_at: Indexed(datetime) = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "voice_analyses"
        indexes = [[("user_id", 1), ("created_at", -1)]]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }