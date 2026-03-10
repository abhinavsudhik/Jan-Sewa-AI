"""Tests for schema adapter functionality.

**Validates: Requirements 1.1**

This module tests the SchemaAdapter class to ensure proper conversion from legacy 
ServiceGuide format to the new EnhancedServiceGuide format. Tests verify backward 
compatibility and data preservation during migration.
"""

import pytest
from datetime import datetime

from app.models.schemas import (
    ServiceGuide,
    ServiceStep,
    ProcessingTime,
    ContactInfo,
    ServiceCategory,
)
from app.services.schema_adapter import SchemaAdapter


def test_legacy_to_enhanced_basic_conversion():
    """Test basic conversion from legacy to enhanced schema."""
    # Create a legacy ServiceGuide
    legacy = ServiceGuide(
        service_id="test_service",
        service_name="Test Service",
        category=ServiceCategory.AADHAAR,
        description="A test service",
        steps=[
            ServiceStep(
                step_number=1,
                description="Visit office",
                requires_in_person=True,
                online_available=False,
                estimated_duration="30 minutes",
            )
        ],
        processing_time=ProcessingTime(
            minimum="1 week",
            maximum="2 weeks",
            typical="10 days",
            factors=["Document verification", "Background check"],
        ),
        official_portal_url="https://example.gov.in",
        contact_info=ContactInfo(
            phone="+91-11-12345678",
            email="info@example.gov.in",
            address="123 Main Street, New Delhi, Delhi 110001",
        ),
        last_updated=datetime(2024, 1, 1, 12, 0, 0),
        available_languages=["en", "hi"],
    )
    
    # Convert to enhanced
    enhanced = SchemaAdapter.legacy_to_enhanced(legacy)
    
    # Verify basic fields
    assert enhanced.service_id == "test_service"
    assert enhanced.service_name == "Test Service"
    assert enhanced.category == ServiceCategory.AADHAAR
    assert enhanced.description == "A test service"
    assert enhanced.data_source == "legacy_migration"
    assert enhanced.available_languages == ["en", "hi"]


def test_office_location_extraction():
    """Test extraction of office location from contact info."""
    legacy = ServiceGuide(
        service_id="test",
        service_name="Test",
        category=ServiceCategory.AADHAAR,
        description="Test",
        steps=[],
        processing_time=ProcessingTime(
            minimum="1 day",
            maximum="2 days",
            typical="1 day",
            factors=[],
        ),
        official_portal_url="https://example.gov.in",
        contact_info=ContactInfo(
            address="456 Park Avenue, Mumbai, Maharashtra 400001",
            phone="+91-22-87654321",
        ),
        last_updated=datetime.now(),
        available_languages=["en"],
    )
    
    enhanced = SchemaAdapter.legacy_to_enhanced(legacy)
    
    # Verify office location
    assert len(enhanced.office_locations) == 1
    location = enhanced.office_locations[0]
    assert location.name == "Main Office"
    assert location.address == "456 Park Avenue, Mumbai, Maharashtra 400001"
    assert location.postal_code == "400001"
    assert location.state == "Maharashtra"
    assert location.contact_phone == "+91-22-87654321"


def test_missing_contact_info():
    """Test handling of missing contact info."""
    legacy = ServiceGuide(
        service_id="test",
        service_name="Test",
        category=ServiceCategory.AADHAAR,
        description="Test",
        steps=[],
        processing_time=ProcessingTime(
            minimum="1 day",
            maximum="2 days",
            typical="1 day",
            factors=[],
        ),
        official_portal_url="https://example.gov.in",
        contact_info=ContactInfo(),  # Empty contact info
        last_updated=datetime.now(),
        available_languages=["en"],
    )
    
    enhanced = SchemaAdapter.legacy_to_enhanced(legacy)
    
    # Should have empty office locations
    assert len(enhanced.office_locations) == 0


