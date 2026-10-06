# Public Review And Deployment Assessment

Review date: 2026-10-06. Baseline: commits `75d6ff7` and `819d4e8` on `main`. This is a snapshot of locally verified work before the publication of this report; GitHub Actions execution is a separate post-push check.

## 1. Overall Assessment

The repository is understandable and reviewable as a document retrieval prototype after these changes. The verified deployment path is a private Docker Compose workspace with documented setup. It is not an anonymous public service, and no remote hosting account, domain, or public deployment is configured.

The three main remaining concerns are shared access without authentication/ownership/quotas; retrieval quality without a benchmark or relevance threshold; and synchronous PDF parsing without process isolation. Language-model answer generation is explicitly absent.

## 2. Findings Before Changes

| Severity / category | Evidence | Impact / outcome |
| --- | --- | --- |
| Critical / dependency | `frontend/package.json`: Next 15.5.21; live npm audit reported a critical Next advisory plus four high findings | Updated Next and patched transitive dependencies; current audit reports zero known findings. |
| High / data loss | `backend/tests/conftest.py` called `drop_all` on the configured application engine | Tests could erase an existing database; now use an independent in-memory engine and offline provider. |
| High / correctness | `services/embeddings.py` used Python `hash(token)` | Persisted vectors changed interpretation between processes; stable SHA-256 hashing and profile compatibility guards added. Legacy data requires owner-directed re-ingestion. |
| High / exposure | API had no authentication, ownership, rate limits, or quotas; upload read was unbounded | Private deployment boundary documented, ports restricted, body/file/text/page limits added. User access controls remain unimplemented. |
| High / dependency | `pypdf` 5.9.0 and pytest 8.4.2; pip-audit reported 87 entries across two packages, including duplicate advisory identifiers | Updated to locked patched versions; current audit reports no known vulnerabilities. Count is audit entries, not distinct exploit count. |
| Medium / availability | Upload route called synchronous PDF/model/database work from an async handler; UnicodeDecodeError caught after its ValueError parent | Extraction now runs in worker threads; invalid UTF-8 and malformed PDFs return controlled 400 errors. |
| Medium / deployment | Compose contained only PostgreSQL, fixed container name, published 5432, and a shared example password | Complete migration/backend/frontend stack, generated secret, health gates, private database, and digest pins added. Existing other-project PostgreSQL was inspected and left untouched. |
| Medium / schema | Alembic allowed null chunk ownership while ORM required it; 128-dimensional migration versus configurable dimensions | Corrective migration and fixed schema dimensions; SQLite/PostgreSQL drift checks pass. |
| Medium / presentation | README, package description, and public GitHub description claimed "internship-ready"; docs implied grounded generation and measured evaluation | Rewritten around excerpt templates, actual limits, and unmeasured retrieval quality. |
| Medium / UX | Initial workspace fetch had no error handler; all failures implied an offline backend; no deletion UI; file input did not reset | Controlled feedback, form constraints, live status, deletion confirmation, visible focus, empty state, and input reset added. |
| Low / automation | No Actions runs or workflows, broken `next lint`, no backend lockfile | Pinned CI, dependency monitoring, Python lock, explicit frontend typecheck, and migration checks added. No standalone frontend lint tool is claimed. |

Inspection found no application SQL string interpolation, command execution, filesystem upload persistence, webhooks, redirects, analytics, cookie sessions, or admin routes. These absent surfaces do not establish that the whole app is secure. Source text is persisted in a shared collection, and optional embeddings send it to OpenAI.

The public repository retained its existing name and empty homepage because no real hosted demo exists. Metadata now describes document ingestion/retrieval with FastAPI, Next.js, and pgvector and adds relevant topics. No license was invented. No release, usage statistic, benchmark, testimonial, or badge asserting unrun CI was fabricated. Published history was not rewritten.

## 3. Changes Made

