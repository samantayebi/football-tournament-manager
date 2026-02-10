# Architecture Overview

This project follows a Clean Architecture style with clear boundaries between layers.

## 1) System Context
- **Browser**: HTMX-enhanced UI served by FastAPI templates.
- **FastAPI app**: HTTP API + server-side rendered UI.
- **MySQL**: Persistent storage for tournaments, teams, and matches.

## 2) Layered / Clean Architecture
- **Presentation/UI + API**: `src/api/`
  - Routes, Jinja2 templates, HTMX endpoints.
  - Example: `src/api/main.py`, `src/api/templates/`.
- **Application**: `src/application/`
  - Use cases and ports (interfaces).
  - Example: `src/application/use_cases/`, `src/application/ports/tournament_repository.py`.
- **Domain**: `src/domain/`
  - Entities and domain services (e.g., standings computation).
  - Example: `src/domain/models/`, `src/domain/services/standings.py`.
- **Infrastructure**: `src/infrastructure/`
  - DB sessions, ORM models, repository implementations.
  - Example: `src/infrastructure/db/session.py`, `src/infrastructure/db/models.py`,
    `src/infrastructure/repositories/mysql_tournament_repository.py`,
    `src/infrastructure/repositories/in_memory_tournament_repository.py`.

## 3) Key Abstractions
- **Repository Port**: `TournamentRepository` in `src/application/ports/tournament_repository.py`.
- **Implementations**:
  - In-memory: `src/infrastructure/repositories/in_memory_tournament_repository.py`
  - MySQL (SQLAlchemy): `src/infrastructure/repositories/mysql_tournament_repository.py`

## 4) Runtime Request Flow (HTMX + API)
- **UI page load**:
  - Browser requests `/` or `/tournaments/{id}`.
  - FastAPI renders templates from `src/api/templates/`.
  - Example: `GET /` and `GET /tournaments/{id}` in `src/api/main.py`.
- **HTMX interactions**:
  - Forms post to `/ui/...` endpoints for partial updates.
  - Server returns HTML fragments such as `src/api/templates/partials/_tournament_list.html`
    and `src/api/templates/partials/_match_and_standings.html`.
- **JSON API**:
  - `/tournaments`, `/tournaments/{id}/matches`, `/tournaments/{id}/standings`, etc.
  - Used by API clients and `/docs`.

## 5) Persistence & Migrations
- **DB session/engine**: `src/infrastructure/db/session.py` (lazy engine initialization).
- **ORM models**: `src/infrastructure/db/models.py`.
- **Alembic**: `alembic/` + `alembic.ini`, configured in `alembic/env.py`.
- **Docker volume**: named volume `db_data` in `docker-compose.yml` for persistence.

## 6) Run with Docker
- See `README.md` for quick start and migration steps.