def test_steps_to_sequence_conversion():
    """Test conversion of steps to office visit sequence."""
    legacy = ServiceGuide(
        service_id="test",
        service_name="Test",
        category=ServiceCategory.AADHAAR,
        description="Test",
        steps=[
            ServiceStep(
                step_number=1,
                description="Submit application",
                requires_in_person=True,
                online_available=False,
                estimated_duration="15 minutes",
            ),
            ServiceStep(
                step_number=2,
                description="Biometric verification",
                requires_in_person=True,
                online_available=False,
                estimated_duration="10 minutes",
            ),
        ],
        processing_time=ProcessingTime(
            minimum="1 day",
            maximum="2 days",
            typical="1 day",
            factors=[],
        ),
        official_portal_url="https://example.gov.in",
        contact_info=ContactInfo(),
        last_updated=datetime.now(),
        available_languages=["en"],
    )
    
    enhanced = SchemaAdapter.legacy_to_enhanced(legacy)
    
    # Verify office visit sequence
    assert len(enhanced.office_visit_sequence) == 2
    assert enhanced.office_visit_sequence[0].sequence_number == 1
    assert enhanced.office_visit_sequence[0].purpose == "Submit application"
    assert enhanced.office_visit_sequence[0].estimated_duration == "15 minutes"
    assert enhanced.office_visit_sequence[1].sequence_number == 2
    assert enhanced.office_visit_sequence[1].purpose == "Biometric verification"


def test_processing_time_conversion():
    """Test conversion of processing time to timeline."""
    legacy = ServiceGuide(
        service_id="test",
        service_name="Test",
        category=ServiceCategory.AADHAAR,
        description="Test",
        steps=[],
        processing_time=ProcessingTime(
            minimum="1 week",
            maximum="3 weeks",
            typical="2 weeks",
            factors=["Document verification", "System load"],
        ),
        official_portal_url="https://example.gov.in",
        contact_info=ContactInfo(),
        last_updated=datetime.now(),
        available_languages=["en"],
    )
    
    enhanced = SchemaAdapter.legacy_to_enhanced(legacy)
    
    # Verify processing timeline
    assert len(enhanced.processing_timelines) == 1
    timeline = enhanced.processing_timelines[0]
    assert timeline.minimum_days == 7  # 1 week
    assert timeline.maximum_days == 21  # 3 weeks
    assert timeline.typical_days == 14  # 2 weeks
    assert timeline.time_unit == "days"
    assert timeline.processing_type == "standard"
    assert "Document verification" in timeline.factors_affecting_time


def test_duration_parsing():
    """Test parsing of various duration formats."""
    test_cases = [
        ("5 days", 5),
        ("2 weeks", 14),
        ("1 month", 30),
        ("3 months", 90),
        ("1 year", 365),
        ("10", 10),  # No unit, defaults to days
        ("", 0),  # Empty string
    ]
    
    for duration_str, expected_days in test_cases:
        result = SchemaAdapter._parse_duration_to_days(duration_str)
        assert result == expected_days, f"Failed for '{duration_str}': expected {expected_days}, got {result}"


def test_portal_url_conversion():
    """Test conversion of portal URL to website link."""
    legacy = ServiceGuide(
        service_id="test",
        service_name="Test",
        category=ServiceCategory.AADHAAR,
        description="Test",
        steps=[],
        processing_time=ProcessingTime(
            minimum="1 day",
            maximum="2 days",
            typical="1 day",
            factors=[],
        ),
        official_portal_url="https://uidai.gov.in",
        contact_info=ContactInfo(),
        last_updated=datetime.now(),
        available_languages=["en"],
    )
    
    enhanced = SchemaAdapter.legacy_to_enhanced(legacy)
    
    # Verify official website
    assert len(enhanced.official_websites) == 1
    website = enhanced.official_websites[0]
    assert str(website.url) == "https://uidai.gov.in/"
    assert website.purpose == "Official Portal"
    assert website.description == "Main government portal for this service"


def test_required_documents_empty():
    """Test that required documents is empty for legacy conversion."""
    legacy = ServiceGuide(
        service_id="test",
        service_name="Test",
        category=ServiceCategory.AADHAAR,
        description="Test",
        steps=[],
        processing_time=ProcessingTime(
            minimum="1 day",
            maximum="2 days",
            typical="1 day",
            factors=[],
        ),
        official_portal_url="https://example.gov.in",
        contact_info=ContactInfo(),
        last_updated=datetime.now(),
        available_languages=["en"],
    )
    
    enhanced = SchemaAdapter.legacy_to_enhanced(legacy)
    
    # Required documents should be empty (not in legacy schema)
    assert len(enhanced.required_documents) == 0


