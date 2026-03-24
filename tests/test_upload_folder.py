import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from cyberette_sdk.client import Cyberette
import os

@pytest.mark.asyncio
class TestUploadFolder:
    async def test_upload_folder_uploads_all_files(self, tmp_path):
        # Create dummy files in a temp directory
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("data1")
        file2.write_text("data2")
        files = {str(file1), str(file2)}

        client = Cyberette(api_key="test_key")
        try:
            # Patch upload to just return the file path for verification (simulate a simple result)
            with patch.object(client, "upload", new=AsyncMock(side_effect=lambda fp: f"uploaded:{fp}")) as mock_upload:
                results = await client.upload_folder(str(tmp_path), concurrency=2)
                uploaded_files = {r["file"] for r in results}
                assert uploaded_files == files
                assert all(r["result"] == f"uploaded:{r['file']}" for r in results)
                assert all(r["error"] is None for r in results)
                assert mock_upload.await_count == 2
        finally:
            await client.close()

    async def test_upload_folder_empty_dir_raises(self, tmp_path):
        client = Cyberette(api_key="test_key")
        try:
            with pytest.raises(ValueError, match="No files found in directory"):
                await client.upload_folder(str(tmp_path))
        finally:
            await client.close()

    async def test_upload_folder_nonexistent_dir_raises(self):
        client = Cyberette(api_key="test_key")
        try:
            with pytest.raises(ValueError, match="Provided path is not a directory"):
                await client.upload_folder("not_a_real_dir")
        finally:
            await client.close()
