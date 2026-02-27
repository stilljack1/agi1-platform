#!/usr/bin/env bash
#═══════════════════════════════════════════════════════════════
#  OPENCLAW COMPLETE v2.0 — AUTONOMOUS LAUNCHER
#  Zero-approval, infinite-loop multi-agent orchestration
#═══════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'
PURPLE='\033[0;35m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'
BOLD='\033[1m'; NC='\033[0m'

# Defaults
MISSION_FILE=""
CONFIG_FILE="agents.json"
DASHBOARD_PORT=8080
LOG_LEVEL="INFO"
RUN_MODE="autonomous"

banner() {
  echo -e "${PURPLE}"
  echo "  ╔═══════════════════════════════════════════════════════════╗"
  echo "  ║                                                           ║"
  echo "  ║   ██████╗ ██████╗ ███████╗███╗   ██╗ ██████╗██╗    ██╗   ║"
  echo "  ║  ██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔════╝██║    ██║   ║"
  echo "  ║  ██║   ██║██████╔╝█████╗  ██╔██╗ ██║██║     ██║ █╗ ██║   ║"
  echo "  ║  ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██║     ██║███╗██║   ║"
  echo "  ║  ╚██████╔╝██║     ███████╗██║ ╚████║╚██████╗╚███╔███╔╝   ║"
  echo "  ║   ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚══╝╚══╝   ║"
  echo "  ║                                                           ║"
  echo "  ║          COMPLETE v2.0 — AUTONOMOUS AGI FACTORY           ║"
  echo "  ║                                                           ║"
  echo "  ║   CEO: Jack              Mode: AUTONOMOUS                 ║"
  echo "  ║   Agents: 9              Providers: 4                     ║"
  echo "  ║   Approval: NONE         Loop: INFINITE                   ║"
  echo "  ║                                                           ║"
  echo "  ╚═══════════════════════════════════════════════════════════╝"
  echo -e "${NC}"
}

usage() {
  echo -e "${BOLD}Usage:${NC} ./launch.sh [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --setup                 Create .env template for API keys"
  echo "  --mission-file FILE     Path to mission file (default: missions/mission.txt)"
  echo "  --mission TEXT          Inline mission text"
  echo "  --config FILE           Config file (default: agents.json)"
  echo "  --port PORT             Dashboard port (default: 8080)"
  echo "  --log-level LEVEL       Log level: DEBUG|INFO|WARNING|ERROR"
  echo "  --dry-run               Validate config without launching"
  echo "  --status                Show system status"
  echo "  --help                  Show this help"
  echo ""
  echo "Examples:"
  echo "  ./launch.sh --setup"
  echo "  ./launch.sh --mission-file missions/mission.txt"
  echo '  ./launch.sh --mission "Build an AGI brain v3.0"'
}

setup_env() {
  if [[ -f .env ]]; then
    echo -e "${YELLOW}⚠ .env already exists. Backing up to .env.bak${NC}"
    cp .env .env.bak
  fi
  cat > .env << 'ENVEOF'
# ═══════════════════════════════════════════════════════════
# OPENCLAW COMPLETE v2.0 — API KEYS
# ═══════════════════════════════════════════════════════════

# Anthropic (Opus 4.6, Sonnet 4.5, Claude Code)
ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXXXX

# OpenAI (CodeX 5.3, GPT 5.2)
OPENAI_API_KEY=sk-XXXXXXXXXXXXX

# Google (Gemini 3 Pro)
GOOGLE_API_KEY=XXXXXXXXXXXXX

# ─── Optional: Notifications ───
# TELEGRAM_BOT_TOKEN=
# TELEGRAM_CHAT_ID=
# SLACK_WEBHOOK_URL=

# ─── Dashboard ───
DASHBOARD_PORT=8080
ENVEOF
  echo -e "${GREEN}✓ Created .env — edit it with your API keys${NC}"
  echo -e "  ${CYAN}nano .env${NC}"
}