def test_legacy_fields_preserved():
    """Test that legacy fields are preserved for backward compatibility."""
    legacy = ServiceGuide(
        service_id="test",
        service_name="Test",
        category=ServiceCategory.AADHAAR,
        description="Test",
        steps=[
            ServiceStep(
                step_number=1,
                description="Test step",
                requires_in_person=True,
                online_available=False,
                estimated_duration="10 minutes",
            )
        ],
        processing_time=ProcessingTime(
            minimum="1 day",
            maximum="2 days",
            typical="1 day",
            factors=["Test factor"],
        ),
        official_portal_url="https://example.gov.in",
        contact_info=ContactInfo(address="Test address"),
        last_updated=datetime.now(),
        available_languages=["en"],
    )
    
    enhanced = SchemaAdapter.legacy_to_enhanced(legacy)
    
    # Verify legacy fields are preserved
    assert enhanced.steps is not None
    assert len(enhanced.steps) == 1
    assert enhanced.processing_time is not None
    assert enhanced.official_portal_url == "https://example.gov.in"
    assert enhanced.contact_info is not None


def test_address_parsing_with_various_formats():
    """Test address parsing with different formats."""
    test_cases = [
        (
            "123 Street, Bangalore, Karnataka 560001",
            ("Bangalore", "Karnataka", "560001")
        ),
        (
            "456 Road, Chennai, Tamil Nadu 600001",
            ("Chennai", "Tamil Nadu", "600001")
        ),
        (
            "789 Avenue, Kolkata, West Bengal 700001",
            ("Kolkata", "West Bengal", "700001")
        ),
        (
            "No postal code here, Delhi",
            ("Unknown", "Delhi", "000000")
        ),
        (
            "Simple address without details",
            ("Unknown", "Unknown", "000000")
        ),
    ]
    
    for address, (expected_city, expected_state, expected_postal) in test_cases:
        city, state, postal = SchemaAdapter._parse_address(address)
        assert state == expected_state, f"State mismatch for '{address}'"
        assert postal == expected_postal, f"Postal code mismatch for '{address}'"


# Additional unit tests for comprehensive coverage

def test_conversion_with_all_fields_populated():
    """Test conversion when all legacy fields are populated."""
    legacy = ServiceGuide(
        service_id="comprehensive_service",
        service_name="Comprehensive Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="A service with all fields populated",
        steps=[
            ServiceStep(
                step_number=1,
                description="Initial application submission",
                requires_in_person=True,
                online_available=True,
                estimated_duration="45 minutes",
                notes="Bring all required documents",
            ),
            ServiceStep(
                step_number=2,
                description="Document verification",
                requires_in_person=True,
                online_available=False,
                estimated_duration="20 minutes",
            ),
            ServiceStep(
                step_number=3,
                description="Final approval",
                requires_in_person=False,
                online_available=True,
                estimated_duration="5 minutes",
            ),
        ],
        processing_time=ProcessingTime(
            minimum="3 days",
            maximum="2 weeks",
            typical="1 week",
            factors=["Document completeness", "Office workload", "Holiday periods"],
        ),
        official_portal_url="https://comprehensive.gov.in/portal",
        contact_info=ContactInfo(
            phone="+91-80-12345678",
            email="support@comprehensive.gov.in",
            address="789 Government Complex, Sector 5, Bangalore, Karnataka 560078",
            helpline="1800-123-4567",
        ),
        last_updated=datetime(2024, 3, 15, 14, 30, 0),
        available_languages=["en", "hi", "kn"],
    )
    
    enhanced = SchemaAdapter.legacy_to_enhanced(legacy)
    
    # Verify all basic fields are preserved
    assert enhanced.service_id == "comprehensive_service"
    assert enhanced.service_name == "Comprehensive Test Service"
    assert enhanced.category == ServiceCategory.CERTIFICATE
    assert enhanced.description == "A service with all fields populated"
    assert enhanced.last_updated == datetime(2024, 3, 15, 14, 30, 0)
    assert enhanced.available_languages == ["en", "hi", "kn"]
    assert enhanced.data_source == "legacy_migration"
    
    # Verify office location extraction
    assert len(enhanced.office_locations) == 1
    location = enhanced.office_locations[0]
    assert location.name == "Main Office"
    assert location.address == "789 Government Complex, Sector 5, Bangalore, Karnataka 560078"
    assert location.city == "Bangalore"
    assert location.state == "Karnataka"
    assert location.postal_code == "560078"
    assert location.contact_phone == "+91-80-12345678"
    
    # Verify office visit sequence conversion
    assert len(enhanced.office_visit_sequence) == 3
    assert enhanced.office_visit_sequence[0].sequence_number == 1
    assert enhanced.office_visit_sequence[0].purpose == "Initial application submission"
    assert enhanced.office_visit_sequence[0].estimated_duration == "45 minutes"
    assert enhanced.office_visit_sequence[1].sequence_number == 2
    assert enhanced.office_visit_sequence[2].sequence_number == 3
    
    # Verify processing timeline conversion
    assert len(enhanced.processing_timelines) == 1
    timeline = enhanced.processing_timelines[0]
    assert timeline.minimum_days == 3
    assert timeline.maximum_days == 14  # 2 weeks
    assert timeline.typical_days == 7   # 1 week
    assert timeline.time_unit == "days"
    assert timeline.processing_type == "standard"
    assert "Document completeness" in timeline.factors_affecting_time
    assert "Office workload" in timeline.factors_affecting_time
    assert "Holiday periods" in timeline.factors_affecting_time
    
    # Verify official website conversion
    assert len(enhanced.official_websites) == 1
    website = enhanced.official_websites[0]
    assert str(website.url) == "https://comprehensive.gov.in/portal"
    assert website.purpose == "Official Portal"
    assert website.description == "Main government portal for this service"
    
    # Verify required documents is empty (not in legacy schema)
    assert len(enhanced.required_documents) == 0
    
    # Verify legacy fields are preserved for backward compatibility
    assert enhanced.steps is not None
    assert len(enhanced.steps) == 3
    assert enhanced.processing_time is not None
    assert enhanced.official_portal_url == "https://comprehensive.gov.in/portal"
    assert enhanced.contact_info is not None


