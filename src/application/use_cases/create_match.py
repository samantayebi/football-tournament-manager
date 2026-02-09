from typing import Any, Dict
from uuid import uuid4

from src.application.ports.tournament_repository import TournamentRepository


class CreateMatchUseCase:
    def __init__(self, repository: TournamentRepository) -> None:
        self._repository = repository

    def execute(
        self, tournament_id: Any, home_team_id: Any, away_team_id: Any
    ) -> Dict[str, Any]:
        match = {
            "id": str(uuid4()),
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "home_goals": None,
            "away_goals": None,
        }
        created = self._repository.create_match(tournament_id, match)
        return created if isinstance(created, dict) else {"id": match["id"]}
