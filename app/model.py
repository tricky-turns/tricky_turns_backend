# app/model.py

from sqlalchemy import (
    MetaData, Table, Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, UniqueConstraint
)
from datetime import datetime

metadata = MetaData()

# Users (Players)
users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),  # Pi username
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("last_login", DateTime),
    Column("is_banned", Boolean, default=False)
)

# Admins (Backend)
admins = Table(
    "admins", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("email", String, unique=True),
    Column("password_hash", String, nullable=False),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime, default=datetime.utcnow)
)

# Game Modes
game_modes = Table(
    "game_modes", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, unique=True, nullable=False),
    Column("description", Text),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime, default=datetime.utcnow)
)

# Leaderboard (best score per user, per mode)
leaderboard_scores = Table(
    "leaderboard_scores", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, ForeignKey("users.username"), nullable=False),
    Column("mode_id", Integer, ForeignKey("game_modes.id"), nullable=False),
    Column("score", Integer, nullable=False),
    Column("achieved_at", DateTime, default=datetime.utcnow),
    UniqueConstraint("username", "mode_id", name="uix_user_mode")
)

# Score history (all attempts, append-only)
score_history = Table(
    "score_history", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, ForeignKey("users.username")),
    Column("mode_id", Integer, ForeignKey("game_modes.id")),
    Column("score", Integer, nullable=False),
    Column("session_id", Integer, ForeignKey("game_sessions.id")),
    Column("submitted_at", DateTime, default=datetime.utcnow),
    Column("ip_address", String),
    Column("device_info", String),
)

# Game sessions (for anti-fraud, analytics, contest linkage)
game_sessions = Table(
    "game_sessions", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, ForeignKey("users.username")),
    Column("mode_id", Integer, ForeignKey("game_modes.id")),
    Column("started_at", DateTime),
    Column("ended_at", DateTime),
    Column("final_score", Integer),
    Column("device_id", String),
    Column("platform", String),
    Column("client_version", String),
    Column("cheat_flag", Boolean, default=False),
    Column("disconnect_reason", String)
)

# Shop Items (IAP/virtual goods)
shop_items = Table(
    "shop_items", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("description", Text),
    Column("price", Float, nullable=False),
    Column("type", String),  # skin, boost, ticket, etc.
    Column("is_active", Boolean, default=True)
)

# Purchases (in-app purchases)
purchases = Table(
    "purchases", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, ForeignKey("users.username")),
    Column("item_id", Integer, ForeignKey("shop_items.id")),
    Column("amount", Float),
    Column("tx_hash", String),
    Column("purchased_at", DateTime, default=datetime.utcnow),
    Column("status", String)  # pending/completed/failed
)

# Contests (scheduled paid competitions)
contests = Table(
    "contests", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("mode_id", Integer, ForeignKey("game_modes.id")),
    Column("start_at", DateTime),
    Column("end_at", DateTime),
    Column("entry_fee", Float),
    Column("reward_pool", Float),
    Column("status", String),
    Column("winner_username", String, ForeignKey("users.username"))
)

# Contest entries (user participation in contests)
contest_entries = Table(
    "contest_entries", metadata,
    Column("id", Integer, primary_key=True),
    Column("contest_id", Integer, ForeignKey("contests.id")),
    Column("username", String, ForeignKey("users.username")),
    Column("session_id", Integer, ForeignKey("game_sessions.id")),
    Column("score", Integer),
    Column("entered_at", DateTime, default=datetime.utcnow),
    Column("prize_awarded", Float)
)

# Admin audit log (full traceability)
admin_audit_log = Table(
    "admin_audit_log", metadata,
    Column("id", Integer, primary_key=True),
    Column("admin_username", String, ForeignKey("admins.username")),
    Column("action", String),
    Column("target_table", String),
    Column("target_id", Integer),
    Column("notes", Text),
    Column("timestamp", DateTime, default=datetime.utcnow)
)

# Player support tickets
support_tickets = Table(
    "support_tickets", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, ForeignKey("users.username")),
    Column("subject", String),
    Column("message", Text),
    Column("status", String, default="open"),
    Column("created_at", DateTime, default=datetime.utcnow)
)

# Promo codes/referral (marketing)
promo_codes = Table(
    "promo_codes", metadata,
    Column("id", Integer, primary_key=True),
    Column("code", String, unique=True),
    Column("reward", String),
    Column("uses", Integer, default=0),
    Column("max_uses", Integer),
    Column("is_active", Boolean, default=True)
)

# Feature toggles (feature readiness, A/B tests)
feature_toggles = Table(
    "feature_toggles", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, unique=True),
    Column("enabled", Boolean, default=False),
    Column("description", Text)
)


admin_sessions = Table(
    "admin_sessions", metadata,
    Column("id", String, primary_key=True),  # session_id, use secrets.token_urlsafe
    Column("admin_id", Integer, ForeignKey("admins.id"), nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("expires_at", DateTime)
)