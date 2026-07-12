# src/oort/config.py
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from worldline.config import WorldlineSettings

from oort.file.schema import S3Config


class OortSettings(WorldlineSettings, BaseSettings):
    """
    Configuration for the oort package.
    Inherits from worldline.config.WorldlineSettings and pydantic_settings.BaseSettings
    as per the architectural blueprint.
    """

    s3_bucket: Optional[str] = Field(None, description="The name of the S3 bucket.")
    s3_access_key: Optional[str] = Field(None, description="AWS Access Key ID.")
    s3_secret_key: Optional[str] = Field(None, description="AWS Secret Access Key.")
    s3_endpoint_url: Optional[str] = Field(
        None, description="Optional custom endpoint URL (e.g., for MinIO or GCS)."
    )
    s3_region: str = Field("us-east-1", description="AWS Region.")
    s3_expires_in: int = Field(
        3600, description="Default expiration time for presigned URLs in seconds."
    )
    s3_path_style: bool = Field(
        False, description="Whether to use path-style addressing."
    )

    @property
    def s3(self) -> Optional[S3Config]:
        if not self.s3_bucket or not self.s3_access_key or not self.s3_secret_key:
            return None
        return S3Config(
            bucket=self.s3_bucket,
            access_key=self.s3_access_key,
            secret_key=self.s3_secret_key,
            endpoint_url=self.s3_endpoint_url,
            region=self.s3_region,
            expires_in=self.s3_expires_in,
            path_style=self.s3_path_style,
        )


settings = OortSettings()


__all__ = ["OortSettings", "settings"]
