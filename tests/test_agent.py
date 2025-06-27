import unittest
from unittest.mock import patch, MagicMock
from src.agent import OrchestratorAgent
from src.models import AgentRequest


class TestAgent(unittest.TestCase):
    def test_get_model_invalid_provider(self):
        agent = OrchestratorAgent()
        with self.assertRaises(ValueError):
            agent._get_model("invalid", "model")

    @patch("src.agent.orchestrator_agent.Agent.run")
    def test_process_request_error(self, mock_run):
        mock_run.side_effect = Exception("fail")
        agent = OrchestratorAgent()
        req = AgentRequest(message="hi")
        resp = agent.process_request_sync(req)
        self.assertEqual(resp.confidence, 0.0)
        self.assertTrue(resp.errors)


if __name__ == "__main__":
    unittest.main()
