from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from db import get_db
from models import User, StudyPlan, Task

app = FastAPI(title="Study Planner API")

# ------------------------
# Users
# ------------------------
@app.post("/users")
async def create_user(username: str, email: str, hashed_password: str, db: AsyncSession = Depends(get_db)):
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    await db.refresh(user)
    return user

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

# ------------------------
# Study Plans
# ------------------------
@app.post("/studyplans")
async def create_study_plan(title: str, owner_id: int, db: AsyncSession = Depends(get_db)):
    study_plan = StudyPlan(title=title, owner_id=owner_id)
    db.add(study_plan)
    await db.commit()
    await db.refresh(study_plan)
    return study_plan

@app.get("/studyplans")
async def get_study_plans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StudyPlan))
    return result.scalars().all()

# ------------------------
# Tasks
# ------------------------
@app.post("/tasks")
async def create_task(title: str, description: str, study_plan_id: int, db: AsyncSession = Depends(get_db)):
    task = Task(title=title, description=description, study_plan_id=study_plan_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@app.get("/tasks")
async def get_tasks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task))
    return result.scalars().all()

@app.get("/tasks/{study_plan_id}")
async def get_tasks_by_plan(study_plan_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.study_plan_id == study_plan_id))
    return result.scalars().all()
