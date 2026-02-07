from typing import Any, Dict, Iterable, Optional

from src.application.ports.tournament_repository import TournamentRepository


class InMemoryTournamentRepository(TournamentRepository):
    def __init__(self) -> None:
        self._tournaments: Dict[int, Any] = {}
        self._next_id = 1

    def create_tournament(self, tournament: Any) -> Any:
        tournament_id = self._extract_id(tournament)
        if tournament_id is None:
            tournament_id = self._next_id
            self._next_id += 1
            tournament = self._attach_id(tournament, tournament_id)

        self._tournaments[int(tournament_id)] = tournament
        return tournament

    def get_tournament(self, tournament_id: Any) -> Optional[Any]:
        try:
            return self._tournaments.get(int(tournament_id))
        except (TypeError, ValueError):
            return None

    def list_tournaments(self) -> Iterable[Any]:
        return list(self._tournaments.values())

    def _extract_id(self, tournament: Any) -> Optional[int]:
        if isinstance(tournament, dict):
            value = tournament.get("id")
            return int(value) if value is not None else None

        value = getattr(tournament, "id", None)
        return int(value) if value is not None else None

    def _attach_id(self, tournament: Any, tournament_id: int) -> Any:
        if isinstance(tournament, dict):
            return {**tournament, "id": tournament_id}

        if hasattr(tournament, "__dict__"):
            setattr(tournament, "id", tournament_id)
            return tournament

        return {"id": tournament_id, "value": tournament}
