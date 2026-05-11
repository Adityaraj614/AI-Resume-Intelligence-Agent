"""
Requirements Analyst Agent.
Wraps the existing deterministic JD parser.
"""
from typing import Any, Dict
from core.workflow.dashboard_workflow import _resolve_job_description

class JDAgentWrapper:
    """
    Acts as the 'Requirements Analyst' agent.
    Delegates to the existing deterministic JD parsing logic.
    """
    
    def __init__(self):
        self.role = "Requirements Analyst"
        self.goal = "Extract structured requirements from JD"
        self.backstory = "Expert HR analyst specializing in role requirements."
        
    def execute(self, inputs: Dict[str, Any]) -> str:
        """
        Processes the JD inputs deterministically.
        """
        return _resolve_job_description(inputs)
