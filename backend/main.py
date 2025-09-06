from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from db import get_db
from models import User, StudyPlan, Task
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import traceback
import models

# ------------------------
# App setup
# ------------------------
app = FastAPI(title="Study Planner API")

SECRET_KEY = "my_name_is_jack"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ------------------------
# Schemas
# ------------------------
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class StudyPlanCreate(BaseModel):
    title: str

class TaskCreate(BaseModel):
    title: str
    description: str
    study_plan_id: int

# ------------------------
# Helpers
# ------------------------
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ------------------------
# Users
# ------------------------
@app.post("/users/", response_model=dict)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    hashed_pw = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return {"id": new_user.id, "username": new_user.username, "email": new_user.email}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="User already exists")
    except Exception:
        await db.rollback()
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/login", response_model=Token)
async def login(form: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form.username))
    user = result.scalars().first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
async def read_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email}

# ------------------------
# Study Plans
# ------------------------
@app.post("/studyplans")
async def create_study_plan(
    data: StudyPlanCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    study_plan = StudyPlan(title=data.title, owner_id=current_user.id)
    db.add(study_plan)
    await db.commit()
    await db.refresh(study_plan)
    return study_plan

@app.get("/studyplans")
async def get_study_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(StudyPlan).where(StudyPlan.owner_id == current_user.id))
    return result.scalars().all()

# ------------------------
# Tasks
# ------------------------
@app.post("/tasks")
async def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Ensure user owns the study plan
    result = await db.execute(select(StudyPlan).where(
        StudyPlan.id == data.study_plan_id, StudyPlan.owner_id == current_user.id
    ))
    study_plan = result.scalars().first()
    if not study_plan:
        raise HTTPException(status_code=403, detail="Not authorized for this study plan")

    task = Task(title=data.title, description=data.description, study_plan_id=data.study_plan_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@app.get("/tasks/{study_plan_id}")
async def get_tasks_by_plan(
    study_plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task).join(StudyPlan).where(
        Task.study_plan_id == study_plan_id, StudyPlan.owner_id == current_user.id
    ))
    return result.scalars().all()
