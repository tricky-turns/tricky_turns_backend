# app/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ScoreSubmitRequest(BaseModel):
    mode_id: int = Field(..., description="Game mode ID")
    score: int = Field(..., ge=0, description="Score achieved")
    session_id: int = Field(..., description="Session ID")

class ScoreSubmitResponse(BaseModel):
    message: str

class SessionStartRequest(BaseModel):
    mode_id: int = Field(..., description="Game mode ID")
    device_id: Optional[str] = Field(None, description="Device identifier")
    platform: Optional[str] = Field(None, description="Platform (ios/android/web)")
    client_version: Optional[str] = Field(None, description="Client app version")

class SessionStartResponse(BaseModel):
    session_id: int

class SessionEndRequest(BaseModel):
    session_id: int = Field(..., description="Session ID")
    final_score: int = Field(..., ge=0, description="Final score for this session")

class SessionEndResponse(BaseModel):
    message: str

class ShopBuyRequest(BaseModel):
    item_id: int = Field(..., description="ID of the shop item")
    amount: float = Field(..., ge=0, description="Purchase amount")
    tx_hash: Optional[str] = Field(None, description="Blockchain transaction hash")

class ShopBuyResponse(BaseModel):
    message: str

class ContestEntryRequest(BaseModel):
    session_id: int = Field(..., description="Session ID used for contest entry")
    score: int = Field(..., ge=0, description="Score achieved in contest session")

class ContestEntryResponse(BaseModel):
    message: str

class SupportTicketRequest(BaseModel):
    subject: str = Field(..., min_length=3, max_length=80, description="Short subject line")
    message: str = Field(..., min_length=8, max_length=2048, description="Detailed message")

class SupportTicketResponse(BaseModel):
    ticket_id: int
    message: str

class PromoRedeemRequest(BaseModel):
    code: str = Field(..., min_length=3, max_length=32, description="Promo or referral code")

class PromoRedeemResponse(BaseModel):
    message: str
class AdminUserActionRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)

# --- Game Mode ---
class AdminGameModeCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=40)
    description: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = True

class AdminGameModeUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=40)
    description: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None

# --- Shop Item ---
class AdminShopItemRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    description: Optional[str] = Field(None, max_length=200)
    price: float = Field(..., ge=0)
    type: Optional[str] = Field(None, max_length=24)
    is_active: Optional[bool] = True

# --- Contest ---
class AdminContestRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=64)
    mode_id: int
    start_at: datetime
    end_at: datetime
    entry_fee: float = Field(..., ge=0)
    reward_pool: float = Field(..., ge=0)
    status: str = Field(..., max_length=20)
    winner_username: Optional[str] = Field(None, max_length=64)

class AdminContestUpdateRequest(BaseModel):
    name: Optional[str]
    mode_id: Optional[int]
    start_at: Optional[datetime]
    end_at: Optional[datetime]
    entry_fee: Optional[float]
    reward_pool: Optional[float]
    status: Optional[str]
    winner_username: Optional[str]

# --- Promo Code ---
class AdminPromoCodeRequest(BaseModel):
    code: str = Field(..., min_length=3, max_length=32)
    reward: str = Field(..., min_length=1, max_length=80)
    uses: Optional[int] = 0
    max_uses: Optional[int] = None
    is_active: Optional[bool] = True

class AdminPromoCodeUpdateRequest(BaseModel):
    code: Optional[str]
    reward: Optional[str]
    uses: Optional[int]
    max_uses: Optional[int]
    is_active: Optional[bool]

# --- Feature Toggle ---
class AdminFeatureToggleRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=32)
    enabled: bool = False
    description: Optional[str] = Field(None, max_length=100)

class AdminFeatureToggleUpdateRequest(BaseModel):
    name: Optional[str]
    enabled: Optional[bool]
    description: Optional[str]

# --- Game Modes ---
class GameModeOut(BaseModel):
    id: int
    name: str
    description: str
    is_active: bool
    created_at: datetime

# --- Leaderboard Entry ---
class LeaderboardEntryOut(BaseModel):
    id: int
    username: str
    mode_id: int
    score: int
    achieved_at: datetime

# --- Leaderboard List (array) ---
class LeaderboardListOut(BaseModel):
    __root__: List[LeaderboardEntryOut]

# --- Score History ---
class ScoreHistoryEntryOut(BaseModel):
    id: int
    username: str
    mode_id: int
    score: int
    session_id: int
    submitted_at: datetime
    ip_address: str = None
    device_info: str = None

class ScoreHistoryListOut(BaseModel):
    __root__: List[ScoreHistoryEntryOut]


class FeatureToggleOut(BaseModel):
    id: int
    name: str
    enabled: bool
    description: Optional[str]

class ShopItemOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    type: Optional[str]
    is_active: bool

class PurchaseOut(BaseModel):
    id: int
    username: str
    item_id: int
    amount: float
    tx_hash: Optional[str]
    purchased_at: datetime
    status: str

class ContestOut(BaseModel):
    id: int
    name: str
    mode_id: int
    start_at: datetime
    end_at: datetime
    entry_fee: float
    reward_pool: float
    status: str
    winner_username: Optional[str]

class ContestEntryOut(BaseModel):
    id: int
    contest_id: int
    username: str
    session_id: int
    score: int
    entered_at: datetime
    prize_awarded: Optional[float]

class SupportTicketOut(BaseModel):
    id: int
    username: str
    subject: str
    message: str
    status: str
    created_at: datetime