def test_conversion_with_minimal_fields():
    """Test conversion when only required legacy fields are present."""
    legacy = ServiceGuide(
        service_id="minimal_service",
        service_name="Minimal Service",
        category=ServiceCategory.AADHAAR,
        description="Service with minimal data",
        steps=[],  # Empty steps
        processing_time=ProcessingTime(
            minimum="Unknown",
            maximum="Unknown",
            typical="Unknown",
            factors=[],
        ),
        official_portal_url="",  # Empty URL
        contact_info=ContactInfo(),  # Empty contact info
        last_updated=datetime(2024, 1, 1),
        available_languages=["en"],
    )
    
    enhanced = SchemaAdapter.legacy_to_enhanced(legacy)
    
    # Verify basic fields
    assert enhanced.service_id == "minimal_service"
    assert enhanced.service_name == "Minimal Service"
    assert enhanced.category == ServiceCategory.AADHAAR
    assert enhanced.description == "Service with minimal data"
    
    # Verify empty collections are handled properly
    assert len(enhanced.office_locations) == 0
    assert len(enhanced.required_documents) == 0
    assert len(enhanced.office_visit_sequence) == 0
    assert len(enhanced.official_websites) == 0
    # Processing timeline is created even with "Unknown" values (converted to 0 days)
    assert len(enhanced.processing_timelines) == 1
    timeline = enhanced.processing_timelines[0]
    assert timeline.minimum_days == 0
    assert timeline.maximum_days == 0
    assert timeline.typical_days == 0
    
    # Verify legacy fields are still preserved
    assert enhanced.steps == []
    assert enhanced.processing_time is not None
    assert enhanced.official_portal_url == ""
    assert enhanced.contact_info is not None


