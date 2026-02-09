from typing import Any, Dict
from uuid import uuid4

from src.application.ports.tournament_repository import TournamentRepository


class EnrollTeamUseCase:
    def __init__(self, repository: TournamentRepository) -> None:
        self._repository = repository

    def execute(self, tournament_id: Any, team_name: str) -> Dict[str, Any]:
        team = {"id": str(uuid4()), "name": team_name}
        self._repository.add_team(tournament_id, team)
        return team
