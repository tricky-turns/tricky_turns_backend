# app/routes.py

from fastapi import APIRouter, Depends, HTTPException, Query
from app.auth import verify_token
from app.model import (
    users, game_modes, leaderboard_scores, score_history, game_sessions,
    shop_items, purchases, contests, contest_entries, support_tickets,
    promo_codes, feature_toggles
)
from app.database import database
from sqlalchemy import func, select
from datetime import datetime
from app.schemas import (
    ScoreSubmitRequest, ScoreSubmitResponse, SessionStartRequest, 
    SessionStartResponse, SessionEndRequest, SessionEndResponse, 
    ShopBuyRequest, ShopBuyResponse, ContestEntryRequest, ContestEntryResponse,
    SupportTicketRequest, SupportTicketResponse, PromoRedeemRequest, PromoRedeemResponse,
    GameModeOut, LeaderboardEntryOut, ScoreHistoryEntryOut, FeatureToggleOut,ShopItemOut,
    PurchaseOut, SupportTicketOut, ContestOut, ContestEntryOut
)
from typing import List

router = APIRouter()

# ---------- GAME MODES ----------

@router.get("/modes", response_model=List[GameModeOut])
async def list_modes():
    query = game_modes.select().where(game_modes.c.is_active == True)
    return await database.fetch_all(query)

# ---------- LEADERBOARD (MODE-AWARE) ----------

@router.get("/leaderboard", response_model=List[LeaderboardEntryOut])
async def get_leaderboard(mode_id: int = Query(...), top: int = 100):
    query = leaderboard_scores.select().where(
        leaderboard_scores.c.mode_id == mode_id
    ).order_by(leaderboard_scores.c.score.desc()).limit(top)
    return await database.fetch_all(query)

@router.get("/leaderboard/me", response_model=LeaderboardEntryOut)
async def get_my_score(mode_id: int = Query(...), user: dict = Depends(verify_token)):
    username = user.get("username")
    query = leaderboard_scores.select().where(
        (leaderboard_scores.c.username == username) &
        (leaderboard_scores.c.mode_id == mode_id)
    )
    result = await database.fetch_one(query)
    if not result:
        raise HTTPException(status_code=404, detail="No score found for this user and mode")
    return result

@router.get("/leaderboard/rank")
async def get_my_rank(mode_id: int = Query(...), user: dict = Depends(verify_token)):
    username = user.get("username")
    user_query = leaderboard_scores.select().where(
        (leaderboard_scores.c.username == username) &
        (leaderboard_scores.c.mode_id == mode_id)
    )
    user_score = await database.fetch_one(user_query)
    if not user_score:
        raise HTTPException(status_code=404, detail="No score found for this user and mode")
    rank_query = select([func.count()]).select_from(leaderboard_scores).where(
        (leaderboard_scores.c.mode_id == mode_id) &
        (leaderboard_scores.c.score > user_score["score"])
    )
    rank = await database.fetch_val(rank_query)
    return {
        "rank": rank + 1,
        "score": user_score["score"],
    }

# ---------- SCORE SUBMISSION & HISTORY ----------

@router.post("/score/submit", response_model=ScoreSubmitResponse)
async def submit_score(
    data: ScoreSubmitRequest, 
    user: dict = Depends(verify_token)
):
    username = user.get("username")
    mode_id = data.mode_id
    score = data.score
    session_id = data.session_id

    # Update best score if needed
    existing_query = leaderboard_scores.select().where(
        (leaderboard_scores.c.username == username) &
        (leaderboard_scores.c.mode_id == mode_id)
    )
    existing = await database.fetch_one(existing_query)
    if existing:
        if score > existing["score"]:
            await database.execute(
                leaderboard_scores.update().where(
                    (leaderboard_scores.c.username == username) &
                    (leaderboard_scores.c.mode_id == mode_id)
                ).values(score=score, achieved_at=datetime.utcnow())
            )
    else:
        await database.execute(
            leaderboard_scores.insert().values(
                username=username, mode_id=mode_id,
                score=score, achieved_at=datetime.utcnow()
            )
        )
    # Always log to score_history
    await database.execute(
        score_history.insert().values(
            username=username, mode_id=mode_id, score=score,
            session_id=session_id, submitted_at=datetime.utcnow()
        )
    )
    return ScoreSubmitResponse(message="Score processed")

@router.get("/score/history", response_model=List[ScoreHistoryEntryOut])
async def get_score_history(user: dict = Depends(verify_token), mode_id: int = None, limit: int = 20):
    username = user.get("username")
    query = score_history.select().where(score_history.c.username == username)
    if mode_id:
        query = query.where(score_history.c.mode_id == mode_id)
    query = query.order_by(score_history.c.submitted_at.desc()).limit(limit)
    return await database.fetch_all(query)

# ---------- GAME SESSIONS ----------

