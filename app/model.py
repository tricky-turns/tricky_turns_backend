from sqlalchemy import MetaData, Table, Column, Integer, String
from app.database import database

metadata = MetaData()

leaderboard = Table(
    "leaderboard",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True),
    Column("score", Integer),
)
