import pytest
import os
from unittest.mock import patch
from oort.file.main import File


def test_file_create_empty():
    f = File.create_empty("test.txt", touch=True)
    assert os.path.exists(f.path)
    assert f.filename == "test.txt"
    f.cleanup()
    assert not os.path.exists(f.path)


def test_file_from_bytes():
    f = File.from_bytes(b"hello", "hello.txt")
    assert f.bytes == b"hello"
    f.cleanup()


@patch("oort.file.main.upload")
@patch("oort.file.main.generate_presigned_url")
def test_file_presigned_url_sync(mock_gen, mock_upload):
    mock_gen.return_value = "https://example.com/url"

    f = File.from_bytes(b"hello", "hello.txt")
    url = f.presigned_url
    assert url == "https://example.com/url"
    mock_upload.assert_called_once()
    mock_gen.assert_called_once()
    f.cleanup()


@patch("oort.file.main.aupload")
@patch("oort.file.main.agenerate_presigned_url")
@pytest.mark.asyncio
async def test_file_aget_presigned_url(mock_gen, mock_upload):
    mock_gen.return_value = "https://example.com/url"

    f = File.from_bytes(b"hello", "hello.txt")
    url = await f.aget_presigned_url()
    assert url == "https://example.com/url"
    mock_upload.assert_called_once()
    mock_gen.assert_called_once()
    f.cleanup()

@pytest.mark.asyncio
async def test_file_afrom_playwright_download():
    class MockDownload:
        def __init__(self):
            self.suggested_filename = "downloaded.txt"
        async def save_as(self, path):
            with open(path, "w") as f:
                f.write("mock download content")
    
    download = MockDownload()
    f = await File.afrom_playwright_download(download)
    assert os.path.exists(f.path)
    assert f.filename == "downloaded.txt"
    assert f.bytes == b"mock download content"
    f.cleanup()
