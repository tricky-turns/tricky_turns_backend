# routes.py

from fastapi import APIRouter, Depends, HTTPException, status
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
    username = user.get("username")
    print(f"📌 Authenticated request for score of: {username}")
    query = leaderboard.select().where(leaderboard.c.username == username)
    result = await database.fetch_one(query)
    if not result:
        raise HTTPException(status_code=404, detail="No score found for this user")
    return result

@router.get("/leaderboard/rank")
async def get_my_rank(user: dict = Depends(verify_token)):
    username = user.get("username")
    print(f"📌 Authenticated request for rank of: {username}")
    user_query = leaderboard.select().where(leaderboard.c.username == username)
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
    username = user.get("username")
    score = data.get("score")
    # Ignore username from client for identity—use only verified username
    if score is None or not isinstance(score, int):
        raise HTTPException(status_code=400, detail="Invalid score")
    print(f"📌 Submitting score {score} for user: {username}")
    existing_query = leaderboard.select().where(leaderboard.c.username == username)
    existing = await database.fetch_one(existing_query)
    if existing:
        if score > existing["score"]:
            update_query = leaderboard.update().where(
                leaderboard.c.username == username
            ).values(score=score)
            await database.execute(update_query)
    else:
        insert_query = leaderboard.insert().values(
            username=username,
            score=score
        )
        await database.execute(insert_query)
    return {"message": "Score submitted"}

@router.delete("/leaderboard/all", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_leaderboard_entries():
    """
    Danger: This deletes ALL leaderboard entries.
    Secure this route before using in production!
    """
    delete_query = leaderboard.delete()
    await database.execute(delete_query)
    return None  # 204 No Content
