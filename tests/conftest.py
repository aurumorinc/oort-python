import pytest
from oort.config import settings
from oort.file.schema import S3Config


@pytest.fixture(autouse=True)
def setup_oort_config():
    s3_config = S3Config(
        bucket="test-bucket",
        access_key="test-key",
        secret_key="test-secret",
        region="us-east-1",
    )
    settings.s3 = s3_config
    yield settings
