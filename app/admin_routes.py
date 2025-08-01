# app/admin_routes.py

from fastapi import APIRouter, Depends, HTTPException
from app.admin_auth import get_current_admin
from app.model import (
    users, admins, game_modes, leaderboard_scores, score_history, game_sessions,
    shop_items, purchases, contests, contest_entries, admin_audit_log,
    support_tickets, promo_codes, feature_toggles
)
from datetime import datetime
from app.database import database
from app.schemas import (
    AdminUserActionRequest,
    AdminGameModeCreateRequest, AdminGameModeUpdateRequest,
    AdminShopItemRequest,
    AdminContestRequest, AdminContestUpdateRequest,
    AdminPromoCodeRequest, AdminPromoCodeUpdateRequest,
    AdminFeatureToggleRequest, AdminFeatureToggleUpdateRequest,
)

router = APIRouter()

### -- USER & ADMIN MANAGEMENT ---

@router.get("/users")
async def admin_list_users(admin=Depends(get_current_admin)):
    return await database.fetch_all(users.select())

@router.post("/users/ban")
async def admin_ban_user(data: AdminUserActionRequest, admin=Depends(get_current_admin)):
    username = data.username
    await database.execute(users.update().where(users.c.username == username).values(is_banned=True))
    await database.execute(admin_audit_log.insert().values(
        admin_username=admin["username"], action="ban_user",
        target_table="users", notes=f"Banned {username}", timestamp=datetime.utcnow()
    ))
    return {"message": f"User {username} banned"}

@router.post("/users/unban")
async def admin_unban_user(data: AdminUserActionRequest, admin=Depends(get_current_admin)):
    username = data.username
    await database.execute(users.update().where(users.c.username == username).values(is_banned=False))
    await database.execute(admin_audit_log.insert().values(
        admin_username=admin["username"], action="unban_user",
        target_table="users", notes=f"Unbanned {username}", timestamp=datetime.utcnow()
    ))
    return {"message": f"User {username} unbanned"}

@router.get("/admins")
async def admin_list_admins(admin=Depends(get_current_admin)):
    return await database.fetch_all(admins.select())

### -- GAME MODES ---

@router.get("/game_modes")
async def admin_list_modes(admin=Depends(get_current_admin)):
    return await database.fetch_all(game_modes.select())

@router.post("/game_modes")
async def admin_create_mode(data: AdminGameModeCreateRequest, admin=Depends(get_current_admin)):
    res = await database.execute(game_modes.insert().values(
        name=data.name,
        description=data.description or "",
        is_active=data.is_active,
        created_at=datetime.utcnow()
    ))
    return {"id": res, "message": "Mode created"}

@router.put("/game_modes/{mode_id}")
async def admin_update_mode(mode_id: int, data: AdminGameModeUpdateRequest, admin=Depends(get_current_admin)):
    await database.execute(game_modes.update().where(game_modes.c.id == mode_id).values(**data.dict(exclude_unset=True)))
    return {"message": "Mode updated"}

@router.delete("/game_modes/{mode_id}")
async def admin_delete_mode(mode_id: int, admin=Depends(get_current_admin)):
    await database.execute(game_modes.delete().where(game_modes.c.id == mode_id))
    return {"message": "Mode deleted"}

### -- LEADERBOARDS & SCORES ---

@router.get("/leaderboards")
async def admin_list_leaderboards(admin=Depends(get_current_admin)):
    return await database.fetch_all(leaderboard_scores.select())

@router.get("/score_history")
async def admin_score_history(admin=Depends(get_current_admin), username: str = None):
    query = score_history.select()
    if username:
        query = query.where(score_history.c.username == username)
    return await database.fetch_all(query)

@router.get("/game_sessions")
async def admin_sessions(admin=Depends(get_current_admin), username: str = None):
    query = game_sessions.select()
    if username:
        query = query.where(game_sessions.c.username == username)
    return await database.fetch_all(query)

### -- SHOP & PURCHASES ---

@router.get("/shop/items")
async def admin_list_shop_items(admin=Depends(get_current_admin)):
    return await database.fetch_all(shop_items.select())

@router.post("/shop/items")
async def admin_create_shop_item(data: AdminShopItemRequest, admin=Depends(get_current_admin)):
    res = await database.execute(shop_items.insert().values(**data.dict(exclude_unset=True)))
    return {"id": res, "message": "Shop item created"}

@router.put("/shop/items/{item_id}")
async def admin_update_shop_item(item_id: int, data: AdminShopItemRequest, admin=Depends(get_current_admin)):
    await database.execute(shop_items.update().where(shop_items.c.id == item_id).values(**data.dict(exclude_unset=True)))
    return {"message": "Shop item updated"}

