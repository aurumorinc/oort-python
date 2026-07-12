import pytest
import boto3
from moto import mock_aws

from oort.file.schema import S3Config
from oort.file.main import File


@pytest.fixture(autouse=True)
def setup_moto():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")

        s3_config = S3Config(
            bucket="test-bucket",
            access_key="fake-key",
            secret_key="fake-secret",
            region="us-east-1",
        )
        # Mock settings for integration test
        from oort.config import settings

        settings.s3_bucket = "test-bucket"
        settings.s3_access_key = "fake-key"
        settings.s3_secret_key = "fake-secret"
        settings.s3_region = "us-east-1"
        yield


def test_file_integration_sync():
    """Test file presigned URL generation and upload via File wrapper (sync context)"""
    f = File.from_bytes(b"hello world", "integration.txt", "text/plain")
    url = f.presigned_url

    assert url is not None
    assert "https://s3.amazonaws.com/test-bucket/" in url or "test-bucket" in url

    # We can verify it's in moto
    client = boto3.client("s3", region_name="us-east-1")
    obj = client.get_object(Bucket="test-bucket", Key=f._object_name)
    assert obj["Body"].read() == b"hello world"

    f.cleanup()


@pytest.mark.asyncio
async def test_file_integration_async():
    """Test file presigned URL generation and upload via File wrapper (async context)"""
    f = File.from_bytes(b"hello world async", "integration_async.txt", "text/plain")
    url = await f.get_presigned_url_async()

    assert url is not None
    assert "https://s3.amazonaws.com/test-bucket/" in url or "test-bucket" in url

    # We can verify it's in moto
    client = boto3.client("s3", region_name="us-east-1")
    obj = client.get_object(Bucket="test-bucket", Key=f._object_name)
    assert obj["Body"].read() == b"hello world async"

    f.cleanup()