def test_missing_optional_fields_handling():
    """Test handling of missing optional fields with appropriate defaults."""
    # Create legacy service with minimal required fields
    legacy = ServiceGuide(
        service_id="test_optional",
        service_name="Test Optional Fields",
        category=ServiceCategory.CERTIFICATE,
        description="Testing optional field handling",
        steps=[
            ServiceStep(
                step_number=1,
                description="Basic step",
                requires_in_person=True,
                online_available=False,
                estimated_duration="30 minutes",
                notes=None,  # Optional field
            )
        ],
        processing_time=ProcessingTime(
            minimum="1 day",
            maximum="2 days", 
            typical="1 day",
            factors=[],
        ),
        official_portal_url="",  # Empty but not None
        contact_info=ContactInfo(
            phone=None,  # Optional field
            email=None,  # Optional field
            address="Basic address, Delhi, Delhi 110001",
            helpline=None,  # Optional field
        ),
        last_updated=datetime.now(),
        available_languages=["en"],
    )
    
    enhanced = SchemaAdapter.legacy_to_enhanced(legacy)
    
    # Verify basic fields are preserved
    assert enhanced.service_id == "test_optional"
    assert enhanced.service_name == "Test Optional Fields"
    
    # Verify office location handles missing phone
    assert len(enhanced.office_locations) == 1
    location = enhanced.office_locations[0]
    assert location.contact_phone is None
    assert location.address == "Basic address, Delhi, Delhi 110001"
    
    # Verify office sequence is created from steps
    assert len(enhanced.office_visit_sequence) == 1
    step = enhanced.office_visit_sequence[0]
    assert step.purpose == "Basic step"
    assert step.estimated_duration == "30 minutes"
    
    # Verify processing timeline is created
    assert len(enhanced.processing_timelines) == 1
    
    # Verify empty websites when URL is empty
    assert len(enhanced.official_websites) == 0


def test_data_preservation_during_conversion():
    """Test that existing data is preserved during conversion without loss."""
    original_datetime = datetime(2024, 2, 14, 10, 15, 30)
    
    legacy = ServiceGuide(
        service_id="preservation_test",
        service_name="Data Preservation Test",
        category=ServiceCategory.CERTIFICATE,  # Use valid category
        description="Testing data preservation during conversion",
        steps=[
            ServiceStep(
                step_number=1,
                description="Step with special characters: àáâãäå",
                requires_in_person=True,
                online_available=False,
                estimated_duration="1 hour 15 minutes",
                notes="Special note with unicode: ñáéíóú",
            ),
            ServiceStep(
                step_number=2,
                description="Step with numbers: 123-456-789",
                requires_in_person=False,
                online_available=True,
                estimated_duration="2.5 hours",
            ),
        ],
        processing_time=ProcessingTime(
            minimum="15 days",
            maximum="45 days",
            typical="30 days",
            factors=[
                "Background verification process",
                "Document authentication",
                "System processing delays",
            ],
        ),
        official_portal_url="https://transport.gov.in/dl-portal?ref=123&lang=en",
        contact_info=ContactInfo(
            phone="+91-11-2345-6789",
            email="dl-support@transport.gov.in",
            address="Transport Bhawan, 1 Parliament Street, New Delhi, Delhi 110001",
            helpline="1800-TRANSPORT",
        ),
        last_updated=original_datetime,
        available_languages=["en", "hi", "ta", "te"],
    )
    
    enhanced = SchemaAdapter.legacy_to_enhanced(legacy)
    
    # Verify exact preservation of text with special characters
    assert enhanced.service_name == "Data Preservation Test"
    assert enhanced.description == "Testing data preservation during conversion"
    
    # Verify step descriptions with special characters are preserved
    assert enhanced.office_visit_sequence[0].purpose == "Step with special characters: àáâãäå"
    assert enhanced.office_visit_sequence[1].purpose == "Step with numbers: 123-456-789"
    
    # Verify datetime is exactly preserved
    assert enhanced.last_updated == original_datetime
    
    # Verify language list is preserved
    assert enhanced.available_languages == ["en", "hi", "ta", "te"]
    
    # Verify complex URL with parameters is preserved
    assert str(enhanced.official_websites[0].url) == "https://transport.gov.in/dl-portal?ref=123&lang=en"
    
    # Verify processing factors are preserved
    timeline = enhanced.processing_timelines[0]
    assert "Background verification process" in timeline.factors_affecting_time
    assert "Document authentication" in timeline.factors_affecting_time
    assert "System processing delays" in timeline.factors_affecting_time
    
    # Verify contact info details are preserved
    location = enhanced.office_locations[0]
    assert location.contact_phone == "+91-11-2345-6789"
    assert "Transport Bhawan" in location.address
    assert "Parliament Street" in location.address
    
    # Verify legacy fields contain original data
    assert len(enhanced.steps) == 2
    assert enhanced.steps[0]["description"] == "Step with special characters: àáâãäå"
    assert enhanced.steps[0]["notes"] == "Special note with unicode: ñáéíóú"
    assert enhanced.contact_info["email"] == "dl-support@transport.gov.in"
    assert enhanced.contact_info["helpline"] == "1800-TRANSPORT"


