from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship,declarative_base
from db import Base




class User(Base):
    __tablename__= "users"
    id= Column(Integer,primary_key=True,index=True)
    username= Column(String, unique=True,nullable=False,  index=True)
    email=Column(String, unique=True,nullable=False,index=True)
    hashed_password= Column(String,nullable=False)

    study_plans= relationship("StudyPlan", back_populates="owner", cascade="all, delete-orphan")

class StudyPlan(Base):
    __tablename__="study_plans"
    id= Column(Integer,primary_key=True,index=True)
    title=Column(String,nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    

    owner = relationship("User", back_populates="study_plans")
    tasks = relationship("Task", back_populates="study_plan",cascade ="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String,nullable=True)
    study_plan_id = Column(Integer, ForeignKey("study_plans.id",ondelete="CASCADE"))

    study_plan = relationship("StudyPlan", back_populates="tasks")

    
