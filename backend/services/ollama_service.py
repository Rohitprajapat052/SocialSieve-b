# import requests
# from config.settings import settings

# class OllamaService:
    
#     @staticmethod
#     async def analyze_transcript(transcript: str):
#         """
#         Send transcript to Ollama AI for analysis
        
#         Flow:
#         1. Create a smart prompt
#         2. Send to Ollama
#         3. Get back summary + action items
        
#         Think of it like:
#         You give AI a long essay
#         AI gives back bullet points
#         """
        
#         # Create a clear instruction for AI
#         prompt = f"""
# You are a helpful assistant. Analyze this transcript and provide:

# 1. A brief summary (3-5 bullet points)
# 2. Action items (things that need to be done)

# Transcript:
# {transcript}

# Format your response like this:

# SUMMARY:
# - Point 1
# - Point 2
# - Point 3

# ACTION ITEMS:
# - Task 1
# - Task 2
# - Task 3
# """
        
#         # Send request to Ollama
#         response = requests.post(
#             f"{settings.ollama_url}/api/generate",
#             json={
#                 "model": "qwen2.5-coder:7b",
#                 "prompt": prompt,
#                 "stream": False  # Get complete response at once
#             }
#         )
        
#         # Get AI's response
#         result = response.json()
#         analysis = result["response"]
        
#         # Parse the response to extract summary and action items
#         summary, action_items = OllamaService._parse_analysis(analysis)
        
#         return {
#             "summary": summary,
#             "action_items": action_items,
#             "full_analysis": analysis
#         }
    
#     @staticmethod
#     def _parse_analysis(analysis: str):
#         """
#         Extract summary and action items from AI response
        
#         Simple text processing:
#         - Find "SUMMARY:" section
#         - Find "ACTION ITEMS:" section
#         - Extract bullet points
#         """
        
#         summary = ""
#         action_items = []
        
#         # Split response into lines
#         lines = analysis.split('\n')
        
#         current_section = None
        
#         for line in lines:
#             line = line.strip()
            
#             # Check which section we're in
#             if 'SUMMARY' in line.upper():
#                 current_section = 'summary'
#                 continue
#             elif 'ACTION' in line.upper():
#                 current_section = 'action'
#                 continue
            
#             # Add content to appropriate section
#             if line.startswith('•') or line.startswith('-') or line.startswith('*'):
#                 if current_section == 'summary':
#                     summary += line + '\n'
#                 elif current_section == 'action':
#                     # Remove bullet point and add to list
#                     item = line.lstrip('•-* ').strip()
#                     if item:
#                         action_items.append(item)
        
#         # If parsing failed, use whole response as summary
#         if not summary:
#             summary = analysis
        
#         return summary.strip(), action_items

# # Create instance
# ollama_service = OllamaService()


from groq import Groq
from config.settings import settings

class OllamaService:
    """
    Now using Groq API instead of local Ollama
    Free, fast, and always available!
    """
    
    @staticmethod
    async def analyze_transcript(transcript: str):
        """
        Analyze transcript using Groq's Llama model
        """
        
        try:
            client = Groq(api_key=settings.groq_api_key)
            
            prompt = f"""Analyze this transcript and provide:

1. A brief summary (3-5 bullet points)
2. Action items (things that need to be done)

Transcript:
{transcript}

Format your response EXACTLY like this:

SUMMARY:
- Point 1
- Point 2
- Point 3

ACTION ITEMS:
- Task 1
- Task 2
"""
            
            # Call Groq API
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            analysis = response.choices[0].message.content
            
            # Parse response
            summary = ""
            action_items = []
            
            lines = analysis.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if 'SUMMARY' in line.upper():
                    current_section = 'summary'
                    continue
                elif 'ACTION' in line.upper():
                    current_section = 'action'
                    continue
                
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    if current_section == 'summary':
                        summary += line + '\n'
                    elif current_section == 'action':
                        item = line.lstrip('•-* ').strip()
                        if item:
                            action_items.append(item)
            
            # Fallback if parsing fails
            if not summary:
                summary = analysis
            
            return {
                "summary": summary.strip(),
                "action_items": action_items,
                "full_analysis": analysis
            }
            
        except Exception as e:
            print(f"Groq API error: {e}")
            return {
                "summary": "⚠️ AI analysis temporarily unavailable. Please try again.",
                "action_items": [],
                "full_analysis": f"Error: {str(e)}"
            }

# Create instance
ollama_service = OllamaService()