check_deps() {
  echo -e "${BLUE}Checking dependencies...${NC}"
  local missing=0

  if ! command -v python3 &>/dev/null; then
    echo -e "${RED}✗ python3 not found${NC}"
    missing=1
  else
    echo -e "${GREEN}✓ python3 $(python3 --version 2>&1 | awk '{print $2}')${NC}"
  fi

  # Check Python packages
  for pkg in aiohttp; do
    if python3 -c "import $pkg" 2>/dev/null; then
      echo -e "${GREEN}✓ $pkg${NC}"
    else
      echo -e "${YELLOW}⚠ $pkg not installed, installing...${NC}"
      pip3 install "$pkg" --break-system-packages --quiet 2>/dev/null || \
        pip3 install "$pkg" --quiet 2>/dev/null || {
          echo -e "${RED}✗ Failed to install $pkg${NC}"
          missing=1
        }
    fi
  done

  if [[ ! -f "$CONFIG_FILE" ]]; then
    echo -e "${RED}✗ Config file not found: $CONFIG_FILE${NC}"
    missing=1
  else
    echo -e "${GREEN}✓ Config: $CONFIG_FILE${NC}"
  fi

  if [[ ! -f .env ]]; then
    echo -e "${YELLOW}⚠ No .env file found. Run: ./launch.sh --setup${NC}"
    missing=1
  else
    echo -e "${GREEN}✓ .env loaded${NC}"
    source .env 2>/dev/null || true
  fi

  return $missing
}

validate_keys() {
  echo -e "${BLUE}Validating API keys...${NC}"
  local keys=0

  if [[ -n "${ANTHROPIC_API_KEY:-}" && "${ANTHROPIC_API_KEY}" != sk-ant-XXXXXXXXXXXXX ]]; then
    echo -e "${GREEN}✓ Anthropic key configured${NC}"
    ((keys++))
  else
    echo -e "${YELLOW}⚠ Anthropic key not set (Opus, Sonnet, Claude Code won't work)${NC}"
  fi

  if [[ -n "${OPENAI_API_KEY:-}" && "${OPENAI_API_KEY}" != sk-XXXXXXXXXXXXX ]]; then
    echo -e "${GREEN}✓ OpenAI key configured${NC}"
    ((keys++))
  else
    echo -e "${YELLOW}⚠ OpenAI key not set (CodeX, GPT won't work)${NC}"
  fi

  if [[ -n "${GOOGLE_API_KEY:-}" && "${GOOGLE_API_KEY}" != XXXXXXXXXXXXX ]]; then
    echo -e "${GREEN}✓ Google key configured${NC}"
    ((keys++))
  else
    echo -e "${YELLOW}⚠ Google key not set (Gemini won't work)${NC}"
  fi

  if [[ $keys -eq 0 ]]; then
    echo -e "${RED}✗ No API keys configured! Run: ./launch.sh --setup${NC}"
    return 1
  fi

  echo -e "${GREEN}✓ $keys provider(s) ready${NC}"
  return 0
}

create_runner() {
  # Create the Python entry point that ties everything together
  cat > "$SCRIPT_DIR/__main__.py" << 'PYEOF'
#!/usr/bin/env python3
"""OpenClaw Complete v2.0 — Main Entry Point"""
import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ralph_loop import RalphLoop
from core.dashboard import start_dashboard, DashboardState

def setup_logging(level: str = "INFO"):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(name)-20s | %(levelname)-7s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "openclaw.log"),
        ]
    )

