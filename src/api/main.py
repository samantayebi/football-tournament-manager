import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.application.use_cases.create_match import CreateMatchUseCase
from src.application.use_cases.create_tournament import CreateTournamentUseCase
from src.application.use_cases.enroll_team import EnrollTeamUseCase
from src.application.use_cases.list_tournaments import ListTournamentsUseCase
from src.application.use_cases.record_match_result import RecordMatchResultUseCase
from src.domain.models import Match, Team, Tournament
from src.domain.services import compute_standings
from src.infrastructure.repositories.in_memory_tournament_repository import (
    InMemoryTournamentRepository,
)
from src.infrastructure.repositories.mysql_tournament_repository import (
    MySQLTournamentRepository,
)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
repository = (
    MySQLTournamentRepository()
    if os.getenv("DATABASE_URL")
    else InMemoryTournamentRepository()
)
list_tournaments_use_case = ListTournamentsUseCase(repository)
create_tournament_use_case = CreateTournamentUseCase(repository)
enroll_team_use_case = EnrollTeamUseCase(repository)
create_match_use_case = CreateMatchUseCase(repository)
record_match_result_use_case = RecordMatchResultUseCase(repository)


class TournamentCreateRequest(BaseModel):
    name: str


class TeamCreateRequest(BaseModel):
    name: str


class MatchCreateRequest(BaseModel):
    home_team_id: str
    away_team_id: str


class MatchResultRequest(BaseModel):
    home_goals: int
    away_goals: int


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    tournaments = list_tournaments_use_case.execute()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Football Tournament Manager",
            "tournaments": tournaments,
        },
    )


@app.post("/ui/tournaments", response_class=HTMLResponse)
async def create_tournament_ui(request: Request):
    form = await request.form()
    name = form.get("name")
    if not name:
        tournaments = list_tournaments_use_case.execute()
        return templates.TemplateResponse(
            "partials/_tournament_list.html",
            {"request": request, "tournaments": tournaments},
        )

    create_tournament_use_case.execute(str(name))
    tournaments = list_tournaments_use_case.execute()
    return templates.TemplateResponse(
        "partials/_tournament_list.html",
        {"request": request, "tournaments": tournaments},
    )


@app.get("/tournaments")
def list_tournaments():
    return list_tournaments_use_case.execute()


@app.post("/tournaments")
def create_tournament(payload: TournamentCreateRequest):
    return create_tournament_use_case.execute(payload.name)


@app.post("/tournaments/{tournament_id}/teams")
def enroll_team(tournament_id: str, payload: TeamCreateRequest):
    return enroll_team_use_case.execute(tournament_id, payload.name)


@app.post("/tournaments/{tournament_id}/matches")
def create_match(tournament_id: str, payload: MatchCreateRequest):
    return create_match_use_case.execute(
        tournament_id, payload.home_team_id, payload.away_team_id
    )


@app.post("/tournaments/{tournament_id}/matches/{match_id}/result")
def record_match_result(
    tournament_id: str, match_id: str, payload: MatchResultRequest
):
    return record_match_result_use_case.execute(
        tournament_id, match_id, payload.home_goals, payload.away_goals
    )


@app.get("/tournaments/{tournament_id}/standings")
def get_standings(tournament_id: str):
    tournament = repository.get_tournament(tournament_id)
    if tournament is None:
        raise HTTPException(status_code=404, detail="Tournament not found")

    domain_tournament = _to_domain_tournament(tournament)
    standings = compute_standings(domain_tournament)
    return [_standing_to_dict(standing) for standing in standings]


def _to_domain_tournament(tournament: object) -> Tournament:
    if isinstance(tournament, dict):
        teams = [_to_domain_team(team) for team in tournament.get("teams") or []]
        matches = [
            _to_domain_match(match) for match in tournament.get("matches") or []
        ]
        return Tournament(
            id=str(tournament.get("id")),
            name=str(tournament.get("name")),
            teams=teams,
            matches=matches,
        )

    teams = [_to_domain_team(team) for team in getattr(tournament, "teams", []) or []]
    matches = [
        _to_domain_match(match) for match in getattr(tournament, "matches", []) or []
    ]
    return Tournament(
        id=str(getattr(tournament, "id")),
        name=str(getattr(tournament, "name")),
        teams=teams,
        matches=matches,
    )


def _to_domain_team(team: object) -> Team:
    if isinstance(team, dict):
        return Team(id=str(team.get("id")), name=str(team.get("name")))
    return Team(id=str(getattr(team, "id")), name=str(getattr(team, "name")))


def _to_domain_match(match: object) -> Match:
    if isinstance(match, dict):
        return Match(
            id=str(match.get("id")),
            home_team_id=str(match.get("home_team_id")),
            away_team_id=str(match.get("away_team_id")),
            home_goals=match.get("home_goals"),
            away_goals=match.get("away_goals"),
        )
    return Match(
        id=str(getattr(match, "id")),
        home_team_id=str(getattr(match, "home_team_id")),
        away_team_id=str(getattr(match, "away_team_id")),
        home_goals=getattr(match, "home_goals", None),
        away_goals=getattr(match, "away_goals", None),
    )


def _standing_to_dict(standing: object) -> dict:
    return {
        "team_id": standing.team_id,
        "played": standing.played,
        "wins": standing.wins,
        "draws": standing.draws,
        "losses": standing.losses,
        "goals_for": standing.goals_for,
        "goals_against": standing.goals_against,
        "points": standing.points,
        "goal_diff": standing.goal_diff,
    }
