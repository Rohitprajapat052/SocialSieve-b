from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import connect_db, close_db
from config.settings import settings
from routers import auth, voice , text 
from datetime import datetime

app = FastAPI(
    title="SocialSieve API",
    description="AI-powered voice notes and comment analysis platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting SocialSieve API...")
    await connect_db()
    print("✅ Application ready!")

@app.on_event("shutdown")
async def shutdown_event():
    print("⏸️  Shutting down...")
    await close_db()

# Include routers
app.include_router(auth.router)
app.include_router(voice.router)  
app.include_router(text.router)

@app.get("/")
async def root():
    return {
        "message": "SocialSieve API is running!",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)