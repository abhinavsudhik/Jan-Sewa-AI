"""Enhanced data models for government service information.

This module defines the enhanced data models for the five information categories:
1. Office Locations
2. Required Documents
3. Office Visit Sequence
4. Official Website Links
5. Processing Timelines

These models include comprehensive Pydantic validation for data integrity.
"""

from pydantic import BaseModel, HttpUrl, field_validator, model_validator
from datetime import datetime
from typing import List, Optional
from enum import Enum
import logging

from .schemas import ServiceCategory

logger = logging.getLogger(__name__)


class Coordinates(BaseModel):
    """Geographic coordinates for office locations."""
    latitude: float
    longitude: float
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        """Validate latitude is within valid range [-90, 90]."""
        if not -90 <= v <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {v}")
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """Validate longitude is within valid range [-180, 180]."""
        if not -180 <= v <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {v}")
        return v


class OfficeLocation(BaseModel):
    """Physical location where a government service can be accessed."""
    name: str
    address: str
    city: str
    state: str
    postal_code: str
    coordinates: Optional[Coordinates] = None
    operating_hours: Optional[str] = None
    contact_phone: Optional[str] = None


class RequiredDocument(BaseModel):
    """Document required for a government service."""
    document_name: str
    description: Optional[str] = None
    copies_required: int = 1
    format_requirements: Optional[str] = None
    is_mandatory: bool = True
    alternatives: Optional[List[str]] = None
    
    @field_validator('copies_required')
    @classmethod
    def validate_copies_required(cls, v: int) -> int:
        """Validate copies_required is at least 1."""
        if v < 1:
            raise ValueError(f"copies_required must be >= 1, got {v}")
        return v


class OfficeVisitStep(BaseModel):
    """A step in the office visit sequence."""
    sequence_number: int
    office_name: str
    purpose: str
    estimated_duration: str
    is_optional: bool = False
    is_conditional: bool = False
    condition: Optional[str] = None


class OfficialWebsiteLink(BaseModel):
    """Official government website link."""
    url: HttpUrl
    purpose: str
    description: Optional[str] = None
    
    @field_validator('url')
    @classmethod
    def validate_https(cls, v: HttpUrl) -> HttpUrl:
        """Prefer HTTPS when available, log warning for HTTP."""
        if v.scheme == 'http':
            logger.warning(
                f"HTTP URL detected (HTTPS preferred): {v}. "
                "This is allowed for government sites that may not have HTTPS."
            )
        return v


class ProcessingTimeline(BaseModel):
    """Processing timeline for a government service."""
    minimum_days: int
    maximum_days: int
    typical_days: int
    time_unit: str = "days"
    processing_type: str = "standard"
    notes: Optional[str] = None
    factors_affecting_time: List[str] = []
    
    @model_validator(mode='after')
    def validate_timeline_range(self) -> 'ProcessingTimeline':
        """Ensure minimum_days <= typical_days <= maximum_days."""
        if not (self.minimum_days <= self.typical_days <= self.maximum_days):
            raise ValueError(
                f"Timeline must satisfy minimum <= typical <= maximum. "
                f"Got: min={self.minimum_days}, typical={self.typical_days}, "
                f"max={self.maximum_days}"
            )
        return self
    
    def as_range_string(self) -> str:
        """Format as human-readable range."""
        return f"{self.minimum_days}-{self.maximum_days} {self.time_unit}"


class EnhancedServiceGuide(BaseModel):
    """Complete service guide with all required information categories."""
    # Basic information
    service_id: str
    service_name: str
    category: ServiceCategory
    description: str
    
    # Five required information categories
    office_locations: List[OfficeLocation] = []
    required_documents: List[RequiredDocument] = []
    office_visit_sequence: List[OfficeVisitStep] = []
    official_websites: List[OfficialWebsiteLink] = []
    processing_timelines: List[ProcessingTimeline] = []
    
    # Metadata
    last_updated: datetime
    data_source: str
    available_languages: List[str] = ["en"]
    
    # Legacy compatibility fields (for gradual migration)
    steps: Optional[List[dict]] = None
    processing_time: Optional[dict] = None
    official_portal_url: Optional[str] = None
    contact_info: Optional[dict] = None
