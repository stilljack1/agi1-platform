# OpenClaw Complete v2.0

**Autonomous Multi-Agent AGI Orchestration Framework**

## Quick Start

```bash
# 1. Setup API keys
./launch.sh --setup
nano .env

# 2. Launch (fully autonomous, no approvals)
./launch.sh --mission-file missions/mission.txt
```

## Architecture

```
launch.sh               Master launcher (bash)
├── __main__.py          Entry point
├── core/
│   ├── agent_gateway.py Unified API layer (Anthropic, OpenAI, Google)
│   ├── ralph_loop.py    Autonomous orchestrator (infinite loop)
│   ├── cowork.py        Workflow & task queue manager
│   └── dashboard.py     Live monitoring (localhost:8080)
├── agents.json          Agent config & routing rules
├── missions/            Mission files (CEO directives)
├── reports/             Auto-generated CEO reports
└── logs/                System logs & state persistence
```

## Agents

| Agent | Role | Provider |
|-------|------|----------|
| Opus 4.6 | Chief AI Research Officer | Anthropic |
| Sonnet 4.5 | Code Reviewer & Tester | Anthropic |
| Gemini 3 Pro | CTO | Google |
| CodeX 5.3 | Chief System Design & Data | OpenAI |
| GPT 5.2 | Chief Architecture Officer | OpenAI |
| OpenClaw | Head of Project & Product | Internal |
| Claude Code | DevOps & Deployment | Anthropic |
| Cowork | Workflow Manager | Internal |
| Ralph Loop | Autonomous Orchestrator | Internal |

## Commands

```bash
./launch.sh --setup                     # Create .env template
./launch.sh --mission-file FILE         # Launch with mission file
./launch.sh --mission "Build X"         # Launch with inline mission
./launch.sh --dry-run                   # Validate without launching
./launch.sh --status                    # Check current state
./launch.sh --port 9090                 # Custom dashboard port
./launch.sh --log-level DEBUG           # Verbose logging
```

## Requirements

- Python 3.10+
- `aiohttp` (auto-installed)
- API keys for at least one provider
