from typing import Any, Dict, Iterable, List, Optional

from src.application.ports.tournament_repository import TournamentRepository


class InMemoryTournamentRepository(TournamentRepository):
    def __init__(self) -> None:
        self._tournaments: Dict[Any, Any] = {}

    def create_tournament(self, tournament: Any) -> Any:
        tournament_id = self._extract_id(tournament)
        if tournament_id is None:
            raise ValueError("Tournament id is required")

        self._tournaments[tournament_id] = tournament
        return tournament

    def get_tournament(self, tournament_id: Any) -> Optional[Any]:
        return self._tournaments.get(tournament_id)

    def list_tournaments(self) -> Iterable[Any]:
        return list(self._tournaments.values())

    def add_team(self, tournament_id: Any, team: Any) -> Any:
        tournament = self._require_tournament(tournament_id)
        teams = self._get_or_init_list(tournament, "teams")
        teams.append(team)
        return team

    def list_teams(self, tournament_id: Any) -> List[Any]:
        tournament = self._require_tournament(tournament_id)
        return list(self._get_or_init_list(tournament, "teams"))

    def create_match(self, tournament_id: Any, match: Any) -> Any:
        tournament = self._require_tournament(tournament_id)
        matches = self._get_or_init_list(tournament, "matches")
        matches.append(match)
        return match

    def list_matches(self, tournament_id: Any) -> List[Any]:
        tournament = self._require_tournament(tournament_id)
        return list(self._get_or_init_list(tournament, "matches"))

    def record_result(
        self, tournament_id: Any, match_id: Any, home_goals: int, away_goals: int
    ) -> Any:
        tournament = self._require_tournament(tournament_id)
        match = self._find_match(tournament, match_id)
        if match is None:
            raise ValueError("Match not found")

        if isinstance(match, dict):
            match["home_goals"] = home_goals
            match["away_goals"] = away_goals
        else:
            setattr(match, "home_goals", home_goals)
            setattr(match, "away_goals", away_goals)

        return match

    def _extract_id(self, tournament: Any) -> Optional[Any]:
        if isinstance(tournament, dict):
            return tournament.get("id")

        return getattr(tournament, "id", None)

    def _require_tournament(self, tournament_id: Any) -> Any:
        tournament = self.get_tournament(tournament_id)
        if tournament is None:
            raise ValueError("Tournament not found")
        return tournament

    def _get_or_init_list(self, tournament: Any, field: str) -> List[Any]:
        if isinstance(tournament, dict):
            items = tournament.get(field)
            if items is None:
                items = []
                tournament[field] = items
            return items

        items = getattr(tournament, field, None)
        if items is None:
            items = []
            setattr(tournament, field, items)
        return items

    def _find_match(self, tournament: Any, match_id: Any) -> Optional[Any]:
        for match in self._get_or_init_list(tournament, "matches"):
            if isinstance(match, dict):
                if match.get("id") == match_id:
                    return match
            else:
                if getattr(match, "id", None) == match_id:
                    return match
        return None
