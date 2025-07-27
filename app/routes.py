from fastapi import APIRouter, Depends, HTTPException
from app.auth import verify_token
from app.model import leaderboard, database
from sqlalchemy import func, select

router = APIRouter()

@router.get("/leaderboard")
async def get_leaderboard(top: int = 100):
    query = leaderboard.select().order_by(leaderboard.c.score.desc()).limit(top)
    return await database.fetch_all(query)

@router.get("/leaderboard/me")
async def get_my_score(user: dict = Depends(verify_token)):
    owner_id = user.get("owner_id")
    print(f"📌 Authenticated request for score of: {owner_id}")

    query = leaderboard.select().where(leaderboard.c.username == owner_id)
    result = await database.fetch_one(query)

    if not result:
        raise HTTPException(status_code=404, detail="No score found for this user")

    return result

@router.get("/leaderboard/rank")
async def get_my_rank(user: dict = Depends(verify_token)):
    owner_id = user.get("owner_id")
    print(f"📌 Authenticated request for rank of: {owner_id}")

    user_query = leaderboard.select().where(leaderboard.c.username == owner_id)
    user_score = await database.fetch_one(user_query)

    if not user_score:
        raise HTTPException(status_code=404, detail="No score found for this user")

    rank_query = select([func.count()]).select_from(leaderboard).where(
        leaderboard.c.score > user_score["score"]
    )
    rank = await database.fetch_val(rank_query)

    return {
        "rank": rank + 1,
        "score": user_score["score"],
    }

@router.post("/leaderboard")
async def submit_score(data: dict, user: dict = Depends(verify_token)):
    owner_id = user.get("owner_id")
    score = data.get("score")

    if score is None or not isinstance(score, int):
        raise HTTPException(status_code=400, detail="Invalid score data")

    print(f"📌 Submitting score {score} for user: {owner_id}")

    existing_query = leaderboard.select().where(leaderboard.c.username == owner_id)
    existing = await database.fetch_one(existing_query)

    if existing:
        if score > existing["score"]:
            update_query = leaderboard.update().where(
                leaderboard.c.username == owner_id
            ).values(score=score)
            await database.execute(update_query)
    else:
        insert_query = leaderboard.insert().values(username=owner_id, score=score)
        await database.execute(insert_query)

    return {"message": "Score submitted"}