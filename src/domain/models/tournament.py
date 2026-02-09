from dataclasses import dataclass, field

from .match import Match
from .team import Team


@dataclass
class Tournament:
    # Aggregate root holding teams and scheduled matches.
    id: str
    name: str
    teams: list[Team] = field(default_factory=list)
    matches: list[Match] = field(default_factory=list)

