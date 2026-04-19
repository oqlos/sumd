# examples/integrations/

Integration examples for common tools and platforms.

## Files

| File | Tool | What it demonstrates |
|------|------|---------------------|
| `github-actions.yml` | GitHub Actions | CI workflow: scan → lint → upload report |
| `pre-commit-config.yaml` | pre-commit | Lint SUMD.md on every commit |
| `taskfile.yml` | Taskfile | docs / lint / refactor tasks |
| `vscode-tasks.json` | VS Code | Build/test tasks for SUMD commands |
| `Dockerfile` | Docker | Container that generates SUMD.md |
| `docker-compose.yml` | Docker Compose | Compose service for doc generation |
| `makefile` | GNU Make | Make targets for SUMD workflow |

## Quick Setup

### GitHub Actions (copy to `.github/workflows/sumd.yml`)

```bash
cp examples/integrations/github-actions.yml .github/workflows/sumd.yml
```

### pre-commit (add to `.pre-commit-config.yaml`)

```bash
cat examples/integrations/pre-commit-config.yaml >> .pre-commit-config.yaml
pre-commit install
```

### VS Code tasks

```bash
cp examples/integrations/vscode-tasks.json .vscode/tasks.json
```
