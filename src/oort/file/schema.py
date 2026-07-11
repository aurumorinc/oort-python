from typing import Optional
from pydantic import BaseModel, Field


class S3Config(BaseModel):
    """Configuration for S3 integration."""

    bucket: str = Field(..., description="The name of the S3 bucket.")
    access_key: str = Field(..., description="AWS Access Key ID.")
    secret_key: str = Field(..., description="AWS Secret Access Key.")
    endpoint_url: Optional[str] = Field(
        None, description="Optional custom endpoint URL (e.g., for MinIO or GCS)."
    )
    region: str = Field("us-east-1", description="AWS Region.")
    expires_in: int = Field(
        3600, description="Default expiration time for presigned URLs in seconds."
    )
    path_style: bool = Field(
        False,
        description="Whether to use path-style addressing (required for some S3-compatible APIs).",
    )


__all__ = ["S3Config"]
