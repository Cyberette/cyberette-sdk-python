# cyberette-sdk-python

**Python SDK for Cyberette Deepfake Detection APIs**

A powerful, async-first Python SDK for detecting deepfakes in images, videos, and audio files. Automatically classifies media types, handles batch processing with parallel requests, and provides comprehensive error handling.

---

## Features

- ✨ **Automatic File Classification** — Detects media type (image, video, audio) and routes to the correct endpoint
- ⚡ **Async-First Architecture** — Built on `aiohttp` for high-concurrency, non-blocking operations
- 🎯 **Intelligent Video Routing** — Automatically detects audio in videos and routes to appropriate endpoint
- 📦 **Batch Processing** — Process multiple files in parallel with built-in batch API
- 🔔 **Event System** — Real-time event listeners for upload, completion, and error handling
- 🛠️ **Helper Functions** — ResponseParser for easy result extraction and formatting
- 📊 **Data Models** — Pydantic models for type-safe response validation
- 🧪 **Comprehensive Testing** — 107 unit tests with 92% code coverage
- 📚 **Full Documentation** — Check [docs.cyberette.ai](https://docs.cyberette.ai) for detailed API docs

---

## Installation

```bash
pip install cyberette
```

**Requirements:**
- Python 3.8+
- aiohttp
- pydantic
- moviepy (for audio detection in videos)

---

## Quick Start

### Basic Upload

```python
from cyberette_sdk import Cyberette
import asyncio

async def main():
    # Initialize client
    client = Cyberette(api_key="YOUR_API_KEY")
    
    try:
        # Upload and analyze a file
        result = await client.upload("image.jpg")
        print(f"Verdict: {result['deepfake']['detection']['verdict']}")
        print(f"Confidence: {result['deepfake']['detection']['score']}%")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Using ResponseParser Helper

```python
from cyberette_sdk import Cyberette, ResponseParser
import asyncio

async def main():
    client = Cyberette(api_key="YOUR_API_KEY")
    
    try:
        result = await client.upload("video.mp4")
        
        # Extract detection info easily
        verdict = ResponseParser.get_detection_verdict(result)
        confidence = ResponseParser.get_detection_percentage(result)
        model = ResponseParser.get_model_name(result)
        
        print(f"Model: {model}")
        print(f"Verdict: {verdict}")
        print(f"Confidence: {confidence}%")
    finally:
        await client.close()

asyncio.run(main())
```

### With Pydantic Models for Type Safety

```python
from cyberette_sdk import Cyberette, ImageResponse
import asyncio

async def main():
    client = Cyberette(api_key="YOUR_API_KEY")
    
    try:
        result = await client.upload("image.jpg")
        
        # Validate and parse with Pydantic
        image = ImageResponse(**result)
        
        print(f"Verdict: {image.deepfake.detection.verdict}")
        print(f"Confidence: {image.deepfake.detection.score}%")
    finally:
        await client.close()

asyncio.run(main())
```

---

## Core Features

### Automatic File Classification

The SDK automatically detects file types and routes them to the correct endpoint. Just pass the file path:

```python
# Image
result = await client.upload("photo.jpg")  # Routes to image endpoint

# Audio
result = await client.upload("audio.mp3")  # Routes to audio endpoint

# Video (visual only)
result = await client.upload("video.mp4")  # Routes to video endpoint

# Video with audio
result = await client.upload("video_with_sound.mp4")  # Auto-detects audio, routes to video+audio endpoint
```

### Batch Processing with Parallel Requests

Process multiple files efficiently with automatic parallelization:

```python
async def batch_upload():
    client = Cyberette(api_key="YOUR_API_KEY")
    
    try:
        files = [
            "image1.jpg",
            "image2.jpg",
            "video.mp4",
            "audio.mp3"
        ]
        
        # Upload all files in parallel
        results = await client.batch_upload(files)
        
        # Access results
        for file_result in results:
            print(f"{file_result['file']}: {file_result['verdict']}")
    finally:
        await client.close()

asyncio.run(batch_upload())
```

### Event Handling

Listen for real-time events during processing:

```python
async def upload_with_events():
    client = Cyberette(api_key="YOUR_API_KEY")
    
    # Register event handlers
    async def on_upload_start(event):
        print(f"Upload started: {event.data['file']}")
    
    async def on_upload_complete(event):
        print(f"Upload complete: {event.data['result']}")
    
    def on_error(event):
        print(f"Error: {event.data['error']}")
    
    client.emitter.on("upload_start", on_upload_start)
    client.emitter.on("upload_complete", on_upload_complete)
    client.emitter.on("error", on_error)
    
    try:
        result = await client.upload("video.mp4")
    finally:
        await client.close()

asyncio.run(upload_with_events())
```

### ResponseParser Helper Functions

Extract and format detection results easily:

```python
from cyberette_sdk import ResponseParser

# Extract detection info
verdict = ResponseParser.get_detection_verdict(result)
confidence = ResponseParser.get_detection_percentage(result)
model_name = ResponseParser.get_model_name(result)
model_version = ResponseParser.get_model_version(result)
segments = ResponseParser.get_segments(result)  # For audio/video

# Format for display
summary = ResponseParser.format_detection(result)
segment_summaries = ResponseParser.format_segments(result)

# Batch processing
batch_summaries = ResponseParser.summarize_batch(batch_results)
```

### Type-Safe Data Models

Use Pydantic models for validation:

```python
from cyberette_sdk import (
    ImageResponse,
    AudioResponse,
    VideoResponse,
    MultimodalVideoResponse,
    Detection,
    DeepfakeAnalysis,
    Segment
)

# Parse and validate responses
image = ImageResponse(**result)
audio = AudioResponse(**result)
video = VideoResponse(**result)
multimodal = MultimodalVideoResponse(**result)

# Access nested data with type safety
verdict = image.deepfake.detection.verdict
confidence = image.deepfake.detection.score
segments = audio.deepfake.detection.segments
```

---

## API Reference

### Cyberette Client

#### `__init__(api_key: str)`

Initialize the SDK client.

**Parameters:**
- `api_key` (str) — Your Cyberette API key

#### `async upload(file_path: str) → dict`

Upload and analyze a media file. Automatically classifies and routes to correct endpoint.

**Parameters:**
- `file_path` (str) — Path to the file to upload

**Returns:** Detection result dictionary

**Raises:** `FileNotFoundError`, `ValueError`, `Exception`

#### `async batch_upload(file_paths: List[str]) → List[dict]`

Upload multiple files in parallel.

**Parameters:**
- `file_paths` (List[str]) — List of file paths


**Returns:** List of detection results

#### `def classify_file(file_path: str) → str | None`

Classify a file type by MIME type.

**Returns:** `"image"`, `"video"`, `"audio"`, or `None`

#### `async close()`

Close the aiohttp session and cleanup resources.

---

## Examples

More detailed examples are available in the [examples/](./examples/) folder:

- `basic.py` — Basic upload and analysis
- `datamodels_usage.py` — Pydantic model usage
- `batch_usage.py` — Batch upload example
- `events_direct.py` — Event listener examples
- `utils_usage.py` — ResponseParser helper usage

For comprehensive documentation, visit [docs.cyberette.ai](https://docs.cyberette.ai).

---

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=cyberette_sdk --cov-report=html

# Run specific test file
pytest tests/test_client.py -v
```

**Test Coverage:** 107 unit tests with 92% code coverage

---

## Error Handling

The SDK provides clear exceptions for different error scenarios:

```python
from cyberette_sdk import Cyberette

async def main():
    client = Cyberette(api_key="YOUR_API_KEY")
    
    try:
        result = await client.upload("image.jpg")
    except FileNotFoundError:
        print("File not found")
    except ValueError:
        print("Invalid file type")
    except Exception as e:
        print(f"API error: {e}")
    finally:
        await client.close()
```

---

## License

Licensed under the Apache License 2.0. See [LICENSE](./LICENSE) for details.

---

## Author

**Stefan Saveski**

For support and questions, visit [docs.cyberette.ai](https://docs.cyberette.ai) or contact support.

---

## Changelog

### v0.1.1 (Initial Release)
- Core SDK with async/await support
- Automatic file classification and routing
- Batch processing with parallel requests
- Event system for real-time updates
- ResponseParser helper functions
- Pydantic data models
- 107 unit tests with 92% coverage