async def main():
    parser = argparse.ArgumentParser(description="OpenClaw Complete v2.0")
    parser.add_argument("--config", default="agents.json")
    parser.add_argument("--mission-file", default=None)
    parser.add_argument("--mission", default=None)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    setup_logging(args.log_level)
    logger = logging.getLogger("openclaw.main")

    # Handle inline mission
    mission_file = args.mission_file
    if args.mission and not mission_file:
        Path("missions").mkdir(exist_ok=True)
        mf = Path("missions/_inline_mission.txt")
        mf.write_text(args.mission)
        mission_file = str(mf)

    # Start dashboard
    logger.info(f"Starting dashboard on port {args.port}")
    start_dashboard(args.port)

    # Create and run Ralph Loop
    ralph = RalphLoop(config_path=args.config, mission_file=mission_file)

    # Connect dashboard to Ralph's state
    state = DashboardState()

    logger.info("=" * 60)
    logger.info("  OPENCLAW COMPLETE v2.0 — ALL SYSTEMS GO")
    logger.info("  Mode: FULLY AUTONOMOUS — NO APPROVALS")
    logger.info(f"  Dashboard: http://localhost:{args.port}")
    logger.info("=" * 60)

    await ralph.run()

if __name__ == "__main__":
    asyncio.run(main())
PYEOF
  echo -e "${GREEN}✓ Runner created${NC}"
}

launch() {
  banner

  echo -e "${CYAN}━━━ PREFLIGHT CHECKS ━━━${NC}"
  check_deps || { echo -e "${RED}Fix dependencies first.${NC}"; exit 1; }

  if [[ -f .env ]]; then
    set -a; source .env 2>/dev/null; set +a
  fi

  validate_keys || exit 1

  echo ""
  echo -e "${CYAN}━━━ PREPARING LAUNCH ━━━${NC}"
  create_runner

  mkdir -p logs reports missions

  # Determine mission file
  local mf_arg=""
  if [[ -n "$MISSION_FILE" ]]; then
    mf_arg="--mission-file $MISSION_FILE"
  elif [[ -f missions/mission.txt ]]; then
    mf_arg="--mission-file missions/mission.txt"
  fi

  echo ""
  echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${GREEN}  LAUNCHING OPENCLAW v2.0 — AUTONOMOUS MODE${NC}"
  echo -e "${GREEN}  Dashboard: ${CYAN}http://localhost:${DASHBOARD_PORT}${NC}"
  echo -e "${GREEN}  Logs: ${CYAN}logs/openclaw.log${NC}"
  echo -e "${GREEN}  Press Ctrl+C for graceful shutdown${NC}"
  echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  exec python3 "$SCRIPT_DIR/__main__.py" \
    --config "$CONFIG_FILE" \
    --port "$DASHBOARD_PORT" \
    --log-level "$LOG_LEVEL" \
    $mf_arg
}

# ─── Parse Arguments ───
while [[ $# -gt 0 ]]; do
  case "$1" in
    --setup)       setup_env; exit 0 ;;
    --help|-h)     usage; exit 0 ;;
    --mission-file) MISSION_FILE="$2"; shift 2 ;;
    --mission)     MISSION_FILE="__inline__"
                   mkdir -p missions
                   echo "$2" > missions/_inline_mission.txt
                   MISSION_FILE="missions/_inline_mission.txt"
                   shift 2 ;;
    --config)      CONFIG_FILE="$2"; shift 2 ;;
    --port)        DASHBOARD_PORT="$2"; shift 2 ;;
    --log-level)   LOG_LEVEL="$2"; shift 2 ;;
    --dry-run)     RUN_MODE="dry"; shift ;;
    --status)      RUN_MODE="status"; shift ;;
    *)             echo "Unknown option: $1"; usage; exit 1 ;;
  esac
done

# ─── Execute ───
case "$RUN_MODE" in
  autonomous) launch ;;
  dry)
    banner
    echo -e "${CYAN}━━━ DRY RUN ━━━${NC}"
    check_deps && validate_keys && echo -e "${GREEN}✓ All checks passed. Ready to launch.${NC}"
    ;;
  status)
    if [[ -f logs/ralph_state.json ]]; then
      python3 -c "import json; d=json.load(open('logs/ralph_state.json')); print(json.dumps(d, indent=2))"
    else
      echo "No state file found. System may not be running."
    fi
    ;;
esac
