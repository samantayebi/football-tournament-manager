from src.domain.models import Match, Team, Tournament
from src.domain.services import compute_standings


def make_team(team_id: str, name: str | None = None) -> Team:
    return Team(id=team_id, name=name or f"Team {team_id}")


def make_match(
    match_id: str,
    home_team_id: str,
    away_team_id: str,
    home_goals: int | None = None,
    away_goals: int | None = None,
) -> Match:
    return Match(
        id=match_id,
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        home_goals=home_goals,
        away_goals=away_goals,
    )


def make_tournament(
    teams: list[Team] | None = None,
    matches: list[Match] | None = None,
) -> Tournament:
    return Tournament(
        id="t1",
        name="Test Tournament",
        teams=teams or [],
        matches=matches or [],
    )


def test_empty_tournament_has_no_standings():
    tournament = make_tournament()

    standings = compute_standings(tournament)

    assert standings == []


def test_home_win_updates_points_and_stats():
    teams = [make_team("a", "Alpha"), make_team("b", "Beta")]
    matches = [make_match("m1", "a", "b", 2, 1)]
    tournament = make_tournament(teams, matches)

    standings = compute_standings(tournament)
    standings_by_id = {standing.team_id: standing for standing in standings}

    alpha = standings_by_id["a"]
    beta = standings_by_id["b"]
    assert alpha.played == 1
    assert alpha.wins == 1
    assert alpha.draws == 0
    assert alpha.losses == 0
    assert alpha.goals_for == 2
    assert alpha.goals_against == 1
    assert alpha.points == 3
    assert beta.played == 1
    assert beta.wins == 0
    assert beta.draws == 0
    assert beta.losses == 1
    assert beta.goals_for == 1
    assert beta.goals_against == 2
    assert beta.points == 0


def test_draw_gives_one_point_each():
    teams = [make_team("a", "Alpha"), make_team("b", "Beta")]
    matches = [make_match("m1", "a", "b", 1, 1)]
    tournament = make_tournament(teams, matches)

    standings = compute_standings(tournament)
    standings_by_id = {standing.team_id: standing for standing in standings}

    alpha = standings_by_id["a"]
    beta = standings_by_id["b"]
    assert alpha.points == 1
    assert alpha.draws == 1
    assert beta.points == 1
    assert beta.draws == 1


def test_tie_on_points_resolved_by_goal_difference():
    teams = [make_team("a", "Alpha"), make_team("b", "Beta")]
    matches = [
        make_match("m1", "a", "b", 3, 0),
        make_match("m2", "b", "a", 1, 0),
    ]
    tournament = make_tournament(teams, matches)

    standings = compute_standings(tournament)

    assert [standing.team_id for standing in standings] == ["a", "b"]


def test_tie_on_points_and_goal_diff_resolved_by_goals_for():
    teams = [
        make_team("a", "Alpha"),
        make_team("b", "Beta"),
        make_team("c", "Charlie"),
    ]
    matches = [
        make_match("m1", "a", "c", 2, 1),
        make_match("m2", "b", "c", 1, 0),
    ]
    tournament = make_tournament(teams, matches)

    standings = compute_standings(tournament)

    assert [standing.team_id for standing in standings[:2]] == ["a", "b"]


def test_final_tie_break_by_team_name():
    teams = [
        make_team("t2", "Zulu"),
        make_team("t1", "Alpha"),
        make_team("t3", "Beta"),
    ]
    tournament = make_tournament(teams, [])

    standings = compute_standings(tournament)

    assert [standing.team_id for standing in standings] == ["t1", "t3", "t2"]
