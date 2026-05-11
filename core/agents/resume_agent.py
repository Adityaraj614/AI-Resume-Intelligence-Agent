"""
Candidate Profiler Agent.
Wraps the existing parsing, embedding, and LinkedIn JSON pipeline.
"""
from typing import Any, Dict, List, Tuple
from core.workflow.dashboard_workflow import _build_candidate_profiles

class ResumeAgentWrapper:
    """
    Acts as the 'Candidate Profiler' agent.
    Delegates to the existing deterministic resume and LinkedIn JSON parsing logic.
    """
    
    def __init__(self):
        self.role = "Candidate Profiler"
        self.goal = "Process resumes and structured LinkedIn profiles"
        self.backstory = "Expert talent sourcer capable of standardizing candidate data."
        
    def execute(self, resume_files: List[Any], linkedin_files: List[Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Processes candidate files deterministically.
        Supports lightweight LinkedIn JSON ingestion by reusing the existing core.linkedin module.
        """
        return _build_candidate_profiles(resume_files, linkedin_files)
