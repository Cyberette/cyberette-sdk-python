import pytest
import asyncio
from unittest.mock import AsyncMock
from cyberette_sdk.client import Cyberette

@pytest.mark.asyncio
class TestEventSystem:
    """Tests for Cyberette SDK event system."""

    async def test_upload_started_event(self):
        client = Cyberette(api_key="test_key")
        try:
            mock_listener = AsyncMock()

            @client.on("upload_started")
            async def listener(file_path):
                await mock_listener(file_path)

            # Emit event manually
            await client.events.emit("upload_started", file_path="test.png")

            mock_listener.assert_awaited_once_with("test.png")
        finally:
            await client.close()

    async def test_upload_success_event(self):
        client = Cyberette(api_key="test_key")
        try:
            mock_listener = AsyncMock()

            @client.on("upload_success")
            async def listener(file_path, response):
                await mock_listener(file_path, response)

            await client.events.emit("upload_success", file_path="test.png", response={"id": 1})

            mock_listener.assert_awaited_once_with("test.png", {"id": 1})
        finally:
            await client.close()

    async def test_upload_error_event(self):
        client = Cyberette(api_key="test_key")
        try:
            mock_listener = AsyncMock()

            @client.on("upload_error")
            async def listener(file_path, error):
                await mock_listener(file_path, error)

            test_error = Exception("test")
            await client.events.emit("upload_error", file_path="test.png", error=test_error)

            mock_listener.assert_awaited_once_with("test.png", test_error)
        finally:
            await client.close()

    async def test_multiple_listeners(self):
        client = Cyberette(api_key="test_key")
        try:
            mock1 = AsyncMock()
            mock2 = AsyncMock()

            @client.on("upload_started")
            async def listener1(file_path):
                await mock1(file_path)

            @client.on("upload_started")
            async def listener2(file_path):
                await mock2(file_path)

            await client.events.emit("upload_started", file_path="test.png")

            mock1.assert_awaited_once_with("test.png")
            mock2.assert_awaited_once_with("test.png")
        finally:
            await client.close()

@pytest.mark.asyncio
class TestDirectEventSystem:
    """Tests for Cyberette SDK direct-style events."""

    async def test_direct_event_listener_called(self):
        """Test that a direct-style listener is called when event is emitted."""
        client = Cyberette(api_key="test_key")
        try:
            mock_listener = AsyncMock()
            
            # Register listener using direct style
            client.on("upload_started", mock_listener)

            # Emit event manually
            await client.events.emit("upload_started", file_path="test.png")

            mock_listener.assert_awaited_once_with(file_path="test.png")
        finally:
            await client.close()

    async def test_multiple_direct_listeners_called(self):
        """Test that multiple direct-style listeners are all called."""
        client = Cyberette(api_key="test_key")
        try:
            listener1 = AsyncMock()
            listener2 = AsyncMock()

            client.on("upload_started", listener1)
            client.on("upload_started", listener2)

            await client.events.emit("upload_started", file_path="test.png")

            listener1.assert_awaited_once_with(file_path="test.png")
            listener2.assert_awaited_once_with(file_path="test.png")
        finally:
            await client.close()

    async def test_direct_listener_removed(self):
        """Test that removing a listener prevents it from being called."""
        client = Cyberette(api_key="test_key")
        try:
            listener = AsyncMock()
            client.on("upload_started", listener)

            # Remove listener manually
            client.events._events["upload_started"].remove(listener)

            await client.events.emit("upload_started", file_path="test.png")

            listener.assert_not_awaited()
        finally:
            await client.close()

    async def test_event_with_no_listeners_direct(self):
        """Emitting an event with no listeners does not raise errors."""
        client = Cyberette(api_key="test_key")
        try:
            # Should not raise any exception
            await client.events.emit("nonexistent_event", data=123)
        finally:
            await client.close()

    async def test_listener_exception_handling_direct(self):
        """Exceptions in one direct listener do not prevent others from running."""
        client = Cyberette(api_key="test_key")
        try:
            listener1 = AsyncMock(side_effect=Exception("Listener error"))
            listener2 = AsyncMock()

            client.on("upload_started", listener1)
            client.on("upload_started", listener2)

            # Emitting should still call listener2
            await client.events.emit("upload_started", file_path="test.png")

            listener2.assert_awaited_once_with(file_path="test.png")
        finally:
            await client.close()