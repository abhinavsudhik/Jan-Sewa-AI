from fastapi import APIRouter
from app.models.schemas import ChatMessage, ChatResponse, ServiceGuide
from app.api.v1.services import MOCK_SERVICES
import uuid

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def process_chat(message: ChatMessage):
    """Process chat message and return response"""
    session_id = message.session_id or str(uuid.uuid4())
    
    # Simple keyword matching for prototype
    user_message = message.message.lower()
    
    if "aadhaar" in user_message and "name" in user_message:
        return ChatResponse(
            message="I can help you with Aadhaar name change. Here's the complete guide:",
            language=message.language,
            session_id=session_id,
            service_guide=MOCK_SERVICES["aadhaar_name_change"]
        )
    
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
