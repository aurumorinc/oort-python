from oort.config import OortSettings
from oort.file.schema import S3Config


import os
from unittest.mock import patch


@patch.dict(os.environ, {}, clear=True)
def test_oort_settings_s3_property_valid():
    """Test that the s3 property returns a valid S3Config when required fields are present."""
    settings = OortSettings(
        s3_bucket="my-bucket",
        s3_access_key="my-access",
        s3_secret_key="my-secret",
        s3_region="us-west-2",
        s3_path_style=True,
    )

    s3_config = settings.s3
    assert isinstance(s3_config, S3Config)
    assert s3_config.bucket == "my-bucket"
    assert s3_config.access_key == "my-access"
    assert s3_config.secret_key == "my-secret"
    assert s3_config.region == "us-west-2"
    assert s3_config.path_style is True
    assert s3_config.expires_in == 3600  # Default value
    assert s3_config.endpoint_url is None


@patch.dict(os.environ, {}, clear=True)
def test_oort_settings_s3_property_missing_bucket():
    """Test that the s3 property returns None if bucket is missing."""
    settings = OortSettings(
        s3_access_key="my-access",
        s3_secret_key="my-secret",
    )
    assert settings.s3 is None


@patch.dict(os.environ, {}, clear=True)
def test_oort_settings_s3_property_missing_access_key():
    """Test that the s3 property returns None if access_key is missing."""
    settings = OortSettings(
        s3_bucket="my-bucket",
        s3_secret_key="my-secret",
    )
    assert settings.s3 is None


@patch.dict(os.environ, {}, clear=True)
def test_oort_settings_s3_property_missing_secret_key():
    """Test that the s3 property returns None if secret_key is missing."""
    settings = OortSettings(
        s3_bucket="my-bucket",
        s3_access_key="my-access",
    )
    assert settings.s3 is None


@patch.dict(os.environ, {}, clear=True)
def test_oort_settings_s3_property_all_missing():
    """Test that the s3 property returns None if all required fields are missing."""
    settings = OortSettings()
    assert settings.s3 is None
