from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from crud import create_user, get_user_by_username

router = APIRouter(prefix="/users")

@router.post("/")
async def register_user(username: str, email: str, password: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, username)
    if user:
        return {"error": "User already exists"}
    new_user = await create_user(db, username, email, password)
    return new_user
