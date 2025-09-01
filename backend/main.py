from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from db import get_db
from models import User, StudyPlan, Task
#from api import users 
from jose import jwt,JWTError
from datetime import datetime,timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

app = FastAPI(title="Study Planner API")


#app.include_router(users.router, prefix="/users", tags=["Users"])


#------------------------
# config
#------------------------

SECRET_KEY ="my_name_is_jack"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES= 30

pwd_context= CryptContext(schemes =["bcrypt"],deprecated="auto")
oauth2_scheme= OAuth2PasswordBearer(tokenUrl ="login")


app = FastAPI()

#-------------------------

# helper functions

#---------------------------
def hash_password(password:str):
    return pwd_context.hash(password)
def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data: dict):
    to_encode=data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode= updaye({"exp":expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)







# ------------------------
# Users
# ------------------------
@app.post("/users/")
async def create_user(
    username: str,
    email: str,
    password: str,  # plain password from user
    db: AsyncSession = Depends(get_db)
):
    hashed_pw = hash_password(password)
    new_user = User(username=username, email=email, hashed_password=hashed_pw)
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return {"id": new_user.id, "username": new_user.username, "email": new_user.email}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="User already exists")


@app.post("/login")
async def login(username: str, password: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
async def read_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


















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
