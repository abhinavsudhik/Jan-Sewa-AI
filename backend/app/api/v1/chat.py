from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatMessage, ChatResponse, ServiceGuide, EnhancedServiceResponse, ResponseSection
from app.models.enhanced_service import EnhancedServiceGuide
from app.services.query_processor import QueryProcessor, ServiceRepository, QueryResult
from app.services.response_formatter import ResponseFormatter, FormattedServiceResponse
from app.services.schema_adapter import SchemaAdapter
from app.api.v1.services import MOCK_SERVICES
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize enhanced services
service_repository = ServiceRepository()
query_processor = QueryProcessor(service_repository)
response_formatter = ResponseFormatter()

@router.post("/", response_model=ChatResponse)
async def process_chat(message: ChatMessage):
    """Process chat message and return enhanced structured response"""
    session_id = message.session_id or str(uuid.uuid4())
    
    try:
        # Check for generic greetings first (preserve legacy behavior)
        if _is_generic_greeting(message.message):
            return ChatResponse(
                message="Hello! I'm your Government Services Assistant. I can help you with:\n"
                        "- Aadhaar name changes\n"
                        "- Data access requests\n"
                        "- Service status tracking\n\n"
                        "What would you like help with today?",
                language=message.language,
                session_id=session_id
            )
        
        # Process query using enhanced QueryProcessor
        query_result = query_processor.process_query(message.message)
        
        if query_result.status == "success" and query_result.service:
            # Format service information using ResponseFormatter
            formatted_response = response_formatter.format_service_response(query_result.service)
            
            # Convert to response model
            enhanced_response = EnhancedServiceResponse(
                service_name=formatted_response.service_name,
                description=formatted_response.description,
                sections=[
                    ResponseSection(
                        header=section.header,
                        content=section.content,
                        is_empty=section.is_empty
                    )
                    for section in formatted_response.sections
                ],
                last_updated=formatted_response.last_updated
            )
            
            # Also provide legacy format for backward compatibility
            legacy_service = SchemaAdapter.enhanced_to_legacy(query_result.service)
            
            return ChatResponse(
                message=f"I can help you with {query_result.service.service_name}. Here's the complete guide:",
                language=message.language,
                session_id=session_id,
                service_guide=legacy_service,
                enhanced_service_guide=enhanced_response
            )
            
        elif query_result.status == "no_match":
            # No matching service found - provide suggestions or welcome message
            if query_result.suggestions:
                # Get service names for suggestions
                suggestion_names = []
                for suggestion_id in query_result.suggestions:
                    service = service_repository.get_service(suggestion_id)
                    if service:
                        suggestion_names.append(service.service_name)
                
                if suggestion_names:
                    suggestions_text = f"{query_result.message}\n\nDid you mean:\n" + "\n".join(f"- {name}" for name in suggestion_names)
                    return ChatResponse(
                        message=suggestions_text,
                        language=message.language,
                        session_id=session_id
                    )
            
            # No suggestions or empty suggestions - return welcome message
            return ChatResponse(
                message="Hello! I'm your Government Services Assistant. I can help you with:\n"
                        "- Aadhaar name changes\n"
                        "- Data access requests\n"
                        "- Service status tracking\n\n"
                        "What would you like help with today?",
                language=message.language,
                session_id=session_id
            )
            
        elif query_result.status == "ambiguous":
            # Multiple matches - request clarification
            clarification_text = query_result.message or "I found multiple services matching your query."
            
            if query_result.matches:
                # Get service names for matches
                match_names = []
                for match_id in query_result.matches:
                    service = service_repository.get_service(match_id)
                    if service:
                        match_names.append(service.service_name)
                
                if match_names:
                    clarification_text += f"\n\nWhich one do you need?\n" + "\n".join(f"- {name}" for name in match_names)
            
            return ChatResponse(
                message=clarification_text,
                language=message.language,
                session_id=session_id
            )
            
        else:
            # Unexpected status - system error
            logger.error(f"Unexpected query result status: {query_result.status}")
            return ChatResponse(
                message="I'm sorry, I encountered an error processing your request. Please try again.",
                language=message.language,
                session_id=session_id
            )
            
    except Exception as e:
        # System error - graceful degradation
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        
        # Fall back to legacy keyword matching for graceful degradation
        return await _fallback_legacy_processing(message, session_id)


def _is_generic_greeting(message: str) -> bool:
    """Check if message is a generic greeting that should return welcome message."""
    message_lower = message.lower().strip()
    
    # Generic greetings and unclear queries
    generic_patterns = [
        "hello", "hi", "hey", "greetings", "good morning", "good afternoon", 
        "good evening", "namaste", "help", "what can you do", "what do you do",
        "how are you", "who are you", "what is this", "start", "begin"
    ]
    
    # Check if message is exactly one of these patterns or very short
    if message_lower in generic_patterns or len(message_lower) <= 3:
        return True
    
    # Check if message contains only greeting words
    words = message_lower.split()
    if len(words) <= 2 and all(word in generic_patterns for word in words):
        return True
    
    return False


async def _fallback_legacy_processing(message: ChatMessage, session_id: str) -> ChatResponse:
    """Fallback to legacy processing when enhanced services fail."""
    logger.info("Using legacy fallback processing")
    
    # Legacy service keyword mapping
    service_keyword_map = {
        "aadhaar_name_change": ["aadhaar", "name"],
        "data_access_request": ["data", "access"],
        "service_status_tracking": ["status", "tracking"],
        "service_status": ["service", "status"],
        "driving_license": ["driving", "license"],
        "driving_licence": ["driving", "licence"]
    }
    
    user_message = message.message.lower()
    
    for service_id, keywords in service_keyword_map.items():
        if all(keyword in user_message for keyword in keywords):
            if service_id in MOCK_SERVICES:
                return ChatResponse(
                    message=f"I can help you with {MOCK_SERVICES[service_id].service_name}. Here's the complete guide:",
                    language=message.language,
                    session_id=session_id,
                    service_guide=MOCK_SERVICES[service_id]
                )
            else:
                service_name = service_id.replace("_", " ").title()
                return ChatResponse(
                    message=f"I understand you're asking about {service_name}. This service guide is coming soon. For now, please contact the relevant government department for assistance.",
                    language=message.language,
                    session_id=session_id
                )
    
    # Final fallback - welcome message
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
