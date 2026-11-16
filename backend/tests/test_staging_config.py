import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.main import create_app


def staging_settings(**overrides):
    values = {
        "environment": "staging",
        "database_url": "postgresql+psycopg://eduops_runtime:synthetic@db/eduops360",
        "cors_origins": [],
        "allowed_hosts": ["staging.example.test"],
        "preview_access_key": "synthetic-preview-key-longer-than-32-characters",
        "_env_file": None,
    }
    return Settings(**(values | overrides))


def test_staging_accepts_explicit_isolated_configuration():
    assert staging_settings().environment == "staging"


def test_preview_auth_gate_protects_ui_and_api_but_not_health():
    app = create_app(staging_settings())
    with TestClient(app, base_url="https://staging.example.test") as client:
        assert client.get("/api/v1/health/live").status_code == 200
        for path in ("/", "/users", "/api/v1/auth/me", "/api/docs"):
            denied = client.get(path)
            assert denied.status_code == 401
            assert denied.headers["www-authenticate"].startswith("Basic")
        assert client.get("/api/v1/auth/me", auth=("preview", "wrong-key")).status_code == 401
        accepted = client.get(
            "/api/v1/auth/me", auth=("preview", "synthetic-preview-key-longer-than-32-characters")
        )
        assert accepted.status_code == 401
        assert accepted.json()["error"]["code"] == "AUTH_REQUIRED"
        assert "synthetic-preview-key" not in accepted.text


def test_compiled_frontend_handles_deep_links_without_masking_api_or_asset_errors(tmp_path):
    (tmp_path / "index.html").write_text("<html>synthetic SPA</html>")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "bundle.js").write_text("// synthetic asset")
    app = create_app(Settings(environment="test", frontend_directory=tmp_path, _env_file=None))
    with TestClient(app) as client:
        assert "synthetic SPA" in client.get("/users").text
        assert client.get("/assets/bundle.js").status_code == 200
        assert client.get("/assets/missing.js").status_code == 404
        missing = client.get("/api/v1/missing")
        assert missing.status_code == 404
        assert missing.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.parametrize(
    "overrides",
    [
        {"database_url": None},
        {"database_url": "postgresql+psycopg://postgres:synthetic@db/eduops360"},
        {"session_cookie_secure": False},
        {"allowed_hosts": []},
        {"allowed_hosts": ["*"]},
        {"allowed_hosts": ["https://staging.example.test"]},
        {"cors_origins": ["http://localhost:5173"]},
        {"preview_access_key": None},
        {"preview_access_key": "short"},
    ],
)
def test_staging_rejects_incomplete_or_insecure_configuration(overrides):
    with pytest.raises(ValidationError):
        staging_settings(**overrides)


def test_staging_denies_unknown_host_and_spoofed_forwarded_host():
    app = create_app(staging_settings())
    with TestClient(app, base_url="https://staging.example.test") as client:
        assert client.get("/api/v1/health/live").status_code == 200
        assert (
            client.get("/api/v1/health/live", headers={"Host": "attacker.invalid"}).status_code
            == 400
        )
        assert (
            client.get(
                "/api/v1/health/live",
                headers={"Host": "attacker.invalid", "X-Forwarded-Host": "staging.example.test"},
            ).status_code
            == 400
        )
