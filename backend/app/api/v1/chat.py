from fastapi import APIRouter
from app.models.schemas import ChatMessage, ChatResponse, ServiceGuide
from app.api.v1.services import MOCK_SERVICES
import uuid

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def process_chat(message: ChatMessage):
    """Process chat message and return response"""
    session_id = message.session_id or str(uuid.uuid4())
    
    # Service keyword mapping - maps keywords to service IDs in MOCK_SERVICES
    service_keyword_map = {
        "aadhaar_name_change": ["aadhaar", "name"],
        "data_access_request": ["data", "access"],
        "service_status_tracking": ["status", "tracking"],
        "service_status": ["service", "status"]  # Alternative keyword pattern for status queries
    }
    
    # Flexible keyword matching - check all service keyword patterns
    user_message = message.message.lower()
    
    for service_id, keywords in service_keyword_map.items():
        # Check if all keywords for this service appear in the user message
        if all(keyword in user_message for keyword in keywords):
            # Check if service exists in MOCK_SERVICES
            if service_id in MOCK_SERVICES:
                return ChatResponse(
                    message=f"I can help you with {MOCK_SERVICES[service_id].service_name}. Here's the complete guide:",
                    language=message.language,
                    session_id=session_id,
                    service_guide=MOCK_SERVICES[service_id]
                )
            else:
                # Service not yet implemented - return "coming soon" message
                service_name = service_id.replace("_", " ").title()
                return ChatResponse(
                    message=f"I understand you're asking about {service_name}. This service guide is coming soon. For now, please contact the relevant government department for assistance.",
                    language=message.language,
                    session_id=session_id
                )
    
    # Final fallback - welcome message for unclear queries
    return ChatResponse(
        message="Hello! I'm your Government Services Assistant. I can help you with:\n"
                "- Aadhaar name changes\n"
                "- Data access requests\n"
                "- Service status tracking\n\n"
                "What would you like help with today?",
        language=message.language,
        session_id=session_id
    )

@router.get("/history")
async def get_chat_history(session_id: str):
    """Get conversation history for a session"""
    return {"session_id": session_id, "messages": []}
