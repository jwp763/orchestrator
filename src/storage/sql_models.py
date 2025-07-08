from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from src.models.project import ProjectStatus
from src.models.task import TaskStatus, TaskPriority

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    priority = Column(Integer, default=3)
    tags = Column(JSON, default=list)
    due_date = Column(DateTime)
    start_date = Column(DateTime)
    motion_project_id = Column(String)
    linear_project_id = Column(String)
    notion_page_id = Column(String)
    gitlab_project_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String)
    task_count = Column(Integer, default=0)
    completed_task_count = Column(Integer, default=0)

    tasks = relationship("Task", back_populates="project")

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    project_id = Column(String, ForeignKey('projects.id'))
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    parent_id = Column(String, ForeignKey('tasks.id'))
    estimated_minutes = Column(Integer)
    actual_minutes = Column(Integer)
    depth = Column(Integer, default=0)
    dependencies = Column(JSON, default=list)
    due_date = Column(DateTime)
    assignee = Column(String)
    tags = Column(JSON, default=list)
    labels = Column(JSON, default=list)
    motion_task_id = Column(String)
    linear_issue_id = Column(String)
    notion_task_id = Column(String)
    gitlab_issue_id = Column(String)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    created_by = Column(String)
    is_overdue = Column(Integer, default=0)
    days_until_due = Column(Integer)

    project = relationship("Project", back_populates="tasks")
    parent = relationship("Task", remote_side=[id], back_populates="children")
    children = relationship("Task", back_populates="parent")
