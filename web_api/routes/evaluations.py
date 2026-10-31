"""Model evaluation routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from web_api.schemas import EvaluationItem
from web_api.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/api/evaluations", tags=["evaluations"])

_eval_service = EvaluationService()


def get_eval_service() -> EvaluationService:
    return _eval_service


@router.get("", response_model=List[EvaluationItem])
def list_evaluations(service: EvaluationService = Depends(get_eval_service)) -> List[EvaluationItem]:
    """Retrieve normalized evaluation records from results directory."""
    return service.get_all_evaluations()


@router.get("/{evaluation_id}", response_model=EvaluationItem)
def get_evaluation(
    evaluation_id: str,
    service: EvaluationService = Depends(get_eval_service),
) -> EvaluationItem:
    """Retrieve a specific evaluation record."""
    item = service.get_evaluation_by_id(evaluation_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Evaluation record '{evaluation_id}' not found")
    return item

