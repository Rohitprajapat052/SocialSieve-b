from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UsageStats(BaseModel):
    voice_minutes_used: int = 0
    comments_analyzed: int = 0
    last_reset: datetime = Field(default_factory=datetime.utcnow)

class UserLimits(BaseModel):
    voice_minutes_per_month: int = 30
    comments_per_month: int = 20

class User(Document):
    email: Indexed(EmailStr, unique=True)
    name: str
    password_hash: str
    plan: str = "free"
    usage: UsageStats = Field(default_factory=UsageStats)
    limits: UserLimits = Field(default_factory=UserLimits)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = ["email", "created_at"]
    
    def reset_usage_if_needed(self):
        now = datetime.utcnow()
        if self.usage.last_reset.month != now.month or self.usage.last_reset.year != now.year:
            self.usage.voice_minutes_used = 0
            self.usage.comments_analyzed = 0
            self.usage.last_reset = now
    
    async def check_voice_limit(self, duration_minutes: int) -> bool:
        self.reset_usage_if_needed()
        if self.plan in ["pro", "creator"]:
            return True
        new_total = self.usage.voice_minutes_used + duration_minutes
        return new_total <= self.limits.voice_minutes_per_month
    
    async def check_comment_limit(self) -> bool:
        self.reset_usage_if_needed()
        if self.plan in ["pro", "creator"]:
            return True
        return self.usage.comments_analyzed < self.limits.comments_per_month
    
    async def increment_voice_usage(self, duration_minutes: int):
        self.reset_usage_if_needed()
        self.usage.voice_minutes_used += duration_minutes
        self.updated_at = datetime.utcnow()
        await self.save()
    
    async def increment_comment_usage(self):
        self.reset_usage_if_needed()
        self.usage.comments_analyzed += 1
        self.updated_at = datetime.utcnow()
        await self.save()