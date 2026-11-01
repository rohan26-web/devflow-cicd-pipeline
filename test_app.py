import pytest

import app as app_module
from app import PROJECT_NAME, app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


# ---------- Home ----------
def test_home_returns_200_and_json(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.is_json


def test_home_json_structure(client):
    data = client.get("/").get_json()
    assert data["project"] == PROJECT_NAME
    assert "message" in data
    assert data["version"] == "1.0.0"


# ---------- Health ----------
def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_json_structure(client):
    data = client.get("/health").get_json()
    assert data == {
        "project": PROJECT_NAME,
        "status": "healthy",
        "version": "1.0.0",
    }


# ---------- Version ----------
def test_version_default_values(client, monkeypatch):
    monkeypatch.delenv("APP_VERSION", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    data = client.get("/version").get_json()
    assert data == {"version": "1.0.0", "environment": "development"}


def test_version_uses_environment_variables(client, monkeypatch):
    monkeypatch.setenv("APP_VERSION", "2.5.1")
    monkeypatch.setenv("APP_ENV", "production")
    data = client.get("/version").get_json()
    assert data == {"version": "2.5.1", "environment": "production"}


# ---------- Invalid routes and unexpected input ----------
def test_unknown_route_returns_json_404(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["error"] == "Not Found"


@pytest.mark.parametrize(
    "path",
    [
        "/health/extra",
        "/VERSION",
        "/%00",
        "/" + "a" * 2000,
        "/<script>alert(1)</script>",
        "/../etc/passwd",
    ],
)
def test_unexpected_paths_return_404_not_500(client, path):
    response = client.get(path)
    assert response.status_code == 404
    assert response.is_json


@pytest.mark.parametrize("path", ["/", "/health", "/version"])
def test_query_string_is_ignored(client, path):
    response = client.get(f"{path}?x=1&y=%00&z=" + "b" * 500)
    assert response.status_code == 200


@pytest.mark.parametrize("method", ["post", "put", "delete", "patch"])
def test_wrong_http_method_returns_json_405(client, method):
    response = getattr(client, method)("/health", json={"a": 1})
    assert response.status_code == 405
    assert response.is_json
    assert response.get_json()["error"] == "Method Not Allowed"


def test_unhandled_exception_returns_json_500(monkeypatch):
    def boom():
        raise RuntimeError("simulated failure")

    monkeypatch.setitem(app.view_functions, "home", boom)
    app.config.update(TESTING=False, PROPAGATE_EXCEPTIONS=False)
    try:
        with app.test_client() as test_client:
            response = test_client.get("/")
    finally:
        app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=None)
    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal Server Error"


def test_helpers_read_environment(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "9.9.9")
    monkeypatch.setenv("APP_ENV", "staging")
    assert app_module.get_version() == "9.9.9"
    assert app_module.get_environment() == "staging"
