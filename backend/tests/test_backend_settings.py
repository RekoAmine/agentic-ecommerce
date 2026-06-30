from fba_advisor.config import BackendSettings


def test_backend_settings_have_safe_defaults() -> None:
    settings = BackendSettings()

    assert settings.app_env == "local"
    assert settings.log_level == "INFO"
    assert settings.database_url.startswith("postgresql://")
