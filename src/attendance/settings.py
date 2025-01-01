"""
アプリケーションの設定モジュール
"""

import os
from pathlib import Path
from typing import Tuple, Type

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, YamlConfigSettingsSource


class Settings(BaseSettings):
    """
    アプリケーションの設定クラス
    """
    model_config = SettingsConfigDict(
        env_file=".env", 
        yaml_file="settings.yaml", 
        env_file_encoding="utf-8",
        extra="ignore"  
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls), dotenv_settings)