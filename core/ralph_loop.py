from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def read_root():
    return {"status": "AGI Platform Core Online", "loop": "Active"}

#!/usr/bin/env python3
"""
OpenClaw Complete v2.0 - Ralph Loop Agent
==========================================
The autonomous orchestration engine. Runs an infinite loop that:
1. Reads the current mission
2. Decomposes it into tasks
3. Routes tasks to the best agents
4. Monitors execution
5. Reports to CEO (Jack)
"""

import os
import json
import asyncio
import logging
import signal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum

from agent_gateway import AgentGateway, create_gateway

logger = logging.getLogger("openclaw.ralph")


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(int, Enum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class Task:
    id: str
    title: str
    description: str
    task_type: str  # coding, research, testing, etc.
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    retries: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["status"] = self.status.value
        d["priority"] = self.priority.value
        return d


class CEOReporter:
    """Handles all reporting to Jack (CEO)."""

    def __init__(self, config: Dict, reports_dir: str = "reports"):
        self.ceo = config.get("system", {}).get("ceo", {})
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        self.report_count = 0

    def generate_report(self, loop_stats: Dict, tasks: List[Task],
                        cycle_number: int) -> str:
        now = datetime.now()
        completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        in_progress = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
        failed = [t for t in tasks if t.status == TaskStatus.FAILED]
        pending = [t for t in tasks if t.status == TaskStatus.PENDING]

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          OPENCLAW v2.0 — CEO STATUS REPORT #{self.report_count + 1:<15}║
╠══════════════════════════════════════════════════════════════╣
║  To: {self.ceo.get('name', 'CEO'):<55}║
║  Role: {self.ceo.get('role', 'Founder & CEO'):<53}║
║  Time: {now.strftime('%Y-%m-%d %H:%M:%S'):<53}║
║  Cycle: {cycle_number:<52}║
╠══════════════════════════════════════════════════════════════╣
║  TASK SUMMARY                                                ║
║  ─────────────────────────────────────────────────────────── ║
║  Completed:   {len(completed):<46}║
║  In Progress: {len(in_progress):<46}║
║  Pending:     {len(pending):<46}║
║  Failed:      {len(failed):<46}║
║  Total:       {len(tasks):<46}║
╠══════════════════════════════════════════════════════════════╣
║  SYSTEM STATS                                                ║
║  ─────────────────────────────────────────────────────────── ║
║  Uptime: {loop_stats.get('uptime', 'N/A'):<51}║
║  Total API Calls: {loop_stats.get('total_api_calls', 0):<41}║
║  Tokens Used: {loop_stats.get('total_tokens', 0):<46}║
║  Active Agents: {loop_stats.get('active_agents', 0):<44}║
╠══════════════════════════════════════════════════════════════╣"""

        if in_progress:
            report += "\n║  ACTIVE TASKS                                                ║\n"
            for t in in_progress[:5]:
                agent = t.assigned_to or "unassigned"
                line = f"  • [{t.id}] {t.title[:30]} → {agent}"
                report += f"║{line:<61}║\n"

        if completed and self.report_count > 0:
            recent = [t for t in completed if t.completed_at and
                      datetime.fromisoformat(t.completed_at) > now - timedelta(minutes=15)]
            if recent:
                report += "╠══════════════════════════════════════════════════════════════╣\n"
                report += "║  RECENTLY COMPLETED                                          ║\n"
                for t in recent[:5]:
                    line = f"  ✓ {t.title[:55]}"
                    report += f"║{line:<61}║\n"

        if failed:
            report += "╠══════════════════════════════════════════════════════════════╣\n"
            report += "║  ⚠ FAILURES (Needs Attention)                                ║\n"
            for t in failed[:3]:
                line = f"  ✗ {t.title[:55]}"
                report += f"║{line:<61}║\n"

        report += "╚══════════════════════════════════════════════════════════════╝"

        self.report_count += 1
        # Save report to file
        filename = f"report_{now.strftime('%Y%m%d_%H%M%S')}.txt"
        (self.reports_dir / filename).write_text(report)

        return report


class RalphLoop:
    """
    The autonomous orchestration engine.
    Runs infinitely, processing tasks and coordinating agents.
    """

    def __init__(self, config_path: str = "agents.json", mission_file: str = None):
        self.config_path = config_path
        self.gateway: Optional[AgentGateway] = None
        self.tasks: Dict[str, Task] = {}
        self.task_counter = 0
        self.cycle_count = 0
        self.start_time = datetime.now()
        self.running = False
        self.mission = ""
        self.mission_file = mission_file

        # Load config
        with open(config_path) as f:
            self.config = json.load(f)

        self.loop_interval = self.config["system"].get("loop_interval_seconds", 30)
        self.report_interval = self.config["system"].get("report_interval_minutes", 15)
        self.reporter = CEOReporter(self.config)
        self.last_report_time = datetime.now()

        # State persistence
        self.state_file = Path("logs/ralph_state.json")

    async def initialize(self):
        """Initialize the gateway and load state."""
        self.gateway = create_gateway(self.config_path)
        self._load_state()
        if self.mission_file:
            self._load_mission(self.mission_file)
        logger.info("Ralph Loop initialized")

    def _load_mission(self, filepath: str):
        p = Path(filepath)
        if p.exists():
            self.mission = p.read_text().strip()
            logger.info(f"Mission loaded: {len(self.mission)} chars")
        else:
            logger.warning(f"Mission file not found: {filepath}")

    def _load_state(self):
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text())
                for tid, tdata in data.get("tasks", {}).items():
                    tdata["status"] = TaskStatus(tdata["status"])
                    tdata["priority"] = TaskPriority(tdata["priority"])
                    self.tasks[tid] = Task(**tdata)
                self.task_counter = data.get("task_counter", 0)
                logger.info(f"Restored {len(self.tasks)} tasks from state")
            except Exception as e:
                logger.warning(f"Could not restore state: {e}")

    def _save_state(self):
        self.state_file.parent.mkdir(exist_ok=True)
        data = {
            "tasks": {tid: t.to_dict() for tid, t in self.tasks.items()},
            "task_counter": self.task_counter,
            "cycle_count": self.cycle_count,
            "saved_at": datetime.now().isoformat()
        }
        self.state_file.write_text(json.dumps(data, indent=2))

    def create_task(self, title: str, description: str, task_type: str,
                    priority: TaskPriority = TaskPriority.MEDIUM,
                    dependencies: List[str] = None) -> Task:
        self.task_counter += 1
        task_id = f"TASK-{self.task_counter:04d}"
        task = Task(
            id=task_id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            dependencies=dependencies or []
        )
        self.tasks[task_id] = task
        logger.info(f"Created task {task_id}: {title}")
        return task

    async def decompose_mission(self):
        """Use Opus to break the mission into actionable tasks."""
        if not self.mission:
            logger.warning("No mission loaded")
            return

        if self.tasks:
            logger.info("Tasks already exist, skipping decomposition")
            return

        system_prompt = """You are OpenClaw's mission decomposition engine.
Break the given mission into specific, actionable tasks.
Return a JSON array of tasks, each with:
- title: short task name
- description: detailed description
- task_type: one of [research, coding, debugging, code_review, testing, deployment, architecture, documentation, data, strategy, workflow]
- priority: 0=critical, 1=high, 2=medium, 3=low
- dependencies: list of task titles this depends on (empty if none)

Return ONLY valid JSON, no markdown."""

        result = await self.gateway.send_to_agent(
            "opus_cairo",
            [{"role": "user", "content": f"MISSION:\n{self.mission}\n\nDecompose this into tasks."}],
            system=system_prompt
        )

        if result.get("success"):
            try:
                content = result["content"].strip()
                # Try to extract JSON from response
                if "```" in content:
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()
                task_list = json.loads(content)
                for t in task_list:
                    self.create_task(
                        title=t["title"],
                        description=t["description"],
                        task_type=t.get("task_type", "coding"),
                        priority=TaskPriority(t.get("priority", 2)),
                        dependencies=t.get("dependencies", [])
                    )
                logger.info(f"Decomposed mission into {len(task_list)} tasks")
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Failed to parse mission decomposition: {e}")
                # Create a default task
                self.create_task(
                    "Process mission manually",
                    f"Opus response needs manual parsing:\n{result['content'][:500]}",
                    "strategy", TaskPriority.HIGH
                )
        else:
            logger.error(f"Mission decomposition failed: {result.get('error')}")

    def _get_next_task(self) -> Optional[Task]:
        """Get the highest priority task that's ready to execute."""
        ready = []
        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            # Check dependencies
            deps_met = all(
                any(t.title == dep and t.status == TaskStatus.COMPLETED
                    for t in self.tasks.values())
                for dep in task.dependencies
            )
            if deps_met:
                ready.append(task)

        if not ready:
            return None

        ready.sort(key=lambda t: t.priority.value)
        return ready[0]

    def _select_agent(self, task: Task) -> Optional[str]:
        """Select the best agent for a task based on type and routing."""
        candidates = self.gateway.get_agents_for_task(task.task_type)
        if not candidates:
            candidates = ["codex_dev"]  # Default fallback

        # Check which agents have working providers
        for agent_id in candidates:
            agent = self.gateway.get_agent(agent_id)
            if agent:
                provider = agent["provider"]
                if provider == "internal" or provider in self.gateway.clients:
                    return agent_id

        return candidates[0] if candidates else None

    async def execute_task(self, task: Task) -> bool:
        """Execute a task using the assigned agent."""
        agent_id = self._select_agent(task)
        if not agent_id:
            task.status = TaskStatus.BLOCKED
            logger.warning(f"No agent available for task {task.id}")
            return False

        task.assigned_to = agent_id
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now().isoformat()

        agent = self.gateway.get_agent(agent_id)
        system = f"""You are {agent['name']}, role: {agent['role']}.
Your responsibilities: {', '.join(agent['responsibilities'])}
You are part of the OpenClaw autonomous system.
Execute the following task thoroughly and return actionable results.
Include code if relevant. Be specific and implementation-ready."""

        result = await self.gateway.send_to_agent(
            agent_id,
            [{"role": "user", "content": f"TASK: {task.title}\n\nDETAILS:\n{task.description}"}],
            system=system
        )

        if result.get("success"):
            task.result = result["content"]

            # If it's code, send for review
            if task.task_type in ["coding", "debugging", "api"]:
                task.status = TaskStatus.REVIEW
                review = await self._review_task(task)
                if review:
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now().isoformat()
                    logger.info(f"Task {task.id} completed and reviewed")
                    return True
                else:
                    task.retries += 1
                    if task.retries >= task.max_retries:
                        task.status = TaskStatus.FAILED
                        return False
                    task.status = TaskStatus.PENDING
                    return False
            else:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now().isoformat()
                logger.info(f"Task {task.id} completed")
                return True
        else:
            task.retries += 1
            if task.retries >= task.max_retries:
                task.status = TaskStatus.FAILED
                logger.error(f"Task {task.id} failed after {task.retries} retries")
            else:
                task.status = TaskStatus.PENDING
                logger.warning(f"Task {task.id} retry {task.retries}")
            return False

    async def _review_task(self, task: Task) -> bool:
        """Send code output to Sonnet for review."""
        result = await self.gateway.send_to_agent(
            "sonnet_reviewer",
            [{"role": "user", "content": f"Review this output for task '{task.title}':\n\n{task.result[:4000]}"}],
            system="You are a code reviewer. Check for bugs, security issues, and best practices. Reply APPROVED if acceptable, or list issues."
        )
        if result.get("success"):
            content = result["content"].upper()
            return "APPROVED" in content or "LGTM" in content
        return True  # On review failure, accept the task

    def _get_loop_stats(self) -> Dict:
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        gw_stats = self.gateway.get_stats() if self.gateway else {}
        total_api = sum(p.get("total_requests", 0) for p in gw_stats.get("providers", {}).values())
        total_tokens = sum(p.get("total_tokens", 0) for p in gw_stats.get("providers", {}).values())

        active = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])

        return {
            "uptime": f"{hours}h {minutes}m {seconds}s",
            "total_api_calls": total_api,
            "total_tokens": total_tokens,
            "active_agents": active,
            "cycle": self.cycle_count,
            "providers": gw_stats.get("providers", {})
        }

    async def _maybe_report(self):
        """Send CEO report if interval has elapsed."""
        now = datetime.now()
        if now - self.last_report_time >= timedelta(minutes=self.report_interval):
            stats = self._get_loop_stats()
            report = self.reporter.generate_report(stats, list(self.tasks.values()), self.cycle_count)
            print(report)
            self.last_report_time = now

    async def run(self):
        """Main infinite loop."""
        self.running = True
        await self.initialize()

        # Handle graceful shutdown
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))

        logger.info("=" * 60)
        logger.info("  RALPH LOOP — AUTONOMOUS ORCHESTRATOR STARTED")
        logger.info(f"  Mission loaded: {'YES' if self.mission else 'NO'}")
        logger.info(f"  Loop interval: {self.loop_interval}s")
        logger.info(f"  Report interval: {self.report_interval}min")
        logger.info("=" * 60)

        # Initial mission decomposition
        await self.decompose_mission()

        # Initial report
        stats = self._get_loop_stats()
        report = self.reporter.generate_report(stats, list(self.tasks.values()), 0)
        print(report)

        while self.running:
            self.cycle_count += 1
            logger.info(f"--- Cycle {self.cycle_count} ---")

            # Get and execute next task
            task = self._get_next_task()
            if task:
                await self.execute_task(task)
            else:
                # Check if all tasks are done
                all_done = all(t.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
                               for t in self.tasks.values()) if self.tasks else True
                if all_done and self.tasks:
                    logger.info("All tasks completed! Waiting for new mission...")

            # Save state and maybe report
            self._save_state()
            await self._maybe_report()

            # Wait for next cycle
            await asyncio.sleep(self.loop_interval)

    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down Ralph Loop...")
        self.running = False
        self._save_state()
        if self.gateway:
            await self.gateway.close_all()

        # Final report
        stats = self._get_loop_stats()
        report = self.reporter.generate_report(stats, list(self.tasks.values()), self.cycle_count)
        print("\n📋 FINAL REPORT:")
        print(report)


async def main(config_path: str = "agents.json", mission_file: str = None):
    """Entry point for Ralph Loop."""
    ralph = RalphLoop(config_path=config_path, mission_file=mission_file)
    await ralph.run()
