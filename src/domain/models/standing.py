from dataclasses import dataclass


@dataclass
class Standing:
    # Snapshot of a team's table statistics.
    team_id: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int

    @property
    def goal_diff(self) -> int:
        # Goal difference is derived, not stored.
        return self.goals_for - self.goals_against

