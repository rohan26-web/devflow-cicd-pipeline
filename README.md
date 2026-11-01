# DevFlow - Automated CI/CD Pipeline with GitHub Actions and Docker

![CI](https://github.com/YOUR_USERNAME/devflow-cicd-pipeline/actions/workflows/ci.yml/badge.svg)
![CI-CD](https://github.com/YOUR_USERNAME/devflow-cicd-pipeline/actions/workflows/ci-cd.yml/badge.svg)

A small Flask API (DevFlow Status API) used to demonstrate a complete CI/CD and DevSecOps workflow: Git branching, pull requests, automated tests and coverage, linting, Docker, vulnerability scanning and publishing to GitHub Container Registry.

## Problem statement
Manual building, testing and releasing is slow and error-prone. Broken code can reach production, builds differ between machines, and vulnerabilities go unnoticed. DevFlow automates these steps so every change is verified the same way, every time.

## Objectives
- Automate lint, test and coverage checks on every push and pull request.
- Containerize the app so it runs identically everywhere.
- Publish versioned images to GHCR only after all checks pass.
- Scan images for vulnerabilities and keep dependencies updated.

## Features
- Flask JSON API: `/`, `/health`, `/version`, JSON 404/405/500 handlers
- 22 pytest tests with an 80% coverage gate
- Ruff linting
- Docker image: non-root user, gunicorn, health check
- GitHub Actions: `ci.yml` (lint, test, docker build, smoke test, Trivy) and `ci-cd.yml` (publish to GHCR)
- Dependabot for pip, GitHub Actions and Docker

## Technology stack
Python 3.12, Flask, gunicorn, pytest, pytest-cov, Ruff, Git, GitHub, GitHub Actions, Docker, GHCR, Trivy, Dependabot.

## Repository structure
```
devflow-cicd-pipeline/
├── app.py
├── test_app.py
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml            # Ruff, pytest and coverage settings
├── Dockerfile
├── .dockerignore
├── .gitignore
├── LICENSE
├── README.md
├── .github/
│   ├── workflows/ci.yml
│   ├── workflows/ci-cd.yml
│   ├── dependabot.yml
│   └── pull_request_template.md
├── docs/
│   ├── architecture.md       # six Mermaid diagrams
│   ├── setup-guide.md        # step-by-step Windows guide
│   ├── interview-prep.md     # slides, Q&A, 2-minute pitch
│   └── screenshots/
└── reports/
```
`pyproject.toml` is the one addition to the requested structure; it keeps tool settings in one place.

## Quick start
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python app.py                       # http://127.0.0.1:5000/health
```

Tests and lint:
```powershell
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
ruff check .
```

Docker:
```powershell
docker build -t devflow:1.0.0 .
docker run -d --name devflow -p 5000:5000 devflow:1.0.0
curl.exe http://localhost:5000/health
docker logs devflow
docker stop devflow; docker rm devflow
```

Full instructions: [docs/setup-guide.md](docs/setup-guide.md).

## API
| Method and path | Response |
|---|---|
| `GET /` | project name, welcome message, version |
| `GET /health` | project, `status: healthy`, version (HTTP 200) |
| `GET /version` | version and environment (`APP_VERSION`, `APP_ENV` variables) |
| anything else | JSON 404 (wrong method: JSON 405) |

## Workflow explanation
- Branches: `main` (stable), `develop` (integration), `feature/*` and `bugfix/*` (work), merged via pull requests.
- `ci.yml` runs on pushes to any branch except `main`, and on pull requests to `main` or `develop`. Jobs: `lint` and `test` in parallel, then `docker-build-and-scan` (needs both).
- `ci-cd.yml` runs only on pushes to `main`. It calls `ci.yml`, then the `publish` job (needs `ci`) pushes `ghcr.io/<owner>/devflow-cicd-pipeline:latest` and `:<commit-sha>`. Pull requests never publish.
- Permissions default to `contents: read`; only `publish` gets `packages: write`.

Diagrams: [docs/architecture.md](docs/architecture.md).

## GHCR
```powershell
docker pull ghcr.io/YOUR_USERNAME/devflow-cicd-pipeline:latest
docker run -d -p 5000:5000 ghcr.io/YOUR_USERNAME/devflow-cicd-pipeline:latest
```
Private packages require `docker login ghcr.io` with a token that has `read:packages`.

## Security implementation
- Trivy scans the built image; the job fails on fixable CRITICAL/HIGH findings, MEDIUM is reported.
- Ruff catches errors, unused imports and style issues.
- Dependabot opens weekly update PRs (target branch `develop`).
- No secrets in code; publishing uses the automatic `GITHUB_TOKEN`; container runs as non-root.

## Testing methodology
Unit tests with Flask's test client cover each endpoint, status codes, JSON structure, unknown routes, wrong methods, odd paths and query strings, environment-variable configuration and the 500 handler.

## Verification status
Verified while building this project (Python 3.13 sandbox): `ruff check .` passes and all 22 tests pass. **Not yet verified by me:** the 80% pytest-cov gate (the plugin could not be installed in the sandbox; a stdlib trace showed every statement executing), Docker build, GitHub Actions runs, GHCR publishing and Trivy results. These need to be confirmed on your machine and on GitHub using the setup guide. The action versions used (checkout v4, setup-python v5, upload-artifact v4, docker/* v3/v5/v6, trivy-action 0.28.0) are standard but may have newer releases; Dependabot will propose updates.

## Screenshots
Add images to `docs/screenshots/` and link them here: passing Actions run, PR with failed check, GHCR package page, container running at `/health`.

## Limitations
Single small service; no deployment to a server or cloud; no integration tests; Trivy gate ignores unfixed vulnerabilities.

## Future enhancements
Deploy to a free host or Kubernetes, multi-stage Docker build, Docker Compose, image signing (cosign), SBOM generation, matrix testing across Python versions, release tagging workflow.

## Learning outcomes
Git branching and PR workflow; writing GitHub Actions YAML; job dependencies and least-privilege permissions; Docker image and container basics; registry publishing; automated testing and coverage; DevSecOps basics.

## License
MIT
