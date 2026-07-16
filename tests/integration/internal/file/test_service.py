import pytest
import boto3
from moto import mock_aws

from oort.file.main import File


import os
from unittest.mock import patch


@pytest.fixture(autouse=True)
def setup_moto():
    import oort.file.service
    oort.file.service._s3_client = None

    with patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "testing",
        "AWS_SECRET_ACCESS_KEY": "testing",
        "AWS_SECURITY_TOKEN": "testing",
        "AWS_SESSION_TOKEN": "testing",
        "AWS_DEFAULT_REGION": "us-east-1"
    }, clear=True):
        with mock_aws():
            client = boto3.client("s3", region_name="us-east-1")
            client.create_bucket(Bucket="test-bucket")

            # Mock settings for integration test
            from oort.config import settings

            settings.s3_bucket = "test-bucket"
            settings.s3_access_key = "testing"
            settings.s3_secret_key = "testing"
            settings.s3_region = "us-east-1"
            
            yield
            
            oort.file.service._s3_client = None


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
    url = await f.aget_presigned_url()

    assert url is not None
    assert "https://s3.amazonaws.com/test-bucket/" in url or "test-bucket" in url

    # We can verify it's in moto
    client = boto3.client("s3", region_name="us-east-1")
    obj = client.get_object(Bucket="test-bucket", Key=f._object_name)
    assert obj["Body"].read() == b"hello world async"

    f.cleanup()
