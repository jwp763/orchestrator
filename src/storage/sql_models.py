from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, Text, Enum, JSON, Date, Float, Boolean
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime

from src.models.schemas import ProjectStatus, TaskStatus, Priority

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    priority = Column(Integer, default=3)
    tags = Column(JSON, default=list)
    due_date = Column(Date)
    start_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey('projects.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    due_date = Column(Date)
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    assignee = Column(String)
    tags = Column(JSON, default=list)
    labels = Column(JSON, default=list)
    depends_on = Column(JSON, default=list)
    blocks = Column(JSON, default=list)
    task_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    created_by = Column(String, nullable=False)

    project = relationship("Project", back_populates="tasks")
