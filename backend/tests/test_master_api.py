"""
Phase V — Master API endpoint tests (direct function calls).

Tests the route handler functions directly without TestClient
to avoid startup event / anyio compatibility issues.
"""

import os
import pytest

os.environ["VERCEL"] = "1"
os.environ.setdefault("MOCK_MODE", "true")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_master.db")
os.environ.setdefault("SECRET_KEY", "test-secret")

from app.api.routes.master import (
    master_status,
    run_step1_features,
    run_step2_kafka,
    run_step3_dapr,
    run_step4_deployment,
    run_full_phase_v,
    verify_urdu,
    verify_voice,
    verify_reusable_intelligence,
    test_scenarios,
    test_scenario_by_id as _get_scenario_by_id,
    pqp_trail,
)
from app.api.routes.advanced_features import (
    feature_status,
    feature_matrix,
    chat_commands,
    explain_recurring,
    next_due_date,
)


def test_master_status():
    data = master_status()
    assert data["phase"] == "V"
    assert "sub_agents" in data


def test_step1_features():
    result = run_step1_features()
    assert result["agent"] == "AdvancedFeatureAgent"
    assert result["all_ok"] is True


def test_step2_kafka():
    result = run_step2_kafka()
    assert result["agent"] == "KafkaAgent"
    assert result["success"] is True


def test_step3_dapr():
    result = run_step3_dapr()
    assert result["agent"] == "DaprAgent"
    assert result["success"] is True


def test_step4_deployment():
    result = run_step4_deployment()
    assert result["agent"] == "DeploymentAgent"
    assert result["success"] is True


def test_run_all():
    result = run_full_phase_v()
    assert result["success"] is True
    assert result["sub_agents"]["features"] is True
    assert result["sub_agents"]["kafka"] is True
    assert result["sub_agents"]["dapr"] is True
    assert result["sub_agents"]["deployment"] is True


def test_verify_urdu():
    result = verify_urdu()
    assert result["urdu_verified"] is True
    assert len(result["capabilities"]["chatbot_intents"]) >= 8


def test_verify_voice():
    result = verify_voice()
    assert result["voice_verified"] is True
    assert "en-US" in result["capabilities"]["languages"]
    assert "ur-PK" in result["capabilities"]["languages"]


def test_verify_reusable():
    result = verify_reusable_intelligence()
    assert result["total_skills"] >= 11


def test_12_scenarios():
    result = test_scenarios()
    assert len(result) == 12
    ids = [s["id"] for s in result]
    assert "TS-001" in ids
    assert "TS-012" in ids


def test_scenario_by_id():
    result = _get_scenario_by_id("TS-007")
    assert result["feature"] == "Urdu Chatbot"


def test_pqp_trail():
    run_full_phase_v()
    trail = pqp_trail()
    assert len(trail) > 0
    agents = set(e.get("agent") for e in trail)
    assert "master" in agents


def test_feature_status():
    result = feature_status()
    assert "features" in result
    assert len(result["features"]) == 5


def test_feature_matrix():
    result = feature_matrix()
    assert "recurring_tasks" in result
    assert "priorities" in result


def test_chat_commands():
    result = chat_commands()
    assert len(result) >= 10


def test_explain_recurring():
    result = explain_recurring()
    assert result["success"] is True


def test_next_due():
    result = next_due_date(pattern="weekly", current_due=None)
    assert result["pattern"] == "weekly"
    assert "next_due" in result
