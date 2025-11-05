import os
import tempfile
from deepgram import Deepgram
import langid

class WhisperService:
    def __init__(self):
        print("🎧 Initializing Deepgram client...")
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            raise ValueError("❌ Deepgram API key not found in environment variables.")
        
        self.dg_client = Deepgram(api_key)
        print("✅ Deepgram ready!")

    async def transcribe_audio(self, audio_file):
        """
        Transcribe audio using Deepgram API
        - Auto-detects English/Hindi
        - Includes fallback detection using langid if Deepgram doesn’t return language
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')

        try:
            # Read audio file contents
            contents = await audio_file.read()
            temp_file.write(contents)
            temp_file.close()

            print(f"🎤 Sending to Deepgram: {audio_file.filename}")
            with open(temp_file.name, "rb") as f:
                source = {'buffer': f, 'mimetype': 'audio/mp3'}

                # Request Deepgram transcription with language auto-detection
                response = await self.dg_client.transcription.prerecorded(
                    source,
                    {
                        'smart_format': True,
                        'detect_language': True  # ✅ Deepgram auto-detects language
                    }
                )

            # Extract transcript
            transcript = response["results"]["channels"][0]["alternatives"][0].get("transcript", "")
            print("✅ Transcription done!")

            # Try to get Deepgram’s detected language
            language = None
            try:
                language = response["results"]["channels"][0]["alternatives"][0].get("language", None)
            except (KeyError, IndexError, TypeError):
                language = None

            # Fallback with langid if Deepgram didn’t return a language
            if not language or language.strip() == "":
                lang_code, _ = langid.classify(transcript)
                language = lang_code or "unknown"

            print(f"🈯 Detected language: {language}")

            return {
                "transcript": transcript,
                "language": language
            }

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
                print("🗑️ Temporary file deleted")



#git+https://github.com/openai/whisper.git

# import whisper
# import os
# import tempfile

# class WhisperService:
    
#     def __init__(self):
#         """
#         Load Whisper model when service starts
        
#         Models available:
#         - tiny: Fast but less accurate
#         - base: Good balance (WE USE THIS!)
#         - small: Better accuracy
#         - medium: Even better
#         - large: Best but slow
        
#         We use 'base' - good for learning!
#         """
#         print("📡 Loading Whisper model...")
#         self.model = whisper.load_model("tiny")
#          #self.model = whisper.load_model("base")

#         print("✅ Whisper model ready!")
    
#     async def transcribe_audio(self, audio_file):
#         """
#         Convert audio file to text
        
#         Simple flow:
#         1. Save uploaded file temporarily
#         2. Whisper reads and transcribes
#         3. Delete temporary file
#         4. Return transcript
        
#         Example:
#         Input: meeting.mp3
#         Output: "In today's meeting we discussed..."
#         """
        
#         # Create a temporary file
#         # Think of it like: making a copy to work with
#         temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        
#         try:
#             # Read the uploaded file
#             contents = await audio_file.read()
            
#             # Write it to temporary file
#             temp_file.write(contents)
#             temp_file.close()
            
#             # Now Whisper can read it!
#             print(f"🎤 Transcribing audio: {audio_file.filename}")
#             result = self.model.transcribe(temp_file.name)
            
#             # Get the text
#             transcript = result["text"]
#             language = result.get("language", "en")
            
#             print(f"✅ Transcription complete! Language: {language}")
            
#             return {
#                 "transcript": transcript,
#                 "language": language
#             }
            
#         finally:
#             # ALWAYS cleanup - delete temporary file
#             # Like throwing away scratch paper
#             if os.path.exists(temp_file.name):
#                 os.unlink(temp_file.name)
#                 print("🗑️ Temporary file deleted")

# # Create one instance to use everywhere
# whisper_service = WhisperService()
