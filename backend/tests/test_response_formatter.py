"""Tests for ResponseFormatter service."""

import pytest
from datetime import datetime

from app.services.response_formatter import ResponseFormatter, ResponseSection, FormattedServiceResponse
from app.models.enhanced_service import (
    EnhancedServiceGuide,
    OfficeLocation,
    RequiredDocument,
    OfficeVisitStep,
    OfficialWebsiteLink,
    ProcessingTimeline
)
from app.models.schemas import ServiceCategory


def test_format_service_with_all_empty_categories():
    """Test formatting when all categories have no data."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test description",
        office_locations=[],
        required_documents=[],
        office_visit_sequence=[],
        official_websites=[],
        processing_timelines=[],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Verify response structure
    assert response.service_name == "Test Service"
    assert response.description == "Test description"
    assert len(response.sections) == 5
    
    # Verify all sections are present with correct headers
    expected_headers = [
        "📍 Office Locations",
        "📄 Required Documents",
        "🏢 Office Visit Sequence",
        "🔗 Official Websites",
        "⏱️ Processing Timeline"
    ]
    
    actual_headers = [section.header for section in response.sections]
    assert actual_headers == expected_headers
    
    # Verify all sections show "Information not available"
    for section in response.sections:
        assert section.is_empty
        assert section.content == "Information not available"


def test_format_service_with_populated_categories():
    """Test formatting when categories have data."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test description",
        office_locations=[
            OfficeLocation(
                name="Main Office",
                address="123 Main St",
                city="Mumbai",
                state="Maharashtra",
                postal_code="400001"
            )
        ],
        required_documents=[
            RequiredDocument(
                document_name="Aadhaar Card",
                copies_required=1
            )
        ],
        office_visit_sequence=[
            OfficeVisitStep(
                sequence_number=1,
                office_name="Main Office",
                purpose="Submit application",
                estimated_duration="30 minutes"
            )
        ],
        official_websites=[
            OfficialWebsiteLink(
                url="https://example.gov.in",
                purpose="Application Portal"
            )
        ],
        processing_timelines=[
            ProcessingTimeline(
                minimum_days=7,
                maximum_days=14,
                typical_days=10
            )
        ],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Verify response structure
    assert len(response.sections) == 5
    
    # Verify no sections are empty
    for section in response.sections:
        assert not section.is_empty
        assert section.content != "Information not available"
    
    # Verify content contains expected data
    assert "Main Office" in response.sections[0].content
    assert "Aadhaar Card" in response.sections[1].content
    assert "Submit application" in response.sections[2].content
    assert "https://example.gov.in" in response.sections[3].content
    assert "10 days" in response.sections[4].content


def test_category_order_consistency():
    """Test that category order is consistent across different services."""
    service1 = EnhancedServiceGuide(
        service_id="test1",
        service_name="Service 1",
        category=ServiceCategory.CERTIFICATE,
        description="Test 1",
        office_locations=[],
        required_documents=[],
        office_visit_sequence=[],
        official_websites=[],
        processing_timelines=[],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    service2 = EnhancedServiceGuide(
        service_id="test2",
        service_name="Service 2",
        category=ServiceCategory.IDENTITY_CARD,
        description="Test 2",
        office_locations=[
            OfficeLocation(
                name="Office",
                address="123 St",
                city="City",
                state="State",
                postal_code="123456"
            )
        ],
        required_documents=[],
        office_visit_sequence=[],
        official_websites=[],
        processing_timelines=[],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response1 = formatter.format_service_response(service1)
    response2 = formatter.format_service_response(service2)
    
    # Verify headers are in the same order
    headers1 = [s.header for s in response1.sections]
    headers2 = [s.header for s in response2.sections]
    
    assert headers1 == headers2


def test_mixed_empty_and_populated_categories():
    """Test formatting when some categories are empty and others are populated."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test description",
        office_locations=[
            OfficeLocation(
                name="Main Office",
                address="123 Main St",
                city="Mumbai",
                state="Maharashtra",
                postal_code="400001"
            )
        ],
        required_documents=[],  # Empty
        office_visit_sequence=[
            OfficeVisitStep(
                sequence_number=1,
                office_name="Main Office",
                purpose="Submit application",
                estimated_duration="30 minutes"
            )
        ],
        official_websites=[],  # Empty
        processing_timelines=[
            ProcessingTimeline(
                minimum_days=7,
                maximum_days=14,
                typical_days=10
            )
        ],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Verify all 5 sections are present
    assert len(response.sections) == 5
    
    # Verify empty sections
    assert response.sections[1].is_empty  # required_documents
    assert response.sections[1].content == "Information not available"
    assert response.sections[3].is_empty  # official_websites
    assert response.sections[3].content == "Information not available"
    
    # Verify populated sections
    assert not response.sections[0].is_empty  # office_locations
    assert "Main Office" in response.sections[0].content
    assert not response.sections[2].is_empty  # office_visit_sequence
    assert "Submit application" in response.sections[2].content
    assert not response.sections[4].is_empty  # processing_timelines
    assert "10 days" in response.sections[4].content
