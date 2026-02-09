from typing import Any, Dict
from uuid import uuid4

from src.application.ports.tournament_repository import TournamentRepository


class CreateTournamentUseCase:
    def __init__(self, repository: TournamentRepository) -> None:
        self._repository = repository

    def execute(self, name: str) -> Dict[str, Any]:
        tournament = {"id": str(uuid4()), "name": name, "teams": [], "matches": []}
        created = self._repository.create_tournament(tournament)
        return created if isinstance(created, dict) else {"id": created.id, "name": name}
