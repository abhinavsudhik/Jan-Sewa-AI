"""Tests for enhanced mock service data.

Verifies that the mock data:
- Loads correctly
- Contains all required services
- Has proper data structure
- Includes edge cases (empty categories, single items)
- Has valid metadata
"""

import pytest
from datetime import datetime

from app.data.enhanced_mock_services import get_enhanced_mock_services
from app.models.enhanced_service import EnhancedServiceGuide
from app.models.schemas import ServiceCategory


class TestEnhancedMockData:
    """Test suite for enhanced mock service data."""
    
    def test_loads_all_services(self):
        """Test that all expected services are loaded."""
        services = get_enhanced_mock_services()
        
        assert len(services) == 4
        assert "aadhaar_name_change" in services
        assert "data_access_request" in services
        assert "birth_certificate" in services
        assert "service_status_tracking" in services
    
    def test_all_services_are_valid(self):
        """Test that all services are valid EnhancedServiceGuide instances."""
        services = get_enhanced_mock_services()
        
        for service_id, service in services.items():
            assert isinstance(service, EnhancedServiceGuide)
            assert service.service_id == service_id
            assert service.service_name
            assert service.description
            assert isinstance(service.category, ServiceCategory)
    
    def test_aadhaar_service_fully_populated(self):
        """Test that Aadhaar service has all categories populated."""
        services = get_enhanced_mock_services()
        aadhaar = services["aadhaar_name_change"]
        
        # Should have multiple items in each category
        assert len(aadhaar.office_locations) == 3
        assert len(aadhaar.required_documents) == 4
        assert len(aadhaar.office_visit_sequence) == 3
        assert len(aadhaar.official_websites) == 4
        assert len(aadhaar.processing_timelines) == 2
        
        # Verify coordinates are present
        assert aadhaar.office_locations[0].coordinates is not None
        assert aadhaar.office_locations[0].coordinates.latitude == 28.5672
        assert aadhaar.office_locations[0].coordinates.longitude == 77.2100
        
        # Verify document specifications
        assert aadhaar.required_documents[0].copies_required == 2
        assert aadhaar.required_documents[0].format_requirements is not None
        
        # Verify office sequence numbering
        assert aadhaar.office_visit_sequence[0].sequence_number == 1
        assert aadhaar.office_visit_sequence[1].sequence_number == 2
        assert aadhaar.office_visit_sequence[2].sequence_number == 3
        
        # Verify conditional and optional steps
        assert aadhaar.office_visit_sequence[1].is_conditional is True
        assert aadhaar.office_visit_sequence[2].is_optional is True
        
        # Verify both standard and expedited timelines
        timeline_types = [t.processing_type for t in aadhaar.processing_timelines]
        assert "standard" in timeline_types
        assert "expedited" in timeline_types
    
    def test_data_access_request_empty_categories(self):
        """Test that Data Access Request has some empty categories."""
        services = get_enhanced_mock_services()
        dar = services["data_access_request"]
        
        # Should have empty office locations and office visit sequence
        assert len(dar.office_locations) == 0
        assert len(dar.office_visit_sequence) == 0
        
        # Should have populated other categories
        assert len(dar.required_documents) > 0
        assert len(dar.official_websites) > 0
        assert len(dar.processing_timelines) > 0
    
    def test_birth_certificate_single_items(self):
        """Test that Birth Certificate has single items in each category."""
        services = get_enhanced_mock_services()
        bc = services["birth_certificate"]
        
        # Should have exactly one item in each category
        assert len(bc.office_locations) == 1
        assert len(bc.required_documents) == 1
        assert len(bc.office_visit_sequence) == 1
        assert len(bc.official_websites) == 1
        assert len(bc.processing_timelines) == 1
    
    def test_service_status_tracking_mixed_categories(self):
        """Test that Service Status Tracking has mixed category population."""
        services = get_enhanced_mock_services()
        sst = services["service_status_tracking"]
        
        # Should have mixed population - some multiple, some single, some empty
        assert len(sst.office_locations) == 2  # Multiple locations
        assert len(sst.required_documents) == 1  # Single document
        assert len(sst.office_visit_sequence) == 0  # Empty (online service)
        assert len(sst.official_websites) == 3  # Multiple websites
        assert len(sst.processing_timelines) == 2  # Multiple timelines
        
        # Verify it has different timeline types
        timeline_types = [t.processing_type for t in sst.processing_timelines]
        assert "status_update" in timeline_types
        assert "issue_resolution" in timeline_types
    
    def test_metadata_present(self):
        """Test that all services have required metadata."""
        services = get_enhanced_mock_services()
        
        for service in services.values():
            assert isinstance(service.last_updated, datetime)
            assert service.data_source
            assert len(service.available_languages) > 0
            assert "en" in service.available_languages
    
    def test_coordinates_validation(self):
        """Test that coordinates are within valid ranges."""
        services = get_enhanced_mock_services()
        
        for service in services.values():
            for location in service.office_locations:
                if location.coordinates:
                    assert -90 <= location.coordinates.latitude <= 90
                    assert -180 <= location.coordinates.longitude <= 180
    
    def test_timeline_validation(self):
        """Test that timelines satisfy min <= typical <= max."""
        services = get_enhanced_mock_services()
        
        for service in services.values():
            for timeline in service.processing_timelines:
                assert timeline.minimum_days <= timeline.typical_days
                assert timeline.typical_days <= timeline.maximum_days
                assert timeline.time_unit in ["days", "weeks", "months"]
    
    def test_document_copies_validation(self):
        """Test that document copies_required is at least 1."""
        services = get_enhanced_mock_services()
        
        for service in services.values():
            for document in service.required_documents:
                assert document.copies_required >= 1
    
    def test_website_urls_are_https(self):
        """Test that website URLs use HTTPS protocol."""
        services = get_enhanced_mock_services()
        
        for service in services.values():
            for website in service.official_websites:
                # All our mock data uses HTTPS
                assert str(website.url).startswith("https://")
    
    def test_office_sequence_numbering(self):
        """Test that office visit sequences are properly numbered."""
        services = get_enhanced_mock_services()
        
        for service in services.values():
            if service.office_visit_sequence:
                sequence_numbers = [step.sequence_number for step in service.office_visit_sequence]
                # Should be sequential starting from 1
                assert sequence_numbers == list(range(1, len(sequence_numbers) + 1))
    
    def test_realistic_indian_addresses(self):
        """Test that addresses contain realistic Indian location data."""
        services = get_enhanced_mock_services()
        
        for service in services.values():
            for location in service.office_locations:
                # Should have Indian state
                assert location.state in ["Delhi", "Maharashtra", "Karnataka", "Tamil Nadu", 
                                         "West Bengal", "Gujarat", "Rajasthan", "Uttar Pradesh",
                                         "Madhya Pradesh", "Bihar", "Andhra Pradesh", "Telangana",
                                         "Kerala", "Odisha", "Punjab", "Haryana", "Assam",
                                         "Jharkhand", "Chhattisgarh", "Uttarakhand", "Himachal Pradesh",
                                         "Tripura", "Meghalaya", "Manipur", "Nagaland", "Goa",
                                         "Arunachal Pradesh", "Mizoram", "Sikkim", "Jammu and Kashmir",
                                         "Ladakh"]
                # Should have 6-digit postal code
                assert len(location.postal_code) == 6
                assert location.postal_code.isdigit()
