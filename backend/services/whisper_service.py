from deepgram import Deepgram
import os
import tempfile
import asyncio

class WhisperService:
    def __init__(self):
        print("🎧 Initializing Deepgram client...")
        self.dg_client = Deepgram(os.getenv("DEEPGRAM_API_KEY"))
        print("✅ Deepgram ready!")

    async def transcribe_audio(self, audio_file):
        """
        Transcribe audio using Deepgram API
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')

        try:
            contents = await audio_file.read()
            temp_file.write(contents)
            temp_file.close()

            print(f"🎤 Sending to Deepgram: {audio_file.filename}")
            with open(temp_file.name, "rb") as f:
                source = {'buffer': f, 'mimetype': 'audio/mp3'}
                response = await self.dg_client.transcription.prerecorded(source, {'smart_format': True})

            transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
            print("✅ Transcription done!")
            return {"transcript": transcript}
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
                print("🗑️ Temporary file deleted")

whisper_service = WhisperService()

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
