"""
Agent Orchestrator managing the checkpoint-based repair state machine.
Enforces the 7-phase repair lifecycle, execution safety, and verification gates.
"""

from __future__ import annotations

import logging
import shutil
import tempfile
import time
from pathlib import Path
from typing import Optional

from repairforge.agent.context import (
    BugReport,
    ExecutionContext,
    RepoSummary,
    ReproductionResult,
    RootCauseRecord,
    PatchRecord,
    VerificationResult,
)
from repairforge.agent.state import AgentState, StateMachine, InvalidStateTransitionError
from repairforge.config import AppConfig
from repairforge.evaluation.reporter import RepairReporter
from repairforge.execution.policy import ExecutionPolicy, ExecutionMode
from repairforge.execution.runner import CommandRunner
from repairforge.investigation.investigator import BugInvestigator
from repairforge.investigation.issue_parser import IssueParser
from repairforge.investigation.reproducer import BugReproducer
from repairforge.investigation.root_cause import RootCauseAnalyzer
from repairforge.models.base import BaseModelAdapter
from repairforge.models.mock import MockModelAdapter
from repairforge.models.openai_compatible import OpenAICompatibleModelAdapter
from repairforge.repair.patch_applier import PatchApplier
from repairforge.repair.patch_generator import PatchGenerator
from repairforge.repair.verifier import PatchVerifier
from repairforge.repository.analyzer import RepositoryAnalyzer

logger = logging.getLogger(__name__)


