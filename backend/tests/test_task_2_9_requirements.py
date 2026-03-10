"""Verification tests for Task 2.9 requirements.

This test module verifies that the implementation meets all the specific
requirements outlined in Task 2.9:

For _format_official_websites():
1. Display each website as a bulleted item
2. Show purpose label followed by URL
3. Include description when available (indented below)
4. Format multiple websites with proper spacing

For _format_processing_timelines():
1. Display processing type (Standard/Expedited)
2. Show typical days
3. Show range (minimum-maximum)
4. Include notes when available
5. List factors affecting time when available
6. Format multiple timelines (standard and expedited) with proper spacing
"""

import pytest
from datetime import datetime

from app.services.response_formatter import ResponseFormatter
from app.models.enhanced_service import (
    EnhancedServiceGuide,
    OfficialWebsiteLink,
    ProcessingTimeline
)
from app.models.schemas import ServiceCategory


class TestTask29WebsiteRequirements:
    """Verify all requirements for _format_official_websites()."""
    
    def test_requirement_1_bulleted_items(self):
        """Requirement 1: Display each website as a bulleted item."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            official_websites=[
                OfficialWebsiteLink(url="https://site1.gov.in", purpose="Portal 1"),
                OfficialWebsiteLink(url="https://site2.gov.in", purpose="Portal 2")
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        websites_section = response.sections[3]
        
        # Each website should start with bullet point
        assert websites_section.content.count("• ") == 2
    
    def test_requirement_2_purpose_label_and_url(self):
        """Requirement 2: Show purpose label followed by URL."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            official_websites=[
                OfficialWebsiteLink(
                    url="https://uidai.gov.in",
                    purpose="UIDAI Official Portal"
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        websites_section = response.sections[3]
        
        # Should have format: "• Purpose: URL"
        assert "• UIDAI Official Portal: https://uidai.gov.in" in websites_section.content
    
    def test_requirement_3_description_indented(self):
        """Requirement 3: Include description when available (indented below)."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            official_websites=[
                OfficialWebsiteLink(
                    url="https://uidai.gov.in",
                    purpose="UIDAI Official Portal",
                    description="Main website for Aadhaar services"
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        websites_section = response.sections[3]
        
        lines = websites_section.content.split('\n')
        # First line: bullet with purpose and URL
        assert lines[0].startswith("• UIDAI Official Portal:")
        # Second line: indented description (2 spaces)
        assert lines[1] == "  Main website for Aadhaar services"
    
    def test_requirement_4_proper_spacing_multiple_websites(self):
        """Requirement 4: Format multiple websites with proper spacing."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            official_websites=[
                OfficialWebsiteLink(
                    url="https://uidai.gov.in",
                    purpose="UIDAI Official Portal",
                    description="Main website for Aadhaar services"
                ),
                OfficialWebsiteLink(
                    url="https://myaadhaar.uidai.gov.in",
                    purpose="Online Update Portal",
                    description="Portal for online Aadhaar updates"
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        websites_section = response.sections[3]
        
        # Multiple websites should be separated by double newline
        assert "\n\n" in websites_section.content
        
        # Verify both websites are present
        assert "UIDAI Official Portal" in websites_section.content
        assert "Online Update Portal" in websites_section.content


class TestTask29TimelineRequirements:
    """Verify all requirements for _format_processing_timelines()."""
    
    def test_requirement_1_display_processing_type(self):
        """Requirement 1: Display processing type (Standard/Expedited)."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            processing_timelines=[
                ProcessingTimeline(
                    minimum_days=7,
                    maximum_days=30,
                    typical_days=14,
                    processing_type="standard"
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        timeline_section = response.sections[4]
        
        # Should display "Standard Processing" (title case)
        assert "• Standard Processing" in timeline_section.content
    
    def test_requirement_2_show_typical_days(self):
        """Requirement 2: Show typical days."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            processing_timelines=[
                ProcessingTimeline(
                    minimum_days=7,
                    maximum_days=30,
                    typical_days=14,
                    processing_type="standard"
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        timeline_section = response.sections[4]
        
        # Should show "Typical: 14 days"
        assert "  Typical: 14 days" in timeline_section.content
    
    def test_requirement_3_show_range(self):
        """Requirement 3: Show range (minimum-maximum)."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            processing_timelines=[
                ProcessingTimeline(
                    minimum_days=7,
                    maximum_days=30,
                    typical_days=14,
                    processing_type="standard"
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        timeline_section = response.sections[4]
        
        # Should show "Range: 7-30 days"
        assert "  Range: 7-30 days" in timeline_section.content
    
    def test_requirement_4_include_notes_when_available(self):
        """Requirement 4: Include notes when available."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            processing_timelines=[
                ProcessingTimeline(
                    minimum_days=7,
                    maximum_days=30,
                    typical_days=14,
                    processing_type="standard",
                    notes="Processing time may vary based on verification requirements"
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        timeline_section = response.sections[4]
        
        # Should include note with "Note:" prefix
        assert "  Note: Processing time may vary based on verification requirements" in timeline_section.content
    
    def test_requirement_5_list_factors_when_available(self):
        """Requirement 5: List factors affecting time when available."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            processing_timelines=[
                ProcessingTimeline(
                    minimum_days=7,
                    maximum_days=30,
                    typical_days=14,
                    processing_type="standard",
                    factors_affecting_time=[
                        "Document verification complexity",
                        "Biometric verification requirement",
                        "Regional office workload"
                    ]
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        timeline_section = response.sections[4]
        
        # Should include factors section
        assert "  Factors affecting time:" in timeline_section.content
        # Each factor should be indented with dash
        assert "    - Document verification complexity" in timeline_section.content
        assert "    - Biometric verification requirement" in timeline_section.content
        assert "    - Regional office workload" in timeline_section.content
    
    def test_requirement_6_multiple_timelines_with_spacing(self):
        """Requirement 6: Format multiple timelines (standard and expedited) with proper spacing."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            processing_timelines=[
                ProcessingTimeline(
                    minimum_days=7,
                    maximum_days=30,
                    typical_days=14,
                    processing_type="standard",
                    notes="Processing time may vary based on verification requirements",
                    factors_affecting_time=[
                        "Document verification complexity",
                        "Biometric verification requirement",
                        "Regional office workload"
                    ]
                ),
                ProcessingTimeline(
                    minimum_days=1,
                    maximum_days=3,
                    typical_days=2,
                    processing_type="expedited",
                    notes="Available for urgent cases with additional fee"
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        timeline_section = response.sections[4]
        
        # Should have both standard and expedited
        assert "• Standard Processing" in timeline_section.content
        assert "• Expedited Processing" in timeline_section.content
        
        # Should be separated by double newline
        assert "\n\n" in timeline_section.content
        
        # Verify standard timeline details
        assert "  Typical: 14 days" in timeline_section.content
        assert "  Range: 7-30 days" in timeline_section.content
        
        # Verify expedited timeline details
        assert "  Typical: 2 days" in timeline_section.content
        assert "  Range: 1-3 days" in timeline_section.content


class TestTask29ExpectedFormat:
    """Verify the exact expected format from task details."""
    
    def test_website_expected_format(self):
        """Verify website formatting matches the expected format from task details."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            official_websites=[
                OfficialWebsiteLink(
                    url="https://uidai.gov.in",
                    purpose="UIDAI Official Portal",
                    description="Main website for Aadhaar services"
                ),
                OfficialWebsiteLink(
                    url="https://myaadhaar.uidai.gov.in",
                    purpose="Online Update Portal",
                    description="Portal for online Aadhaar updates"
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        websites_section = response.sections[3]
        
        # Note: Pydantic's HttpUrl may add trailing slash, so we check structure not exact match
        lines = websites_section.content.split('\n')
        
        # Verify structure: bullet + purpose + URL, then indented description
        assert lines[0].startswith("• UIDAI Official Portal: https://uidai.gov.in")
        assert lines[1] == "  Main website for Aadhaar services"
        assert lines[2] == ""  # Blank line separator
        assert lines[3].startswith("• Online Update Portal: https://myaadhaar.uidai.gov.in")
        assert lines[4] == "  Portal for online Aadhaar updates"
    
    def test_timeline_expected_format(self):
        """Verify timeline formatting matches the expected format from task details."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            processing_timelines=[
                ProcessingTimeline(
                    minimum_days=7,
                    maximum_days=30,
                    typical_days=14,
                    processing_type="standard",
                    notes="Processing time may vary based on verification requirements",
                    factors_affecting_time=[
                        "Document verification complexity",
                        "Biometric verification requirement",
                        "Regional office workload"
                    ]
                ),
                ProcessingTimeline(
                    minimum_days=1,
                    maximum_days=3,
                    typical_days=2,
                    processing_type="expedited",
                    notes="Available for urgent cases with additional fee"
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        timeline_section = response.sections[4]
        
        # Verify key components are present in correct format
        lines = timeline_section.content.split('\n')
        
        # Standard processing section
        assert lines[0] == "• Standard Processing"
        assert lines[1] == "  Typical: 14 days"
        assert lines[2] == "  Range: 7-30 days"
        assert lines[3] == "  Note: Processing time may vary based on verification requirements"
        assert lines[4] == "  Factors affecting time:"
        assert lines[5] == "    - Document verification complexity"
        assert lines[6] == "    - Biometric verification requirement"
        assert lines[7] == "    - Regional office workload"
        
        # Blank line separator
        assert lines[8] == ""
        
        # Expedited processing section
        assert lines[9] == "• Expedited Processing"
        assert lines[10] == "  Typical: 2 days"
        assert lines[11] == "  Range: 1-3 days"
        assert lines[12] == "  Note: Available for urgent cases with additional fee"
