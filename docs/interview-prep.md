# Presentation and Interview Preparation

## Project abstract
DevFlow is a lightweight Flask status API wrapped in an automated CI/CD pipeline. GitHub Actions lints and tests every change, builds and scans a Docker image, and publishes versioned images to GitHub Container Registry only when the code is merged to `main` and all checks pass.

## Requirements
- Software: Windows 10/11, Python 3.12, Git, VS Code, Docker Desktop (WSL 2), GitHub account.
- Hardware: 8 GB RAM recommended, about 10 GB free disk, internet connection.
- Functional: three JSON endpoints, JSON error responses, automated tests, CI on push/PR, image build and publish.
- Non-functional: lightweight, reproducible, secure (no secrets, non-root, scanned), maintainable.

## Modules
1. Application (`app.py`) 2. Tests (`test_app.py`) 3. CI workflow 4. CI/CD publish workflow 5. Docker packaging 6. Security (Trivy, Ruff, Dependabot) 7. Documentation.

## 10-12 slide outline
1. Title: DevFlow - CI/CD with GitHub Actions and Docker
2. Introduction: what CI/CD is and why it matters
3. Problem: manual, inconsistent, unsafe releases
4. Objectives: automate test, build, scan, publish
5. Proposed system: push/PR triggers pipeline, merge to main publishes image
6. Technology stack: Python, Flask, pytest, Ruff, Docker, GitHub Actions, GHCR, Trivy
7. Architecture: diagram 1 from `docs/architecture.md`
8. CI/CD workflow: lint + test, then build and scan, then publish (needs chain)
9. Implementation: key files (`ci.yml`, `Dockerfile`, tests), non-root container, least privilege
10. Results: screenshots of green run, failed PR check, GHCR package, `/health` response
11. Limitations and future scope: no cloud deployment yet, add Compose/Kubernetes, signing, SBOM
12. Conclusion: repeatable, secure, automated delivery

## Two-minute interview explanation
"DevFlow is a small Flask API that I used to build a full CI/CD pipeline. I work with a branching model of main, develop and feature branches. When I push or open a pull request, GitHub Actions runs Ruff for linting and pytest with an 80 percent coverage gate in parallel. If both pass, it builds the Docker image, smoke-tests the container and scans it with Trivy, failing on fixable critical or high vulnerabilities. Branch protection requires those checks before a merge. When code lands on main, a second workflow reuses the same checks and then publishes the image to GitHub Container Registry with a latest tag and a commit-SHA tag, using the built-in GITHUB_TOKEN and write permission limited to that one job. The container runs as a non-root user under gunicorn with a health check, and Dependabot keeps dependencies, actions and the base image updated. I also practiced failure scenarios like failing tests, bad Dockerfiles and invalid tags, and diagnosed them from the logs."

## Interview questions and answers
**Git and version control**
1. *What is version control?* Tracking changes to files over time so you can collaborate, review history and roll back.
2. *Git vs GitHub?* Git is the distributed version control tool; GitHub hosts Git repositories and adds pull requests, issues and Actions.
3. *What is a branch?* A movable pointer to a line of commits that lets you work in isolation.
4. *merge vs rebase?* Merge joins histories with a merge commit; rebase replays commits on a new base for a linear history. Do not rebase shared branches.
5. *What is a pull request?* A request to merge a branch, used for review and automated checks.
6. *git fetch vs git pull?* Fetch downloads changes only; pull is fetch plus merge.
7. *How do you resolve a merge conflict?* Open the conflicted files, choose the correct content, remove the markers, `git add`, then commit.
8. *Why protect main?* To force reviews and passing checks so broken code cannot reach it.

**CI/CD and GitHub Actions**
9. *CI vs CD?* CI automatically integrates and tests every change. Continuous Delivery keeps the code always releasable; Continuous Deployment also releases automatically.
10. *What is GitHub Actions?* GitHub's built-in automation platform driven by YAML workflows.
11. *Workflow, job, step?* A workflow is a YAML file; it has jobs that run on runners; jobs contain sequential steps.
12. *What is a runner?* The machine that executes a job, such as `ubuntu-latest` hosted by GitHub.
13. *What triggers can you use?* `push`, `pull_request`, `workflow_call`, `schedule`, `workflow_dispatch`, and more.
14. *How do jobs depend on each other?* With `needs`; a failed job makes dependent jobs skipped.
15. *Why `permissions`?* The `GITHUB_TOKEN` is limited to what you grant, following least privilege.
16. *How did you avoid duplicate runs?* `ci.yml` ignores pushes to main; on main, `ci-cd.yml` calls it once via `workflow_call`.
17. *What is `GITHUB_TOKEN`?* A short-lived token GitHub creates for each run, so no stored password is needed.
18. *How do you debug a failed workflow?* Open the run, expand the failed step logs, reproduce locally, fix and re-run.

**YAML**
19. *Key YAML rules?* Indentation with spaces (no tabs) defines structure; lists use `-`; key: value maps.

**Testing**
20. *What is code coverage?* The percentage of code executed by tests; a gate fails the build below a threshold.
21. *Why test error paths?* Unexpected input and 404/405/500 behavior are where bugs hide.

**Docker and GHCR**
22. *Image vs container?* An image is a read-only template; a container is a running instance of it.
23. *What are layers?* Each Dockerfile instruction creates a cached layer; order instructions to maximize cache reuse.
24. *Why copy requirements before code?* The dependency layer is reused until requirements change, speeding builds.
25. *Why a non-root user?* It limits damage if the app is compromised.
26. *What does `-p 5000:5000` do?* Maps host port to container port.
27. *What is `.dockerignore` for?* Keeps junk and secrets out of the build context and image.
28. *What is GHCR?* GitHub's container registry at `ghcr.io`; images are named `ghcr.io/owner/name:tag` in lowercase.
29. *Why tag with both latest and a SHA?* `latest` is convenient; the SHA is immutable and traceable to an exact commit for rollback.
30. *Public vs private packages?* Public can be pulled anonymously; private needs `docker login` with a token scoped `read:packages`.

**DevSecOps and failures**
31. *What is DevSecOps?* Building security checks into the pipeline instead of at the end.
32. *What does Trivy do?* Scans images and dependencies for known CVEs and reports severity and fixed versions.
33. *How do you handle a critical vulnerability?* Check the fixed version, upgrade the package or base image, rebuild, re-scan.
34. *What does Dependabot do?* Opens PRs to update dependencies, actions and base images.
35. *How do you handle secrets?* Never commit them; use GitHub Secrets or the automatic token and environment variables.
36. *A container exits immediately: what do you do?* `docker ps -a`, `docker logs`, `docker inspect` for the exit code, fix and rerun.
37. *Why not publish on pull requests?* PR code may be untrusted, and publishing needs write access.
