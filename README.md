# Football Tournament Manager

FastAPI app with Jinja2 + HTMX UI and MySQL persistence for managing tournaments.

## Features
- Tournaments
- Teams
- Matches
- Results
- Standings

## Prerequisites
- Docker Desktop
- Docker Compose

## Quick Start
```bash
cp .env.example .env
docker compose up --build -d
docker compose exec app alembic upgrade head
```

Open:
- http://127.0.0.1:8000/
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

## Verify persistence
1) Create data in the UI (tournaments, teams, matches, results).
2) Restart:
```bash
docker compose down
docker compose up -d
```
3) Confirm tournaments still exist on the homepage.

## Troubleshooting
- Port 8000 busy: stop the process using it or change the host port in `docker-compose.yml`.
- Rebuild cleanly:
```bash
docker compose down -v
docker compose up --build -d
```