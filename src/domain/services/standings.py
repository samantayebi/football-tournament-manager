from ..models import Standing, Tournament


def compute_standings(tournament: Tournament) -> list[Standing]:
    team_by_id: dict[str, Team] = {team.id: team for team in tournament.teams}

    standings_by_id: dict[str, Standing] = {
        team.id: Standing(
            team_id=team.id,
            played=0,
            wins=0,
            draws=0,
            losses=0,
            goals_for=0,
            goals_against=0,
            points=0,
        )
        for team in tournament.teams
    }

    for match in tournament.matches:
        if not match.is_played():
            continue

        home = standings_by_id.get(match.home_team_id)
        away = standings_by_id.get(match.away_team_id)
        if home is None or away is None:
            continue

        home_goals = match.home_goals or 0
        away_goals = match.away_goals or 0

        home.played += 1
        away.played += 1
        home.goals_for += home_goals
        home.goals_against += away_goals
        away.goals_for += away_goals
        away.goals_against += home_goals

        if home_goals > away_goals:
            home.wins += 1
            home.points += 3
            away.losses += 1
        elif home_goals < away_goals:
            away.wins += 1
            away.points += 3
            home.losses += 1
        else:
            home.draws += 1
            away.draws += 1
            home.points += 1
            away.points += 1

    return sorted(
        standings_by_id.values(),
        key=lambda standing: (
            -standing.points,
            -standing.goal_diff,
            -standing.goals_for,
            team_by_id.get(standing.team_id).name
            if team_by_id.get(standing.team_id) is not None
            else "",
        ),
    )
