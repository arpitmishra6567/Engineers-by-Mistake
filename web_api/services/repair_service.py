"""
Repair execution service integrating the RepairOrchestrator with task persistence and logging.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from repairforge.agent.context import BugReport, ExecutionContext
from repairforge.agent.orchestrator import RepairOrchestrator
from repairforge.agent.state import AgentState
from repairforge.config import AppConfig, ProviderConfig
from repairforge.evaluation.reporter import RepairReporter
from web_api.schemas import LogEntry, RepairCreateRequest, RepairTaskResponse
from web_api.services.repository_service import RepositoryService

logger = logging.getLogger(__name__)


class TaskLogHandler(logging.Handler):
    """Custom logging handler to stream task-specific execution logs."""

    def __init__(self, task_id: str, log_container: List[LogEntry], context_ref: Dict[str, Any]) -> None:
        super().__init__()
        self.task_id = task_id
        self.log_container = log_container
        self.context_ref = context_ref

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            current_stage = self.context_ref.get("stage", "Processing")
            entry = LogEntry(
                timestamp=time.time(),
                level=record.levelname,
                stage=current_stage,
                message=msg,
            )
            self.log_container.append(entry)
        except Exception:
            pass


class RepairService:
    """Manages active and historical repair tasks."""

    def __init__(self, results_dir: Optional[Path] = None) -> None:
        self.results_dir = (results_dir or Path("results")).resolve()
        self.repo_service = RepositoryService()
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.task_logs: Dict[str, List[LogEntry]] = {}
        self._load_historical_reports()

    def _load_historical_reports(self) -> None:
        """Hydrate historical tasks from the results directory."""
        if not self.results_dir.exists():
            return

        for json_path in self.results_dir.glob("repair_report_*.json"):
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                task_id = data.get("task_id", json_path.stem.replace("repair_report_", ""))
                data["task_id"] = task_id

                status = data.get("report_status") or RepairReporter.determine_status(
                    ExecutionContext.model_validate(data)
                )
                data["status"] = status
                start = data.get("start_time", 0)
                end = data.get("end_time")
                data["duration_seconds"] = round(end - start, 2) if end and start else 0.0

                self.tasks[task_id] = data

                # Populate historical log summary
                history = data.get("state_history", [])
                logs = []
                for h in history:
                    logs.append(
                        LogEntry(
                            timestamp=h.get("timestamp", time.time()),
                            level="INFO",
                            stage=h.get("to_state", "TRANSITION"),
                            message=f"Transitioned to {h.get('to_state')}: {h.get('reason') or ''}",
                        )
                    )
                self.task_logs[task_id] = logs
            except Exception as e:
                logger.error("Could not load report %s: %s", json_path, e)

    def list_tasks(self) -> List[RepairTaskResponse]:
        """Return list of all repair tasks sorted by start time."""
        responses = []
        for task_id, t in self.tasks.items():
            responses.append(self._format_task_response(task_id, t))
        return sorted(responses, key=lambda x: x.start_time, reverse=True)

    def get_task(self, task_id: str) -> Optional[RepairTaskResponse]:
        """Get task by ID."""
        task_data = self.tasks.get(task_id)
        if not task_data:
            return None
        return self._format_task_response(task_id, task_data)

    def get_logs(self, task_id: str) -> List[LogEntry]:
        """Get logs for a specific task."""
        return self.task_logs.get(task_id, [])

    def start_repair(self, req: RepairCreateRequest) -> RepairTaskResponse:
        """
        Initiate a repair task in a background thread.
        Uses existing RepairOrchestrator and captures live logs.
        """
        # Validate path
        safe_path = self.repo_service._resolve_and_validate(req.repo_path)

        # Generate temporary ID
        import uuid
        task_id = f"rf-{uuid.uuid4().hex[:8]}"

        bug_report = BugReport(
            title=req.title,
            description=req.description,
            expected_behavior=req.expected_behavior,
            actual_behavior=req.actual_behavior,
            error_message=req.error_message,
            stack_trace=req.stack_trace,
            reproduction_command=req.test_command,
        )

        initial_state = AgentState.INITIALIZED.value
        task_record: Dict[str, Any] = {
            "task_id": task_id,
            "repo_path": str(safe_path),
            "model_name": "mock-repair-model" if req.provider_type == "mock" else "gpt-4o-mini",
            "is_mock": (req.provider_type == "mock"),
            "current_state": initial_state,
            "status": "RUNNING",
            "start_time": time.time(),
            "end_time": None,
            "duration_seconds": None,
            "bug_report": bug_report.model_dump(),
            "repo_summary": None,
            "reproduction_result": None,
            "root_cause_analysis": None,
            "patch": None,
            "verification_result": None,
            "state_history": [],
            "failure_reason": None,
            "human_approved": None,
        }

        self.tasks[task_id] = task_record
        self.task_logs[task_id] = [
            LogEntry(
                timestamp=time.time(),
                level="INFO",
                stage="INITIALIZED",
                message=f"Initialized repair task {task_id} for {safe_path.name}",
            )
        ]

        # Launch background execution thread
        thread = threading.Thread(
            target=self._run_repair_worker,
            args=(task_id, safe_path, bug_report, req),
            daemon=True,
        )
        thread.start()

        return self._format_task_response(task_id, task_record)

    def _run_repair_worker(
        self,
        task_id: str,
        repo_path: Path,
        bug_report: BugReport,
        req: RepairCreateRequest,
    ) -> None:
        """Worker executing orchestrator workflow and collecting real-time logs."""
        config = AppConfig()
        config.provider.provider_type = req.provider_type
        config.agent.auto_approve_human_review = req.auto_approve

        orchestrator = RepairOrchestrator(config=config)

        # Attach log handler
        log_buffer = self.task_logs.setdefault(task_id, [])
        stage_tracker = {"stage": "Repository Analysis"}
        handler = TaskLogHandler(task_id, log_buffer, stage_tracker)
        rf_logger = logging.getLogger("repairforge")
        rf_logger.addHandler(handler)

        try:
            log_buffer.append(
                LogEntry(
                    timestamp=time.time(),
                    level="INFO",
                    stage="Phase 1: Repository Understanding",
                    message="Starting repository analysis and dependency indexing...",
                )
            )

            # Run orchestrator
            context = orchestrator.run(
                repo_path=repo_path,
                bug_report=bug_report,
                test_command=req.test_command,
                isolate_workspace=req.isolate_workspace,
                human_approval_callback=req.auto_approve,
            )

            # Update task data from resulting context
            dumped = context.model_dump(mode="json")
            status = RepairReporter.determine_status(context)
            dumped["status"] = status
            dumped["duration_seconds"] = round((dumped.get("end_time", time.time()) - dumped["start_time"]), 2)
            self.tasks[task_id] = dumped

            log_buffer.append(
                LogEntry(
                    timestamp=time.time(),
                    level="INFO",
                    stage="COMPLETED" if status == "VERIFIED" else "FAILED",
                    message=f"Repair workflow concluded with status: {status}",
                )
            )
        except Exception as e:
            logger.error("Error executing repair %s: %s", task_id, e)
            task_rec = self.tasks.get(task_id, {})
            task_rec["status"] = "EXECUTION_BLOCKED"
            task_rec["current_state"] = AgentState.EXECUTION_BLOCKED.value
            task_rec["failure_reason"] = str(e)
            task_rec["end_time"] = time.time()
            log_buffer.append(
                LogEntry(
                    timestamp=time.time(),
                    level="ERROR",
                    stage="EXECUTION_BLOCKED",
                    message=f"Execution error: {str(e)}",
                )
            )
        finally:
            rf_logger.removeHandler(handler)

    def _format_task_response(self, task_id: str, data: Dict[str, Any]) -> RepairTaskResponse:
        """Format dictionary into standard response schema."""
        start = data.get("start_time", 0.0)
        end = data.get("end_time")
        dur = data.get("duration_seconds")
        if dur is None and end and start:
            dur = round(end - start, 2)

        return RepairTaskResponse(
            task_id=task_id,
            repo_path=str(data.get("repo_path", "")),
            model_name=data.get("model_name", "mock-repair-model"),
            is_mock=bool(data.get("is_mock", True)),
            current_state=str(data.get("current_state", "INITIALIZED")),
            status=str(data.get("status", "RUNNING")),
            start_time=start,
            end_time=end,
            duration_seconds=dur,
            bug_report=data.get("bug_report"),
            repo_summary=data.get("repo_summary"),
            reproduction_result=data.get("reproduction_result"),
            root_cause_analysis=data.get("root_cause_analysis"),
            patch=data.get("patch"),
            verification_result=data.get("verification_result"),
            state_history=data.get("state_history", []),
            failure_reason=data.get("failure_reason"),
            human_approved=data.get("human_approved"),
        )

