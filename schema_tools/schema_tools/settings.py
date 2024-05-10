from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource


class Settings(BaseSettings):
    model_config = SettingsConfigDict(yaml_file='config.yml')

    out_dir: str
    layout_name: str = 'layout'
    classes_file_name: str
    enums_file_name: str

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (init_settings, env_settings, dotenv_settings,
                file_secret_settings, YamlConfigSettingsSource(settings_cls), )
