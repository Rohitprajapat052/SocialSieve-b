from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from config.settings import settings
from models.user import User
from models.voice_analysis import VoiceAnalysis
from models.text_analysis import TextAnalysis

class Database:
    client: AsyncIOMotorClient = None

async def connect_db():
    try:
        print("📡 Connecting to MongoDB...")
        Database.client = AsyncIOMotorClient(settings.mongodb_url, serverSelectionTimeoutMS=5000)
        await init_beanie(
            database=Database.client.socialsieve,
            document_models=[User, VoiceAnalysis, TextAnalysis]

        )
        await Database.client.admin.command('ping')
        print("✅ Connected to MongoDB successfully!")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise

async def close_db():
    if Database.client:
        Database.client.close()
        print("❌ Closed MongoDB connection")