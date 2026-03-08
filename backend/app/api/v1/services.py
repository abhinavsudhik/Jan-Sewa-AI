from fastapi import APIRouter, HTTPException
from app.models.schemas import ServiceGuide, ServiceCategory, ServiceStep, ProcessingTime, ContactInfo
from datetime import datetime
from typing import List

router = APIRouter()

# Mock data for prototype
MOCK_SERVICES = {
    "aadhaar_name_change": ServiceGuide(
        service_id="aadhaar_name_change",
        service_name="Aadhaar Name Change",
        category=ServiceCategory.AADHAAR,
        description="Update your name in Aadhaar card",
        steps=[
            ServiceStep(
                step_number=1,
                description="Visit UIDAI website or Aadhaar center",
                requires_in_person=False,
                online_available=True,
                estimated_duration="10 minutes"
            ),
            ServiceStep(
                step_number=2,
                description="Fill the update form with correct details",
                requires_in_person=False,
                online_available=True,
                estimated_duration="15 minutes"
            ),
            ServiceStep(
                step_number=3,
                description="Upload supporting documents",
                requires_in_person=False,
                online_available=True,
                estimated_duration="5 minutes"
            )
        ],
        processing_time=ProcessingTime(
            minimum="7 days",
            maximum="90 days",
            typical="30 days",
            factors=["Document verification", "Biometric update"]
        ),
        official_portal_url="https://uidai.gov.in",
        contact_info=ContactInfo(
            phone="1947",
            email="help@uidai.gov.in",
            helpline="1947"
        ),
        last_updated=datetime.now(),
        available_languages=["en", "hi", "ta", "te"]
    )
}

@router.get("/", response_model=List[str])
async def list_services():
    """List all available services"""
    return list(MOCK_SERVICES.keys())

@router.get("/{service_id}", response_model=ServiceGuide)
async def get_service(service_id: str):
    """Get detailed information about a specific service"""
    if service_id not in MOCK_SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    return MOCK_SERVICES[service_id]
