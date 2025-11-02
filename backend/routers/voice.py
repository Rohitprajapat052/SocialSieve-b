from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from models.user import User
from models.voice_analysis import VoiceAnalysis
from services.cloudinary_service import CloudinaryService
from services.whisper_service import whisper_service
from services.ollama_service import ollama_service
from utils.dependencies import get_current_user
from datetime import datetime

# Create router
router = APIRouter(
    prefix="/api/voice",
    tags=["Voice Analysis"]
)

@router.post("/analyze")
async def analyze_voice(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze voice note
    
    What happens:
    1. Check user's monthly limit
    2. Upload audio to Cloudinary
    3. Transcribe with Whisper
    4. Analyze with Ollama
    5. Save to database
    6. Return results
    
    User uploads: meeting.mp3
    User gets back: transcript + summary + action items
    """
    
    # STEP 1: Check if file is actually audio
    if not audio.content_type.startswith('audio'):
        raise HTTPException(
            status_code=400,
            detail="File must be audio (mp3, wav, m4a, etc.)"
        )
    
    print(f"🎤 Processing audio: {audio.filename}")
    
    # STEP 2: Upload to Cloudinary
    print("☁️ Uploading to Cloudinary...")
    cloudinary_result = await CloudinaryService.upload_audio(audio)
    audio_url = cloudinary_result["url"]
    duration_seconds = int(cloudinary_result.get("duration", 0))
    
    print(f"✅ Uploaded! URL: {audio_url}")
    
    # STEP 3: Check user's monthly limit (convert seconds to minutes)
    duration_minutes = max(1, duration_seconds // 60)  # At least 1 minute
    
    can_process = await current_user.check_voice_limit(duration_minutes)
    if not can_process:
        raise HTTPException(
            status_code=403,
            detail=f"Monthly limit exceeded! Used: {current_user.usage.voice_minutes_used}/{current_user.limits.voice_minutes_per_month} minutes"
        )
    
    # STEP 4: Reset file pointer and transcribe with Whisper
    # (Cloudinary already read the file, so we need to reset)
    await audio.seek(0)  # Go back to start of file
    
    print("🎧 Transcribing with Whisper...")
    whisper_result = await whisper_service.transcribe_audio(audio)
    transcript = whisper_result["transcript"]
    language = whisper_result["language"]
    
    print(f"✅ Transcription done! Length: {len(transcript)} characters")
    
    # STEP 5: Analyze with Ollama
    print("🤖 Analyzing with Ollama AI...")
    analysis_result = await ollama_service.analyze_transcript(transcript)
    summary = analysis_result["summary"]
    action_items = analysis_result["action_items"]
    
    print(f"✅ Analysis complete! Found {len(action_items)} action items")
    
    # STEP 6: Save to database
    voice_analysis = VoiceAnalysis(
        user_id=str(current_user.id),
        file_name=audio.filename,
        audio_url=audio_url,
        duration_seconds=duration_seconds,
        file_size_bytes=audio.size,
        transcript=transcript,
        summary=summary,
        action_items=action_items,
        language=language
    )
    
    await voice_analysis.save()
    
    # STEP 7: Update user's usage
    await current_user.increment_voice_usage(duration_minutes)
    
    print("💾 Saved to database!")
    print("🎉 Processing complete!")
    
    # STEP 8: Return everything to user
    return {
        "id": str(voice_analysis.id),
        "file_name": audio.filename,
        "audio_url": audio_url,
        "duration_seconds": duration_seconds,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "language": language,
        "created_at": voice_analysis.created_at
    }


@router.get("/history")
async def get_voice_history(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's voice analysis history
    
    Returns last 20 analyses, newest first
    """
    
    analyses = await VoiceAnalysis.find(
        VoiceAnalysis.user_id == str(current_user.id)
    ).sort(-VoiceAnalysis.created_at).limit(20).to_list()
    
    return analyses


@router.get("/{analysis_id}")
async def get_voice_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get specific voice analysis by ID
    """
    
    analysis = await VoiceAnalysis.get(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Make sure user owns this analysis
    if analysis.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return analysis

@router.delete("/{analysis_id}")
async def delete_voice_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a voice analysis
    """
    
    analysis = await VoiceAnalysis.get(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Make sure user owns this
    if analysis.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await analysis.delete()
    
    return {"message": "Voice analysis deleted successfully"}