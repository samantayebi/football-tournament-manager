from abc import ABC, abstractmethod
from typing import Any, Iterable


class TournamentRepository(ABC):
    @abstractmethod
    def create_tournament(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def get_tournament(self, tournament_id: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def list_tournaments(self) -> Iterable[Any]:
        raise NotImplementedError
