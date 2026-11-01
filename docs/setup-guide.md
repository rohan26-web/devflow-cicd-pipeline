# DevFlow Setup Guide (Windows 10/11, PowerShell)

Follow the steps in order. Replace `YOUR_USERNAME` with your GitHub username (use lowercase in image names).

## Step 0 - Install the tools

| Tool | Download | Verify |
|---|---|---|
| Python 3.12 | https://www.python.org/downloads/ (tick "Add python.exe to PATH") | `python --version` |
| Git | https://git-scm.com/download/win | `git --version` |
| VS Code | https://code.visualstudio.com/ | open it |
| Docker Desktop | https://www.docker.com/products/docker-desktop/ (choose WSL 2 backend) | `docker --version` |

WSL 2 (run PowerShell as Administrator, then restart):

```powershell
wsl --install
wsl --set-default-version 2
```

Verify everything:

```powershell
python --version        # Python 3.12.x
git --version           # git version 2.x
docker --version        # Docker version 2x.x
docker run hello-world  # prints "Hello from Docker!"
```

Common errors:
- `python is not recognized` - reinstall Python and tick "Add to PATH", or use `py --version`.
- Docker "WSL 2 installation is incomplete" - run `wsl --update`, restart, open Docker Desktop.
- `docker: error during connect` - Docker Desktop is not running; start it and wait for the green icon.

## Step 1 - Get the project

If you downloaded the zip, extract it so you have a folder `devflow-cicd-pipeline`. Then:

```powershell
cd C:\Users\YOUR_NAME\Projects\devflow-cicd-pipeline
code .
```

## Step 2 - Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python app.py
```

If activation is blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then retry.

Open http://127.0.0.1:5000/health in a browser. Expected:

```json
{"project":"DevFlow Status API","status":"healthy","version":"1.0.0"}
```

Stop with Ctrl+C. Other endpoints: `/` and `/version`. Unknown URLs return a JSON 404.

## Step 3 - Run tests, coverage and lint

```powershell
pytest --cov=app --cov-report=term-missing --cov-report=html:reports/htmlcov --cov-fail-under=80
ruff check .
```

Reading the output: `.` = passed, `F` = failed, `E` = error. A failure prints the test name, the failing line and `assert X == Y`. The coverage table shows `Miss` lines not exercised by tests. Open `reports\htmlcov\index.html` for a visual report. Fix the code or test, then re-run.

## Step 4 - Create the GitHub repository

1. Go to https://github.com/new
2. Repository name: `devflow-cicd-pipeline`, Public (simplest for GHCR and branch protection on free plans), do NOT add README/.gitignore/license (they already exist).
3. Click Create repository.

Configure Git once:

```powershell
git config --global user.name "rohan26-web"
git config --global user.email "jrohanreddy5@gmail.com"
git config --global init.defaultBranch main
```

## Step 5 - First commit and push

```powershell
git init
git add .
git status
git commit -m "feat: initial DevFlow project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/devflow-cicd-pipeline.git
git remote -v
git push -u origin main
```

A browser window may ask you to sign in to GitHub (Git Credential Manager); approve it. Never paste a personal access token into a file.

Create the `develop` branch:

```powershell
git switch -c develop
git push -u origin develop
```

On the first push to `main`, the **CI-CD** workflow runs automatically (Actions tab). Open it and watch the jobs. The `publish` job may fail until Step 8 is done; that is expected only if Actions permissions are restricted.

## Step 6 - Feature branch and pull request

```powershell
git switch develop
git pull
git switch -c feature/add-readme-note
# edit README.md in VS Code, save
git add README.md
git commit -m "docs: add note to README"
git push -u origin feature/add-readme-note
```

On GitHub click "Compare & pull request", base `develop`, create it. The **CI** workflow runs on the PR. When green, click Merge. Then open a PR from `develop` to `main` to release; merging it triggers publishing.

Handy commands: `git log --oneline --graph --all`, `git branch`, `git merge develop`, `git clone <url>`.

## Step 7 - Require CI before merging

Repository -> Settings -> Rules -> Rulesets -> New branch ruleset (or Settings -> Branches -> Add branch protection rule):

- Target: `main` (and optionally `develop`)
- Enable "Require a pull request before merging"
- Enable "Require status checks to pass" and add the checks `lint`, `test`, `docker-build-and-scan`. (Checks appear in the picker only after they have run at least once.)

Demonstrate a failure: on a feature branch change `"healthy"` to `"ok"` in `app.py`, push, open a PR. The `test` job fails, the PR shows a red X, and the merge button is blocked. Revert the change to recover.

## Step 8 - Allow GHCR publishing

Repository -> Settings -> Actions -> General -> Workflow permissions. Either option works because `ci-cd.yml` declares its own `permissions`. If publishing fails with "denied", select "Read and write permissions" and re-run the failed job (Actions -> run -> Re-run failed jobs).

After the first successful publish: your profile -> Packages -> `devflow-cicd-pipeline`. For a public pull without login, open the package -> Package settings -> Change visibility -> Public. Also make sure the package is linked to the repo (it normally is automatically, via the OCI source label).

## Step 9 - Docker locally

```powershell
docker build -t devflow:1.0.0 .
docker images
docker run -d --name devflow -p 5000:5000 devflow:1.0.0
docker ps
curl http://localhost:5000/health
docker logs devflow
docker inspect devflow
docker stop devflow
docker rm devflow
docker rmi devflow:1.0.0
```

Expected `docker ps` shows `devflow:1.0.0` with `0.0.0.0:5000->5000/tcp` and status `Up ... (healthy)` after a few seconds. In PowerShell, `curl` is an alias for `Invoke-WebRequest`; use `curl.exe http://localhost:5000/health` for plain output.

