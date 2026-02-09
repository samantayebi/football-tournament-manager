from typing import Any, Dict

from src.application.ports.tournament_repository import TournamentRepository


class RecordMatchResultUseCase:
    def __init__(self, repository: TournamentRepository) -> None:
        self._repository = repository

    def execute(
        self,
        tournament_id: Any,
        match_id: Any,
        home_goals: int,
        away_goals: int,
    ) -> Dict[str, Any]:
        if home_goals < 0 or away_goals < 0:
            raise ValueError("Goals must be non-negative")

        match = self._repository.record_result(
            tournament_id, match_id, home_goals, away_goals
        )
        return match if isinstance(match, dict) else {"id": match_id}
