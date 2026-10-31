"""Agent Skill routes."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from web_api.schemas import SkillInfo
from web_api.services.skill_service import SkillService

router = APIRouter(prefix="/api/skills", tags=["skills"])

_skill_service = SkillService()


def get_skill_service() -> SkillService:
    return _skill_service


@router.get("", response_model=SkillInfo)
def get_skill_info(service: SkillService = Depends(get_skill_service)) -> SkillInfo:
    """Retrieve BugRepro Agent Skill details, phases, and supporting resources."""
    info = service.get_skill_info("bugrepro")
    if not info:
        raise HTTPException(status_code=404, detail="Skill 'bugrepro' not found")
    return info


@router.post("/validate")
def validate_skill(service: SkillService = Depends(get_skill_service)) -> Dict[str, Any]:
    """Execute live validation of the BugRepro Agent Skill package."""
    result = service.validate_skill("bugrepro")
    return result

