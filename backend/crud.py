from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User, StudyPlan, Task

async def get_user_by_username(db:asyncSession, username:str):
    result =await db.execute(select(User).where(User.username==username))
    return result.scalars().first()

async def create_user(db:AsyncSession,username: str,email:str,hashed_password:str ):
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def create_study_plan(db: AsyncSession, title: str, owner_id: int):
    plan = StudyPlan(title=title,owner_id=owner_id)
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan

async def create_task(db: AsyncSession, title: str, description: str, study_plan_id: int):
    task= Task(title=title,description=description,study_plan_id=study_plan_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task



    