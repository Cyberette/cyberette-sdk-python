import aiohttp
import os
import mimetypes
import moviepy
import asyncio

MEDIA_TYPE_MAP = {
    "image": "image",
    "video": "video",
    "audio": "audio",
}

class AsyncEventEmitter:
    def __init__(self):
        self._events = {}

    def on(self, event_name, callback):
        self._events.setdefault(event_name, []).append(callback)

    async def emit(self, event_name, *args, **kwargs):
        handlers = self._events.get(event_name, [])
        tasks = []

        for handler in handlers:
            # async handler
            if asyncio.iscoroutinefunction(handler):

                async def safe_call(h=handler):
                    try:
                        await h(*args, **kwargs)
                    except Exception as e:
                        print(f"[Event Error] {event_name}: {e}")

                tasks.append(asyncio.create_task(safe_call()))
            else:
                # sync handler
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    print(f"[Event Error] {event_name}: {e}")

        if tasks:
            await asyncio.gather(*tasks)


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
        # Add event system
        self.events = AsyncEventEmitter()

    def on(self, event_name, callback=None):
        if callback is None:
            # decorator style
            def decorator(cb):
                self.events.on(event_name, cb)
                return cb
            return decorator
        else:
            # direct style
            self.events.on(event_name, callback)



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
        # Emit event: upload started
        await self.events.emit("upload_started", file_path=file_path)

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
                    await self.events.emit("upload_sent", file_path=file_path, url=url)

                    r.raise_for_status()
                    data = await r.json()

                    await self.events.emit("upload_success", file_path=file_path, response=data)
                    return data
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except aiohttp.ClientError as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            await self.events.emit("upload_error", file_path=file_path, error=e)
            raise
    
    async def batch_upload(self, file_paths: list[str]):
        await self.events.emit("batch_started", files=file_paths)

        tasks = []
        results = []

        async def process(file_path):
            try:
                result = await self.upload(file_path)
                await self.events.emit("batch_file_success", file=file_path, result=result)
                return {"file": file_path, "result": result, "error": None}
            except Exception as e:
                await self.events.emit("batch_file_error", file=file_path, error=e)
                return {"file": file_path, "result": None, "error": e}

        # start all tasks in parallel
        for fp in file_paths:
            tasks.append(asyncio.create_task(process(fp)))

        # wait for all
        results = await asyncio.gather(*tasks)

        await self.events.emit("batch_finished", results=results)
        return results

    async def close(self):
        await self.session.close()