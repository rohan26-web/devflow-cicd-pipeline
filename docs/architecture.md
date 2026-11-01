# DevFlow Architecture

All diagrams use [Mermaid](https://mermaid.js.org/), which GitHub renders automatically in Markdown.

## 1. Overall architecture

```mermaid
flowchart LR
    Dev[Developer<br/>VS Code + Git] -->|git push / PR| GH[GitHub Repository]
    GH -->|triggers| GA[GitHub Actions<br/>ci.yml / ci-cd.yml]
    GA -->|lint + test + scan| Q{All checks pass?}
    Q -- no --> Stop[Pipeline stops<br/>PR blocked]
    Q -- yes, main only --> GHCR[(GitHub Container Registry<br/>ghcr.io)]
    GHCR -->|docker pull| Run[Docker container<br/>localhost:5000]
    Dep[Dependabot] -->|update PRs| GH
```

| Component | Responsibility |
|---|---|
| Developer machine | Write code, run tests locally, commit and push |
| GitHub repo | Stores code, branches, pull requests, branch protection |
| GitHub Actions | Runs automated pipelines on GitHub-hosted runners |
| GHCR | Stores versioned Docker images |
| Dependabot | Opens PRs for outdated dependencies |

## 2. Git branching workflow

```mermaid
gitGraph
    commit id: "init"
    branch develop
    checkout develop
    commit id: "setup"
    branch feature/add-endpoint
    checkout feature/add-endpoint
    commit id: "code"
    commit id: "tests"
    checkout develop
    merge feature/add-endpoint id: "PR merged"
    checkout main
    merge develop id: "release" tag: "v1.0.0"
```

- `main`: stable, production-ready. Merges here publish the image.
- `develop`: integration branch.
- `feature/*`, `bugfix/*`: short-lived branches; merged through pull requests.

## 3. CI pipeline (ci.yml)

```mermaid
flowchart LR
    T[Push or PR] --> L[lint<br/>ruff check]
    T --> U[test<br/>pytest + coverage >= 80%]
    L --> D[docker-build-and-scan<br/>build, smoke test, Trivy]
    U --> D
    U --> A[(coverage-report artifact)]
    D --> R[(trivy-report artifact)]
```

`lint` and `test` run in parallel. `docker-build-and-scan` uses `needs: [lint, test]`, so it only starts if both succeed.

## 4. Docker build and publish (ci-cd.yml)

```mermaid
flowchart LR
    M[Push to main] --> CI[call ci.yml]
    CI -->|needs: ci| P[publish job<br/>packages: write]
    P --> Login[docker/login-action<br/>GITHUB_TOKEN]
    Login --> Build[build-push-action]
    Build --> T1[tag: latest]
    Build --> T2[tag: commit SHA]
    T1 --> GHCR[(ghcr.io/OWNER/devflow-cicd-pipeline)]
    T2 --> GHCR
```

## 5. Complete CI/CD pipeline

```mermaid
flowchart TD
    A[Feature branch push] --> B[ci.yml runs]
    B --> C[Pull request to develop/main]
    C --> D[Required check: CI passes]
    D --> E[Merge to main]
    E --> F[ci-cd.yml runs]
    F --> G[ci.yml reused: lint, test, scan]
    G --> H[Publish latest + SHA tags to GHCR]
    H --> I[docker pull + docker run anywhere]
```

Duplicate-run prevention: `ci.yml` ignores pushes to `main`; on `main`, `ci-cd.yml` calls `ci.yml` once through `workflow_call`.

## 6. DevSecOps integration

```mermaid
flowchart LR
    Code --> Ruff[Ruff<br/>code quality]
    Code --> Tests[pytest-cov<br/>coverage gate]
    Code --> Img[Docker image]
    Img --> Trivy[Trivy<br/>CRITICAL/HIGH gate]
    Deps[requirements / actions / base image] --> Dependabot
    Secrets[GITHUB_TOKEN<br/>no hardcoded secrets] --> Publish[GHCR publish]
    Ruff --> Gate{Gate}
    Tests --> Gate
    Trivy --> Gate
    Gate -- pass --> Publish
```

Security controls: least-privilege `permissions`, `packages: write` only in the publish job, non-root container user, no secrets in the repo, publish never runs on pull requests.
