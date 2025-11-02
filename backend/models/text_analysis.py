from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import List
from bson import ObjectId

class TextAnalysis(Document):
    """
    Stores text analysis results
    
    Simple structure:
    - Who analyzed it (user_id)
    - What text they analyzed
    - AI's summary
    - Action items found
    - When it was analyzed
    """
    
    user_id: Indexed(str)  # Who owns this
    text: str  # Original text user pasted
    summary: str  # AI summary
    action_items: List[str] = []  # Things to do
    character_count: int  # How long was the text
    analyzed_at: Indexed(datetime) = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "text_analyses"  # Collection name in MongoDB
        indexes = [
            [("user_id", 1), ("analyzed_at", -1)]  # Fast queries for user's history
        ]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }