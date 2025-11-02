import cloudinary
import cloudinary.uploader
from config.settings import settings

# Configure Cloudinary with our account details
cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret
)

class CloudinaryService:
    
    @staticmethod
    async def upload_audio(file):
        """
        Upload audio file to Cloudinary
        
        Simple flow:
        1. Read the file user uploaded
        2. Send it to Cloudinary
        3. Get back a URL
        
        Real-world example:
        You give file: meeting.mp3
        Cloudinary returns: https://cloudinary.com/xyz/meeting.mp3
        """
        
        # Read file content (the actual audio data)
        contents = await file.read()
        
        # Upload to Cloudinary's servers
        result = cloudinary.uploader.upload(
            contents,
            resource_type="video",  # Audio files use "video" type
            folder="socialsieve/audio"  # Organize in a folder
        )
        
        # Return the important info
        return {
            "url": result["secure_url"],  # The link to the file
            "public_id": result["public_id"],  # ID to delete it later
            "duration": result.get("duration", 0)  # How long is the audio
        }