from sqlalchemy import MetaData, Table, Column, Integer, String
from app.database import database

metadata = MetaData()

leaderboard = Table(
    "leaderboard",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("owner_id", String, unique=True),   # ✅ add this
    Column("username", String),                # ✅ not unique — usernames can change
    Column("score", Integer),
)

