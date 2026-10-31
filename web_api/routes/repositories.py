"""Repository inspection routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from web_api.schemas import RepositoryInspectResponse
from web_api.services.repository_service import RepositoryService

router = APIRouter(prefix="/api/repositories", tags=["repositories"])

_repo_service = RepositoryService()


def get_repo_service() -> RepositoryService:
    return _repo_service


@router.get("/known")
def list_known_repositories(
    service: RepositoryService = Depends(get_repo_service),
) -> List[dict]:
    """List accessible project repositories and demonstration fixtures."""
    return service.list_known_repositories()


@router.get("/inspect", response_model=RepositoryInspectResponse)
def inspect_repository(
    path: str = Query(".", description="Path to repository"),
    service: RepositoryService = Depends(get_repo_service),
) -> RepositoryInspectResponse:
    """Inspect repository structure, languages, tests, and dependencies."""
    try:
        return service.inspect(path)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except (FileNotFoundError, NotADirectoryError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inspection failed: {str(e)}")

