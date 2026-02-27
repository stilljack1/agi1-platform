#!/usr/bin/env python3
"""
OpenClaw Complete v2.0 - Cowork Workflow Manager
==================================================
Manages task queues, dependencies, resource allocation,
and workflow state for the autonomous system.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from collections import deque
from dataclasses import dataclass, field, asdict

logger = logging.getLogger("openclaw.cowork")


class WorkflowPhase:
    PLANNING = "planning"
    DEVELOPMENT = "development"
    REVIEW = "review"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"


@dataclass
class WorkItem:
    id: str
    name: str
    phase: str
    agent_id: str
    input_data: Dict = field(default_factory=dict)
    output_data: Dict = field(default_factory=dict)
    status: str = "queued"  # queued, running, done, error
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


class Pipeline:
    """A sequence of workflow phases with their assigned agents."""

    def __init__(self, name: str, phases: List[Dict]):
        self.name = name
        self.phases = phases  # [{"phase": "...", "agent_id": "...", "config": {...}}]
        self.current_phase_idx = 0
        self.results: Dict[str, Any] = {}

    @property
    def current_phase(self) -> Optional[Dict]:
        if self.current_phase_idx < len(self.phases):
            return self.phases[self.current_phase_idx]
        return None

    def advance(self, result: Any):
        phase = self.current_phase
        if phase:
            self.results[phase["phase"]] = result
            self.current_phase_idx += 1

    @property
    def is_complete(self) -> bool:
        return self.current_phase_idx >= len(self.phases)


class CoworkManager:
    """
    Workflow manager that coordinates task execution pipelines.
    Handles resource allocation, dependency resolution, and progress tracking.
    """

    def __init__(self):
        self.queues: Dict[str, deque] = {
            "high": deque(),
            "normal": deque(),
            "low": deque()
        }
        self.active_items: Dict[str, WorkItem] = {}
        self.completed_items: List[WorkItem] = []
        self.pipelines: Dict[str, Pipeline] = {}
        self.item_counter = 0
        self.agent_workload: Dict[str, int] = {}
        self.max_concurrent_per_agent = 3
        self.workflow_log: List[Dict] = []

    def enqueue(self, name: str, phase: str, agent_id: str,
                input_data: Dict = None, priority: str = "normal") -> WorkItem:
        """Add a work item to the queue."""
        self.item_counter += 1
        item = WorkItem(
            id=f"WI-{self.item_counter:05d}",
            name=name,
            phase=phase,
            agent_id=agent_id,
            input_data=input_data or {}
        )
        self.queues[priority].append(item)
        logger.info(f"Enqueued {item.id}: {name} → {agent_id} [{priority}]")
        return item

    def dequeue(self) -> Optional[WorkItem]:
        """Get the next work item, respecting priority and agent capacity."""
        for priority in ["high", "normal", "low"]:
            queue = self.queues[priority]
            for i, item in enumerate(queue):
                load = self.agent_workload.get(item.agent_id, 0)
                if load < self.max_concurrent_per_agent:
                    queue.remove(item)
                    item.status = "running"
                    self.active_items[item.id] = item
                    self.agent_workload[item.agent_id] = load + 1
                    logger.info(f"Dequeued {item.id}: {item.name}")
                    return item
        return None

    def complete_item(self, item_id: str, output: Dict = None, error: str = None):
        """Mark a work item as complete or failed."""
        item = self.active_items.pop(item_id, None)
        if not item:
            logger.warning(f"Work item {item_id} not found in active items")
            return

        load = self.agent_workload.get(item.agent_id, 1)
        self.agent_workload[item.agent_id] = max(0, load - 1)

        if error:
            item.status = "error"
            item.error = error
        else:
            item.status = "done"
            item.output_data = output or {}

        item.completed_at = datetime.now().isoformat()
        self.completed_items.append(item)

        self.workflow_log.append({
            "timestamp": datetime.now().isoformat(),
            "item_id": item.id,
            "name": item.name,
            "status": item.status,
            "agent": item.agent_id
        })

        logger.info(f"Completed {item.id}: {item.status}")

    def create_pipeline(self, name: str, task_description: str) -> Pipeline:
        """Create a standard development pipeline for a task."""
        phases = [
            {"phase": WorkflowPhase.PLANNING, "agent_id": "opus_cairo",
             "config": {"prompt": f"Plan the approach for: {task_description}"}},
            {"phase": WorkflowPhase.DEVELOPMENT, "agent_id": "codex_dev",
             "config": {"prompt": f"Implement: {task_description}"}},
            {"phase": WorkflowPhase.REVIEW, "agent_id": "sonnet_reviewer",
             "config": {"prompt": "Review the implementation for quality and security"}},
            {"phase": WorkflowPhase.TESTING, "agent_id": "sonnet_reviewer",
             "config": {"prompt": "Generate and run tests for the implementation"}},
            {"phase": WorkflowPhase.DEPLOYMENT, "agent_id": "claude_devops",
             "config": {"prompt": "Prepare deployment configuration"}}
        ]
        pipeline = Pipeline(name, phases)
        self.pipelines[name] = pipeline
        logger.info(f"Created pipeline: {name} with {len(phases)} phases")
        return pipeline

    def get_status(self) -> Dict:
        """Get full workflow status."""
        return {
            "queues": {k: len(v) for k, v in self.queues.items()},
            "active": len(self.active_items),
            "completed": len(self.completed_items),
            "error_count": len([i for i in self.completed_items if i.status == "error"]),
            "agent_workload": dict(self.agent_workload),
            "pipelines": {
                name: {
                    "current_phase": p.current_phase["phase"] if p.current_phase else "complete",
                    "progress": f"{p.current_phase_idx}/{len(p.phases)}"
                } for name, p in self.pipelines.items()
            }
        }

    def get_dashboard_data(self) -> Dict:
        """Get data formatted for the monitoring dashboard."""
        recent = self.workflow_log[-20:] if self.workflow_log else []
        return {
            "status": self.get_status(),
            "recent_activity": recent,
            "active_items": [item.to_dict() for item in self.active_items.values()],
            "timestamp": datetime.now().isoformat()
        }
