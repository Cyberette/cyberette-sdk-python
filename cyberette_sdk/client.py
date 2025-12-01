import aiohttp
import os
import mimetypes

MEDIA_TYPE_MAP = {
    "image": "image",
    "video": "video",
    "audio": "audio",
}

class Cyberette:
    def __init__(self, api_key: str, base_url_image: str = "https://api-image-dev-neu-002.azurewebsites.net/api/image", base_url_video: str = "https://api-video-dev-neu-002.azurewebsites.net/api/video", base_url_audio: str = "https://api-audio-dev-neu-002.azurewebsites.net/api/audio"):
        self.api_key = api_key
        self.base_url_image = base_url_image
        self.base_url_video = base_url_video
        self.base_url_audio = base_url_audio
        self.session = aiohttp.ClientSession()

    #File classification based on mime type
    def classify_file(self, file_path: str):
        mime, _ = mimetypes.guess_type(file_path)  # e.g. "image/png"
        if not mime:
            return None
        
        main_type = mime.split("/")[0]

        # For image, audio, video
        return MEDIA_TYPE_MAP.get(main_type)
    
    async def upload(self, file_path: str):
        #Moviepy for audio detection
        file_type = self.classify_file(file_path)
        url = ""
        if file_type == "image":
            url = self.base_url_image
        elif file_type == "video":
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