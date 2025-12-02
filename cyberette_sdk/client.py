import aiohttp
import os
import mimetypes
import moviepy

MEDIA_TYPE_MAP = {
    "image": "image",
    "video": "video",
    "audio": "audio",
}

class Cyberette:
    def __init__(self, api_key: str, base_url_image: str = "https://api-image-dev-neu-002.azurewebsites.net/api/image", 
                 base_url_audio: str = "https://api-audio-dev-neu-002.azurewebsites.net/api/audio",
                 base_url_video: str = "http://localhost:5300/api/video", 
                 base_url_video_audio: str = "http://localhost:5300/api/video_and_audio"):
        self.api_key = api_key
        self.base_url_image = base_url_image
        self.base_url_audio = base_url_audio
        self.base_url_video = base_url_video
        self.base_url_video_audio = base_url_video_audio
        self.session = aiohttp.ClientSession()

    #File classification based on mime type
    def classify_file(self, file_path: str):
        mime, _ = mimetypes.guess_type(file_path)  # e.g. "image/png"
        if not mime:
            return None
        
        main_type = mime.split("/")[0]

        # For image, audio, video
        return MEDIA_TYPE_MAP.get(main_type)
    
    # Check if a video file has an audio track.
    # Import moviepy lazily so importing the SDK doesn't fail when moviepy
    # is not installed and the user doesn't need video-audio detection.
    def has_audio(self, video_path):
        clip = moviepy.VideoFileClip(video_path)
        has_audio_track = clip.audio is not None
        clip.close()
        return has_audio_track
    
    async def upload(self, file_path: str):
        file_type = self.classify_file(file_path)
        url = ""
        if file_type == "image":
            url = self.base_url_image
        elif file_type == "video":
            print("Checking for audio track in video...")
            if self.has_audio(file_path):
                print("Audio track detected in video.")
                url = self.base_url_video_audio
            else:
                print("No audio track detected in video.")
                url = self.base_url_video
        elif file_type == "audio":
            url = self.base_url_audio
        else:
            raise ValueError("Unsupported file type")
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            with open(file_path, "rb") as f:
                form = aiohttp.FormData()
                form.add_field("file", f, filename=os.path.basename(file_path))
                async with self.session.post(url, headers=headers, data=form) as r:
                    r.raise_for_status()
                    return await r.json()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except aiohttp.ClientError as e:
            raise Exception(f"Network error: {str(e)}")
            
    async def close(self):
        await self.session.close()