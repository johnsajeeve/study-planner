from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from crud import create_study_plan

router = APIRouter(prefix="/study-plans")

@router.post("/")
async def add_study_plan(title: str, owner_id: int, db: AsyncSession = Depends(get_db)):
    plan = await create_study_plan(db, title, owner_id)
    return plan
