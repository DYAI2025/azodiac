---
description: Deploy app to Fly.io — build, deploy, verify health
allowed-tools: Bash, Read, Edit, Glob
---

## Your Task

Deploy the current project to Fly.io and verify everything works.

### Steps

1. **Pre-flight checks:**
   ```bash
   # Verify deploy files exist
   ls -la Dockerfile fly.toml .dockerignore

   # Read fly.toml for app name and config
   cat fly.toml | head -20

   # Run tests first
   # (adapt test command to project — pytest, npm test, go test, etc.)
   ```

2. **Deploy:**
   ```bash
   # FLY_API_TOKEN must be set in environment
   # Read app name from fly.toml
   fly deploy
   ```

3. **Verify deployment:**
   ```bash
   # Get app URL from fly.toml or fly status
   fly status

   # Health check (adapt path to project)
   curl -s https://<app-name>.fly.dev/health | python3 -m json.tool
   ```

4. **Check custom domain (if configured):**
   ```bash
   fly certs list
   ```

5. **Report status:**
   - Deployment successful/failed
   - Health check response
   - Custom domain/SSL status

### Guardrails

- **FLY_API_TOKEN:** Needed as env var. Don't use `fly auth login` (doesn't work in Claude's shell). If token not set, ask user to provide it.
- **Tests first:** Always run tests before deploying. Don't deploy broken code.
- **Auto-stop:** Fly machines may auto-stop when idle. First request after stop has cold start. This is expected.
