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


@app.post("/ui/tournaments/{tournament_id}/teams", response_class=HTMLResponse)
async def add_team_ui(request: Request, tournament_id: str):
    form = await request.form()
    name = form.get("name")
    tournament = repository.get_tournament(tournament_id)
    if tournament is None:
        return templates.TemplateResponse(
            "partials/_teams.html",
            {
                "request": request,
                "tournament": {"id": tournament_id, "teams": []},
                "error": "Tournament not found",
            },
            status_code=404,
        )

    if not name:
        return templates.TemplateResponse(
            "partials/_teams.html",
            {
                "request": request,
                "tournament": tournament,
                "error": "Team name is required",
            },
        )

    try:
        enroll_team_use_case.execute(tournament_id, str(name))
    except Exception as exc:
        return templates.TemplateResponse(
            "partials/_teams.html",
            {
                "request": request,
                "tournament": tournament,
                "error": str(exc),
            },
        )

    tournament = repository.get_tournament(tournament_id)
    return templates.TemplateResponse(
        "partials/_teams.html",
        {"request": request, "tournament": tournament},
    )


@app.post("/ui/tournaments/{tournament_id}/matches", response_class=HTMLResponse)
async def create_match_ui(request: Request, tournament_id: str):
    form = await request.form()
    home_team_id = form.get("home_team_id")
    away_team_id = form.get("away_team_id")
    tournament = repository.get_tournament(tournament_id)
    if tournament is None:
        return templates.TemplateResponse(
            "partials/_matches.html",
            {
                "request": request,
                "tournament": {"id": tournament_id, "teams": [], "matches": []},
                "team_name_by_id": {},
                "error": "Tournament not found",
            },
            status_code=404,
        )

    if not home_team_id or not away_team_id:
        return templates.TemplateResponse(
            "partials/_matches.html",
            {
                "request": request,
                "tournament": tournament,
                "team_name_by_id": _team_name_by_id(tournament),
                "error": "Both teams are required",
            },
        )

    if home_team_id == away_team_id:
        return templates.TemplateResponse(
            "partials/_matches.html",
            {
                "request": request,
                "tournament": tournament,
                "team_name_by_id": _team_name_by_id(tournament),
                "error": "Home and away teams must be different",
            },
        )

    try:
        create_match_use_case.execute(
            tournament_id, str(home_team_id), str(away_team_id)
        )
    except Exception as exc:
        return templates.TemplateResponse(
            "partials/_matches.html",
            {
                "request": request,
                "tournament": tournament,
                "team_name_by_id": _team_name_by_id(tournament),
                "error": str(exc),
            },
        )

    tournament = repository.get_tournament(tournament_id)
    return templates.TemplateResponse(
        "partials/_matches.html",
        {
            "request": request,
            "tournament": tournament,
            "team_name_by_id": _team_name_by_id(tournament),
        },
    )


@app.post(
    "/ui/tournaments/{tournament_id}/matches/{match_id}/result",
    response_class=HTMLResponse,
)
async def record_match_result_ui(
    request: Request, tournament_id: str, match_id: str
):
    form = await request.form()
    home_goals = form.get("home_goals")
    away_goals = form.get("away_goals")
    tournament = repository.get_tournament(tournament_id)
    if tournament is None:
        return templates.TemplateResponse(
            "partials/_match_and_standings.html",
            {
                "request": request,
                "tournament": {"id": tournament_id, "teams": [], "matches": []},
                "standings": [],
                "team_name_by_id": {},
                "error": "Tournament not found",
            },
            status_code=404,
        )

    try:
        record_match_result_use_case.execute(
            tournament_id, match_id, int(home_goals), int(away_goals)
        )
    except Exception as exc:
        domain_tournament = _to_domain_tournament(tournament)
        standings = compute_standings(domain_tournament)
        return templates.TemplateResponse(
            "partials/_match_and_standings.html",
            {
                "request": request,
                "tournament": tournament,
                "standings": [_standing_to_dict(standing) for standing in standings],
                "team_name_by_id": _team_name_by_id(tournament),
                "error": str(exc),
            },
        )

    tournament = repository.get_tournament(tournament_id)
    domain_tournament = _to_domain_tournament(tournament)
    standings = compute_standings(domain_tournament)
    return templates.TemplateResponse(
        "partials/_match_and_standings.html",
        {
            "request": request,
            "tournament": tournament,
            "standings": [_standing_to_dict(standing) for standing in standings],
            "team_name_by_id": _team_name_by_id(tournament),
        },
    )


@app.get("/tournaments")
def list_tournaments():
    return list_tournaments_use_case.execute()


@app.get("/tournaments/{tournament_id}", response_class=HTMLResponse)
def tournament_detail(request: Request, tournament_id: str):
    tournament = repository.get_tournament(tournament_id)
    if tournament is None:
        return templates.TemplateResponse(
            "tournament_detail.html",
            {
                "request": request,
                "tournament": {"id": tournament_id, "name": "Tournament not found"},
                "standings": [],
            },
            status_code=404,
        )

    domain_tournament = _to_domain_tournament(tournament)
    standings = compute_standings(domain_tournament)
    return templates.TemplateResponse(
        "tournament_detail.html",
        {
            "request": request,
            "tournament": tournament,
            "standings": [_standing_to_dict(standing) for standing in standings],
            "team_name_by_id": _team_name_by_id(tournament),
        },
    )


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


def _team_name_by_id(tournament: object) -> dict:
    teams = []
    if isinstance(tournament, dict):
        teams = tournament.get("teams") or []
    else:
        teams = getattr(tournament, "teams", []) or []

    name_by_id = {}
    for team in teams:
        if isinstance(team, dict):
            team_id = team.get("id")
            name = team.get("name")
        else:
            team_id = getattr(team, "id", None)
            name = getattr(team, "name", None)
        if team_id is not None and name is not None:
            name_by_id[str(team_id)] = str(name)
    return name_by_id
