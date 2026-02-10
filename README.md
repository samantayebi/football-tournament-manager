# Football Tournament Manager

FastAPI app with Jinja2 + HTMX UI and MySQL persistence for managing football tournaments.

## Features
- Tournaments
- Teams
- Matches
- Results
- Standings (points + goal difference)

## Architecture at a glance
This project follows a Clean Architecture style:
- `src/api` — FastAPI routes + Jinja2 templates + HTMX UI endpoints
- `src/application` — use cases (application logic) + ports/interfaces
- `src/domain` — domain models + domain services (e.g., standings computation)
- `src/infrastructure` — DB session/ORM models + repository implementations (MySQL / in-memory)
- `alembic/` — database migrations

## Prerequisites
- Docker Desktop
- Docker Compose

## Quick Start (Docker)
```bash
cp .env.example .env
docker compose up --build -d
docker compose exec app alembic upgrade head
```

## Production (server)

Deploy on a VPS with Caddy for TLS at `ftm.samyland.com`. **Do not commit secrets** — create a `.env` on the server with real values (see `.env.example` for variable names; ensure `DATABASE_URL` matches your `MYSQL_*` settings).

```bash
# On the server: create .env from .env.example and set real secrets, then:
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec app alembic upgrade head
```

- **Caddy** serves the app and obtains/renews HTTPS certificates automatically.
- **App** is only reachable via Caddy (no public port).
- **DB** uses a named volume; secrets come from `.env` only.