"""Dashboard summary aggregation route."""

from pathlib import Path
from fastapi import APIRouter, Depends
from web_api.schemas import DashboardSummary
from web_api.services.repair_service import RepairService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

_repair_service = RepairService()


def get_repair_service() -> RepairService:
    return _repair_service


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    service: RepairService = Depends(get_repair_service),
) -> DashboardSummary:
    """Derive dashboard metrics directly from real execution and report records."""
    tasks = service.list_tasks()

    total = len(tasks)
    verified = sum(1 for t in tasks if t.status == "VERIFIED")
    active = sum(1 for t in tasks if t.status == "RUNNING")
    failed_val = sum(1 for t in tasks if t.status == "VALIDATION_FAILED")

    reproduced = sum(
        1 for t in tasks if t.reproduction_result and t.reproduction_result.get("status") == "REPRODUCED"
    )

    tests_passed = 0
    for t in tasks:
        if t.verification_result and t.verification_result.get("tests_passed"):
            tests_passed += len(t.verification_result.get("tests_passed"))

    # Discover available report files
    results_dir = Path("results")
    reports_meta = []
    if results_dir.exists():
        for md_file in sorted(results_dir.glob("repair_report_*.md"), reverse=True):
            reports_meta.append({
                "filename": md_file.name,
                "task_id": md_file.stem.replace("repair_report_", ""),
                "size_bytes": md_file.stat().st_size,
                "modified": md_file.stat().st_mtime,
            })

    recent = [t.model_dump() for t in tasks[:6]]

    return DashboardSummary(
        total_repairs=total,
        verified_repairs=verified,
        reproduced_count=reproduced,
        tests_passed=tests_passed,
        active_repairs=active,
        failed_validations=failed_val,
        configured_provider="mock",
        execution_mode="SAFE_FIXTURE",
        recent_repairs=recent,
        recent_reports=reports_meta,
    )

