import aiohttp
import os
import mimetypes
import moviepy
import asyncio
import sys

MEDIA_TYPE_MAP = {
    "image": "image",
    "video": "video",
    "audio": "audio",
}
DEFAULT_BASE_URL_IMAGE = "https://api-image-dev-neu-002.azurewebsites.net/api/image"
DEFAULT_BASE_URL_VIDEO = "https://api-video-dev-neu-003.azurewebsites.net/api/video"
DEFAULT_BASE_URL_AUDIO = "https://api-audio-dev-neu-004.azurewebsites.net/api/audio"
DEFAULT_BASE_URL_VIDEO_AUDIO = "https://api-video-dev-neu-003.azurewebsites.net/api/video_and_audio"
DEFAULT_API_GATEWAY = "https://cyberette-api-gateway-01.azurewebsites.net/upload"


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
    def __init__(
        self,
        api_key: str,
        base_url_image: str = DEFAULT_BASE_URL_IMAGE,
        base_url_audio: str = DEFAULT_BASE_URL_AUDIO,
        base_url_video: str = DEFAULT_BASE_URL_VIDEO,
        base_url_video_audio: str = DEFAULT_BASE_URL_VIDEO_AUDIO,
        base_url_api_gateway: str = DEFAULT_API_GATEWAY,
        use_gateway: bool = False,
        timeout_seconds: float = 300.0,
        verdict_thresholds: tuple[float, float] | None = None,  # (modified_threshold, generated_threshold)
        verdict_labels: tuple[str, str, str] = ("Real", "AI Modified", "AI Generated")
    ):
        self.api_key = api_key
        # TODO Add authentication with API key, raises error
        self.base_url_image = base_url_image
        self.base_url_audio = base_url_audio
        self.base_url_video = base_url_video
        self.base_url_video_audio = base_url_video_audio
        self.base_url_api_gateway = base_url_api_gateway
        self.use_gateway = use_gateway
        if verdict_thresholds is not None:
            if (
                not isinstance(verdict_thresholds, tuple)
                or len(verdict_thresholds) != 2
            ):
                raise ValueError("verdict_thresholds must be a tuple(modified_threshold, generated_threshold) or None")

            modified_th, generated_th = verdict_thresholds
            if not (0.0 <= modified_th <= 1.0 and 0.0 <= generated_th <= 1.0):
                raise ValueError("verdict_thresholds values must be within [0.0, 1.0]")
            if modified_th > generated_th:
                raise ValueError("modified_threshold must be <= generated_threshold")
        self.verdict_thresholds = verdict_thresholds
        self.verdict_labels = verdict_labels
        timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self.session = aiohttp.ClientSession(timeout=timeout)
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

    # File classification based on mime type
    def classify_file(self, file_path: str):
        mime, _ = mimetypes.guess_type(file_path)  # e.g. "image/png"
        if not mime:
            return None

        main_type = mime.split("/")[0]

        # For image, audio, video
        return MEDIA_TYPE_MAP.get(main_type)

    # Check if a video file has an audio track.
    def has_audio(self, video_path):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
            
            clip = moviepy.VideoFileClip(video_path)
            has_audio_track = clip.audio is not None
            clip.close()
            return has_audio_track
        finally:
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def classify_verdict_from_thresholds(
        self,
        score: float,
        thresholds: tuple[float, float] | None = None, # (modified_threshold, generated_threshold)
        labels: tuple[str, str, str] | None = None,  
    ) -> str:
        """
        Classify into one of: 'Real' | 'AI Modified' | 'AI Generated'

        Rules:
          score < modified_threshold              => 'Real'
          modified_threshold <= score < generated_threshold => 'AI Modified'
          score >= generated_threshold            => 'AI Generated'

        If `thresholds` is None, uses `self.verdict_thresholds` if present.
        """
        th = thresholds if thresholds is not None else getattr(self, "verdict_thresholds", None)
        if th is None:
            raise ValueError("thresholds not provided and self.verdict_thresholds is not set")

        if not isinstance(th, tuple) or len(th) != 2:
            raise ValueError("thresholds must be a tuple(modified_threshold, generated_threshold)")

        modified_th, generated_th = th

        try:
            s = float(score)
            modified_th = float(modified_th)
            generated_th = float(generated_th)
        except (TypeError, ValueError):
            raise ValueError("score and thresholds must be numeric")

        if not (0.0 <= s <= 1.0):
            raise ValueError("score must be within [0.0, 1.0]")
        if not (0.0 <= modified_th <= 1.0 and 0.0 <= generated_th <= 1.0):
            raise ValueError("thresholds must be within [0.0, 1.0]")
        if modified_th > generated_th:
            raise ValueError("modified_threshold must be <= generated_threshold")

        if s < modified_th:
            return labels[0]
        if s < generated_th:
            return labels[1]
        return labels[2]

    async def upload(
        self,
        file_path: str,
        retries: int = 3,
        retry_backoff_seconds: float = 1.0,
    ):
        # Emit event: upload started
        await self.events.emit("upload_started", file_path=file_path)

        file_type = self.classify_file(file_path)
        url = ""
        if self.use_gateway:
            url = self.base_url_api_gateway
        else:
            if file_type == "image":
                url = self.base_url_image
            elif file_type == "video":
                # print("Checking for audio track in video...")
                if self.has_audio(file_path):
                    # print("Audio track detected in video.")
                    url = self.base_url_video_audio
                else:
                    # print("No audio track detected in video.")
                    url = self.base_url_video
            elif file_type == "audio":
                url = self.base_url_audio
            else:
                raise ValueError("Unsupported file type")

        headers = {"Authorization": f"Bearer {self.api_key}"}

        def _should_retry_response_status(status: int) -> bool:
            return status in (408, 425, 429, 500, 502, 503, 504)

        def _is_transient_error(exc: BaseException) -> bool:
            if isinstance(exc, asyncio.TimeoutError):
                return True
            if isinstance(exc, aiohttp.ClientConnectionError):
                return True
            if isinstance(exc, aiohttp.ServerTimeoutError):
                return True
            if isinstance(exc, aiohttp.ClientOSError):
                return True
            return False

        attempt = 0
        while True:
            try:
                with open(file_path, "rb") as f:
                    form = aiohttp.FormData()
                    form.add_field("file", f, filename=os.path.basename(file_path))

                    async with self.session.post(url, headers=headers, data=form) as r:
                        await self.events.emit("upload_sent", file_path=file_path, url=url)

                        if r.status >= 400:
                            if attempt < retries and _should_retry_response_status(r.status):
                                delay = retry_backoff_seconds * (2**attempt)
                                await asyncio.sleep(delay)
                                attempt += 1
                                continue

                            r.raise_for_status()

                        data = await r.json()

                        # Reclassify verdict only when thresholds are configured
                        if self.verdict_thresholds is not None:
                            # print(data.get("audio", {}))
                            if data.get("audio", {}) != {}:
                                det = data.get("audio", {}).get("deepfake", {}).get("detection", {})
                                score = det.get("score")
                                if score is not None:
                                    det["verdict"] = self.classify_verdict_from_thresholds(score, labels=self.verdict_labels)
                                    data["audio"]["deepfake"]["detection"] = det
                                det = data.get("video", {}).get("deepfake", {}).get("detection", {})
                                score = det.get("score")
                                if score is not None:
                                    det["verdict"] = self.classify_verdict_from_thresholds(score, labels=self.verdict_labels)
                                    data["video"]["deepfake"]["detection"] = det
                            else:
                                det = data.get("deepfake", {}).get("detection", {})
                                score = det.get("score")
                                if score is not None:
                                    det["verdict"] = self.classify_verdict_from_thresholds(score, labels=self.verdict_labels)
                                    data["deepfake"]["detection"] = det

                        await self.events.emit(
                            "upload_success", file_path=file_path, response=data
                        )
                        return data
            except FileNotFoundError:
                raise FileNotFoundError(f"File not found: {file_path}")
            except aiohttp.ClientResponseError as e:
                if attempt < retries and e.status is not None and _should_retry_response_status(e.status):
                    delay = retry_backoff_seconds * (2**attempt)
                    await asyncio.sleep(delay)
                    attempt += 1
                    continue
                raise Exception(f"Network error: {str(e)}")
            except aiohttp.ClientError as e:
                if attempt < retries and _is_transient_error(e):
                    delay = retry_backoff_seconds * (2**attempt)
                    await asyncio.sleep(delay)
                    attempt += 1
                    continue
                raise Exception(f"Network error: {str(e)}")
            except asyncio.TimeoutError as e:
                if attempt < retries:
                    delay = retry_backoff_seconds * (2**attempt)
                    await asyncio.sleep(delay)
                    attempt += 1
                    continue
                raise Exception(f"Network error: {str(e)}")
            except Exception as e:
                await self.events.emit("upload_error", file_path=file_path, error=e)
                raise

    async def batch_upload(self, file_paths: list[str], concurrency: int = 5):
        await self.events.emit("batch_started", files=file_paths)

        if concurrency < 1:
            raise ValueError("concurrency must be >= 1")

        semaphore = asyncio.Semaphore(concurrency)
        tasks = []

        async def process(file_path):
            await semaphore.acquire()
            try:
                try:
                    result = await self.upload(file_path)
                    await self.events.emit(
                        "batch_file_success", file=file_path, result=result
                    )
                    return {"file": file_path, "result": result, "error": None}
                except Exception as e:
                    await self.events.emit("batch_file_error", file=file_path, error=e)
                    return {"file": file_path, "result": None, "error": e}
            finally:
                semaphore.release()

        # Start all tasks; semaphore enforces concurrency.
        for fp in file_paths:
            tasks.append(asyncio.create_task(process(fp)))

        results = await asyncio.gather(*tasks)

        await self.events.emit("batch_finished", results=results)
        return results

    async def close(self):
        await self.session.close()
