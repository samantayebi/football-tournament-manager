from typing import Any, Iterable, List, Optional

from sqlalchemy.orm import Session

from src.application.ports.tournament_repository import TournamentRepository
from src.infrastructure.db.models import MatchModel, TeamModel, TournamentModel
from src.infrastructure.db.session import get_session


class MySQLTournamentRepository(TournamentRepository):
    def create_tournament(self, tournament: Any) -> Any:
        tournament_id = _get_field(tournament, "id")
        name = _get_field(tournament, "name")
        if not tournament_id:
            raise ValueError("Tournament id is required")
        if not name:
            raise ValueError("Tournament name is required")

        with get_session() as session:
            try:
                existing = session.get(TournamentModel, tournament_id)
                if existing is None:
                    existing = TournamentModel(
                        id=tournament_id,
                        name=name,
                    )
                    session.add(existing)
                else:
                    existing.name = name
                session.commit()
                return _tournament_to_dict(existing)
            except Exception:
                session.rollback()
                raise

    def get_tournament(self, tournament_id: Any) -> Optional[Any]:
        with get_session() as session:
            tournament = session.get(TournamentModel, tournament_id)
            if tournament is None:
                return None
            return _tournament_to_dict(tournament)

    def list_tournaments(self) -> Iterable[Any]:
        with get_session() as session:
            tournaments = session.query(TournamentModel).all()
            return [_tournament_to_dict(tournament) for tournament in tournaments]

    def add_team(self, tournament_id: Any, team: Any) -> Any:
        team_id = _get_field(team, "id")
        name = _get_field(team, "name")
        if not team_id:
            raise ValueError("Team id is required")
        if not name:
            raise ValueError("Team name is required")

        with get_session() as session:
            try:
                _require_tournament(session, tournament_id)
                model = TeamModel(
                    id=team_id, tournament_id=tournament_id, name=name
                )
                session.add(model)
                session.commit()
                return _team_to_dict(model)
            except Exception:
                session.rollback()
                raise

    def list_teams(self, tournament_id: Any) -> List[Any]:
        with get_session() as session:
            _require_tournament(session, tournament_id)
            teams = (
                session.query(TeamModel)
                .filter(TeamModel.tournament_id == tournament_id)
                .all()
            )
            return [_team_to_dict(team) for team in teams]

    def create_match(self, tournament_id: Any, match: Any) -> Any:
        match_id = _get_field(match, "id")
        home_team_id = _get_field(match, "home_team_id")
        away_team_id = _get_field(match, "away_team_id")
        if not match_id:
            raise ValueError("Match id is required")
        if not home_team_id or not away_team_id:
            raise ValueError("Match team ids are required")

        with get_session() as session:
            try:
                _require_tournament(session, tournament_id)
                model = MatchModel(
                    id=match_id,
                    tournament_id=tournament_id,
                    home_team_id=home_team_id,
                    away_team_id=away_team_id,
                    home_goals=_get_field(match, "home_goals"),
                    away_goals=_get_field(match, "away_goals"),
                )
                session.add(model)
                session.commit()
                return _match_to_dict(model)
            except Exception:
                session.rollback()
                raise

    def list_matches(self, tournament_id: Any) -> List[Any]:
        with get_session() as session:
            _require_tournament(session, tournament_id)
            matches = (
                session.query(MatchModel)
                .filter(MatchModel.tournament_id == tournament_id)
                .all()
            )
            return [_match_to_dict(match) for match in matches]

    def record_result(
        self, tournament_id: Any, match_id: Any, home_goals: int, away_goals: int
    ) -> Any:
        with get_session() as session:
            try:
                _require_tournament(session, tournament_id)
                match = (
                    session.query(MatchModel)
                    .filter(
                        MatchModel.tournament_id == tournament_id,
                        MatchModel.id == match_id,
                    )
                    .one_or_none()
                )
                if match is None:
                    raise ValueError("Match not found")

                match.home_goals = home_goals
                match.away_goals = away_goals
                session.commit()
                return _match_to_dict(match)
            except Exception:
                session.rollback()
                raise


def _get_field(obj: Any, name: str) -> Optional[Any]:
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def _require_tournament(session: Session, tournament_id: Any) -> TournamentModel:
    tournament = session.get(TournamentModel, tournament_id)
    if tournament is None:
        raise ValueError("Tournament not found")
    return tournament


def _tournament_to_dict(model: TournamentModel) -> dict:
    return {
        "id": model.id,
        "name": model.name,
        "teams": [_team_to_dict(team) for team in list(model.teams or [])],
        "matches": [_match_to_dict(match) for match in list(model.matches or [])],
    }


def _team_to_dict(model: TeamModel) -> dict:
    return {"id": model.id, "tournament_id": model.tournament_id, "name": model.name}


def _match_to_dict(model: MatchModel) -> dict:
    return {
        "id": model.id,
        "tournament_id": model.tournament_id,
        "home_team_id": model.home_team_id,
        "away_team_id": model.away_team_id,
        "home_goals": model.home_goals,
        "away_goals": model.away_goals,
    }
