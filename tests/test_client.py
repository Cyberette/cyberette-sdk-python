"""Unit tests for cyberette_sdk.client.Cyberette."""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from cyberette_sdk.client import Cyberette


@pytest.mark.asyncio
class TestUpload:
    """Tests for file upload through API gateway."""

    async def test_upload_image(self):
        """Test uploading an image file through the API gateway endpoint."""
        client = Cyberette(api_key="test_key")
        try:
            with patch("builtins.open", create=True):
                with patch.object(client.session, "post") as mock_post:
                    mock_response = AsyncMock()
                    mock_response.status = 200
                    mock_response.json = AsyncMock(return_value={"id": "123", "deepfake": False})
                    mock_response.raise_for_status = Mock()
                    mock_post.return_value.__aenter__.return_value = mock_response
                    
                    result = await client.upload("testing_data\\photo.png")
                    
                    # Verify endpoint called with gateway URL
                    call_args = mock_post.call_args
                    assert call_args[0][0] == client.base_url_api_gateway
                    assert call_args[1]["headers"]["cyberette-api-key"] == "test_key"
                    assert result == {"id": "123", "deepfake": False}
        finally:
            await client.close()

    async def test_upload_audio(self):
        """Test uploading an audio file through the API gateway endpoint."""
        client = Cyberette(api_key="test_key")
        try:
            with patch("builtins.open", create=True):
                with patch.object(client.session, "post") as mock_post:
                    mock_response = AsyncMock()
                    mock_response.status = 200
                    mock_response.json = AsyncMock(return_value={"id": "456", "deepfake": True})
                    mock_response.raise_for_status = Mock()
                    mock_post.return_value.__aenter__.return_value = mock_response
                    
                    result = await client.upload("testing_data\\song.mp3")
                    
                    # Verify endpoint called with gateway URL
                    call_args = mock_post.call_args
                    assert call_args[0][0] == client.base_url_api_gateway
                    assert call_args[1]["headers"]["cyberette-api-key"] == "test_key"
                    assert result == {"id": "456", "deepfake": True}
        finally:
            await client.close()

    async def test_upload_video_uses_gateway(self):
        """Test uploading a video file uses gateway endpoint."""
        client = Cyberette(api_key="test_key")
        try:
            with patch("builtins.open", create=True):
                with patch.object(client.session, "post") as mock_post:
                    mock_response = AsyncMock()
                    mock_response.status = 200
                    mock_response.json = AsyncMock(return_value={"id": "789"})
                    mock_response.raise_for_status = Mock()
                    mock_post.return_value.__aenter__.return_value = mock_response

                    result = await client.upload("testing_data\\movie.mp4")

                    call_args = mock_post.call_args
                    assert call_args[0][0] == client.base_url_api_gateway
                    assert call_args[1]["headers"]["cyberette-api-key"] == "test_key"
                    assert result == {"id": "789"}
        finally:
            await client.close()

    async def test_upload_file_not_found(self):
        """Test uploading a non-existent file raises FileNotFoundError."""
        client = Cyberette(api_key="test_key")
        try:
            with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
                with pytest.raises(FileNotFoundError):
                    await client.upload("testing_data\\nonexistent.png")
        finally:
            await client.close()

    async def test_upload_network_error(self):
        """Test network errors during upload are caught and raised."""
        import aiohttp
        client = Cyberette(api_key="test_key")
        try:
            with patch("builtins.open", create=True):
                with patch.object(client.session, "post") as mock_post:
                    mock_post.side_effect = aiohttp.ClientError("Connection failed")
                    
                    with pytest.raises(Exception, match="Network error"):
                        await client.upload("testing_data\\photo.png")
        finally:
            await client.close()


@pytest.mark.asyncio
class TestSession:
    """Tests for session management."""

    async def test_session_created_on_init(self):
        """Test that aiohttp session is created on __init__."""
        client = Cyberette(api_key="test_key")
        try:
            assert client.session is not None
        finally:
            await client.close()

    async def test_close_closes_session(self):
        """Test that close() closes the session."""
        client = Cyberette(api_key="test_key")
        await client.close()
        # Verify session is closed (calling it again should not error)
        await client.close()


class TestCustomURLs:
    """Tests for custom API gateway URL."""

    def test_custom_gateway_url(self):
        async def run_test():
            custom_gateway = "https://custom-gateway-api.com/upload"
            
            custom_client = Cyberette(
                api_key="test_key",
                base_url_api_gateway=custom_gateway,
            )
            
            try:
                assert custom_client.base_url_api_gateway == custom_gateway
            finally:
                await custom_client.close()
        
        asyncio.run(run_test())
