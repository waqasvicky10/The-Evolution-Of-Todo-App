"""
Master Phase V API — Orchestration endpoints.

Exposes the MasterPhaseVAgent for full pipeline orchestration,
individual step execution, bonus verifications, and test scenarios.
"""

from fastapi import APIRouter, Query
from typing import Any, Dict, List

from ...agents.master_agent import MasterPhaseVAgent

router = APIRouter(prefix="/api/master", tags=["master-orchestrator"])

_agent = MasterPhaseVAgent(dry_run=True)


# ------------------------------------------------------------------
# Status & overview
# ------------------------------------------------------------------

@router.get("/status")
def master_status() -> Dict[str, Any]:
    """Return the current state of the Phase V orchestration."""
    return _agent.get_status()


# ------------------------------------------------------------------
# Individual steps
# ------------------------------------------------------------------

@router.post("/step1/features")
def run_step1_features() -> Dict[str, Any]:
    """Step 1: Run AdvancedFeatureAgent — verify all advanced features."""
    return _agent.run_step1_features()


@router.post("/step2/kafka")
def run_step2_kafka() -> Dict[str, Any]:
    """Step 2: Run KafkaAgent — set up event-driven infrastructure."""
    return _agent.run_step2_kafka()


@router.post("/step3/dapr")
def run_step3_dapr() -> Dict[str, Any]:
    """Step 3: Run DaprAgent — set up distributed runtime."""
    return _agent.run_step3_dapr()


@router.post("/step4/deployment")
def run_step4_deployment(image_tag: str = Query("latest")) -> Dict[str, Any]:
    """Step 4: Run DeploymentAgent — deploy to DOKS."""
    return _agent.run_step4_deployment(image_tag)


# ------------------------------------------------------------------
# Full pipeline
# ------------------------------------------------------------------

@router.post("/run-all")
def run_full_phase_v(image_tag: str = Query("latest")) -> Dict[str, Any]:
    """Execute the complete Phase V pipeline (all 4 steps + bonuses)."""
    return _agent.run_full_phase_v(image_tag)


# ------------------------------------------------------------------
# Bonus verifications
# ------------------------------------------------------------------

@router.get("/verify/urdu")
def verify_urdu() -> Dict[str, Any]:
    """Verify Urdu language support across all layers."""
    return _agent.verify_urdu_support()


@router.get("/verify/voice")
def verify_voice() -> Dict[str, Any]:
    """Verify browser Speech API voice command integration."""
    return _agent.verify_voice_commands()


@router.get("/verify/reusable-intelligence")
def verify_reusable_intelligence() -> Dict[str, Any]:
    """Verify all skills are documented in .claude/agents/ with P+Q+P."""
    return _agent.verify_reusable_intelligence()


# ------------------------------------------------------------------
# Test scenarios
# ------------------------------------------------------------------

@router.get("/test-scenarios")
def test_scenarios() -> List[Dict[str, Any]]:
    """Return comprehensive test scenarios for all Phase V features."""
    return _agent.get_test_scenarios()


@router.get("/test-scenarios/{scenario_id}")
def test_scenario_by_id(scenario_id: str) -> Dict[str, Any]:
    """Return a specific test scenario by ID."""
    for s in _agent.get_test_scenarios():
        if s["id"] == scenario_id:
            return s
    return {"error": f"Scenario '{scenario_id}' not found"}


# ------------------------------------------------------------------
# Audit trail
# ------------------------------------------------------------------

@router.get("/pqp-trail")
def pqp_trail() -> List[Dict[str, Any]]:
    """Return the combined P+Q+P audit trail from master + all sub-agents."""
    return _agent.get_audit_trail()


@router.get("/pqp-trail/{agent_name}")
def pqp_trail_by_agent(agent_name: str) -> List[Dict[str, Any]]:
    """Return P+Q+P trail filtered by agent name."""
    return [s for s in _agent.get_audit_trail() if s.get("agent", "").lower() == agent_name.lower()]
