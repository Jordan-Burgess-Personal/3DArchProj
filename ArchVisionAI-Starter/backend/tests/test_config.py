from app.config import settings


def test_application_settings_load():
    assert settings.app_name
    assert settings.app_version
    assert settings.backend_port > 0
    assert settings.database_url.startswith("postgresql://")


def test_cors_origins_are_loaded_as_list():
    assert isinstance(settings.cors_origins, list)
    assert len(settings.cors_origins) > 0
    assert "http://localhost:5173" in settings.cors_origins