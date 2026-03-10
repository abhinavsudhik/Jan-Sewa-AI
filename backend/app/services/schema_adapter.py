"""Schema adapter for converting legacy ServiceGuide to EnhancedServiceGuide.

This module provides the SchemaAdapter class that handles conversion between
the legacy ServiceGuide model and the new EnhancedServiceGuide model, ensuring
backward compatibility during the migration period.
"""

import re
from typing import Optional
from datetime import datetime

from ..models.schemas import ServiceGuide, ServiceStep, ProcessingTime, ContactInfo
from ..models.enhanced_service import (
    EnhancedServiceGuide,
    OfficeLocation,
    RequiredDocument,
    OfficeVisitStep,
    OfficialWebsiteLink,
    ProcessingTimeline,
)


class SchemaAdapter:
    """Adapts between legacy and enhanced service guide schemas."""
    
    @staticmethod
    def legacy_to_enhanced(legacy: ServiceGuide) -> EnhancedServiceGuide:
        """Convert legacy ServiceGuide to EnhancedServiceGuide.
        
        Args:
            legacy: The legacy ServiceGuide instance to convert
            
        Returns:
            EnhancedServiceGuide with data mapped from legacy format
            
        Handles missing fields gracefully with appropriate defaults.
        """
        # Convert contact_info.address to OfficeLocation
        office_locations = SchemaAdapter._extract_office_locations(legacy.contact_info)
        
        # Convert steps to office_visit_sequence
        office_sequence = SchemaAdapter._convert_steps_to_sequence(legacy.steps)
        
        # Convert processing_time to ProcessingTimeline
        timelines = SchemaAdapter._convert_processing_time(legacy.processing_time)
        
        # Convert official_portal_url to OfficialWebsiteLink
        websites = SchemaAdapter._convert_portal_url(legacy.official_portal_url)
        
        # Create EnhancedServiceGuide with converted data
        return EnhancedServiceGuide(
            service_id=legacy.service_id,
            service_name=legacy.service_name,
            category=legacy.category,
            description=legacy.description,
            office_locations=office_locations,
            required_documents=[],  # Not in legacy schema
            office_visit_sequence=office_sequence,
            official_websites=websites,
            processing_timelines=timelines,
            last_updated=legacy.last_updated,
            data_source="legacy_migration",
            available_languages=legacy.available_languages,
            # Preserve legacy fields for backward compatibility
            steps=[step.model_dump() for step in legacy.steps],
            processing_time=legacy.processing_time.model_dump(),
            official_portal_url=legacy.official_portal_url,
            contact_info=legacy.contact_info.model_dump(),
        )
    
    @staticmethod
    def _extract_office_locations(contact_info: Optional[ContactInfo]) -> list[OfficeLocation]:
        """Extract office location from legacy contact_info.
        
        Args:
            contact_info: Legacy ContactInfo object
            
        Returns:
            List containing a single OfficeLocation if address exists, empty list otherwise
        """
        if not contact_info or not contact_info.address:
            return []
        
        # Try to parse city, state, postal code from address
        city, state, postal_code = SchemaAdapter._parse_address(contact_info.address)
        
        return [
            OfficeLocation(
                name="Main Office",
                address=contact_info.address,
                city=city,
                state=state,
                postal_code=postal_code,
                contact_phone=contact_info.phone,
            )
        ]
    
    @staticmethod
    def _parse_address(address: str) -> tuple[str, str, str]:
        """Parse city, state, and postal code from address string.
        
        Args:
            address: Full address string
            
        Returns:
            Tuple of (city, state, postal_code) with defaults if parsing fails
        """
        # Try to extract postal code (6 digits for Indian postal codes)
        postal_match = re.search(r'\b(\d{6})\b', address)
        postal_code = postal_match.group(1) if postal_match else "000000"
        
        # Try to extract state (common Indian state names)
        state_patterns = [
            r'\b(Delhi|Maharashtra|Karnataka|Tamil Nadu|Kerala|Gujarat|'
            r'Rajasthan|Uttar Pradesh|West Bengal|Andhra Pradesh|Telangana|'
            r'Punjab|Haryana|Bihar|Madhya Pradesh|Odisha)\b'
        ]
        state = "Unknown"
        for pattern in state_patterns:
            state_match = re.search(pattern, address, re.IGNORECASE)
            if state_match:
                state = state_match.group(1)
                break
        
        # Try to extract city (word before state or postal code)
        city = "Unknown"
        # Simple heuristic: look for word before state or postal code
        parts = address.split(',')
        if len(parts) >= 2:
            # Assume city is in the second-to-last or third-to-last part
            for part in reversed(parts[:-1]):
                part = part.strip()
                if part and not part.isdigit():
                    city = part
                    break
        
        return city, state, postal_code
    
    @staticmethod
    def _convert_steps_to_sequence(steps: list[ServiceStep]) -> list[OfficeVisitStep]:
        """Convert legacy ServiceStep list to OfficeVisitStep list.
        
        Args:
            steps: List of legacy ServiceStep objects
            
        Returns:
            List of OfficeVisitStep objects
        """
        return [
            OfficeVisitStep(
                sequence_number=step.step_number,
                office_name="Service Office",  # Generic name as legacy doesn't specify
                purpose=step.description,
                estimated_duration=step.estimated_duration,
                is_optional=False,  # Legacy doesn't track this
                is_conditional=False,  # Legacy doesn't track this
            )
            for step in steps
        ]
    
    @staticmethod
    def _convert_processing_time(processing_time: Optional[ProcessingTime]) -> list[ProcessingTimeline]:
        """Convert legacy ProcessingTime to ProcessingTimeline list.
        
        Args:
            processing_time: Legacy ProcessingTime object
            
        Returns:
            List containing a single ProcessingTimeline if data exists, empty list otherwise
        """
        if not processing_time:
            return []
        
        # Parse string durations to days
        minimum_days = SchemaAdapter._parse_duration_to_days(processing_time.minimum)
        maximum_days = SchemaAdapter._parse_duration_to_days(processing_time.maximum)
        typical_days = SchemaAdapter._parse_duration_to_days(processing_time.typical)
        
        return [
            ProcessingTimeline(
                minimum_days=minimum_days,
                maximum_days=maximum_days,
                typical_days=typical_days,
                time_unit="days",
                processing_type="standard",
                factors_affecting_time=processing_time.factors,
            )
        ]
    
    @staticmethod
    def _parse_duration_to_days(duration_str: str) -> int:
        """Parse duration string to number of days.
        
        Args:
            duration_str: Duration string like "2 weeks", "30 days", "1 month"
            
        Returns:
            Number of days as integer, defaults to 0 if parsing fails
        """
        if not duration_str:
            return 0
        
        duration_str = duration_str.lower().strip()
        
        # Extract number
        number_match = re.search(r'(\d+)', duration_str)
        if not number_match:
            return 0
        
        number = int(number_match.group(1))
        
        # Determine unit and convert to days
        if 'day' in duration_str:
            return number
        elif 'week' in duration_str:
            return number * 7
        elif 'month' in duration_str:
            return number * 30  # Approximate
        elif 'year' in duration_str:
            return number * 365  # Approximate
        else:
            # Default to days if unit unclear
            return number
    
    @staticmethod
    def enhanced_to_legacy(enhanced: EnhancedServiceGuide) -> Optional[ServiceGuide]:
        """Convert EnhancedServiceGuide to legacy ServiceGuide format.
        
        Args:
            enhanced: The EnhancedServiceGuide instance to convert
            
        Returns:
            ServiceGuide with data mapped from enhanced format, or None if conversion fails
            
        Uses legacy compatibility fields when available, otherwise extracts from enhanced data.
        """
        try:
            # Use legacy fields if available (for backward compatibility)
            if enhanced.steps and enhanced.processing_time and enhanced.contact_info:
                # Direct conversion from preserved legacy fields
                steps = [ServiceStep(**step) for step in enhanced.steps]
                processing_time = ProcessingTime(**enhanced.processing_time)
                contact_info = ContactInfo(**enhanced.contact_info)
                official_portal_url = enhanced.official_portal_url or ""
            else:
                # Convert from enhanced fields
                steps = SchemaAdapter._convert_sequence_to_steps(enhanced.office_visit_sequence)
                processing_time = SchemaAdapter._convert_timelines_to_processing_time(enhanced.processing_timelines)
                contact_info = SchemaAdapter._convert_locations_to_contact_info(enhanced.office_locations)
                official_portal_url = SchemaAdapter._extract_portal_url(enhanced.official_websites)
            
            return ServiceGuide(
                service_id=enhanced.service_id,
                service_name=enhanced.service_name,
                category=enhanced.category,
                description=enhanced.description,
                steps=steps,
                processing_time=processing_time,
                official_portal_url=official_portal_url,
                contact_info=contact_info,
                last_updated=enhanced.last_updated,
                available_languages=enhanced.available_languages,
            )
        except Exception as e:
            # Log error and return None if conversion fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to convert enhanced to legacy format: {e}")
            return None
    
    @staticmethod
    def _convert_sequence_to_steps(sequence: list[OfficeVisitStep]) -> list[ServiceStep]:
        """Convert OfficeVisitStep list to legacy ServiceStep list."""
        return [
            ServiceStep(
                step_number=step.sequence_number,
                description=step.purpose,
                requires_in_person=True,  # Default assumption
                online_available=False,  # Default assumption
                estimated_duration=step.estimated_duration,
                notes=step.condition if step.is_conditional else None,
            )
            for step in sequence
        ]
    
    @staticmethod
    def _convert_timelines_to_processing_time(timelines: list[ProcessingTimeline]) -> ProcessingTime:
        """Convert ProcessingTimeline list to legacy ProcessingTime."""
        if not timelines:
            return ProcessingTime(
                minimum="Unknown",
                maximum="Unknown", 
                typical="Unknown",
                factors=[]
            )
        
        # Use the first timeline (standard processing)
        timeline = timelines[0]
        
        return ProcessingTime(
            minimum=f"{timeline.minimum_days} {timeline.time_unit}",
            maximum=f"{timeline.maximum_days} {timeline.time_unit}",
            typical=f"{timeline.typical_days} {timeline.time_unit}",
            factors=timeline.factors_affecting_time,
        )
    
    @staticmethod
    def _convert_locations_to_contact_info(locations: list[OfficeLocation]) -> ContactInfo:
        """Convert OfficeLocation list to legacy ContactInfo."""
        if not locations:
            return ContactInfo()
        
        # Use the first location
        location = locations[0]
        
        return ContactInfo(
            phone=location.contact_phone,
            email=None,  # Not in enhanced schema
            address=f"{location.address}, {location.city}, {location.state} {location.postal_code}",
            helpline=None,  # Not in enhanced schema
        )
    
    @staticmethod
    def _extract_portal_url(websites: list[OfficialWebsiteLink]) -> str:
        """Extract portal URL from OfficialWebsiteLink list."""
        if not websites:
            return ""
        
        # Look for "Official Portal" or use the first website
        for website in websites:
            if "portal" in website.purpose.lower():
                return str(website.url)
        
        # Fallback to first website
        return str(websites[0].url)
    
    @staticmethod
    def _convert_portal_url(portal_url: Optional[str]) -> list[OfficialWebsiteLink]:
        """Convert legacy official_portal_url to OfficialWebsiteLink list.
        
        Args:
            portal_url: Legacy portal URL string
            
        Returns:
            List containing a single OfficialWebsiteLink if URL exists, empty list otherwise
        """
        if not portal_url:
            return []
        
        return [
            OfficialWebsiteLink(
                url=portal_url,
                purpose="Official Portal",
                description="Main government portal for this service",
            )
        ]