class RepairOrchestrator:
    """Coordinates the full investigation, reproduction, repair, and verification pipeline."""

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        model_adapter: Optional[BaseModelAdapter] = None,
    ) -> None:
        self.config = config or AppConfig()
        self.model_adapter = model_adapter or self._init_model_adapter()

        # Shared execution runner adhering to security policy
        policy = ExecutionPolicy(
            mode=ExecutionMode.SAFE_FIXTURE,
            command_timeout_seconds=self.config.execution.command_timeout_seconds,
            allow_destructive_ops=False,
            enforce_safe_commands_only=True,
        )
        self.runner = CommandRunner(policy=policy)

        # Components
        self.reproducer = BugReproducer(runner=self.runner)
        self.root_cause_analyzer = RootCauseAnalyzer(model_adapter=self.model_adapter)
        self.patch_generator = PatchGenerator(model_adapter=self.model_adapter)
        self.verifier = PatchVerifier(runner=self.runner)

    def _init_model_adapter(self) -> BaseModelAdapter:
        """Instantiate configured model adapter."""
        ptype = self.config.provider.provider_type.lower()
        if ptype == "openai_compatible":
            return OpenAICompatibleModelAdapter(
                model_name=self.config.provider.model_name,
                base_url=self.config.provider.base_url,
                api_key=self.config.provider.api_key,
                timeout_seconds=self.config.provider.timeout_seconds,
                temperature=self.config.provider.temperature,
            )
        return MockModelAdapter(model_name=self.config.provider.model_name)

    def run(
        self,
        repo_path: Path,
        bug_report: BugReport,
        test_command: Optional[str] = None,
        isolate_workspace: bool = True,
        human_approval_callback: Optional[bool] = None,
    ) -> ExecutionContext:
        """
        Execute the end-to-end repair workflow.
        If isolate_workspace is True, the reproduction and patching occur in a temporary clone
        to leave the original repository completely unchanged.
        """
        state_machine = StateMachine(AgentState.INITIALIZED)
        context = ExecutionContext(
            repo_path=repo_path.resolve(),
            model_name=self.model_adapter.model_name,
            is_mock=self.model_adapter.is_deterministic,
            current_state=state_machine.current_state,
            state_history=[],
            bug_report=bug_report,
            max_retries=self.config.agent.max_retries,
        )

        def _transition(to_state: AgentState, reason: Optional[str] = None) -> None:
            rec = state_machine.transition(to_state, reason=reason)
            context.current_state = rec.to_state
            context.state_history.append(rec)
            logger.info("Transitioned to: %s (Reason: %s)", rec.to_state.value, reason)

        # Setup workspace (temporary copy if isolated)
        temp_dir_obj = None
        if isolate_workspace:
            temp_dir = tempfile.mkdtemp(prefix="repairforge_ws_")
            temp_dir_obj = temp_dir
            working_repo_path = Path(temp_dir)
            # Copy repository contents ignoring git/venvs
            shutil.copytree(
                repo_path,
                working_repo_path,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(".git", ".venv", "venv", "__pycache__", "results"),
            )
        else:
            working_repo_path = repo_path.resolve()

        try:
            # PHASE 1: Repository Understanding
            logger.info("Phase 1: Analyzing repository structure...")
            analyzer = RepositoryAnalyzer(working_repo_path)
            context.repo_summary = analyzer.analyze()
            _transition(AgentState.REPOSITORY_ANALYZED, "Repository scanned and dependencies indexed")

            # PHASE 2: Bug Understanding
            logger.info("Phase 2: Understanding issue specification...")
            investigator = BugInvestigator(working_repo_path)
            candidate_files = investigator.locate_candidate_files(bug_report, context.repo_summary)
            _transition(AgentState.ISSUE_UNDERSTOOD, f"Identified candidates: {candidate_files}")

            # PHASE 3: Bug Reproduction
            logger.info("Phase 3: Reproducing reported bug...")
            _transition(AgentState.REPRODUCTION_ATTEMPTED, "Executing reproduction test command")
            repro_res = self.reproducer.reproduce(working_repo_path, bug_report, custom_command=test_command)
            context.reproduction_result = repro_res

            if repro_res.status == "REPRODUCED":
                _transition(AgentState.REPRODUCED, repro_res.evidence_notes)
            elif repro_res.status == "NOT_REPRODUCED":
                _transition(AgentState.NOT_REPRODUCED, "Test suite did not reproduce the defect")
                context.failure_reason = "Defect could not be reproduced by test command."
                return self._finalize(context)
            else:
                _transition(AgentState.EXECUTION_BLOCKED, repro_res.evidence_notes)
                context.failure_reason = "Execution blocked or timed out during reproduction."
                return self._finalize(context)

            # PHASE 4: Root Cause Analysis
            logger.info("Phase 4: Analyzing root cause...")
            rc_record = self.root_cause_analyzer.analyze(
                working_repo_path, context.repo_summary, bug_report, repro_res
            )
            context.root_cause_analysis = rc_record

            if rc_record.uncertainty_level == "HIGH":
                _transition(AgentState.ROOT_CAUSE_UNCERTAIN, "High uncertainty in defect diagnosis")
                context.failure_reason = "Root cause analysis has high uncertainty."
                return self._finalize(context)

            _transition(AgentState.ROOT_CAUSE_IDENTIFIED, f"Diagnosed in {rc_record.file_path}")

            # PHASE 5 & 6: Patch Generation, Application & Verification Loop
            applier = PatchApplier(working_repo_path)
            patch_success = False

            while context.retry_count <= context.max_retries:
                logger.info("Phase 5: Generating patch (attempt %s)...", context.retry_count + 1)
                _transition(AgentState.PATCH_GENERATED, f"Patch generated (attempt {context.retry_count + 1})")

                try:
                    patch = self.patch_generator.generate_patch(working_repo_path, bug_report, rc_record)
                    context.patch = patch

                    # Apply patch to working repository
                    applier.apply_unified_diff(patch.diff, target_file_override=rc_record.file_path)

                    # Verify patch
                    logger.info("Phase 6: Verifying patch with regression tests...")
                    verif_cmd = test_command or repro_res.command
                    verif_res = self.verifier.verify(working_repo_path, patch, test_command=verif_cmd)
                    context.verification_result = verif_res

                    if verif_res.verified:
                        _transition(AgentState.PATCH_VALIDATED, "All regression tests passed successfully")
                        patch_success = True
                        break
                    else:
                        logger.warning("Verification failed: %s", verif_res.tests_failed)
                        context.retry_count += 1
                        if context.retry_count <= context.max_retries:
                            _transition(AgentState.VALIDATION_FAILED, "Test validation failed, attempting retry")
                            applier.rollback()
                        else:
                            _transition(AgentState.VALIDATION_FAILED, "Retry budget exhausted without passing tests")
                            context.failure_reason = "Patch validation failed after exhausting retry budget."
                            break
                except Exception as e:
                    logger.error("Patch generation or application error: %s", e)
                    context.retry_count += 1
                    if context.retry_count <= context.max_retries:
                        _transition(AgentState.PATCH_GENERATION_FAILED, f"Patch error: {str(e)}")
                    else:
                        _transition(AgentState.PATCH_GENERATION_FAILED, "Max retries reached on patch errors")
                        context.failure_reason = f"Patch error: {str(e)}"
                        break

            if not patch_success:
                return self._finalize(context)

            # PHASE 7: Human Review Gate
            logger.info("Phase 7: Human review checkpoint...")
            _transition(AgentState.HUMAN_REVIEW, "Awaiting explicit human approval")

            # Check approval gate
            approved = False
            if human_approval_callback is not None:
                approved = human_approval_callback
            elif self.config.agent.auto_approve_human_review:
                approved = True

            context.human_approved = approved

            if approved:
                _transition(AgentState.COMPLETED, "Repair verified and approved by human")
            else:
                _transition(AgentState.EXECUTION_BLOCKED, "Human approval rejected or pending")
                context.failure_reason = "Awaiting human review approval."

            return self._finalize(context)

        finally:
            # Clean up temporary isolated workspace if created
            if temp_dir_obj and Path(temp_dir_obj).exists():
                try:
                    shutil.rmtree(temp_dir_obj, ignore_errors=True)
                except Exception:
                    pass

    def _finalize(self, context: ExecutionContext) -> ExecutionContext:
        """Mark end time, save evaluation reports, and return context."""
        context.end_time = time.time()
        out_dir = self.config.agent.output_dir
        try:
            RepairReporter.save_reports(context, out_dir)
        except Exception as e:
            logger.error("Failed to save repair reports: %s", e)
        return context

