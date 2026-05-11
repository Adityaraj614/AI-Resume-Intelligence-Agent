"""
Reporting Specialist Agent.
Wraps the existing report/export modules to generate shortlist outputs.
"""
from typing import Any, Dict, List
from core.workflow.workflow_manager import run_recruiter_workflow
from core.workflow.dashboard_workflow import _current_timestamp

class ReportAgentWrapper:
    """
    Acts as the 'Reporting Specialist' agent.
    Delegates to the existing export generation logic.
    """
    
    def __init__(self):
        self.role = "Reporting Specialist"
        self.goal = "Generate final recruiter shortlists and export payloads"
        self.backstory = "Expert HR coordinator specializing in generating actionable reports."
        
    def execute(self, ranked_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates the final workflow payload and triggers exports deterministically.
        """
        return run_recruiter_workflow(
            ranked_candidates=ranked_candidates,
            execution_timestamp=_current_timestamp(),
        )
