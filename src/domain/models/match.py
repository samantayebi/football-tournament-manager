from dataclasses import dataclass


@dataclass
class Match:
    # Match metadata and optional final score.
    id: str
    home_team_id: str
    away_team_id: str
    home_goals: int | None = None
    away_goals: int | None = None

    def is_played(self) -> bool:
        # Played only when both goal totals are set.
        return self.home_goals is not None and self.away_goals is not None

