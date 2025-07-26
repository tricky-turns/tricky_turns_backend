from app.auth import verify_token
from fastapi import APIRouter, HTTPException, Depends, Request
from app.database import database
from app.model import leaderboard
from sqlalchemy import func


router = APIRouter()

@router.on_event("startup")
async def startup():
    await database.connect()

@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@router.get("/leaderboard")
async def get_leaderboard(top: int = 100):
    query = leaderboard.select().order_by(leaderboard.c.score.desc()).limit(top)
    return await database.fetch_all(query)

@router.get("/leaderboard/{username}")
async def get_user_score(username: str, payload: dict = Depends(verify_token)):
    print(f"📊 Serving rank for user: {payload['username']}")
    query = leaderboard.select().where(leaderboard.c.username == username)
    user_score = await database.fetch_one(query)
    if user_score is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_score


@router.post("/leaderboard")
async def submit_score(payload: dict):
    username = payload.get("username")
    score = payload.get("score")
    if not username or not isinstance(score, int):
        raise HTTPException(status_code=400, detail="Invalid payload")

    query = leaderboard.select().where(leaderboard.c.username == username)
    existing = await database.fetch_one(query)
    if existing:
        if score > existing["score"]:
            update = leaderboard.update().where(leaderboard.c.username == username).values(score=score)
            await database.execute(update)
    else:
        insert = leaderboard.insert().values(username=username, score=score)
        await database.execute(insert)
    return {"success": True}

@router.get("/leaderboard/rank")
async def get_user_rank(username: str):
    # Get the user's score from the leaderboard table
    user_query = leaderboard.select().where(leaderboard.c.username == username)
    user = await database.fetch_one(user_query)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_score = user["score"]

    # Count how many users have a strictly higher score
    rank_query = leaderboard.select().with_only_columns([func.count()]).where(leaderboard.c.score > user_score)
    higher_count = await database.fetch_val(rank_query)

    return {
        "username": username,
        "score": user_score,
        "rank": higher_count + 1
    }

@router.delete("/leaderboard")
async def delete_all_scores():
    query = leaderboard.delete()
    await database.execute(query)
    return {"message": "All scores have been deleted"}


@router.get("/auth-test")
async def auth_test(request: Request):
    print("HEADERS:", request.headers)
    return {"headers": dict(request.headers)}

