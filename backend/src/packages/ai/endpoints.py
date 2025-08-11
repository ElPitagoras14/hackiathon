from fastapi import APIRouter
from .agent import score_application

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/score/{application_id}")
def get_score(application_id: str):
    return score_application(application_id)
