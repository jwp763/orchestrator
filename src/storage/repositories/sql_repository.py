from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.models.project import Project
from src.models.task import Task
from src.storage.repositories.base import BaseStorageRepository
from src.storage.sql_models import Base, Project as SQLProject, Task as SQLTask


class SQLStorageRepository(BaseStorageRepository):
    """SQLAlchemy-based storage repository."""

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the repository with the given configuration."""
        db_uri = config.get("db_uri", "sqlite:///databricks_orchestrator.db")
        self.engine = create_engine(db_uri)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _generate_id(self) -> str:
        return str(uuid.uuid4())

    def get_project(self, project_id: str) -> Optional[Project]:
        with self.Session() as session:
            sql_project = session.query(SQLProject).filter(SQLProject.id == project_id).first()
            if not sql_project:
                return None
            return Project.model_validate(sql_project.__dict__)

    def create_project(self, project: Project) -> Project:
        with self.Session() as session:
            project.id = self._generate_id()
            sql_project = SQLProject(**project.model_dump())
            session.add(sql_project)
            session.commit()
            return project

    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Optional[Project]:
        with self.Session() as session:
            session.query(SQLProject).filter(SQLProject.id == project_id).update(updates)
            session.commit()
            return self.get_project(project_id)

    def get_task(self, task_id: str) -> Optional[Task]:
        with self.Session() as session:
            sql_task = session.query(SQLTask).filter(SQLTask.id == task_id).first()
            if not sql_task:
                return None
            return Task.model_validate(sql_task.__dict__)

    def create_task(self, task: Task) -> Task:
        with self.Session() as session:
            task.id = self._generate_id()
            sql_task = SQLTask(**task.model_dump())
            session.add(sql_task)
            session.commit()
            return task

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        with self.Session() as session:
            session.query(SQLTask).filter(SQLTask.id == task_id).update(updates)
            session.commit()
            return self.get_task(task_id)

    def get_tasks_by_project(self, project_id: str) -> List[Task]:
        with self.Session() as session:
            sql_tasks = session.query(SQLTask).filter(SQLTask.project_id == project_id).all()
            return [Task.model_validate(sql_task.__dict__) for sql_task in sql_tasks]