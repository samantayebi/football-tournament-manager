from abc import ABC, abstractmethod
from typing import Any, Iterable, List


class TournamentRepository(ABC):
    @abstractmethod
    def create_tournament(self, tournament: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def get_tournament(self, tournament_id: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def list_tournaments(self) -> Iterable[Any]:
        raise NotImplementedError

    @abstractmethod
    def add_team(self, tournament_id: Any, team: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def list_teams(self, tournament_id: Any) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def create_match(self, tournament_id: Any, match: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def list_matches(self, tournament_id: Any) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def record_result(
        self, tournament_id: Any, match_id: Any, home_goals: int, away_goals: int
    ) -> Any:
        raise NotImplementedError
