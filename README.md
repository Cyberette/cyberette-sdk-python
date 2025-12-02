# cyberette-sdk-python

Python SDK for the Cyberette detection APIs (image, video, audio deepfake detection).

## Features

- 🎯 **Automatic file classification** — detects media type (image, video, audio) by MIME type
- 🔍 **Video audio detection** — automatically routes videos with audio to the `video_and_audio` endpoint
- ⚡ **Async-first** — built on aiohttp for high-concurrency workloads
- 🛡️ **Error handling** — clear exceptions for file not found, network errors, and unsupported types

## Install

```bash
pip install cyberette
```

## Quick Start

```python
from cyberette import Cyberette
import asyncio

async def main():
    client = Cyberette(api_key="YOUR_KEY")
    try:
        result = await client.upload("image.jpg")
        print(result)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### Cyberette(api_key, base_url_image, base_url_video, base_url_audio, base_url_video_audio)

Initialize the SDK client with optional custom endpoint URLs.

### async upload(file_path: str) → dict

Upload and analyze a media file. Automatically routes to the correct endpoint based on file type.

**Raises:** `FileNotFoundError`, `ValueError`, `Exception`

### def classify_file(file_path: str) → str | None

Classify a file type by MIME type. Returns `"image"`, `"video"`, `"audio"`, or `None`.

### async close()

Close the aiohttp session.

## Testing

```bash
pytest -v
pytest --cov=cyberette_sdk tests/
```

## License

MIT
