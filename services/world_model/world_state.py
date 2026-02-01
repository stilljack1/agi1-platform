class WorldState:
    def __init__(self):
        self.executive_state = {}
        self.market_state = {}
        self.infrastructure_state = {}
        self.revenue_state = {}

        self.CTM = {"active_tasks": [], "knowledge_base": {}, "reasoning_logs": []}
        self.LTM = {"task_queue": [], "completed_tasks": [], "performance_metrics": {}}
        self.SI = {"environment_maps": {}, "agent_positions": {}, "pathfinding_graphs": {}}
        self.LAM = {"action_plan_queue": [], "executed_actions": [], "feedback_logs": []}

    def update_revenue(self, amount):
        self.revenue_state.get('total', 0) + amount
        return self.revenue_state['total']

    def log_ctm_reasoning(self, step_description):
        self.CTM['reasoning_logs'].append(step_description)
