import pytest
from unittest.mock import patch, MagicMock
from oort.file.service import upload, generate_presigned_url
from oort.file.schema import S3Config


@pytest.fixture
def s3_config():
    return S3Config(
        bucket="test-bucket",
        access_key="fake-key",
        secret_key="fake-secret",
        region="us-east-1",
    )


@patch("oort.file.service._s3_client", None)
@patch("oort.file.service.boto3.Session", spec=True)
@pytest.mark.asyncio
async def test_upload_bytes(mock_session_cls, s3_config):
    mock_session = MagicMock()
    mock_client = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session

    data = b"hello"
    await upload(data, "test.txt", "text/plain", s3_config)

    mock_client.put_object.assert_called_once_with(
        Bucket="test-bucket", Key="test.txt", Body=b"hello", ContentType="text/plain"
    )


@patch("oort.file.service._s3_client", None)
@patch("oort.file.service.boto3.Session", spec=True)
@pytest.mark.asyncio
async def test_upload_file_path(mock_session_cls, s3_config):
    mock_session = MagicMock()
    mock_client = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session

    import tempfile
    import os

    fd, path = tempfile.mkstemp()
    os.close(fd)

    try:
        await upload(path, "test.txt", "text/plain", s3_config)
        mock_client.upload_file.assert_called_once_with(
            path, "test-bucket", "test.txt", ExtraArgs={"ContentType": "text/plain"}
        )
    finally:
        os.remove(path)


@patch("oort.file.service._s3_client", None)
@patch("oort.file.service.boto3.Session", spec=True)
@pytest.mark.asyncio
async def test_generate_presigned_url(mock_session_cls, s3_config):
    mock_session = MagicMock()
    mock_client = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session

    mock_client.generate_presigned_url.return_value = "https://example.com"

    url = await generate_presigned_url("test.txt", s3_config)
    assert url == "https://example.com"

    mock_client.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={"Bucket": "test-bucket", "Key": "test.txt"},
        ExpiresIn=3600,
    )
