from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.application.use_cases.list_tournaments import ListTournamentsUseCase
from src.infrastructure.repositories.in_memory_tournament_repository import (
    InMemoryTournamentRepository,
)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
repository = InMemoryTournamentRepository()
list_tournaments_use_case = ListTournamentsUseCase(repository)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Football Tournament Manager"},
    )


@app.get("/tournaments")
def list_tournaments():
    return list_tournaments_use_case.execute()
