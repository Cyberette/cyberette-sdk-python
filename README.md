# cyberette-sdk-python

**Python SDK for Cyberette Deepfake Detection APIs**

A powerful, async-first Python SDK for detecting deepfakes in images, videos, and audio files. Uploads are sent through the Cyberette API Gateway, with built-in batch processing and comprehensive error handling.

---

## Features

- ✨ **API Gateway Routing** — Sends all uploads through a single API gateway endpoint
- ⚡ **Async-First Architecture** — Built on `aiohttp` for high-concurrency, non-blocking operations
- 🔐 **API Key Header Support** — Sends `cyberette-api-key` on every upload request
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
```python
from cyberette_sdk import Cyberette
import asyncio

async def main():
    # Use as async context manager for safe session handling
    async with Cyberette(api_key="YOUR_API_KEY") as client:
        result = await client.upload("image.jpg")
        print(f"Verdict: {result['deepfake']['detection']['verdict']}")
        print(f"Confidence: {result['deepfake']['detection']['score']}%")

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
async def main():
    async with Cyberette(api_key="YOUR_API_KEY") as client:
        result = await client.upload("video.mp4")
        # Extract detection info easily
        verdict = ResponseParser.get_detection_verdict(result)
        confidence = ResponseParser.get_detection_percentage(result)
        model = ResponseParser.get_model_name(result)
        print(f"Model: {model}")
        print(f"Verdict: {verdict}")
        print(f"Confidence: {confidence}%")

asyncio.run(main())

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
async def main():
    async with Cyberette(api_key="YOUR_API_KEY") as client:
        result = await client.upload("image.jpg")
        # Validate and parse with Pydantic
        image = ImageResponse(**result)
        print(f"Verdict: {image.deepfake.detection.verdict}")
        print(f"Confidence: {image.deepfake.detection.score}%")

asyncio.run(main())

---

## Core Features

### API Gateway Upload Routing

The SDK sends every upload request to the configured API gateway endpoint:

```python
result = await client.upload("photo.jpg")
result = await client.upload("audio.mp3")
result = await client.upload("video.mp4")
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
async def batch_upload():
    async with Cyberette(api_key="YOUR_API_KEY") as client:
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
            print(f"{file_result['file']}: {file_result['result']}")

asyncio.run(batch_upload())

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
async def upload_with_events():
    async with Cyberette(api_key="YOUR_API_KEY") as client:
        # Register event handlers
        async def on_upload_started(file_path):
            print(f"Upload started: {file_path}")

        async def on_upload_success(file_path, response):
            print(f"Upload success: {file_path}, response: {response}")

        def on_upload_error(file_path, error):
            print(f"Error: {file_path}, error: {error}")

        client.on("upload_started", on_upload_started)
        client.on("upload_success", on_upload_success)
        client.on("upload_error", on_upload_error)

        result = await client.upload("video.mp4")

asyncio.run(upload_with_events())

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

Upload and analyze a media file through the API gateway.

**Parameters:**
- `file_path` (str) — Path to the file to upload

**Returns:** Detection result dictionary

**Raises:** `FileNotFoundError`, `Exception`

#### `async batch_upload(file_paths: List[str]) → List[dict]`

Upload multiple files in parallel.

**Parameters:**
- `file_paths` (List[str]) — List of file paths


**Returns:** List of detection results

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
    except Exception as e:
        print(f"API error: {e}")
    finally:
        await client.close()
```
async def main():
    async with Cyberette(api_key="YOUR_API_KEY") as client:
        try:
            result = await client.upload("image.jpg")
        except FileNotFoundError:
            print("File not found")
        except Exception as e:
            print(f"API error: {e}")

---

## License

Licensed under the Apache License 2.0. See [LICENSE](./LICENSE) for details.

---

## Author

**Stefan Saveski**

For support and questions, visit [docs.cyberette.ai](https://docs.cyberette.ai) or contact support.

---

## Changelog

### v0.1.2 (Initial Release)
- Core SDK with async/await support
- Gateway-only upload routing with `cyberette-api-key` header
- Batch processing with parallel requests
- Event system for real-time updates
- ResponseParser helper functions
- Pydantic data models
- 107 unit tests with 92% coverage
