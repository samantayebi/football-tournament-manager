from dataclasses import dataclass


@dataclass
class Team:
    # Minimal team data used across the domain.
    id: str
    name: str