Backend changes fix test isolation, stable embeddings, incompatible profile rejection, ingestion limits, parser errors, chunk configuration validation, explicit timeouts/retries, controlled database/provider errors, readiness/liveness, document deletion, connection health, migration URL escaping, and schema drift. Comments explain the key safety and compatibility decisions.

Deployment changes add locked multi-stage non-root images, digest pins, complete Compose startup/migration orchestration, loopback-only publication, generated private configuration, and an integration smoke script. Source/backend ports remain private; the other project's database is unaffected.

UI changes preserve the existing cream/copper style while improving keyboard focus, long-text wrapping, empty/error states, validation, status announcements, deletion, and factual copy. `/api` is a same-origin proxy instead of a browser bundle containing a deployment-specific localhost API URL.

Documentation now covers current behavior, stack, tradeoffs, supported setup, environment variables, security/privacy, backups, rollback, and unfinished work. A screenshot uses synthetic source text from the verified UI. CI runs backend static checks/tests/audits/migrations, frontend typecheck/build/audit, offline secret scans, and Compose smoke tests. Dependabot configuration covers npm, uv, and Actions.

## 4. Verification

| Exact command / check | Result |
| --- | --- |
| Baseline: `$env:RAG_DATABASE_URL='sqlite:///./baseline-review.db'; .\.venv\Scripts\python.exe -m pytest -q` | 3 passed on a deliberately disposable database. |
| Baseline: `npm run build` | Passed, home route 2.13 kB and 105 kB first-load JS. |
| `uv sync --frozen --extra dev` | Locked environment installation succeeded. |
| `uv run --extra dev pytest -q` | 10 tests passed; covers ingestion, citations, uploads, size/UTF-8/PDF errors, deletion, incompatible vectors, whitespace/text limits, overlap, and stable hashing. One Starlette/httpx deprecation warning remains. |
| `uv run --extra dev ruff check .` | Passed selected syntax/undefined-name checks. This is not a comprehensive security analyzer. |
| `uv run --extra dev pip-audit` | No known vulnerabilities. Local project cannot be audited as a PyPI package; its source was reviewed separately. |
| `npm ci`, `npm run typecheck`, `npm run build`, `npm audit` | Installation, typing, production build passed; zero known npm vulnerabilities. Final container home route 2.45 kB and 105 kB first-load JS. |
| `docker compose config --quiet` | Configuration valid; missing required password fails early. |
| `docker compose up --build -d --wait` | Clean Linux container builds and healthy services, with migration completion before backend startup. |
| `./scripts/smoke.ps1` | Actual PostgreSQL/pgvector readiness, ingestion, query/citations, and deletion passed. |
| `uv run alembic upgrade head`, `uv run alembic check` against disposable SQLite | All migrations applied and no ORM/schema drift after corrective migration. |
| `docker compose exec -T backend alembic check` | PostgreSQL metadata/schema drift check passed. |
| `git diff --check` | Passed. |
| Offline Gitleaks v8.24.3 history scan with `--network none --read-only`, read-only repository mount, `--redact` | Two published commits scanned; no credential findings. |
| Offline current directory scan with `--config /repo/.gitleaks.toml --redact --verbose` | 10 expected findings: ignored local generated database password and Next.js generated server keys. Downloaded dependencies/tool caches excluded after broad scan noise. Application build assets remained in scope. No matches were printed without redaction. |
| `git diff --cached --no-ext-diff` piped to offline Gitleaks `stdin --redact --no-banner` | Exact staged publication diff scanned (508 KB); no leaks found. |

The locally generated `.env` and all `.next` assets are ignored and excluded from relevant Docker source contexts. No external credential exposure was found in published history. Rotation is not required for the newly generated local secret based on this review; any previously deployed default/example database password should be replaced deliberately by that deployment's owner. A clean scanner result is not proof that all personal data or vulnerabilities are absent.

Manual UI verification exercised source ingestion and citation retrieval in the production container, checked labels/live status and the 390-pixel responsive layout, and inspected a screenshot of synthetic text. The initial `localhost:3000` reached another IPv6 listener on Windows; `127.0.0.1:3000` was verified and documented. Synthetic test documents were removed. No automated accessibility conformance claim is made.

