"""Tests for schema adapter functionality."""

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