@router.post("/session/start", response_model=SessionStartResponse)
async def start_session(
    data: SessionStartRequest,
    user: dict = Depends(verify_token)
):
    username = user.get("username")
    mode_id = data.mode_id
    device_id = data.device_id
    platform = data.platform
    client_version = data.client_version
    started_at = datetime.utcnow()
    session_id = await database.execute(
        game_sessions.insert().values(
            username=username, mode_id=mode_id,
            device_id=device_id, platform=platform,
            client_version=client_version, started_at=started_at
        )
    )
    return SessionStartResponse(session_id=session_id)

@router.post("/session/end", response_model=SessionEndResponse)
async def end_session(
    data: SessionEndRequest,
    user: dict = Depends(verify_token)
):
    username = user.get("username")
    session_id = data.session_id
    final_score = data.final_score
    ended_at = datetime.utcnow()
    # Update session record
    await database.execute(
        game_sessions.update().where(
            (game_sessions.c.id == session_id) &
            (game_sessions.c.username == username)
        ).values(
            ended_at=ended_at,
            final_score=final_score
        )
    )
    return SessionEndResponse(message="Session ended")

# ---------- SHOP / IAP ----------


@router.get("/shop/items", response_model=List[ShopItemOut])
async def list_shop_items():
    query = shop_items.select().where(shop_items.c.is_active == True)
    return await database.fetch_all(query)

@router.post("/shop/buy", response_model=ShopBuyResponse)
async def shop_buy(
    data: ShopBuyRequest,
    user: dict = Depends(verify_token)
):
    username = user.get("username")
    item_id = data.item_id
    amount = data.amount
    tx_hash = data.tx_hash
    # Insert purchase record
    await database.execute(
        purchases.insert().values(
            username=username, item_id=item_id, amount=amount,
            tx_hash=tx_hash, purchased_at=datetime.utcnow(), status="pending"
        )
    )
    return ShopBuyResponse(message="Purchase recorded (pending verification)")


@router.get("/purchases", response_model=List[PurchaseOut])
async def list_my_purchases(user: dict = Depends(verify_token)):
    username = user.get("username")
    query = purchases.select().where(purchases.c.username == username)
    return await database.fetch_all(query)

# ---------- CONTESTS & ENTRIES ----------


@router.get("/contests/active", response_model=List[ContestOut])
async def list_active_contests():
    now = datetime.utcnow()
    query = contests.select().where(
        (contests.c.start_at <= now) &
        (contests.c.end_at >= now) &
        (contests.c.status == "active")
    )
    return await database.fetch_all(query)

@router.post("/contests/{contest_id}/enter", response_model=ContestEntryResponse)
async def enter_contest(
    contest_id: int,
    data: ContestEntryRequest,
    user: dict = Depends(verify_token)
):
    username = user.get("username")
    await database.execute(
        contest_entries.insert().values(
            contest_id=contest_id, username=username,
            session_id=data.session_id, score=data.score, entered_at=datetime.utcnow()
        )
    )
    return ContestEntryResponse(message="Contest entry submitted")


@router.get("/contests/{contest_id}/leaderboard", response_model=List[ContestEntryOut])
async def contest_leaderboard(contest_id: int, top: int = 100):
    query = contest_entries.select().where(
        contest_entries.c.contest_id == contest_id
    ).order_by(contest_entries.c.score.desc()).limit(top)
    return await database.fetch_all(query)

# ---------- SUPPORT & FEEDBACK ----------

@router.get("/support/tickets", response_model=List[SupportTicketOut])
async def list_my_support_tickets(user: dict = Depends(verify_token)):
    username = user.get("username")
    query = support_tickets.select().where(support_tickets.c.username == username)
    return await database.fetch_all(query)

@router.post("/support/ticket", response_model=SupportTicketResponse)
async def submit_support_ticket(
    data: SupportTicketRequest,
    user: dict = Depends(verify_token)
):
    username = user.get("username")
    ticket_id = await database.execute(
        support_tickets.insert().values(
            username=username, subject=data.subject,
            message=data.message, status="open", created_at=datetime.utcnow()
        )
    )
    return SupportTicketResponse(ticket_id=ticket_id, message="Support ticket submitted")

# ---------- PROMO / REFERRALS ----------

@router.post("/promo/redeem", response_model=PromoRedeemResponse)
async def redeem_promo(
    data: PromoRedeemRequest,
    user: dict = Depends(verify_token)
):
    code = data.code
    username = user.get("username")
    # (Add your logic to validate/reward here)
    return PromoRedeemResponse(message="Promo code redeemed")

# ---------- FEATURE TOGGLES ----------

@router.get("/feature_toggles", response_model=List[FeatureToggleOut])
async def list_feature_toggles():
    query = feature_toggles.select().where(feature_toggles.c.enabled == True)
    return await database.fetch_all(query)
