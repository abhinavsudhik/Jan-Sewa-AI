"""Tests for website links and timeline formatting in ResponseFormatter.

This test module specifically tests Task 2.9 implementation:
- _format_official_websites() with URL formatting and labeling
- _format_processing_timelines() with range and type display
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


class TestOfficialWebsiteFormatting:
    """Tests for _format_official_websites() method."""
    
    def test_single_website_without_description(self):
        """Test formatting a single website without description."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test Service",
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
        
        # Get the official websites section (4th section, index 3)
        websites_section = response.sections[3]
        
        assert not websites_section.is_empty
        assert "• UIDAI Official Portal: https://uidai.gov.in" in websites_section.content
        # Should not have description line
        assert websites_section.content.count('\n') == 0
    
    def test_single_website_with_description(self):
        """Test formatting a single website with description."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test Service",
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
        
        assert not websites_section.is_empty
        assert "• UIDAI Official Portal: https://uidai.gov.in" in websites_section.content
        assert "  Main website for Aadhaar services" in websites_section.content
    
    def test_multiple_websites_with_mixed_descriptions(self):
        """Test formatting multiple websites with some having descriptions."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test Service",
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
        
        assert not websites_section.is_empty
        
        # Check first website
        assert "• UIDAI Official Portal: https://uidai.gov.in" in websites_section.content
        assert "  Main website for Aadhaar services" in websites_section.content
        
        # Check second website
        assert "• Online Update Portal: https://myaadhaar.uidai.gov.in" in websites_section.content
        assert "  Portal for online Aadhaar updates" in websites_section.content
        
        # Check proper spacing between websites (double newline)
        assert "\n\n" in websites_section.content
    
    def test_website_formatting_structure(self):
        """Test that website formatting follows the expected structure."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test Service",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            official_websites=[
                OfficialWebsiteLink(
                    url="https://example.gov.in",
                    purpose="Application Portal",
                    description="Submit your application online"
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        
        websites_section = response.sections[3]
        lines = websites_section.content.split('\n')
        
        # First line should be bullet with purpose and URL
        assert lines[0].startswith("• Application Portal:")
        assert "https://example.gov.in" in lines[0]
        
        # Second line should be indented description
        assert lines[1].startswith("  ")
        assert "Submit your application online" in lines[1]


class TestProcessingTimelineFormatting:
    """Tests for _format_processing_timelines() method."""
    
    def test_single_timeline_basic(self):
        """Test formatting a single timeline with basic information."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test Service",
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
        
        # Get the processing timeline section (5th section, index 4)
        timeline_section = response.sections[4]
        
        assert not timeline_section.is_empty
        assert "• Standard Processing" in timeline_section.content
        assert "  Typical: 14 days" in timeline_section.content
        assert "  Range: 7-30 days" in timeline_section.content
    
    def test_timeline_with_notes(self):
        """Test formatting timeline with notes."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test Service",
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
        
        assert "  Note: Processing time may vary based on verification requirements" in timeline_section.content
    
    def test_timeline_with_factors(self):
        """Test formatting timeline with factors affecting time."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test Service",
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
        
        assert "  Factors affecting time:" in timeline_section.content
        assert "    - Document verification complexity" in timeline_section.content
        assert "    - Biometric verification requirement" in timeline_section.content
        assert "    - Regional office workload" in timeline_section.content
    
    def test_timeline_with_notes_and_factors(self):
        """Test formatting timeline with both notes and factors."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test Service",
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
        
        # Check all components are present
        assert "• Standard Processing" in timeline_section.content
        assert "  Typical: 14 days" in timeline_section.content
        assert "  Range: 7-30 days" in timeline_section.content
        assert "  Note: Processing time may vary" in timeline_section.content
        assert "  Factors affecting time:" in timeline_section.content
        assert "    - Document verification complexity" in timeline_section.content
    
    def test_multiple_timelines_standard_and_expedited(self):
        """Test formatting multiple timelines (standard and expedited)."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test Service",
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
        
        # Check standard processing
        assert "• Standard Processing" in timeline_section.content
        assert "  Typical: 14 days" in timeline_section.content
        assert "  Range: 7-30 days" in timeline_section.content
        
        # Check expedited processing
        assert "• Expedited Processing" in timeline_section.content
        assert "  Typical: 2 days" in timeline_section.content
        assert "  Range: 1-3 days" in timeline_section.content
        assert "  Note: Available for urgent cases with additional fee" in timeline_section.content
        
        # Check proper spacing between timelines (double newline)
        assert "\n\n" in timeline_section.content
    
    def test_timeline_formatting_structure(self):
        """Test that timeline formatting follows the expected structure."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test Service",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            processing_timelines=[
                ProcessingTimeline(
                    minimum_days=7,
                    maximum_days=30,
                    typical_days=14,
                    processing_type="standard",
                    notes="Test note",
                    factors_affecting_time=["Factor 1", "Factor 2"]
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        
        timeline_section = response.sections[4]
        lines = timeline_section.content.split('\n')
        
        # Verify structure
        assert lines[0] == "• Standard Processing"
        assert lines[1] == "  Typical: 14 days"
        assert lines[2] == "  Range: 7-30 days"
        assert lines[3] == "  Note: Test note"
        assert lines[4] == "  Factors affecting time:"
        assert lines[5] == "    - Factor 1"
        assert lines[6] == "    - Factor 2"
    
    def test_timeline_empty_factors_list(self):
        """Test that empty factors list doesn't add factors section."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test Service",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            processing_timelines=[
                ProcessingTimeline(
                    minimum_days=7,
                    maximum_days=30,
                    typical_days=14,
                    processing_type="standard",
                    factors_affecting_time=[]
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        
        timeline_section = response.sections[4]
        
        # Should not contain factors section
        assert "Factors affecting time:" not in timeline_section.content
