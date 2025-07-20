from fastapi import APIRouter, HTTPException
from app.database import database
from app.model import leaderboard

router = APIRouter()

@router.on_event("startup")
async def startup():
    await database.connect()

@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@router.get("/api/leaderboard")
async def get_leaderboard(top: int = 100):
    query = leaderboard.select().order_by(leaderboard.c.score.desc()).limit(top)
    return await database.fetch_all(query)

@router.post("/api/leaderboard")
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
