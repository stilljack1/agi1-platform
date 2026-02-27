#!/usr/bin/env python3
"""
OpenClaw Complete v2.0 - Live Monitoring Dashboard
=====================================================
HTTP server that serves a real-time dashboard showing
agent status, task progress, and system health.
"""

import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

logger = logging.getLogger("openclaw.dashboard")

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OpenClaw v2.0 — Mission Control</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #0a0e17; color: #e0e6ed; font-family: 'Segoe UI', system-ui, sans-serif; }
  .header { background: linear-gradient(135deg, #1a1f3a 0%, #0d1117 100%);
    padding: 20px 30px; border-bottom: 2px solid #30363d;
    display: flex; justify-content: space-between; align-items: center; }
  .header h1 { font-size: 24px; background: linear-gradient(90deg, #58a6ff, #bc8cff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .header .status { display: flex; gap: 15px; align-items: center; }
  .status-dot { width: 10px; height: 10px; border-radius: 50%; background: #3fb950;
    animation: pulse 2s infinite; }
  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 20px; padding: 20px; }
  .card { background: #161b22; border: 1px solid #30363d; border-radius: 12px;
    padding: 20px; }
  .card h2 { color: #58a6ff; font-size: 16px; margin-bottom: 15px;
    padding-bottom: 10px; border-bottom: 1px solid #21262d; }
  .agent-row { display: flex; justify-content: space-between; align-items: center;
    padding: 8px 0; border-bottom: 1px solid #21262d; }
  .agent-name { font-weight: 600; }
  .agent-role { color: #8b949e; font-size: 13px; }
  .badge { padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
  .badge-active { background: rgba(63, 185, 80, 0.15); color: #3fb950; }
  .badge-idle { background: rgba(139, 148, 158, 0.15); color: #8b949e; }
  .badge-error { background: rgba(248, 81, 73, 0.15); color: #f85149; }
  .stat-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .stat { background: #0d1117; border-radius: 8px; padding: 15px; text-align: center; }
  .stat-value { font-size: 28px; font-weight: 700; color: #58a6ff; }
  .stat-label { font-size: 12px; color: #8b949e; margin-top: 4px; }
  .task-item { padding: 10px; margin: 6px 0; background: #0d1117;
    border-radius: 8px; border-left: 3px solid #58a6ff; }
  .task-item.completed { border-left-color: #3fb950; opacity: 0.7; }
  .task-item.failed { border-left-color: #f85149; }
  .task-item.in-progress { border-left-color: #d29922;
    animation: taskPulse 2s infinite; }
  @keyframes taskPulse { 0%, 100% { background: #0d1117; } 50% { background: #1a1f2e; } }
  .task-title { font-weight: 600; font-size: 14px; }
  .task-meta { color: #8b949e; font-size: 12px; margin-top: 4px; }
  .log-entry { font-family: 'Fira Code', monospace; font-size: 12px;
    padding: 4px 0; color: #8b949e; }
  .log-entry .time { color: #484f58; }
  .log-entry .agent { color: #bc8cff; }
  .log-entry .action { color: #58a6ff; }
  #lastUpdate { color: #484f58; font-size: 12px; }
  .footer { text-align: center; padding: 15px; color: #484f58; font-size: 12px;
    border-top: 1px solid #21262d; }
</style>
</head>
<body>
<div class="header">
  <h1>OpenClaw v2.0 — Mission Control</h1>
  <div class="status">
    <div class="status-dot"></div>
    <span>AUTONOMOUS MODE</span>
    <span id="lastUpdate"></span>
  </div>
</div>
<div class="grid">
  <div class="card">
    <h2>System Stats</h2>
    <div class="stat-grid">
      <div class="stat"><div class="stat-value" id="totalTasks">0</div><div class="stat-label">Total Tasks</div></div>
      <div class="stat"><div class="stat-value" id="completedTasks">0</div><div class="stat-label">Completed</div></div>
      <div class="stat"><div class="stat-value" id="activeTasks">0</div><div class="stat-label">Active</div></div>
      <div class="stat"><div class="stat-value" id="totalTokens">0</div><div class="stat-label">Tokens Used</div></div>
    </div>
  </div>
  <div class="card">
    <h2>Agent Status</h2>
    <div id="agentList"></div>
  </div>
  <div class="card" style="grid-column: span 2;">
    <h2>Active Tasks</h2>
    <div id="taskList"></div>
  </div>
  <div class="card" style="grid-column: span 2;">
    <h2>Activity Log</h2>
    <div id="logList" style="max-height: 300px; overflow-y: auto;"></div>
  </div>
</div>
<div class="footer">
  OpenClaw Complete v2.0 — Autonomous AGI Orchestration Framework — CEO: Jack
</div>
<script>
const AGENTS = [
  {id:"opus_cairo", name:"Opus 4.6", role:"CAIRO"},
  {id:"sonnet_reviewer", name:"Sonnet 4.5", role:"Reviewer"},
  {id:"gemini_cto", name:"Gemini Pro", role:"CTO"},
  {id:"codex_dev", name:"CodeX 5.3", role:"Dev Lead"},
  {id:"gpt5_arch", name:"GPT 5.2", role:"Architect"},
  {id:"openclaw_pm", name:"OpenClaw", role:"PM"},
  {id:"claude_devops", name:"Claude Code", role:"DevOps"},
  {id:"cowork_wf", name:"Cowork", role:"Workflow"},
  {id:"ralph_loop", name:"Ralph Loop", role:"Orchestrator"}
];

function updateDashboard() {
  fetch('/api/status')
    .then(r => r.json())
    .then(data => {
      document.getElementById('totalTasks').textContent = data.tasks?.total || 0;
      document.getElementById('completedTasks').textContent = data.tasks?.completed || 0;
      document.getElementById('activeTasks').textContent = data.tasks?.in_progress || 0;
      document.getElementById('totalTokens').textContent = (data.tokens || 0).toLocaleString();
      document.getElementById('lastUpdate').textContent = 'Updated: ' + new Date().toLocaleTimeString();

      const agentList = document.getElementById('agentList');
      agentList.innerHTML = AGENTS.map(a => {
        const active = (data.active_agents || []).includes(a.id);
        const cls = active ? 'badge-active' : 'badge-idle';
        const label = active ? 'ACTIVE' : 'IDLE';
        return '<div class="agent-row"><div><div class="agent-name">' + a.name +
          '</div><div class="agent-role">' + a.role + '</div></div>' +
          '<span class="badge ' + cls + '">' + label + '</span></div>';
      }).join('');

      const taskList = document.getElementById('taskList');
      const tasks = data.task_list || [];
      taskList.innerHTML = tasks.length ? tasks.map(t => {
        const cls = t.status === 'completed' ? 'completed' : t.status === 'failed' ? 'failed' : 'in-progress';
        return '<div class="task-item ' + cls + '"><div class="task-title">' + t.title +
          '</div><div class="task-meta">' + t.id + ' | ' + (t.assigned_to || 'unassigned') +
          ' | ' + t.status + '</div></div>';
      }).join('') : '<div class="task-meta">Waiting for tasks...</div>';

      const logList = document.getElementById('logList');
      const logs = data.log || [];
      logList.innerHTML = logs.slice(-30).reverse().map(l =>
        '<div class="log-entry"><span class="time">[' + (l.time || '') + ']</span> ' +
        '<span class="agent">' + (l.agent || '') + '</span> ' +
        '<span class="action">' + (l.message || '') + '</span></div>'
      ).join('');
    })
    .catch(() => {});
}

setInterval(updateDashboard, 5000);
updateDashboard();
</script>
</body>
</html>"""


class DashboardState:
    """Shared state between the dashboard server and the orchestrator."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.data = {
                "tasks": {"total": 0, "completed": 0, "in_progress": 0, "failed": 0, "pending": 0},
                "tokens": 0,
                "active_agents": [],
                "task_list": [],
                "log": []
            }
        return cls._instance

    def update(self, data: Dict):
        self.data.update(data)

    def add_log(self, agent: str, message: str):
        self.data["log"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "agent": agent,
            "message": message
        })
        # Keep last 200 entries
        if len(self.data["log"]) > 200:
            self.data["log"] = self.data["log"][-200:]

    def to_json(self) -> str:
        return json.dumps(self.data)


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the dashboard."""

    def log_message(self, format, *args):
        pass  # Suppress default logging

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())
        elif self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            state = DashboardState()
            self.wfile.write(state.to_json().encode())
        else:
            self.send_response(404)
            self.end_headers()


def start_dashboard(port: int = 8080) -> threading.Thread:
    """Start the dashboard HTTP server in a background thread."""
    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"Dashboard running at http://localhost:{port}")
    return thread
