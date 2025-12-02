"""Unit tests for cyberette_sdk.client.Cyberette."""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from cyberette_sdk.client import Cyberette


class TestClassifyFile:
    """Tests for file classification based on mime type."""

    def test_classify_image(self):
        async def run_test():
            client = Cyberette(api_key="test_key")
            try:
                assert client.classify_file("testing_data\\photo.png") == "image"
                assert client.classify_file("testing_data\\photo.jpg") == "image"
            finally:
                await client.close()
        asyncio.run(run_test())

    def test_classify_video(self):
        async def run_test():
            client = Cyberette(api_key="test_key")
            try:
                assert client.classify_file("testing_data\\movie.mp4") == "video"
                assert client.classify_file("testing_data\\movie.avi") == "video"
            finally:
                await client.close()
        asyncio.run(run_test())

    def test_classify_audio(self):
        async def run_test():
            client = Cyberette(api_key="test_key")
            try:
                assert client.classify_file("testing_data\\song.mp3") == "audio"
                assert client.classify_file("testing_data\\song.wav") == "audio"
            finally:
                await client.close()
        asyncio.run(run_test())

    def test_classify_unsupported(self):
        async def run_test():
            client = Cyberette(api_key="test_key")
            try:
                assert client.classify_file("testing_data\\document.txt") is None
                assert client.classify_file("testing_data\\file.pdf") is None
            finally:
                await client.close()
        asyncio.run(run_test())


@pytest.mark.asyncio
class TestUpload:
    """Tests for file upload to appropriate endpoints."""

    async def test_upload_image(self):
        """Test uploading an image file to the image endpoint."""
        client = Cyberette(api_key="test_key")
        try:
            with patch("builtins.open", create=True):
                with patch.object(client.session, "post") as mock_post:
                    mock_response = AsyncMock()
                    mock_response.json = AsyncMock(return_value={"id": "123", "deepfake": False})
                    mock_response.raise_for_status = Mock()
                    mock_post.return_value.__aenter__.return_value = mock_response
                    
                    result = await client.upload("testing_data\\photo.png")
                    
                    # Verify endpoint called with correct URL
                    call_args = mock_post.call_args
                    assert "api-image-dev-neu-002" in call_args[0][0]
                    assert result == {"id": "123", "deepfake": False}
        finally:
            await client.close()

    async def test_upload_audio(self):
        """Test uploading an audio file to the audio endpoint."""
        client = Cyberette(api_key="test_key")
        try:
            with patch("builtins.open", create=True):
                with patch.object(client.session, "post") as mock_post:
                    mock_response = AsyncMock()
                    mock_response.json = AsyncMock(return_value={"id": "456", "deepfake": True})
                    mock_response.raise_for_status = Mock()
                    mock_post.return_value.__aenter__.return_value = mock_response
                    
                    result = await client.upload("testing_data\\song.mp3")
                    
                    # Verify endpoint called with correct URL
                    call_args = mock_post.call_args
                    assert "api-audio-dev-neu-002" in call_args[0][0]
                    assert result == {"id": "456", "deepfake": True}
        finally:
            await client.close()

    async def test_upload_video_without_audio(self):
        """Test uploading a video without audio track."""
        client = Cyberette(api_key="test_key")
        try:
            with patch("builtins.open", create=True):
                with patch.object(client, "has_audio", return_value=False):
                    with patch.object(client.session, "post") as mock_post:
                        mock_response = AsyncMock()
                        mock_response.json = AsyncMock(return_value={"id": "789"})
                        mock_response.raise_for_status = Mock()
                        mock_post.return_value.__aenter__.return_value = mock_response
                        
                        result = await client.upload("testing_data\\movie.mp4")
                        
                        # Should use base_url_video (not base_url_video_audio)
                        call_args = mock_post.call_args
                        assert "localhost:5300/api/video" in call_args[0][0]
                        assert "video_and_audio" not in call_args[0][0]
        finally:
            await client.close()

    async def test_upload_video_with_audio(self):
        """Test uploading a video with audio track."""
        client = Cyberette(api_key="test_key")
        try:
            with patch("builtins.open", create=True):
                with patch.object(client, "has_audio", return_value=True):
                    with patch.object(client.session, "post") as mock_post:
                        mock_response = AsyncMock()
                        mock_response.json = AsyncMock(return_value={"id": "999"})
                        mock_response.raise_for_status = Mock()
                        mock_post.return_value.__aenter__.return_value = mock_response
                        
                        result = await client.upload("testing_data\\movie.mp4")
                        
                        # Should use base_url_video_audio
                        call_args = mock_post.call_args
                        assert "localhost:5300/api/video_and_audio" in call_args[0][0]
        finally:
            await client.close()

    async def test_upload_unsupported_file(self):
        """Test uploading an unsupported file type raises ValueError."""
        client = Cyberette(api_key="test_key")
        try:
            with pytest.raises(ValueError, match="Unsupported file type"):
                await client.upload("testing_data\\document.txt")
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
    """Tests for custom endpoint URLs."""

    def test_custom_urls(self):
        async def run_test():
            custom_image = "https://custom-image-api.com/upload"
            custom_video = "https://custom-video-api.com/upload"
            custom_audio = "https://custom-audio-api.com/upload"
            custom_video_audio = "https://custom-video-audio-api.com/upload"
            
            custom_client = Cyberette(
                api_key="test_key",
                base_url_image=custom_image,
                base_url_video=custom_video,
                base_url_audio=custom_audio,
                base_url_video_audio=custom_video_audio,
            )
            
            try:
                assert custom_client.base_url_image == custom_image
                assert custom_client.base_url_video == custom_video
                assert custom_client.base_url_audio == custom_audio
                assert custom_client.base_url_video_audio == custom_video_audio
            finally:
                await custom_client.close()
        
        asyncio.run(run_test())