def test_edge_cases_in_duration_parsing():
    """Test edge cases in duration string parsing."""
    test_cases = [
        # Standard cases
        ("1 day", 1),
        ("7 days", 7),
        ("1 week", 7),
        ("2 weeks", 14),
        ("1 month", 30),
        ("3 months", 90),
        ("1 year", 365),
        
        # Edge cases
        ("0 days", 0),
        ("100 days", 100),
        ("52 weeks", 364),
        ("12 months", 360),
        
        # Variations in formatting
        ("5day", 5),  # No space
        ("3 WEEKS", 21),  # Uppercase
        ("2Days", 2),  # Mixed case
        ("1  month", 30),  # Extra spaces
        
        # Numbers without units (should default to days)
        ("15", 15),
        ("0", 0),
        ("999", 999),
        
        # Invalid/empty cases
        ("", 0),
        ("unknown", 0),
        ("not a number", 0),
        ("days without number", 0),
        ("   ", 0),  # Whitespace only
    ]
    
    for duration_str, expected_days in test_cases:
        result = SchemaAdapter._parse_duration_to_days(duration_str)
        assert result == expected_days, f"Failed for '{duration_str}': expected {expected_days}, got {result}"


def test_address_parsing_edge_cases():
    """Test address parsing with edge cases and malformed addresses."""
    test_cases = [
        # Well-formed addresses
        ("123 Main St, Mumbai, Maharashtra 400001", ("Mumbai", "Maharashtra", "400001")),
        ("456 Park Ave, Chennai, Tamil Nadu 600001", ("Chennai", "Tamil Nadu", "600001")),
        
        # Missing components
        ("Just a street address", ("Unknown", "Unknown", "000000")),
        ("Delhi", ("Unknown", "Delhi", "000000")),
        ("Karnataka 560001", ("Unknown", "Karnataka", "560001")),
        ("123456", ("Unknown", "Unknown", "123456")),
        
        # Multiple postal codes (should pick first)
        ("Address with 110001 and 110002", ("Unknown", "Unknown", "110001")),
        
        # No recognizable state
        ("123 Street, SomeCity, UnknownState 123456", ("Unknown", "Unknown", "123456")),
        
        # Complex formatting
        ("Flat 4B, Tower 2, Complex Name, Sector 15, Gurgaon, Haryana 122001", 
         ("Gurgaon", "Haryana", "122001")),
        
        # Empty/None cases
        ("", ("Unknown", "Unknown", "000000")),
    ]
    
    for address, (expected_city, expected_state, expected_postal) in test_cases:
        city, state, postal = SchemaAdapter._parse_address(address)
        assert state == expected_state, f"State mismatch for '{address}': expected '{expected_state}', got '{state}'"
        assert postal == expected_postal, f"Postal code mismatch for '{address}': expected '{expected_postal}', got '{postal}'"