@router.delete("/shop/items/{item_id}")
async def admin_delete_shop_item(item_id: int, admin=Depends(get_current_admin)):
    await database.execute(shop_items.delete().where(shop_items.c.id == item_id))
    return {"message": "Shop item deleted"}

@router.get("/purchases")
async def admin_list_purchases(admin=Depends(get_current_admin)):
    return await database.fetch_all(purchases.select())

### -- CONTESTS ---

@router.get("/contests")
async def admin_list_contests(admin=Depends(get_current_admin)):
    return await database.fetch_all(contests.select())

@router.post("/contests")
async def admin_create_contest(data: AdminContestRequest, admin=Depends(get_current_admin)):
    res = await database.execute(contests.insert().values(**data.dict(exclude_unset=True)))
    return {"id": res, "message": "Contest created"}

@router.put("/contests/{contest_id}")
async def admin_update_contest(contest_id: int, data: AdminContestUpdateRequest, admin=Depends(get_current_admin)):
    await database.execute(contests.update().where(contests.c.id == contest_id).values(**data.dict(exclude_unset=True)))
    return {"message": "Contest updated"}

@router.delete("/contests/{contest_id}")
async def admin_delete_contest(contest_id: int, admin=Depends(get_current_admin)):
    await database.execute(contests.delete().where(contests.c.id == contest_id))
    return {"message": "Contest deleted"}

@router.get("/contest_entries")
async def admin_list_contest_entries(admin=Depends(get_current_admin), contest_id: int = None):
    query = contest_entries.select()
    if contest_id:
        query = query.where(contest_entries.c.contest_id == contest_id)
    return await database.fetch_all(query)

### -- SUPPORT / FEEDBACK ---

@router.get("/support_tickets")
async def admin_list_support_tickets(admin=Depends(get_current_admin)):
    return await database.fetch_all(support_tickets.select())

@router.post("/support_tickets/{ticket_id}/close")
async def admin_close_support_ticket(ticket_id: int, admin=Depends(get_current_admin)):
    await database.execute(support_tickets.update().where(support_tickets.c.id == ticket_id).values(status="closed"))
    return {"message": "Ticket closed"}

### -- PROMO CODES ---

@router.get("/promo_codes")
async def admin_list_promo_codes(admin=Depends(get_current_admin)):
    return await database.fetch_all(promo_codes.select())

@router.post("/promo_codes")
async def admin_create_promo_code(data: AdminPromoCodeRequest, admin=Depends(get_current_admin)):
    res = await database.execute(promo_codes.insert().values(**data.dict(exclude_unset=True)))
    return {"id": res, "message": "Promo code created"}

@router.put("/promo_codes/{promo_id}")
async def admin_update_promo_code(promo_id: int, data: AdminPromoCodeUpdateRequest, admin=Depends(get_current_admin)):
    await database.execute(promo_codes.update().where(promo_codes.c.id == promo_id).values(**data.dict(exclude_unset=True)))
    return {"message": "Promo code updated"}

@router.delete("/promo_codes/{promo_id}")
async def admin_delete_promo_code(promo_id: int, admin=Depends(get_current_admin)):
    await database.execute(promo_codes.delete().where(promo_codes.c.id == promo_id))
    return {"message": "Promo code deleted"}

### -- FEATURE TOGGLES ---

@router.get("/feature_toggles")
async def admin_list_feature_toggles(admin=Depends(get_current_admin)):
    return await database.fetch_all(feature_toggles.select())

@router.post("/feature_toggles")
async def admin_create_feature_toggle(data: AdminFeatureToggleRequest, admin=Depends(get_current_admin)):
    res = await database.execute(feature_toggles.insert().values(**data.dict(exclude_unset=True)))
    return {"id": res, "message": "Feature toggle created"}

@router.put("/feature_toggles/{toggle_id}")
async def admin_update_feature_toggle(toggle_id: int, data: AdminFeatureToggleUpdateRequest, admin=Depends(get_current_admin)):
    await database.execute(feature_toggles.update().where(feature_toggles.c.id == toggle_id).values(**data.dict(exclude_unset=True)))
    return {"message": "Feature toggle updated"}

@router.delete("/feature_toggles/{toggle_id}")
async def admin_delete_feature_toggle(toggle_id: int, admin=Depends(get_current_admin)):
    await database.execute(feature_toggles.delete().where(feature_toggles.c.id == toggle_id))
    return {"message": "Feature toggle deleted"}

### -- ADMIN AUDIT LOG ---

@router.get("/audit_log")
async def admin_audit_log_view(admin=Depends(get_current_admin)):
    return await database.fetch_all(admin_audit_log.select())
