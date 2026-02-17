from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TournamentModel(Base):
    __tablename__ = "tournaments"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)

    teams = relationship("TeamModel", back_populates="tournament")
    matches = relationship("MatchModel", back_populates="tournament")


class TeamModel(Base):
    __tablename__ = "teams"

    id = Column(String(36), primary_key=True)
    tournament_id = Column(String(36), ForeignKey("tournaments.id"), nullable=False)
    name = Column(String(255), nullable=False)

    tournament = relationship("TournamentModel", back_populates="teams")


class MatchModel(Base):
    __tablename__ = "matches"

    id = Column(String(36), primary_key=True)
    tournament_id = Column(String(36), ForeignKey("tournaments.id"), nullable=False)
    home_team_id = Column(String(36), nullable=False)
    away_team_id = Column(String(36), nullable=False)
    home_goals = Column(Integer, nullable=True)
    away_goals = Column(Integer, nullable=True)

    tournament = relationship("TournamentModel", back_populates="matches")