def test_conversion_maintains_data_types():
    """Test that conversion maintains proper data types for all fields."""
    legacy = ServiceGuide(
        service_id="type_test",
        service_name="Type Test Service",
        category=ServiceCategory.AADHAAR,
        description="Testing data type preservation",
        steps=[
            ServiceStep(
                step_number=1,
                description="Test step",
                requires_in_person=True,
                online_available=False,
                estimated_duration="30 minutes",
            )
        ],
        processing_time=ProcessingTime(
            minimum="1 week",
            maximum="2 weeks",
            typical="10 days",
            factors=["Factor 1", "Factor 2"],
        ),
        official_portal_url="https://example.gov.in",
        contact_info=ContactInfo(
            phone="+91-11-12345678",
            address="Test Address, Delhi, Delhi 110001",
        ),
        last_updated=datetime(2024, 1, 1, 12, 0, 0),
        available_languages=["en", "hi"],
    )
    
    enhanced = SchemaAdapter.legacy_to_enhanced(legacy)
    
    # Verify string fields remain strings
    assert isinstance(enhanced.service_id, str)
    assert isinstance(enhanced.service_name, str)
    assert isinstance(enhanced.description, str)
    assert isinstance(enhanced.data_source, str)
    
    # Verify list fields remain lists
    assert isinstance(enhanced.office_locations, list)
    assert isinstance(enhanced.required_documents, list)
    assert isinstance(enhanced.office_visit_sequence, list)
    assert isinstance(enhanced.official_websites, list)
    assert isinstance(enhanced.processing_timelines, list)
    assert isinstance(enhanced.available_languages, list)
    
    # Verify datetime field remains datetime
    assert isinstance(enhanced.last_updated, datetime)
    
    # Verify enum field remains enum
    assert isinstance(enhanced.category, ServiceCategory)
    
    # Verify nested object types
    if enhanced.office_locations:
        location = enhanced.office_locations[0]
        assert isinstance(location.name, str)
        assert isinstance(location.address, str)
        assert isinstance(location.city, str)
        assert isinstance(location.state, str)
        assert isinstance(location.postal_code, str)
    
    if enhanced.office_visit_sequence:
        step = enhanced.office_visit_sequence[0]
        assert isinstance(step.sequence_number, int)
        assert isinstance(step.office_name, str)
        assert isinstance(step.purpose, str)
        assert isinstance(step.estimated_duration, str)
        assert isinstance(step.is_optional, bool)
        assert isinstance(step.is_conditional, bool)
    
    if enhanced.processing_timelines:
        timeline = enhanced.processing_timelines[0]
        assert isinstance(timeline.minimum_days, int)
        assert isinstance(timeline.maximum_days, int)
        assert isinstance(timeline.typical_days, int)
        assert isinstance(timeline.time_unit, str)
        assert isinstance(timeline.processing_type, str)
        assert isinstance(timeline.factors_affecting_time, list)


def test_backward_compatibility_fields():
    """Test that backward compatibility fields are properly preserved."""
    legacy = ServiceGuide(
        service_id="compat_test",
        service_name="Compatibility Test",
        category=ServiceCategory.CERTIFICATE,
        description="Testing backward compatibility",
        steps=[
            ServiceStep(
                step_number=1,
                description="Original step",
                requires_in_person=True,
                online_available=False,
                estimated_duration="45 minutes",
                notes="Original notes",
            )
        ],
        processing_time=ProcessingTime(
            minimum="5 days",
            maximum="10 days",
            typical="7 days",
            factors=["Original factor"],
        ),
        official_portal_url="https://original.gov.in",
        contact_info=ContactInfo(
            phone="+91-11-11111111",
            email="original@gov.in",
            address="Original Address, Delhi, Delhi 110001",
            helpline="1800-ORIGINAL",
        ),
        last_updated=datetime(2024, 1, 1),
        available_languages=["en"],
    )
    
    enhanced = SchemaAdapter.legacy_to_enhanced(legacy)
    
    # Verify legacy fields are preserved as dictionaries
    assert enhanced.steps is not None
    assert isinstance(enhanced.steps, list)
    assert len(enhanced.steps) == 1
    assert isinstance(enhanced.steps[0], dict)
    assert enhanced.steps[0]["step_number"] == 1
    assert enhanced.steps[0]["description"] == "Original step"
    assert enhanced.steps[0]["requires_in_person"] is True
    assert enhanced.steps[0]["online_available"] is False
    assert enhanced.steps[0]["estimated_duration"] == "45 minutes"
    assert enhanced.steps[0]["notes"] == "Original notes"
    
    assert enhanced.processing_time is not None
    assert isinstance(enhanced.processing_time, dict)
    assert enhanced.processing_time["minimum"] == "5 days"
    assert enhanced.processing_time["maximum"] == "10 days"
    assert enhanced.processing_time["typical"] == "7 days"
    assert enhanced.processing_time["factors"] == ["Original factor"]
    
    assert enhanced.official_portal_url == "https://original.gov.in"
    
    assert enhanced.contact_info is not None
    assert isinstance(enhanced.contact_info, dict)
    assert enhanced.contact_info["phone"] == "+91-11-11111111"
    assert enhanced.contact_info["email"] == "original@gov.in"
    assert enhanced.contact_info["address"] == "Original Address, Delhi, Delhi 110001"
    assert enhanced.contact_info["helpline"] == "1800-ORIGINAL"
