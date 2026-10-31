"""Repair management routes."""

from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from web_api.schemas import LogEntry, RepairCreateRequest, RepairLogsResponse, RepairTaskResponse
from web_api.services.repair_service import RepairService

router = APIRouter(prefix="/api/repairs", tags=["repairs"])

_repair_service = RepairService()


def get_repair_service() -> RepairService:
    return _repair_service


@router.get("", response_model=List[RepairTaskResponse])
def list_repairs(service: RepairService = Depends(get_repair_service)) -> List[RepairTaskResponse]:
    """Retrieve all tracked repairs."""
    return service.list_tasks()


@router.post("", response_model=RepairTaskResponse, status_code=201)
def create_repair(
    req: RepairCreateRequest,
    service: RepairService = Depends(get_repair_service),
) -> RepairTaskResponse:
    """Submit a new repair task for background investigation and repair."""
    try:
        return service.start_repair(req)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except (FileNotFoundError, NotADirectoryError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize repair: {str(e)}")


@router.get("/{task_id}", response_model=RepairTaskResponse)
def get_repair(
    task_id: str,
    service: RepairService = Depends(get_repair_service),
) -> RepairTaskResponse:
    """Retrieve full details and state history for a specific task."""
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Repair task '{task_id}' not found")
    return task


@router.get("/{task_id}/logs", response_model=RepairLogsResponse)
def get_repair_logs(
    task_id: str,
    service: RepairService = Depends(get_repair_service),
) -> RepairLogsResponse:
    """Retrieve timestamped technical logs for a task."""
    logs = service.get_logs(task_id)
    return RepairLogsResponse(task_id=task_id, logs=logs)


@router.get("/{task_id}/report")
def get_repair_report_markdown(
    task_id: str,
) -> dict:
    """Retrieve raw markdown report content for a task if generated."""
    md_file = Path("results") / f"repair_report_{task_id}.md"
    if not md_file.exists():
        raise HTTPException(status_code=404, detail="Markdown report not generated for this task yet")
    return {
        "task_id": task_id,
        "content": md_file.read_text(encoding="utf-8"),
    }

