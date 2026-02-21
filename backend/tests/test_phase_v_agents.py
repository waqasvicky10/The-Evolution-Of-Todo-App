"""
Phase V — Agent orchestration tests.

Tests all 5 agents: AdvancedFeature, Kafka, Dapr, Deployment, Master.
Uses dry_run=True and VERCEL=1 to skip real Dapr/Kafka calls.

These tests do NOT require database setup — they test agent logic only.
"""

import os
import sys

os.environ["VERCEL"] = "1"
os.environ.setdefault("MOCK_MODE", "true")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_agents.db")
os.environ.setdefault("SECRET_KEY", "test-secret")

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.agents.advanced_feature_agent import AdvancedFeatureAgent
from app.agents.kafka_agent import KafkaAgent
from app.agents.dapr_agent import DaprAgent
from app.agents.deployment_agent import DeploymentAgent
from app.agents.master_agent import MasterPhaseVAgent


class TestAdvancedFeatureAgent:
    def setup_method(self):
        self.agent = AdvancedFeatureAgent()

    def test_explain_recurring(self):
        step = self.agent.explain_recurring()
        assert step.success is True
        assert "recurring" in step.question.lower()

    def test_explain_reminders(self):
        step = self.agent.explain_reminders()
        assert step.success is True
        assert "reminder" in step.question.lower()

    def test_explain_priorities(self):
        step = self.agent.explain_priorities()
        assert step.success is True
        assert "priority" in step.question.lower()

    def test_explain_tags(self):
        step = self.agent.explain_tags()
        assert step.success is True
        assert "tag" in step.question.lower()

    def test_explain_search(self):
        step = self.agent.explain_search()
        assert step.success is True
        assert "search" in step.question.lower()

    def test_feature_matrix(self):
        matrix = self.agent.get_feature_matrix()
        assert len(matrix) == 5
        assert "recurring_tasks" in matrix
        assert "priorities" in matrix

    def test_chat_commands(self):
        cmds = self.agent.get_chat_commands()
        assert len(cmds) >= 10

    def test_calculate_next_due(self):
        result = self.agent.calculate_next_due(None, "weekly")
        assert "next_due" in result
        assert result["pattern"] == "weekly"

    def test_status(self):
        status = self.agent.get_status()
        assert "features" in status
        assert "priority_levels" in status

    def test_audit_trail(self):
        self.agent.explain_recurring()
        trail = self.agent.get_audit_trail()
        assert len(trail) >= 1


class TestKafkaAgent:
    def setup_method(self):
        self.agent = KafkaAgent(dry_run=True)

    def test_create_topics(self):
        step = self.agent.create_topics()
        assert step.success is True

    def test_list_topics(self):
        step = self.agent.list_topics()
        assert step.success is True

    def test_full_setup(self):
        result = self.agent.full_setup()
        assert result["success"] is True
        assert len(result["topics"]) == 5

    def test_status(self):
        status = self.agent.get_status()
        assert "topics" in status
        assert "events_published" in status

    def test_cluster_health(self):
        step = self.agent.check_cluster_health()
        assert step.success is True


class TestDaprAgent:
    def setup_method(self):
        self.agent = DaprAgent(dry_run=True)

    def test_install_k8s(self):
        step = self.agent.install_dapr_k8s()
        assert step.success is True

    def test_install_local(self):
        step = self.agent.install_dapr_local()
        assert step.success is True

    def test_list_components(self):
        step = self.agent.list_components()
        assert step.success is True

    def test_apply_components(self):
        step = self.agent.apply_components()
        assert step.success is True

    def test_full_setup(self):
        result = self.agent.full_setup(target="local")
        assert result["success"] is True
        assert len(result["components"]) == 5

    def test_status(self):
        status = self.agent.get_status()
        assert "components" in status
        assert "operations" in status


class TestDeploymentAgent:
    def setup_method(self):
        self.agent = DeploymentAgent(dry_run=True)

    def test_create_cluster(self):
        step = self.agent.create_cluster()
        assert step.success is True
        assert "dry-run" in step.result

    def test_install_dapr(self):
        step = self.agent.install_dapr()
        assert step.success is True

    def test_deploy_app(self):
        step = self.agent.deploy_app("test-tag")
        assert step.success is True

    def test_verify_deployment(self):
        step = self.agent.verify_deployment()
        assert step.success is True

    def test_scale(self):
        step = self.agent.scale("backend", 3)
        assert step.success is True

    def test_full_deploy(self):
        result = self.agent.full_deploy()
        assert result["success"] is True
        assert result["steps_count"] == 5

    def test_audit_trail(self):
        self.agent.create_cluster()
        trail = self.agent.get_audit_trail()
        assert len(trail) >= 1


class TestMasterPhaseVAgent:
    def setup_method(self):
        self.agent = MasterPhaseVAgent(dry_run=True)

    def test_step1_features(self):
        result = self.agent.run_step1_features()
        assert result["agent"] == "AdvancedFeatureAgent"
        assert result["all_ok"] is True

    def test_step2_kafka(self):
        result = self.agent.run_step2_kafka()
        assert result["agent"] == "KafkaAgent"
        assert result["success"] is True

    def test_step3_dapr(self):
        result = self.agent.run_step3_dapr()
        assert result["agent"] == "DaprAgent"
        assert result["success"] is True

    def test_step4_deployment(self):
        result = self.agent.run_step4_deployment()
        assert result["agent"] == "DeploymentAgent"
        assert result["success"] is True

    def test_verify_urdu(self):
        result = self.agent.verify_urdu_support()
        assert result["urdu_verified"] is True

    def test_verify_voice(self):
        result = self.agent.verify_voice_commands()
        assert result["voice_verified"] is True

    def test_verify_reusable_intelligence(self):
        result = self.agent.verify_reusable_intelligence()
        assert result["total_skills"] >= 11

    def test_full_phase_v(self):
        result = self.agent.run_full_phase_v()
        assert result["success"] is True
        assert result["sub_agents"]["features"] is True
        assert result["sub_agents"]["kafka"] is True
        assert result["sub_agents"]["dapr"] is True
        assert result["sub_agents"]["deployment"] is True
        assert result["bonuses"]["urdu"] is True
        assert result["bonuses"]["voice"] is True
        assert result["bonuses"]["reusable_intelligence"] is True

    def test_test_scenarios(self):
        scenarios = self.agent.get_test_scenarios()
        assert len(scenarios) == 12
        ids = [s["id"] for s in scenarios]
        assert "TS-001" in ids
        assert "TS-012" in ids

    def test_combined_audit_trail(self):
        self.agent.run_full_phase_v()
        trail = self.agent.get_audit_trail()
        agents = set(e.get("agent") for e in trail)
        assert "master" in agents
        assert "AdvancedFeatureAgent" in agents
        assert "KafkaAgent" in agents
        assert "DaprAgent" in agents
        assert "DeploymentAgent" in agents

    def test_status(self):
        self.agent.run_full_phase_v()
        status = self.agent.get_status()
        assert status["phase"] == "V"
        assert status["current_step"] == "completed"
        assert status["total_test_scenarios"] == 12
