# cyberette-sdk-python

**Python SDK for Cyberette Deepfake Detection**

An async-first Python SDK for detecting deepfakes in images, videos, and audio files using the Cyberette API.

---

## Installation

```bash
pip install cyberette
```

**Requirements:** Python 3.8+, `aiohttp`, `pydantic`

---

## Quick Start

```python
from cyberette_sdk import Cyberette
import asyncio

async def main():
    async with Cyberette(api_key="YOUR_API_KEY") as client:
        result = await client.upload("image.jpg")
        print(result)

asyncio.run(main())
```

---

## Initialization

```python
client = Cyberette(
    api_key="YOUR_API_KEY",           # Required
    timeout_seconds=300.0,            # Default: 300s
    verdict_thresholds=(0.5, 0.7),    # (modified_threshold, generated_threshold)
    verdict_labels=("Real", "AI Modified", "AI Generated"),
)
```

### Verdict Thresholds

The SDK reclassifies the API score into a verdict using two thresholds:

| Score range | Verdict |
|---|---|
| `< modified_threshold` | `"Real"` (label[0]) |
| `>= modified_threshold` and `< generated_threshold` | `"AI Modified"` (label[1]) |
| `>= generated_threshold` | `"AI Generated"` (label[2]) |

Defaults: `(0.5, 0.7)` thresholds, `("Real", "AI Modified", "AI Generated")` labels.

---

## Uploading Files

### Single upload

```python
result = await client.upload("photo.jpg")
result = await client.upload("audio.mp3")
result = await client.upload("video.mp4")
```

Retries automatically on transient errors (3 retries, exponential backoff).

### Batch upload

```python
files = ["image1.jpg", "image2.jpg", "video.mp4", "audio.mp3"]
results = await client.batch_upload(files, concurrency=5)

for item in results:
    print(item["file"], item["result"], item["error"])
```

Each item in the returned list: `{"file": str, "result": dict | None, "error": Exception | None}`

### Folder upload

```python
results = await client.upload_folder("path/to/folder", concurrency=5)
```

Uploads all files in the folder (non-recursive).

---

## Event System

Register sync or async handlers for upload lifecycle events.

```python
# Decorator style
@client.on("upload_started")
async def on_start(file_path):
    print(f"Starting: {file_path}")

# Direct style
client.on("upload_success", lambda file_path, response: print(f"Done: {file_path}"))
```

### Available events

| Event | Keyword args |
|---|---|
| `upload_started` | `file_path` |
| `upload_sent` | `file_path`, `url` |
| `upload_success` | `file_path`, `response` |
| `upload_error` | `file_path`, `error` |
| `batch_started` | `files` |
| `batch_file_success` | `file`, `result` |
| `batch_file_error` | `file`, `error` |
| `batch_finished` | `results` |

---

## ResponseParser

Helper for extracting fields from response dicts.

```python
from cyberette_sdk import ResponseParser

verdict    = ResponseParser.get_detection_verdict(result)
confidence = ResponseParser.get_detection_percentage(result)
model      = ResponseParser.get_model_name(result)
version    = ResponseParser.get_model_version(result)
segments   = ResponseParser.get_segments(result)

summary    = ResponseParser.format_detection(result)
# "Model: <name> v<version>, Verdict: <verdict> (<confidence>%)"

seg_lines  = ResponseParser.format_segments(result)
# ["Segment: 0.0 -> 2.5, Verdict: Real (0.12%)", ...]
```

For multimodal video responses, pass `media="audio"` or `media="video"`:

```python
audio_verdict = ResponseParser.get_detection_verdict(result, media="audio")
video_verdict = ResponseParser.get_detection_verdict(result, media="video")
```

### Batch summary

```python
summaries = ResponseParser.summarize_batch(results)
# [{"file": ..., "verdict": ..., "percentage": ..., "error": ...}, ...]
```

---

## Pydantic Models

Type-safe wrappers for API responses.

```python
from cyberette_sdk import ImageResponse, AudioResponse, VideoResponse, MultimodalVideoResponse

image = ImageResponse(**result)
print(image.deepfake.detection.verdict)
print(image.deepfake.detection.score)

audio = AudioResponse(**result)
print(audio.deepfake.detection.segments)

video = VideoResponse(**result)

multi = MultimodalVideoResponse(**result)
print(multi.audio.deepfake.detection.verdict)
print(multi.video.deepfake.detection.verdict)
```

**All models:** `Segment`, `Detection`, `DeepfakeAnalysis`, `ImageResponse`, `AudioResponse`, `VideoResponse`, `MultimodalVideoResponse`, `BatchResultItem`, `BatchResult`, `ErrorResponse`

---

## Error Handling

```python
async with Cyberette(api_key="YOUR_API_KEY") as client:
    try:
        result = await client.upload("image.jpg")
    except FileNotFoundError:
        print("File not found")
    except Exception as e:
        print(f"Error: {e}")
```

---

## Examples

See the [examples/](./examples/) folder:

- `basic.py` — Single file upload
- `batch_usage.py` — Batch upload
- `upload_folder.py` — Folder upload
- `events_direct.py` — Event listeners (direct style)
- `events_decorator.py` — Event listeners (decorator style)
- `events_batch.py` — Batch events

---

## Testing

```bash
pytest tests/ -v
pytest tests/ --cov=cyberette_sdk --cov-report=html
```

---

## License

Apache License 2.0. See [LICENSE](./LICENSE) for details.

---

## Changelog

### v0.1.3
- Added `upload_folder()` method
- Retry logic with exponential backoff on transient errors
- Configurable verdict thresholds and labels

### v0.1.2
- Initial release
- Async upload via API gateway
- Batch processing with concurrency control
- Event system
- ResponseParser helpers
- Pydantic response models