Override settings without editing code: `docker run -d -p 5000:5000 -e APP_ENV=staging devflow:1.0.0`.

## Step 10 - Pull and run the published image

```powershell
docker pull ghcr.io/YOUR_USERNAME/devflow-cicd-pipeline:latest
docker images
docker run -d --name devflow-ghcr -p 5000:5000 ghcr.io/YOUR_USERNAME/devflow-cicd-pipeline:latest
curl.exe http://localhost:5000/version
```

Specific commit: `docker pull ghcr.io/YOUR_USERNAME/devflow-cicd-pipeline:<full-commit-sha>`.
Private package: first `docker login ghcr.io -u YOUR_USERNAME` with a personal access token that has the `read:packages` scope (paste it at the prompt only).

## Step 11 - Security scanning

The `docker-build-and-scan` job runs Trivy on every CI run. Open the run -> job log, or download the `trivy-report` artifact. Policy: the job fails on fixable CRITICAL or HIGH vulnerabilities; MEDIUM ones are listed but do not fail.

Reading a report: each row shows Library, Vulnerability ID (CVE), Severity, Installed Version and Fixed Version. If Fixed Version is filled, upgrade to it.

Optional local scan: `docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image devflow:1.0.0`.

## Step 12 - Failure drills

| Scenario | How to trigger | How to diagnose and fix |
|---|---|---|
| Unit test fails | change an expected value in `app.py` | Actions -> failed `test` job -> read the `assert` line; later jobs show "skipped" because of `needs`; fix and push |
| Docker build fails | add `RUN pip install nonexistent-pkg-xyz` to the Dockerfile | `docker build` or the job log shows `No matching distribution`; remove it and push |
| Critical CVE | use an old base image such as `python:3.8-slim` | Trivy gate fails; set `FROM python:3.12-slim` (or bump the vulnerable package) and push |
| Invalid image tag | `docker build -t DevFlow:1.0.0 .` | Error `repository name must be lowercase`; use lowercase `devflow:1.0.0`. GHCR names must be lowercase too |
| Container will not start | `docker run -d --name bad devflow:1.0.0 python nofile.py` | `docker ps -a` shows `Exited (2)`; `docker logs bad` shows `can't open file`; `docker inspect bad --format "{{.State.ExitCode}}"`; remove with `docker rm bad` |
| Port already in use | run two containers on 5000 | `port is already allocated`; use `-p 5001:5000` |

## Step 13 - Final checklist

- [ ] `pytest` passes and coverage >= 80%
- [ ] `ruff check .` passes
- [ ] App works at http://localhost:5000/health
- [ ] `docker build -t devflow:1.0.0 .` works
- [ ] CI is green on a pull request
- [ ] CI-CD run on `main` is green and image appears under Packages
- [ ] Published image pulled and run locally
- [ ] Screenshots saved in `docs/screenshots/`
