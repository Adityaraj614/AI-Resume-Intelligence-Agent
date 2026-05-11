"""
Scoring Engineer Agent.
Wraps the existing similarity ranking and FAISS retrieval engine.
"""
from typing import Any, Dict, List, Tuple
from core.workflow.dashboard_workflow import _build_ranked_candidates

class RankingAgentWrapper:
    """
    Acts as the 'Scoring Engineer' agent.
    Delegates to the existing FAISS similarity ranking engine.
    """
    
    def __init__(self):
        self.role = "Scoring Engineer"
        self.goal = "Score and rank candidates against the JD"
        self.backstory = "Expert data scientist specializing in semantic candidate matching."
        
    def execute(self, job_description: str, candidate_profiles: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executes the ranking pipeline deterministically.
        """
        return _build_ranked_candidates(job_description, candidate_profiles)
