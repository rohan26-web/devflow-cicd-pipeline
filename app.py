"""DevFlow Status API - a small Flask app used to demonstrate CI/CD."""

import os

from flask import Flask, jsonify

PROJECT_NAME = "DevFlow Status API"

app = Flask(__name__)


def get_version() -> str:
    """Application version, configurable via the APP_VERSION env variable."""
    return os.environ.get("APP_VERSION", "1.0.0")


def get_environment() -> str:
    """Deployment environment, configurable via the APP_ENV env variable."""
    return os.environ.get("APP_ENV", "development")


@app.route("/")
def home():
    return jsonify(
        project=PROJECT_NAME,
        message="Welcome to DevFlow - automated CI/CD with GitHub Actions and Docker",
        version=get_version(),
    )


@app.route("/health")
def health():
    return jsonify(
        project=PROJECT_NAME,
        status="healthy",
        version=get_version(),
    ), 200


@app.route("/version")
def version():
    return jsonify(
        version=get_version(),
        environment=get_environment(),
    )


@app.errorhandler(404)
def not_found(_error):
    return jsonify(error="Not Found", message="The requested URL does not exist"), 404


@app.errorhandler(405)
def method_not_allowed(_error):
    return jsonify(error="Method Not Allowed", message="This method is not allowed"), 405


@app.errorhandler(500)
def internal_error(_error):
    return jsonify(error="Internal Server Error", message="Something went wrong"), 500


if __name__ == "__main__":  # pragma: no cover
    # Local development only. In Docker the app is served by gunicorn.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")))
