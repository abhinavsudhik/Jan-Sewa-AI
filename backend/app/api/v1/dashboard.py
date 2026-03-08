from fastapi import APIRouter
from app.models.schemas import DashboardData
from app.api.v1.documents import MOCK_DOCUMENTS

router = APIRouter()

@router.get("/", response_model=DashboardData)
async def get_dashboard():
    """Get dashboard data for user"""
    return DashboardData(
        active_service_requests=[],
        stored_documents=MOCK_DOCUMENTS,
        service_history=[],
        pending_notifications=[]
    )
