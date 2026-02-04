# football-tournament-manager

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn jinja2
uvicorn src.api.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Docker run

```bash
cp .env.example .env
docker compose up --build
```

Open `http://127.0.0.1:8000`.

## Tests

```bash
pip install pytest httpx
pytest
```