from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models.user import User
from models.text_analysis import TextAnalysis  # ← Add this
from services.ollama_service import ollama_service
from utils.dependencies import get_current_user

router = APIRouter(
    prefix="/api/text",
    tags=["Text Analysis"]
)

class TextInput(BaseModel):
    text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Yesterday's meeting was about Q4 strategy. We allocated $50k budget."
            }
        }

@router.post("/analyze")
async def analyze_text(
    input_data: TextInput,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze text and save to history
    
    Now saves every analysis to database!
    """
    
    if not input_data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if len(input_data.text) > 10000 and current_user.plan == "free":
        raise HTTPException(status_code=403, detail="Text too long! Max 10,000 characters")
    
    print(f"📝 Analyzing text ({len(input_data.text)} characters)...")
    
    # Analyze with AI
    result = await ollama_service.analyze_transcript(input_data.text)
    
    print("✅ Analysis complete!")
    
    # Save to database (NEW!)
    text_analysis = TextAnalysis(
        user_id=str(current_user.id),
        text=input_data.text,
        summary=result["summary"],
        action_items=result["action_items"],
        character_count=len(input_data.text)
    )
    
    await text_analysis.save()
    print("💾 Saved to history!")
    
    return {
        "id": str(text_analysis.id),  # Return ID
        "summary": result["summary"],
        "action_items": result["action_items"],
        "character_count": len(input_data.text),
        "analyzed_at": text_analysis.analyzed_at
    }


@router.get("/history")
async def get_text_history(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's text analysis history
    
    Returns last 20 analyses, newest first
    """
    
    analyses = await TextAnalysis.find(
        TextAnalysis.user_id == str(current_user.id)
    ).sort(-TextAnalysis.analyzed_at).limit(20).to_list()
    
    return analyses


@router.get("/{analysis_id}")
async def get_text_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get specific text analysis by ID
    """
    
    analysis = await TextAnalysis.get(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Make sure user owns this
    if analysis.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return analysis


@router.delete("/{analysis_id}")
async def delete_text_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a text analysis
    """
    
    analysis = await TextAnalysis.get(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await analysis.delete()
    
    return {"message": "Analysis deleted successfully"}