from sqlalchemy import MetaData, Table, Column, Integer, String, UniqueConstraint
from app.database import database

metadata = MetaData()

leaderboard = Table(
    "leaderboard",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True),  # Pi username as unique identity
    Column("score", Integer),
)
