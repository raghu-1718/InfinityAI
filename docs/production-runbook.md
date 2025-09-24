# InfinityAI Production Runbook

Operational reference for keeping the InfinityAI backend + frontend healthy in Azure.

---
## 1. Quick Status Commands

| Purpose | Command |
|---------|---------|
| Check readiness | `curl -s https://infinityai-backend-app.azurewebsites.net/ready` |
| Check detailed health | `curl -s https://infinityai-backend-app.azurewebsites.net/health | jq .` |
| Poll until DB connected | `bash scripts/poll_health.sh` |
| Show DNS resolution | `dig +short infinityai.pro api.infinityai.pro www.infinityai.pro` |

---
## 2. Deployment Flow (Backend)
1. Push to `main` (or run workflow_dispatch) → GitHub Actions workflow `Backend Container Deploy` builds & pushes image to ACR, sets Web App container, app settings, and restarts.
2. Health endpoint should become reachable (<2s) even if DB is down (status=degraded, database=timeout || error).
3. After DB firewall/credentials fixed it should show `database: connected`.

### Required Repo Variables (Actions → Variables)
```
ACR_NAME
ACR_LOGIN_SERVER
AZURE_RESOURCE_GROUP
AZURE_WEBAPP_NAME
APP_PORT=8000
CORS_ALLOW_ORIGINS=https://infinityai.pro,https://www.infinityai.pro,https://api.infinityai.pro
```

### Required Secrets (Actions → Secrets)
```
AZURE_CLIENT_ID
AZURE_TENANT_ID
AZURE_SUBSCRIPTION_ID
DB_HOST  (e.g. infinityai-prod-db.mysql.database.azure.com)
DB_NAME  (application DB, NOT the default 'mysql' schema unless intentionally using it)
DB_USER  (format: user@server-name for Azure MySQL Flexible Server)
DB_PASSWORD
```

Optional secrets / vars:
```
DB_CONNECT_TIMEOUT=5
DB_SSL_DISABLED=false (normally omit for production)
ALLOW_FALLBACK_LOGIN=true/false
ADMIN_USERNAME, ADMIN_PASSWORD_HASH (or ADMIN_PASSWORD + ADMIN_ALLOW_PLAINTEXT=true temp only)
```

---
## 3. Database Connectivity Troubleshooting

Symptoms in `/health`:
| database field | Meaning | Action |
|----------------|---------|--------|
| connected | All good | None |
| timeout | Connection attempt exceeded HEALTH_DB_TIMEOUT (thread still alive) | Verify firewall / host / user@server format |
| error | Immediate exception | Check credentials / TLS flags / server reachable |
| disconnected | Query returned but flagged false (unlikely) | Recreate pool, inspect logs |

Checklist:
1. Azure MySQL Server → Networking:
   - Enable "Allow public access from any Azure service..." OR add App Service outbound IPs.
2. Confirm DB_USER uses `user@server` format.
3. Confirm password (rotate if unsure) and update GitHub secret.
4. Confirm DB_NAME exists (`mysql -h host -u user@server -p`). Create if needed.
5. If TLS enforcement enabled (default), DO NOT set `DB_SSL_DISABLED=true` in production.
6. If custom CA required (rare for Azure) add secret `DB_SSL_CA` and var `DB_SSL_VERIFY=true`.
7. Redeploy (push or run workflow) and re-check health.

Pool rebuild: change an env (e.g., increment a dummy var) and redeploy to force new container.

---
## 4. Fallback Admin Login (Temporary Access)
Use only while DB unreachable. Steps:
1. Generate bcrypt hash: `python scripts/generate_bcrypt_hash.py 'YourPassword'`
2. Add repo variable `ALLOW_FALLBACK_LOGIN=true`.
3. Add variable `ADMIN_USERNAME=admin`.
4. Add secret `ADMIN_PASSWORD_HASH=<hash>`.
5. Redeploy → POST `/login` with form body `username=admin&password=YourPassword`.
6. Remove fallback (set ALLOW_FALLBACK_LOGIN=false) once DB works.

Security: Never commit plain passwords; prefer hash + disable fallback ASAP.

---
## 5. Frontend → Backend Integration

Option A (explicit URL): Set `REACT_APP_API_URL=https://api.infinityai.pro` in SWA environment variables.

Option B (SWA linked API): Link the backend App Service in SWA → APIs; frontend can call `/api/...` without explicit env var.

DNS Records Required:
| Host | Type | Value |
|------|------|-------|
| @ (apex) | ALIAS / A | <SWA provided target> |
| www | CNAME | <SWA default hostname> |
| api | CNAME | infinityai-backend-app.azurewebsites.net |

After DNS propagation, confirm:
`dig +short api.infinityai.pro` returns azurewebsites CNAME target.

---
## 6. Rolling Back
1. Locate previous successful workflow run → copy its image digest from ACR.
2. Run `az webapp config container set --docker-custom-image-name <digest>`.
3. Restart web app.

---
## 7. Observability & Logging
Backend uses structured logging (JSON) via `shared.utils.logger` (expand later with App Insights instrumentation key environment variable if needed).

Enhancements (future):
* Add Application Insights key env and configure opencensus-ext-azure.
* Add `/metrics` endpoint (Prometheus) behind auth token.
* Add alert rules on health degradation over N minutes.

---
## 8. Common Error Scenarios
| Scenario | Root Cause | Fix |
|----------|------------|-----|
| Health: timeout | Firewall / wrong DB_USER | Fix networking or user format; redeploy |
| Login 400 even with fallback | Missing ADMIN_PASSWORD_HASH or ALLOW_FALLBACK_LOGIN=false | Set vars/secrets and redeploy |
| CORS blocked | Origin not in CORS_ALLOW_ORIGINS | Update variable & redeploy |
| 502 / startup failure | Image pulled but crashes due to env mismatch | Check container logs in App Service → Log Stream |

---
## 9. Manual Health Poll Example
`bash scripts/poll_health.sh --timeout 300 --interval 5`

---
## 10. Future Roadmap Suggestions
1. Infrastructure as Code (Bicep/Terraform) for reproducible env.
2. Secrets in Azure Key Vault with managed identity.
3. Automated DB migrations via Alembic step in workflow.
4. Canary slot for backend (staging slot + swap).
5. WAF/Front Door in front of frontend & API for global performance.

---
Document version: 2025-09-24
