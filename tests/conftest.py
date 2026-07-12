import pytest
from oort.config import settings
@pytest.fixture(autouse=True)
def setup_oort_config():
    settings.s3_bucket = "test-bucket"
    settings.s3_access_key = "test-key"
    settings.s3_secret_key = "test-secret"
    settings.s3_region = "us-east-1"
    yield settings
