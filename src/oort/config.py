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

    s3: Optional[S3Config] = Field(
        None, description="Configuration for S3 integration used by oort.file."
    )


settings = OortSettings()


__all__ = ["OortSettings", "settings"]
