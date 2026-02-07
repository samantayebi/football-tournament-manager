from typing import Any, List

from src.application.ports.tournament_repository import TournamentRepository


class ListTournamentsUseCase:
    def __init__(self, repository: TournamentRepository) -> None:
        self._repository = repository

    def execute(self) -> List[Any]:
        return list(self._repository.list_tournaments() or [])
