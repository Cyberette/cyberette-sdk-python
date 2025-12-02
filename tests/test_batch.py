import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from cyberette_sdk.client import Cyberette


@pytest.mark.asyncio
async def test_batch_upload_success(monkeypatch):
    """
    Test that batch_upload returns correct results when all uploads succeed.
    """

    sdk = Cyberette(api_key="test")

    # Mock upload() to always succeed
    async def mock_upload(path):
        return {"ok": True, "file": path}

    monkeypatch.setattr(sdk, "upload", mock_upload)

    file_list = ["a.jpg", "b.jpg"]

    results = await sdk.batch_upload(file_list)

    assert len(results) == 2

    assert results[0]["file"] == "a.jpg"
    assert results[0]["result"]["ok"] is True
    assert results[0]["error"] is None

    assert results[1]["file"] == "b.jpg"
    assert results[1]["result"]["ok"] is True
    assert results[1]["error"] is None


@pytest.mark.asyncio
async def test_batch_upload_mixed_results(monkeypatch):
    """
    Mixed case: first successful, second raises error.
    """

    sdk = Cyberette(api_key="test")

    async def mock_upload(path):
        if path == "good.jpg":
            return {"result": "ok"}
        raise ValueError("Upload failed!")

    monkeypatch.setattr(sdk, "upload", mock_upload)

    results = await sdk.batch_upload(["good.jpg", "bad.jpg"])

    assert results[0]["error"] is None
    assert results[0]["result"]["result"] == "ok"

    assert isinstance(results[1]["error"], Exception)
    assert results[1]["result"] is None


@pytest.mark.asyncio
async def test_batch_events(monkeypatch):
    """
    Validate that all correct events are emitted in order.
    """

    sdk = Cyberette(api_key="test")

    # Mock upload to succeed
    async def mock_upload(path):
        return {"done": True}

    monkeypatch.setattr(sdk, "upload", mock_upload)

    # Event collectors
    events = []

    @sdk.on("batch_started")
    def on_batch_started(files):
        events.append(("batch_started", files))

    @sdk.on("batch_file_success")
    def on_file_success(file, result):
        events.append(("success", file))

    @sdk.on("batch_finished")
    def on_batch_finished(results):
        events.append(("batch_finished", len(results)))

    await sdk.batch_upload(["1.jpg", "2.jpg"])

    # Expected 4 events:
    # 1) started
    # 2) file success
    # 3) file success
    # 4) finished
    assert events[0][0] == "batch_started"
    assert events[1][0] == "success"
    assert events[2][0] == "success"
    assert events[-1][0] == "batch_finished"


@pytest.mark.asyncio
async def test_batch_events_async_handlers(monkeypatch):
    """
    Ensures async handlers are awaited and executed properly.
    """

    sdk = Cyberette(api_key="test")

    # Mock upload to succeed
    async def mock_upload(path):
        await asyncio.sleep(0.01)
        return {"ok": True}

    monkeypatch.setattr(sdk, "upload", mock_upload)

    call_order = []

    @sdk.on("batch_started")
    async def async_started(files):
        await asyncio.sleep(0.01)
        call_order.append("started")

    @sdk.on("batch_file_success")
    async def async_success(file, result):
        await asyncio.sleep(0.01)
        call_order.append("file_success")

    @sdk.on("batch_finished")
    async def async_finished(results):
        await asyncio.sleep(0.01)
        call_order.append("finished")

    await sdk.batch_upload(["1.jpg"])

    assert call_order == ["started", "file_success", "finished"]


@pytest.mark.asyncio
async def test_batch_parallel_execution(monkeypatch):
    """
    Ensures uploads are truly performed in parallel by checking
    that total duration is shorter than sequential time.
    """

    sdk = Cyberette(api_key="test")

    async def mock_upload(path):
        await asyncio.sleep(0.1)
        return {"ok": True}

    monkeypatch.setattr(sdk, "upload", mock_upload)

    start = asyncio.get_event_loop().time()
    await sdk.batch_upload(["1", "2", "3"])
    end = asyncio.get_event_loop().time()

    elapsed = end - start

    # Sequential would be ~0.3s
    # Parallel should be ~0.1s
    assert elapsed < 0.20
