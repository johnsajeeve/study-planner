from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    _tablename_= "User"
    id= Column(Integer,primary_key=True,Index=True)
    username= Column(String, unique=True,Index=True)
    email=Column(String, unique=True,Index=True)
    hashed_password= Column(String)

    study_plans= relationship("StudyPlan", back_populates="owner")

class StudyPlan(Base):
    _tablename_="Study_plans"
    id= Column(Integer,primary_key=True,Index=True)
    title=Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="study_plans")
    tasks = relationship("Task", back_populates="study_plan")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    study_plan_id = Column(Integer, ForeignKey("study_plans.id"))

    study_plan = relationship("StudyPlan", back_populates="tasks")
    
    
