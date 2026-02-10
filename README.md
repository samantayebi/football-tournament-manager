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