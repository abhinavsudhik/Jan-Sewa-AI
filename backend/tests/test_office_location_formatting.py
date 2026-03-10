"""Tests for office location formatting in ResponseFormatter.

This test file specifically validates Task 2.3 requirements:
- Complete address details for each location
- Coordinates (latitude, longitude) when available
- Operating hours when available
- Contact phone when available
- Multiple locations as separate list items with proper spacing
"""

import pytest
from datetime import datetime

from app.services.response_formatter import ResponseFormatter
from app.models.enhanced_service import (
    EnhancedServiceGuide,
    OfficeLocation,
    Coordinates
)
from app.models.schemas import ServiceCategory


def test_office_location_with_all_fields():
    """Test formatting of office location with all optional fields present."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test",
        office_locations=[
            OfficeLocation(
                name="District Aadhaar Center",
                address="123 Main Street",
                city="Mumbai",
                state="Maharashtra",
                postal_code="400001",
                coordinates=Coordinates(latitude=19.0760, longitude=72.8777),
                operating_hours="9:00 AM - 5:00 PM",
                contact_phone="+91-22-12345678"
            )
        ],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Get office locations section
    office_section = response.sections[0]
    assert office_section.header == "📍 Office Locations"
    assert not office_section.is_empty
    
    content = office_section.content
    
    # Verify all required fields are present
    assert "• District Aadhaar Center" in content
    assert "123 Main Street, Mumbai, Maharashtra 400001" in content
    assert "Coordinates: 19.076, 72.8777" in content
    assert "Hours: 9:00 AM - 5:00 PM" in content
    assert "Phone: +91-22-12345678" in content


def test_office_location_without_optional_fields():
    """Test formatting of office location with only required fields."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test",
        office_locations=[
            OfficeLocation(
                name="Regional Office",
                address="456 Park Road",
                city="Mumbai",
                state="Maharashtra",
                postal_code="400002"
                # No coordinates, operating_hours, or contact_phone
            )
        ],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    office_section = response.sections[0]
    content = office_section.content
    
    # Verify required fields are present
    assert "• Regional Office" in content
    assert "456 Park Road, Mumbai, Maharashtra 400002" in content
    
    # Verify optional fields are NOT present
    assert "Coordinates:" not in content
    assert "Hours:" not in content
    assert "Phone:" not in content


def test_multiple_office_locations_formatting():
    """Test formatting of multiple office locations with proper spacing."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test",
        office_locations=[
            OfficeLocation(
                name="District Aadhaar Center",
                address="123 Main Street",
                city="Mumbai",
                state="Maharashtra",
                postal_code="400001",
                coordinates=Coordinates(latitude=19.0760, longitude=72.8777),
                operating_hours="9:00 AM - 5:00 PM",
                contact_phone="+91-22-12345678"
            ),
            OfficeLocation(
                name="Regional Office",
                address="456 Park Road",
                city="Mumbai",
                state="Maharashtra",
                postal_code="400002",
                operating_hours="10:00 AM - 4:00 PM"
            )
        ],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    office_section = response.sections[0]
    content = office_section.content
    
    # Verify both locations are present
    assert "• District Aadhaar Center" in content
    assert "• Regional Office" in content
    
    # Verify proper spacing between locations (double newline)
    assert "\n\n" in content
    
    # Verify first location has all fields
    assert "123 Main Street, Mumbai, Maharashtra 400001" in content
    assert "Coordinates: 19.076, 72.8777" in content
    assert "9:00 AM - 5:00 PM" in content
    assert "+91-22-12345678" in content
    
    # Verify second location has its fields
    assert "456 Park Road, Mumbai, Maharashtra 400002" in content
    assert "10:00 AM - 4:00 PM" in content


def test_office_location_with_partial_optional_fields():
    """Test formatting with some optional fields present and others absent."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test",
        office_locations=[
            OfficeLocation(
                name="Main Office",
                address="789 Test Street",
                city="Delhi",
                state="Delhi",
                postal_code="110001",
                coordinates=Coordinates(latitude=28.6139, longitude=77.2090),
                # Has coordinates but no operating_hours or contact_phone
            )
        ],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    office_section = response.sections[0]
    content = office_section.content
    
    # Verify required fields and coordinates are present
    assert "• Main Office" in content
    assert "789 Test Street, Delhi, Delhi 110001" in content
    assert "Coordinates: 28.6139, 77.209" in content
    
    # Verify other optional fields are NOT present
    assert "Hours:" not in content
    assert "Phone:" not in content


def test_office_location_indentation():
    """Test that sub-details are properly indented under the office name."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test",
        office_locations=[
            OfficeLocation(
                name="Test Office",
                address="123 Street",
                city="City",
                state="State",
                postal_code="123456",
                coordinates=Coordinates(latitude=10.0, longitude=20.0),
                operating_hours="9-5",
                contact_phone="123-456"
            )
        ],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    office_section = response.sections[0]
    content = office_section.content
    lines = content.split('\n')
    
    # First line should be the bullet point with office name
    assert lines[0] == "• Test Office"
    
    # All subsequent lines should start with two spaces (indentation)
    for line in lines[1:]:
        if line:  # Skip empty lines
            assert line.startswith("  "), f"Line not properly indented: {line}"
