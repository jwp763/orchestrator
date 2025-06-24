import os, sys; sys.path.insert(0, os.path.abspath("src"))
import unittest
from src.models import ProjectCreate, TaskCreate, Integration, IntegrationConfig, IntegrationType, AgentRequest, AgentResponse, UserCreate
from datetime import date

class TestModels(unittest.TestCase):
    def test_project_create(self):
        p = ProjectCreate(name='Test', description='desc', due_date=date.today())
        self.assertEqual(p.name, 'Test')
        self.assertEqual(p.description, 'desc')

    def test_task_create(self):
        t = TaskCreate(title='Task', project_id='proj1')
        self.assertEqual(t.title, 'Task')
        self.assertEqual(t.project_id, 'proj1')

    def test_integration_model(self):
        cfg = IntegrationConfig(api_key='secret')
        integ = Integration(id='1', type=IntegrationType.MOTION, name='Motion', enabled=True, config=cfg, sync_enabled=True, sync_interval_minutes=60, created_at=date.today(), updated_at=date.today(), created_by='user')
        self.assertEqual(integ.type, IntegrationType.MOTION)

    def test_agent_models(self):
        req = AgentRequest(message='hi')
        resp = AgentResponse(message='ok', provider_used='anthropic', model_used='model')
        self.assertEqual(req.message, 'hi')
        self.assertEqual(resp.message, 'ok')

    def test_user_create(self):
        u = UserCreate(name='John')
        self.assertEqual(u.name, 'John')

if __name__ == '__main__':
    unittest.main()
