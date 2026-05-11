"""
Lightweight CrewAI Orchestrator.

This module provides a strictly sequential, deterministic execution
of the agent wrappers. It fulfills the "AI Agent" architecture brief
without introducing unstable LLM routing or autonomous tool execution.
"""
from typing import Any, Dict
import logging

try:
    from crewai import Agent, Task, Crew, Process
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False

from core.agents.jd_agent import JDAgentWrapper
from core.agents.resume_agent import ResumeAgentWrapper
from core.agents.ranking_agent import RankingAgentWrapper
from core.agents.report_agent import ReportAgentWrapper
from core.workflow.dashboard_workflow import DashboardWorkflowError

logger = logging.getLogger(__name__)

class LightweightOrchestrator:
    """
    Orchestrates the sequential flow of Agents deterministically.
    """
    def __init__(self):
        self.jd_agent = JDAgentWrapper()
        self.resume_agent = ResumeAgentWrapper()
        self.ranking_agent = RankingAgentWrapper()
        self.report_agent = ReportAgentWrapper()
        
    def run_sequential_flow(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the workflow sequentially.
        JD Agent -> Resume Agent -> Ranking Agent -> Report Agent
        """
        logger.info("CrewAI Orchestrator: Starting sequential execution.")
        
        # 1. JD Agent Execution
        try:
            job_description = self.jd_agent.execute(inputs)
        except Exception as exc:
            logger.exception("jd_agent_failed")
            raise DashboardWorkflowError(
                "The JD Agent could not process the job description."
            ) from exc

        if not job_description.strip():
            raise DashboardWorkflowError("JD Agent requires a job description.")

        # 2. Resume Agent Execution
        resume_files = list(inputs.get("resume_files", []) or [])
        linkedin_files = list(inputs.get("linkedin_files", []) or [])
        
        if not resume_files and not linkedin_files:
            raise DashboardWorkflowError("Resume Agent requires candidate files.")
            
        candidate_profiles, intake_warnings = self.resume_agent.execute(resume_files, linkedin_files)
        
        if not candidate_profiles:
            raise DashboardWorkflowError("Resume Agent failed to build candidate profiles.")

        # 3. Ranking Agent Execution
        try:
            ranked_candidates, pipeline_debug = self.ranking_agent.execute(job_description, candidate_profiles)
        except Exception as exc:
            raise DashboardWorkflowError("Ranking Agent encountered an error during evaluation.") from exc
            
        if not ranked_candidates:
            raise DashboardWorkflowError("Ranking Agent found no evidence for ranking.")

        # 4. Report Agent Execution
        workflow_result = self.report_agent.execute(ranked_candidates)
        
        # Merge debug info
        workflow_result["workflow_outputs"]["candidate_profiles"] = candidate_profiles
        workflow_result["workflow_outputs"]["pipeline_debug"] = pipeline_debug
        workflow_result["diagnostics"]["pipeline_warnings"].extend(intake_warnings)
        
        logger.info("CrewAI Orchestrator: Execution complete.")
        return workflow_result