GitHub metadata, public description/topics, existing files/history, absence of a license/homepage, and Actions/PR/release information were inspected using the public API. README rendering should be checked after publication. OpenAI live embeddings were not called: no provider credential/billing use was needed or authorized for verification. SDK timeout/retry behavior was checked against the [official Python SDK documentation](https://developers.openai.com/api/reference/python). No remote cloud deployment, OS-image vulnerability audit, load test, scheduled backup, or backup restore was performed.

An initial scanner container request was rejected by automatic approval review because it had network access to repository contents. The approved retry disabled networking and mounted the repository read-only. A later cleanup approval review timed out; a single retry succeeded. No unresolved approval blocker remains.

## 5. Access And Deployment Handoff

Repository: https://github.com/YangOwen007/ai-rag-assistant. Verified local app: http://127.0.0.1:3000. This is a local URL, not a shareable public deployment.

From a new clone on Windows, run `./scripts/configure.ps1`, `docker compose up --build -d --wait`, then `./scripts/smoke.ps1`. On Unix, use `sh scripts/configure.sh`. Docker Engine/Desktop with Compose v2 and Linux containers is required. The generated root `.env` supplies the required database password. Offline mode needs no paid provider account.

For development, run `uv sync --frozen --extra dev`, `uv run alembic upgrade head`, and `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload` in backend; run `npm ci` and `npm run dev` in frontend. For production without Compose, backend start is `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log`; frontend build/start are `npm run build` and `npm start -- --hostname 127.0.0.1`. Database persistence/backups and migration startup then become operator responsibilities.

OpenAI mode requires a server-side key, provider account access, and billing; source chunks/questions leave the host. Switching provider/model requires re-ingestion. Remote hosting requires a host/account and access-controlled tunnel or gateway. See [deployment.md](deployment.md) for exact setup, health checks, backup commands, and recovery boundaries.

## 6. Recommended Next Steps

1. Before public exposure, add authentication, per-user ownership, quotas/rate limits, HTTPS access control, and isolated resource-limited PDF workers. Keep current deployments private.
2. Build a retrieval evaluation corpus and measure relevant-source recall and no-evidence behavior before adding LLM generation or tuning retrieval. `eval/sample_eval_cases.json` is not a runnable benchmark.
3. Add an owner-controlled export/reindex tool for legacy/provider changes. Preserve source text and backups; no automated destructive reindex was performed.
4. Select a license intentionally. Configure GitHub private vulnerability reporting, branch protections, and release policy if desired; these settings were not assumed or fabricated.
5. On the chosen host, test backup restore, scan OS images, configure monitoring/log retention, and choose a domain/gateway only if public browser access is needed. No hosting or uptime commitment exists.

## 7. File And Repository Summary

Changed tracked files: `.gitignore`, `README.md`, `docker-compose.yml`, `docs/architecture.md`; backend `.env.example`, configuration/database/models/main/schemas, embeddings/extraction/RAG services, migration environment, `pyproject.toml`, and test fixtures/tests; frontend page/CSS/config/package manifest and lockfile.

Added: root `.env.example`, `.gitattributes`, `.gitleaks.toml`, `SECURITY.md`, `CONTRIBUTING.md`, `.github/workflows/checks.yml`, `.github/dependabot.yml`; both Dockerfiles/dockerignore files; backend `uv.lock`, request-limit middleware, embedding-profile and chunk-ownership migrations, safety tests; frontend `.env.example`; configure/smoke scripts; deployment guide, review report, and synthetic UI screenshot.

Intentionally untouched: published commits, original migration revision, existing local application database/source material, other projects and their containers, sample evaluation cases without benchmark claims, repository name/homepage, and licensing. No hosting credentials or public deployment were created. Local generated secrets, caches, databases, dumps, and build output remain ignored.
