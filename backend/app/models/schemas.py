from pydantic import BaseModel, HttpUrl
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union

class ServiceCategory(str, Enum):
    AADHAAR = "aadhaar"
    DATA_ACCESS = "data_access"
    RECORD_MODIFICATION = "record_modification"
    STATUS_INQUIRY = "status_inquiry"
    IDENTITY_CARD = "identity_card"
    CERTIFICATE = "certificate"

class ServiceStep(BaseModel):
    step_number: int
    description: str
    requires_in_person: bool
    online_available: bool
    estimated_duration: str
    notes: Optional[str] = None

class ProcessingTime(BaseModel):
    minimum: str
    maximum: str
    typical: str
    factors: List[str]

class ContactInfo(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    helpline: Optional[str] = None

class ServiceGuide(BaseModel):
    service_id: str
    service_name: str
    category: ServiceCategory
    description: str
    steps: List[ServiceStep]
    processing_time: ProcessingTime
    official_portal_url: str
    contact_info: ContactInfo
    last_updated: datetime
    available_languages: List[str]

# Enhanced response models for structured service information
class ResponseSection(BaseModel):
    """A section in the formatted service response."""
    header: str
    content: str
    is_empty: bool

class EnhancedServiceResponse(BaseModel):
    """Enhanced service response with structured format."""
    service_name: str
    description: str
    sections: List[ResponseSection]
    last_updated: datetime

class ChatMessage(BaseModel):
    message: str
    language: str = "en"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    language: str
    session_id: str
    service_guide: Optional[ServiceGuide] = None
    enhanced_service_guide: Optional[Dict[str, Any]] = None  # Use Dict to avoid circular import

class ErrorResponse(BaseModel):
    """Error response for chat queries."""
    error_type: str  # no_match, ambiguous, system_error
    message: str
    suggestions: Optional[List[str]] = None
    matches: Optional[List[str]] = None

class DocumentUpload(BaseModel):
    document_type: str
    category: str
    description: Optional[str] = None

class DocumentSummary(BaseModel):
    document_id: str
    document_name: str
    document_type: str
    category: str
    upload_date: datetime
    file_size: int

class DashboardData(BaseModel):
    active_service_requests: List[Dict[str, Any]]
    stored_documents: List[DocumentSummary]
    service_history: List[Dict[str, Any]]
    pending_notifications: List[Dict[str, Any]]
