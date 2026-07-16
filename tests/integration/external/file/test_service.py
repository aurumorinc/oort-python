import pytest
import os
import requests
import vcr
from dotenv import load_dotenv

from oort.file.schema import S3Config
from oort.file.service import upload, generate_presigned_url, aupload, agenerate_presigned_url

load_dotenv()

s3_bucket = os.getenv("S3_BUCKET", "dummy-bucket")
s3_access_key = os.getenv("S3_ACCESS_KEY", "dummy-key")
s3_secret_key = os.getenv("S3_SECRET_KEY", "dummy-secret")
s3_region = os.getenv("S3_REGION", "us-east-1")
s3_endpoint_url = os.getenv("S3_ENDPOINT_URL")

my_vcr = vcr.VCR(
    cassette_library_dir="tests/integration/external/file/cassettes",
    record_mode="once",
    filter_headers=["Authorization"],
    filter_query_parameters=["X-Amz-Credential", "X-Amz-Signature", "AWSAccessKeyId", "Signature", "X-Amz-Date", "Expires"],
    match_on=["method", "scheme", "host", "port", "path"]
)

@pytest.fixture
def external_s3_config():
    # If the cassette exists, we can run even with dummy credentials
    return S3Config(
        bucket=s3_bucket,
        access_key=s3_access_key,
        secret_key=s3_secret_key,
        region=s3_region,
        endpoint_url=s3_endpoint_url
    )

@my_vcr.use_cassette("test_external_s3_upload_sync.yaml")
def test_external_s3_upload_and_presign_sync(external_s3_config):
    object_name = "integration-sync-test-fixture.txt"
    data = b"hello from external sync test"
    mimetype = "text/plain"

    # Upload
    upload(data, object_name, mimetype, external_s3_config)

    # Generate URL
    url = generate_presigned_url(object_name, external_s3_config)
    assert url is not None
    assert url.startswith("http")

    # Fetch and verify
    response = requests.get(url)
    response.raise_for_status()
    assert response.content == data

@pytest.mark.asyncio
@my_vcr.use_cassette("test_external_s3_upload_async.yaml")
async def test_external_s3_upload_and_presign_async(external_s3_config):
    object_name = "integration-async-test-fixture.txt"
    data = b"hello from external async test"
    mimetype = "text/plain"

    # Upload
    await aupload(data, object_name, mimetype, external_s3_config)

    # Generate URL
    url = await agenerate_presigned_url(object_name, external_s3_config)
    assert url is not None
    assert url.startswith("http")

    # Fetch and verify
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        assert response.content == data
