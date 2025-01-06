from typing import Tuple, Type
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class PlaywrightSetting(BaseModel):
    headless: bool


class XlwingsSetting(BaseModel):
    visible: bool


class DenbunSetting(BaseModel):
    username: str
    password: str
    url: str
    session_timeout: int


class SurrealDBSetting(BaseModel):
    url: str
    namespace: str
    database: str
    username: str
    password: str


class GoogleSheetSetting(BaseModel):
    ssl_certificate_validation: bool
    credentials_path: str
    spreadsheet_key: str


class Settings(BaseSettings):
    denbun: DenbunSetting
    playwright: PlaywrightSetting
    xlwings: XlwingsSetting
    surrealdb: SurrealDBSetting
    google_sheet: GoogleSheetSetting
    model_config = SettingsConfigDict(
        yaml_file="settings.yaml",
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
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
        return (env_settings, dotenv_settings, YamlConfigSettingsSource(settings_cls))


if __name__ == "__main__":
    settings = Settings()
    print(settings)
