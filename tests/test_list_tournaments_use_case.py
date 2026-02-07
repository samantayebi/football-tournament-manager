from src.application.use_cases.list_tournaments import ListTournamentsUseCase
from src.infrastructure.repositories.in_memory_tournament_repository import (
    InMemoryTournamentRepository,
)


def test_list_tournaments_empty_repository():
    repository = InMemoryTournamentRepository()
    use_case = ListTournamentsUseCase(repository)

    result = use_case.execute()

    assert result == []
