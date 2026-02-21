# MasterPhaseVAgent — Top-Level Orchestrator (P+Q+P)

## Problem
Phase V is a multi-system architecture requiring coordination of:
- 5 advanced task features (recurring, reminders, priorities, tags, search)
- Event-driven infrastructure (Redpanda/Kafka, 5 topics, 3 consumers)
- Distributed runtime (Dapr: Pub/Sub, State, Cron, Secrets, Service Invoke)
- Cloud deployment (DOKS, Helm charts, CI/CD, kubectl-ai, kagent)
- Bilingual support (English + Urdu) with voice commands
- Reusable Intelligence (P+Q+P documented skills)

No single agent can handle all of this. We need an orchestrator.

## Question
How do we coordinate 4 sub-agents in the correct order, verify bonuses,
and produce a comprehensive audit trail with test scenarios?

## Pattern

### Execution Pipeline
```
MasterPhaseVAgent.run_full_phase_v()
│
├── Step 1: AdvancedFeatureAgent.run_step1_features()
│   ├── explain_recurring()     → verify recurring task flow
│   ├── explain_reminders()     → verify cron reminder system
│   ├── explain_priorities()    → verify 4-level priority system
│   ├── explain_tags()          → verify JSON tag system
│   ├── explain_search()        → verify search/filter/sort
│   ├── get_feature_matrix()    → 5 features documented
│   └── get_chat_commands()     → 10 commands (EN + UR)
│
├── Step 2: KafkaAgent.run_step2_kafka()
│   ├── check_cluster_health()  → Redpanda broker status
│   ├── create_topics()         → 5 topics created
│   ├── list_topics()           → verify topics exist
│   ├── check_dapr_pubsub()     → Dapr ↔ Redpanda link
│   └── get_consumer_status()   → 3 consumer groups
│
├── Step 3: DaprAgent.run_step3_dapr()
│   ├── install_dapr_*()        → Dapr runtime
│   ├── apply_components()      → 5 component YAMLs
│   ├── list_components()       → verify loaded
│   ├── configure_sidecar()     → todo-backend annotations
│   ├── verify_components()     → metadata check
│   ├── verify_secrets()        → db-secret accessible
│   └── check_sidecar_health()  → healthz OK
│
├── Step 4: DeploymentAgent.run_step4_deployment()
│   ├── create_cluster()        → DOKS cluster
│   ├── install_dapr()          → Helm install Dapr
│   ├── deploy_app()            → Helm chart deploy
│   ├── verify_deployment()     → all pods running
│   └── get_helm_status()       → release info
│
├── Bonus: verify_urdu_support()
│   ├── Mock provider Urdu intents (8 patterns)
│   ├── Frontend translations (30 keys)
│   ├── Voice recognition ur-PK
│   └── Quick commands (4 Urdu buttons)
│
├── Bonus: verify_voice_commands()
│   ├── SpeechRecognition API
│   ├── en-US + ur-PK languages
│   ├── Mic button with pulse animation
│   └── Transcript → textarea flow
│
└── Bonus: verify_reusable_intelligence()
    └── 11 skills in .claude/agents/ with P+Q+P
```

### Sub-Agents

| Agent | Role | Key Methods |
|-------|------|-------------|
| AdvancedFeatureAgent | 5 advanced features | explain_*, get_feature_matrix, get_chat_commands |
| KafkaAgent | Event infrastructure | create_topics, publish_event, full_setup |
| DaprAgent | Distributed runtime | apply_components, publish, save_state, get_secret |
| DeploymentAgent | DOKS deployment | create_cluster, deploy_app, verify_deployment |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/master/status | GET | Overall Phase V status |
| /api/master/step1/features | POST | Run Step 1 |
| /api/master/step2/kafka | POST | Run Step 2 |
| /api/master/step3/dapr | POST | Run Step 3 |
| /api/master/step4/deployment | POST | Run Step 4 |
| /api/master/run-all | POST | Full pipeline |
| /api/master/verify/urdu | GET | Urdu verification |
| /api/master/verify/voice | GET | Voice verification |
| /api/master/verify/reusable-intelligence | GET | Skills verification |
| /api/master/test-scenarios | GET | 12 test scenarios |
| /api/master/test-scenarios/{id} | GET | Single scenario |
| /api/master/pqp-trail | GET | Combined audit trail |
| /api/master/pqp-trail/{agent} | GET | Agent-filtered trail |

### Test Scenarios (12 total)

| ID | Feature | Chat Command |
|----|---------|--------------|
| TS-001 | Recurring Tasks | "Add task weekly standup repeat weekly" |
| TS-002 | Due Date Reminders | "Add task submit report with reminder" |
| TS-003 | Priority Management | "Set task 1 priority to urgent" |
| TS-004 | Tags System | "Tag task 5 with work devops" |
| TS-005 | Advanced Search | "Search for urgent work tasks" |
| TS-006 | Overdue Detection | "Show overdue tasks" |
| TS-007 | Urdu Chatbot | "فوری ٹاسک شامل کریں" |
| TS-008 | Voice Commands | (browser Speech API) |
| TS-009 | Kafka Event Flow | (infrastructure test) |
| TS-010 | Dapr Integration | (building blocks test) |
| TS-011 | DOKS Deployment | (DevOps test) |
| TS-012 | Quick Commands | (UI test) |

### Reusable Intelligence (11 Skills)

All skills are documented in `.claude/agents/` with P+Q+P format:
1. task-manager.md
2. event-publisher.md
3. reminder-cron.md
4. deployment-agent.md
5. kafka-agent.md
6. dapr-agent.md
7. advanced-feature-agent.md
8. todo-chat-agent.md
9. user_info_subagent.md
10. task_crud_subagent.md
11. conversation_manager_subagent.md

### Reusability
1. Copy MasterPhaseVAgent pattern for any multi-agent orchestration
2. Sub-agent interface is uniform: get_status(), get_audit_trail(), full_setup()
3. P+Q+P audit trail enables debugging and onboarding
4. Test scenarios template is reusable for any feature set
5. The 4-step pipeline pattern (Features → Events → Runtime → Deploy) is generic
