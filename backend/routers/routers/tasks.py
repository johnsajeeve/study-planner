from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from crud import create_task

router = APIRouter(prefix="/tasks")

@router.post("/")
async def add_task(title: str, description: str, study_plan_id: int, db: AsyncSession = Depends(get_db)):
    task = await create_task(db, title, description, study_plan_id)
    return task
