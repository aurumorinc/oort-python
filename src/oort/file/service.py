import asyncio
from typing import Any, Dict, Optional, Union
import boto3
from botocore.config import Config

from oort.exceptions import S3ConfigurationError
from oort.file.schema import S3Config

_s3_client: Optional[Any] = None


def _get_client(config: S3Config) -> Any:
    """Internal helper to lazily instantiate and cache the boto3 S3 client."""
    global _s3_client
    if _s3_client is not None:
        return _s3_client

    endpoint_url = config.endpoint_url
    sig_version = "s3" if endpoint_url and "googleapis.com" in endpoint_url else "s3v4"

    config_kwargs: Dict[str, Any] = {"signature_version": sig_version}
    if config.path_style:
        config_kwargs["s3"] = {"addressing_style": "path"}

    client_kwargs: Dict[str, Any] = {
        "service_name": "s3",
        "aws_access_key_id": config.access_key,
        "aws_secret_access_key": config.secret_key,
        "config": Config(**config_kwargs),
    }

    if endpoint_url:
        client_kwargs["endpoint_url"] = endpoint_url
    if sig_version == "s3v4":
        client_kwargs["region_name"] = config.region

    try:
        session = boto3.Session()
        _s3_client = session.client(**client_kwargs)
        return _s3_client
    except Exception as e:
        raise S3ConfigurationError(f"Failed to initialize S3 client: {e}") from e


def upload(
    data: Union[bytes, str], object_name: str, mimetype: str, config: S3Config
) -> None:
    client = _get_client(config)
    try:
        if isinstance(data, str):
            # Treat as file path
            client.upload_file(
                data, config.bucket, object_name, ExtraArgs={"ContentType": mimetype}
            )
        else:
            # Treat as bytes
            client.put_object(
                Bucket=config.bucket, Key=object_name, Body=data, ContentType=mimetype
            )
    except Exception as e:
        raise S3ConfigurationError(f"Failed to upload object {object_name}: {e}") from e


def generate_presigned_url(
    object_name: str, config: S3Config, expires_in: Optional[int] = None
) -> str:
    client = _get_client(config)
    expiration = expires_in if expires_in is not None else config.expires_in
    try:
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": config.bucket, "Key": object_name},
            ExpiresIn=expiration,
        )
        return str(url)
    except Exception as e:
        raise S3ConfigurationError(
            f"Failed to generate presigned URL for {object_name}: {e}"
        ) from e


async def aupload(
    data: Union[bytes, str], object_name: str, mimetype: str, config: S3Config
) -> None:
    """Asynchronously uploads data or a file path to S3."""
    await asyncio.to_thread(upload, data, object_name, mimetype, config)


async def agenerate_presigned_url(
    object_name: str, config: S3Config, expires_in: Optional[int] = None
) -> str:
    """Asynchronously generates a presigned URL for an S3 object."""
    return await asyncio.to_thread(
        generate_presigned_url, object_name, config, expires_in
    )


__all__ = ["upload", "generate_presigned_url", "aupload", "agenerate_presigned_url"]
