from fba_mcp_server.config import McpServerSettings


def test_mcp_settings_have_safe_defaults() -> None:
    settings = McpServerSettings()

    assert settings.app_env == "local"
    assert settings.log_level == "INFO"
    assert settings.backend_base_url == "http://backend:8000"
