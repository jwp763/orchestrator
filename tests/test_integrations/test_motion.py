import os, sys

sys.path.insert(0, os.path.abspath("src"))
import unittest
from datetime import date, datetime
from unittest.mock import MagicMock

from src.integrations.motion.integration import MotionIntegration
from src.models import IntegrationConfig, Project, ProjectStatus, Task, TaskPriority, TaskStatus


class TestMotionMapping(unittest.TestCase):
    def setUp(self):
        cfg = IntegrationConfig(api_key="k", workspace_id="w")
        self.integration = MotionIntegration(config=cfg, delta_manager=MagicMock())

    def test_project_status_mapping(self):
        self.assertEqual(self.integration._map_project_status_to_motion(ProjectStatus.ACTIVE), "IN_PROGRESS")
        self.assertEqual(self.integration._map_motion_project_status("COMPLETED"), ProjectStatus.COMPLETED)

    def test_task_status_mapping(self):
        self.assertEqual(self.integration._map_task_status_to_motion(TaskStatus.IN_REVIEW), "IN_REVIEW")
        self.assertEqual(self.integration._map_motion_task_status("BLOCKED"), TaskStatus.BLOCKED)

    def test_priority_mapping(self):
        self.assertEqual(self.integration._map_task_priority_to_motion(TaskPriority.HIGH), "HIGH")
        self.assertEqual(self.integration._map_motion_task_priority("ASAP"), TaskPriority.CRITICAL)
