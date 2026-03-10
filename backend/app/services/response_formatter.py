"""Response formatting service for government service information.

This module provides the ResponseFormatter class that structures service information
into a standardized format with five consistent categories:
1. Office Locations
2. Required Documents
3. Office Visit Sequence
4. Official Websites
5. Processing Timelines

The formatter ensures all categories are present in every response, with appropriate
messaging for unavailable data.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import List

from app.models.enhanced_service import (
    EnhancedServiceGuide,
    OfficeLocation,
    RequiredDocument,
    OfficeVisitStep,
    OfficialWebsiteLink,
    ProcessingTimeline
)


class ResponseSection(BaseModel):
    """A section in the formatted response."""
    header: str
    content: str
    is_empty: bool


class FormattedServiceResponse(BaseModel):
    """Complete formatted service response."""
    service_name: str
    description: str
    sections: List[ResponseSection]
    last_updated: datetime


class ResponseFormatter:
    """Formats service information into structured responses.
    
    Ensures:
    - All five categories are present
    - Categories appear in consistent order
    - Missing data is handled gracefully
    - Consistent formatting and spacing
    """
    
    CATEGORY_ORDER = [
        "office_locations",
        "required_documents",
        "office_visit_sequence",
        "official_websites",
        "processing_timelines"
    ]
    
    CATEGORY_HEADERS = {
        "office_locations": "📍 Office Locations",
        "required_documents": "📄 Required Documents",
        "office_visit_sequence": "🏢 Office Visit Sequence",
        "official_websites": "🔗 Official Websites",
        "processing_timelines": "⏱️ Processing Timeline"
    }
    
    def format_service_response(
        self, 
        service: EnhancedServiceGuide
    ) -> FormattedServiceResponse:
        """Format service information into structured response.
        
        Args:
            service: The enhanced service guide to format
            
        Returns:
            FormattedServiceResponse with all five categories
        """
        sections = []
        
        for category in self.CATEGORY_ORDER:
            section = self._format_category(service, category)
            sections.append(section)
        
        return FormattedServiceResponse(
            service_name=service.service_name,
            description=service.description,
            sections=sections,
            last_updated=service.last_updated
        )
    
    def _format_category(
        self, 
        service: EnhancedServiceGuide, 
        category: str
    ) -> ResponseSection:
        """Format a single information category.
        
        Args:
            service: The service guide containing the data
            category: The category name to format
            
        Returns:
            ResponseSection with formatted content or "Information not available"
        """
        header = self.CATEGORY_HEADERS[category]
        data = getattr(service, category)
        
        if not data or len(data) == 0:
            return ResponseSection(
                header=header,
                content="Information not available",
                is_empty=True
            )
        
        # Route to category-specific formatter
        if category == "office_locations":
            content = self._format_office_locations(data)
        elif category == "required_documents":
            content = self._format_required_documents(data)
        elif category == "office_visit_sequence":
            content = self._format_office_sequence(data)
        elif category == "official_websites":
            content = self._format_official_websites(data)
        elif category == "processing_timelines":
            content = self._format_processing_timelines(data)
        else:
            # Fallback for unknown category
            content = "Information not available"
        
        return ResponseSection(
            header=header,
            content=content,
            is_empty=False
        )
    
    def _format_office_locations(
        self, 
        locations: List[OfficeLocation]
    ) -> str:
        """Format office locations as structured text.
        
        Each location is formatted as a bulleted item with:
        - Office name
        - Complete address (address, city, state, postal_code)
        - Coordinates (latitude, longitude) if available
        - Operating hours if available
        - Contact phone if available
        
        Multiple locations are separated by blank lines.
        
        Args:
            locations: List of office locations to format
            
        Returns:
            Formatted string with office location details
        """
        formatted = []
        for loc in locations:
            # Start with office name and address (always present)
            parts = [
                f"• {loc.name}",
                f"  {loc.address}, {loc.city}, {loc.state} {loc.postal_code}"
            ]
            
            # Add optional fields if available
            if loc.coordinates:
                parts.append(
                    f"  Coordinates: {loc.coordinates.latitude}, "
                    f"{loc.coordinates.longitude}"
                )
            
            if loc.operating_hours:
                parts.append(f"  Hours: {loc.operating_hours}")
            
            if loc.contact_phone:
                parts.append(f"  Phone: {loc.contact_phone}")
            
            formatted.append("\n".join(parts))
        
        return "\n\n".join(formatted)
    
    def _format_required_documents(
        self, 
        documents: List[RequiredDocument]
    ) -> str:
        """Format required documents as bulleted list.
        
        Each document is formatted as a bulleted item with:
        - Document name (with "(Optional)" suffix if not mandatory)
        - Description if available
        - Copies required if > 1
        - Format requirements if available
        - Alternatives if available
        
        Multiple documents are separated by blank lines.
        
        Args:
            documents: List of required documents to format
            
        Returns:
            Formatted string with document details
        """
        formatted = []
        for doc in documents:
            # Start with document name
            parts = []
            
            # Add document name with optional indicator
            if doc.is_mandatory:
                parts.append(f"• {doc.document_name}")
            else:
                parts.append(f"• {doc.document_name} (Optional)")
            
            # Add description if available
            if doc.description:
                parts.append(f"  {doc.description}")
            
            # Add copies required if > 1
            if doc.copies_required > 1:
                parts.append(f"  Copies required: {doc.copies_required}")
            
            # Add format requirements if available
            if doc.format_requirements:
                parts.append(f"  Format: {doc.format_requirements}")
            
            # Add alternatives if available
            if doc.alternatives and len(doc.alternatives) > 0:
                parts.append(f"  Alternatives: {', '.join(doc.alternatives)}")
            
            formatted.append("\n".join(parts))
        
        return "\n\n".join(formatted)
    
    def _format_office_sequence(
        self, 
        sequence: List[OfficeVisitStep]
    ) -> str:
        """Format office visit sequence with numbering.
        
        For single office visit: Display without sequence numbering (just bullet point)
        For multiple office visits: Display with numbered sequence (1., 2., 3., etc.)
        
        Each step includes:
        - Office name
        - Purpose
        - Estimated duration
        - Optional indicator (if is_optional=True)
        - Condition text (if is_conditional=True)
        
        Args:
            sequence: List of office visit steps to format
            
        Returns:
            Formatted string with office visit sequence
        """
        # Sort steps by sequence_number to ensure correct order
        sorted_sequence = sorted(sequence, key=lambda x: x.sequence_number)
        
        # Single office - no numbering, use bullet point
        if len(sorted_sequence) == 1:
            step = sorted_sequence[0]
            parts = [
                f"• {step.office_name}",
                f"  {step.purpose}",
                f"  Duration: {step.estimated_duration}"
            ]
            
            # Add optional indicator if applicable
            if step.is_optional:
                parts.append("  (Optional)")
            
            # Add condition if applicable
            if step.is_conditional and step.condition:
                parts.append(f"  Condition: {step.condition}")
            
            return "\n".join(parts)
        
        # Multiple offices - numbered sequence
        formatted = []
        for step in sorted_sequence:
            parts = [
                f"{step.sequence_number}. {step.office_name}",
                f"   {step.purpose}",
                f"   Duration: {step.estimated_duration}"
            ]
            
            # Add optional indicator if applicable
            if step.is_optional:
                parts.append("   (Optional)")
            
            # Add condition if applicable
            if step.is_conditional and step.condition:
                parts.append(f"   Condition: {step.condition}")
            
            formatted.append("\n".join(parts))
        
        return "\n\n".join(formatted)
    
    def _format_official_websites(
        self, 
        websites: List[OfficialWebsiteLink]
    ) -> str:
        """Format official website links.
        
        Each website is formatted as a bulleted item with:
        - Purpose label followed by URL
        - Description (indented below) if available
        
        Multiple websites are separated by blank lines.
        
        Args:
            websites: List of official website links to format
            
        Returns:
            Formatted string with website links
        """
        formatted = []
        for site in websites:
            # Start with purpose and URL
            parts = [f"• {site.purpose}: {site.url}"]
            
            # Add description if available (indented)
            if site.description:
                parts.append(f"  {site.description}")
            
            formatted.append("\n".join(parts))
        
        return "\n\n".join(formatted)
    
    def _format_processing_timelines(
        self, 
        timelines: List[ProcessingTimeline]
    ) -> str:
        """Format processing timeline information.
        
        Each timeline is formatted with:
        - Processing type (Standard/Expedited)
        - Typical days
        - Range (minimum-maximum days)
        - Notes if available
        - Factors affecting time if available (as indented list)
        
        Multiple timelines are separated by blank lines.
        
        Args:
            timelines: List of processing timelines to format
            
        Returns:
            Formatted string with timeline details
        """
        formatted = []
        for timeline in timelines:
            # Start with processing type
            parts = [f"• {timeline.processing_type.title()} Processing"]
            
            # Add typical days
            parts.append(f"  Typical: {timeline.typical_days} {timeline.time_unit}")
            
            # Add range
            parts.append(f"  Range: {timeline.as_range_string()}")
            
            # Add notes if available
            if timeline.notes:
                parts.append(f"  Note: {timeline.notes}")
            
            # Add factors affecting time if available
            if timeline.factors_affecting_time and len(timeline.factors_affecting_time) > 0:
                parts.append("  Factors affecting time:")
                for factor in timeline.factors_affecting_time:
                    parts.append(f"    - {factor}")
            
            formatted.append("\n".join(parts))
        
        return "\n\n".join(formatted)
