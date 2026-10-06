# Private Deployment

## Target And Prerequisites

The supported path is Docker Compose v2 on a host running Linux containers. The UI listens on host loopback; PostgreSQL and FastAPI have no host ports. This is a private shared workspace, not a public multi-user service. A remote host/account and SSH access are still required for remote deployment. A public domain is optional and requires an authenticated HTTPS gateway with rate limits and body limits before exposing the UI.

## First Start

```powershell
./scripts/configure.ps1
docker compose config --quiet
docker compose up --build -d
docker compose ps
./scripts/smoke.ps1
```

Use `sh scripts/configure.sh` on Unix with OpenSSL installed. Root `.env` is private. Its password must be URL-safe (the generator uses hex). Keep that password stable for an existing volume; changing the environment does not change PostgreSQL's stored password. `RAG_EMBEDDING_PROVIDER=openai` additionally needs `RAG_OPENAI_API_KEY`, provider account access, and API billing. That path is optional and not required to run offline.

To access a remote private host:

```sh
ssh -L 3000:127.0.0.1:3000 user@your-host
```

Open `http://127.0.0.1:3000` while the tunnel is connected. Give reviewers repository access and instructions to run their own local checkout. Never send database credentials or real documents as demo fixtures.

## Health And Verification

`GET /api/live` checks the backend process. `GET /api/ready` checks the migrated schema and embedding profile. `GET /api/health` reports collection counts. `scripts/smoke.ps1` checks readiness, ingestion, pgvector retrieval, and deletion using temporary synthetic text. It deletes only its own document. Check `docker compose ps` and `docker compose logs --tail 100 backend migrate frontend` for failures. Avoid exporting logs with source documents or credentials.

## Updates And Recovery

1. Back up before pulling new code or running migrations.
2. Record the current Git commit and container image IDs (`git rev-parse HEAD`, `docker compose images`).
3. Pull the reviewed commit, then run `docker compose up --build -d` and the smoke check.
4. Keep the previous images and database backup until verification succeeds.

Migrations may change data compatibility. Rolling back only the app does not undo a schema change. Test the old app against the migrated schema or restore the matching database backup in an isolated environment first. Do not run `docker compose down -v` as routine recovery; that deletes the database volume.

Backup commands (the dump is created inside PostgreSQL before copying, avoiding shell binary-redirection differences):

```sh
docker compose exec -T postgres pg_dump -U rag_user -d rag_assistant -Fc -f /tmp/rag-backup.dump
docker compose cp postgres:/tmp/rag-backup.dump ./rag-backup.dump
docker compose exec -T postgres rm /tmp/rag-backup.dump
```

Keep the dump outside the repository, encrypt it, and set retention. Restore only into a designated recovery database/host after confirming the target; `pg_restore --clean` is destructive. Validate the restored counts and smoke behavior before routing traffic. This guide does not configure scheduled backups or claim a tested recovery-time objective.

Common failures:

- Port occupied: choose another `APP_PORT`; update the tunnel and smoke base URL.
- Migration failure: read migration logs, preserve the volume, inspect schema revision, and repair on a backup copy.
- Embedding-profile conflict: export source text, delete incompatible documents via the API, then re-ingest; do not discard source data blindly.
- Provider unavailable: confirm account/key outside logs, use retry after recovery; changing providers on existing vectors requires reindexing.
- Database authentication failure after editing password: restore the matching secret or deliberately rotate the database credential.

## Release Boundaries

Base images and the scanner are pinned by digest; Python and npm dependencies are locked. A release should also scan OS packages and publish application images tied to a commit. CI verifies builds but does not deploy or store hosting credentials. There is no configured cloud service, domain, public URL, automated backup schedule, or uptime monitor.
