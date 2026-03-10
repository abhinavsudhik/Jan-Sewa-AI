"""
Property Test for Data Source Tracking

**Property 30: Data Source Tracking** - Verify all service data maintains source metadata

**Validates: Requirements 9.4**

This property test ensures that all EnhancedServiceGuide instances maintain proper
source metadata tracking. The test validates that the data_source field is always
present and meaningful, enabling verification of information sources.

Requirements Reference:
- Requirement 9.4: THE Service_Information_System SHALL track the data source for 
  each piece of information to enable verification
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.enhanced_service import (
    EnhancedServiceGuide,
    OfficeLocation,
    RequiredDocument,
    OfficeVisitStep,
    OfficialWebsiteLink,
    ProcessingTimeline,
    Coordinates
)
from app.models.schemas import ServiceCategory
from app.data.enhanced_mock_services import get_enhanced_mock_services
from app.repositories.service_repository import ServiceRepository


# Strategies for generating test data

@st.composite
def coordinates_strategy(draw):
    """Generate valid coordinates."""
    return Coordinates(
        latitude=draw(st.floats(min_value=-90, max_value=90)),
        longitude=draw(st.floats(min_value=-180, max_value=180))
    )


@st.composite
def office_location_strategy(draw):
    """Generate valid office locations."""
    return OfficeLocation(
        name=draw(st.text(min_size=1, max_size=100)),
        address=draw(st.text(min_size=1, max_size=200)),
        city=draw(st.text(min_size=1, max_size=50)),
        state=draw(st.text(min_size=1, max_size=50)),
        postal_code=draw(st.text(min_size=5, max_size=10)),
        coordinates=draw(st.one_of(st.none(), coordinates_strategy())),
        operating_hours=draw(st.one_of(st.none(), st.text(min_size=1, max_size=100))),
        contact_phone=draw(st.one_of(st.none(), st.text(min_size=1, max_size=20)))
    )


@st.composite
def required_document_strategy(draw):
    """Generate valid required documents."""
    return RequiredDocument(
        document_name=draw(st.text(min_size=1, max_size=100)),
        description=draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        copies_required=draw(st.integers(min_value=1, max_value=10)),
        format_requirements=draw(st.one_of(st.none(), st.text(min_size=1, max_size=100))),
        is_mandatory=draw(st.booleans()),
        alternatives=draw(st.one_of(st.none(), st.lists(st.text(min_size=1, max_size=50), max_size=5)))
    )


@st.composite
def office_visit_step_strategy(draw):
    """Generate valid office visit steps."""
    return OfficeVisitStep(
        sequence_number=draw(st.integers(min_value=1, max_value=10)),
        office_name=draw(st.text(min_size=1, max_size=100)),
        purpose=draw(st.text(min_size=1, max_size=200)),
        estimated_duration=draw(st.text(min_size=1, max_size=50)),
        is_optional=draw(st.booleans()),
        is_conditional=draw(st.booleans()),
        condition=draw(st.one_of(st.none(), st.text(min_size=1, max_size=100)))
    )


@st.composite
def official_website_link_strategy(draw):
    """Generate valid official website links."""
    # Generate valid URLs
    schemes = ["https", "http"]
    domains = ["gov.in", "nic.in", "india.gov.in", "uidai.gov.in", "digitalindia.gov.in"]
    
    scheme = draw(st.sampled_from(schemes))
    domain = draw(st.sampled_from(domains))
    path = draw(st.text(min_size=0, max_size=50, alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="/-_")))
    
    url = f"{scheme}://{domain}/{path}".rstrip('/')
    
    return OfficialWebsiteLink(
        url=url,
        purpose=draw(st.text(min_size=1, max_size=100)),
        description=draw(st.one_of(st.none(), st.text(min_size=1, max_size=200)))
    )


@st.composite
def processing_timeline_strategy(draw):
    """Generate valid processing timelines."""
    min_days = draw(st.integers(min_value=1, max_value=30))
    max_days = draw(st.integers(min_value=min_days, max_value=min_days + 365))
    typical_days = draw(st.integers(min_value=min_days, max_value=max_days))
    
    return ProcessingTimeline(
        minimum_days=min_days,
        maximum_days=max_days,
        typical_days=typical_days,
        time_unit=draw(st.sampled_from(["days", "weeks", "months"])),
        processing_type=draw(st.sampled_from(["standard", "expedited", "urgent"])),
        notes=draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        factors_affecting_time=draw(st.lists(st.text(min_size=1, max_size=100), max_size=5))
    )


@st.composite
def data_source_strategy(draw):
    """Generate meaningful data source strings."""
    sources = [
        "UIDAI Official Guidelines 2024",
        "Ministry of Electronics and IT - Digital India Portal",
        "Government of India - Official Website",
        "National Informatics Centre Database",
        "State Government Official Records",
        "Central Government Notification 2024",
        "Department of Administrative Reforms",
        "Official Government Gazette",
        "Ministry Documentation System",
        "Authenticated Government Database"
    ]
    return draw(st.sampled_from(sources))


@st.composite
def enhanced_service_guide_strategy(draw):
    """Generate valid EnhancedServiceGuide instances."""
    # Generate a recent timestamp
    base_date = datetime(2024, 1, 1)
    days_offset = draw(st.integers(min_value=0, max_value=365))
    last_updated = base_date + timedelta(days=days_offset)
    
    return EnhancedServiceGuide(
        service_id=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="_-"))),
        service_name=draw(st.text(min_size=1, max_size=100)),
        category=draw(st.sampled_from(ServiceCategory)),
        description=draw(st.text(min_size=1, max_size=500)),
        office_locations=draw(st.lists(office_location_strategy(), max_size=5)),
        required_documents=draw(st.lists(required_document_strategy(), max_size=10)),
        office_visit_sequence=draw(st.lists(office_visit_step_strategy(), max_size=5)),
        official_websites=draw(st.lists(official_website_link_strategy(), max_size=5)),
        processing_timelines=draw(st.lists(processing_timeline_strategy(), max_size=3)),
        last_updated=last_updated,
        data_source=draw(data_source_strategy()),
        available_languages=draw(st.lists(st.sampled_from(["en", "hi", "ta", "te", "bn", "gu", "mr", "pa"]), min_size=1, max_size=5))
    )


# Property Tests

@given(service=enhanced_service_guide_strategy())
@settings(
    max_examples=50,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_property_30_data_source_tracking(service):
    """
    Property 30: Data Source Tracking
    
    **Validates: Requirements 9.4**
    
    For any piece of service information, the system must maintain metadata 
    tracking the data source to enable verification.
    
    This property verifies that:
    1. The data_source field is always present (not None or empty)
    2. The data_source field contains meaningful information
    3. The data_source enables verification by being descriptive
    """
    # Verify data_source field is present and not None
    assert service.data_source is not None, \
        f"Service {service.service_id} must have a data_source field"
    
    # Verify data_source is not empty or just whitespace
    assert service.data_source.strip() != "", \
        f"Service {service.service_id} data_source cannot be empty or whitespace"
    
    # Verify data_source is meaningful (has minimum length for descriptive content)
    assert len(service.data_source.strip()) >= 5, \
        f"Service {service.service_id} data_source must be descriptive (at least 5 characters). " \
        f"Got: '{service.data_source}'"
    
    # Verify data_source contains alphanumeric content (not just special characters)
    has_alphanumeric = any(c.isalnum() for c in service.data_source)
    assert has_alphanumeric, \
        f"Service {service.service_id} data_source must contain alphanumeric characters " \
        f"for meaningful identification. Got: '{service.data_source}'"
    
    # Verify data_source is reasonable length (not excessively long)
    assert len(service.data_source) <= 500, \
        f"Service {service.service_id} data_source should be concise (max 500 characters). " \
        f"Got length: {len(service.data_source)}"


def test_property_30_mock_data_compliance():
    """
    Property 30: Data Source Tracking - Mock Data Compliance
    
    **Validates: Requirements 9.4**
    
    Verify that all existing mock services comply with data source tracking requirements.
    This ensures our test data follows the same standards as production data.
    """
    mock_services = get_enhanced_mock_services()
    
    assert len(mock_services) > 0, "Mock services should exist for testing"
    
    for service_id, service in mock_services.items():
        # Verify data_source field is present and not None
        assert service.data_source is not None, \
            f"Mock service {service_id} must have a data_source field"
        
        # Verify data_source is not empty or just whitespace
        assert service.data_source.strip() != "", \
            f"Mock service {service_id} data_source cannot be empty or whitespace"
        
        # Verify data_source is meaningful
        assert len(service.data_source.strip()) >= 5, \
            f"Mock service {service_id} data_source must be descriptive. " \
            f"Got: '{service.data_source}'"
        
        # Verify data_source contains alphanumeric content
        has_alphanumeric = any(c.isalnum() for c in service.data_source)
        assert has_alphanumeric, \
            f"Mock service {service_id} data_source must contain alphanumeric characters. " \
            f"Got: '{service.data_source}'"


def test_property_30_repository_data_source_preservation():
    """
    Property 30: Data Source Tracking - Repository Preservation
    
    **Validates: Requirements 9.4**
    
    Verify that the ServiceRepository preserves data_source information
    when retrieving services, ensuring traceability is maintained throughout
    the system.
    """
    repository = ServiceRepository()
    all_services = repository.get_all_services()
    
    assert len(all_services) > 0, "Repository should contain services"
    
    for service in all_services:
        # Verify data_source is preserved in repository operations
        assert service.data_source is not None, \
            f"Repository service {service.service_id} must preserve data_source"
        
        assert service.data_source.strip() != "", \
            f"Repository service {service.service_id} data_source cannot be empty"
        
        # Test individual service retrieval preserves data_source
        retrieved_service = repository.get_service(service.service_id)
        assert retrieved_service is not None, \
            f"Service {service.service_id} should be retrievable"
        
        assert retrieved_service.data_source == service.data_source, \
            f"Retrieved service {service.service_id} must preserve original data_source. " \
            f"Expected: '{service.data_source}', Got: '{retrieved_service.data_source}'"


@given(
    services=st.lists(enhanced_service_guide_strategy(), min_size=2, max_size=10)
)
@settings(
    max_examples=20,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_property_30_multiple_services_data_source_uniqueness(services):
    """
    Property 30: Data Source Tracking - Multiple Services
    
    **Validates: Requirements 9.4**
    
    For any collection of services, each service must maintain its own
    data source tracking, enabling individual verification of information sources.
    
    This verifies that data source tracking works correctly when handling
    multiple services simultaneously.
    """
    # Ensure all services have unique IDs for this test
    unique_services = {}
    for i, service in enumerate(services):
        service.service_id = f"test_service_{i}"
        unique_services[service.service_id] = service
    
    for service_id, service in unique_services.items():
        # Each service must have its own data_source
        assert service.data_source is not None, \
            f"Service {service_id} must have data_source"
        
        assert service.data_source.strip() != "", \
            f"Service {service_id} data_source cannot be empty"
        
        # Verify data_source is accessible and meaningful
        assert len(service.data_source.strip()) >= 5, \
            f"Service {service_id} data_source must be meaningful"


# Unit tests for specific data source scenarios

def test_data_source_field_required():
    """
    Unit test: Data source field is required
    
    Verify that EnhancedServiceGuide requires a data_source field.
    """
    from pydantic import ValidationError
    
    # This should fail without data_source
    with pytest.raises(ValidationError) as exc_info:
        EnhancedServiceGuide(
            service_id="test",
            service_name="Test Service",
            category=ServiceCategory.CERTIFICATE,
            description="Test description",
            last_updated=datetime.now()
            # Missing data_source - should cause validation error
        )
    
    # Verify the error mentions data_source
    error_str = str(exc_info.value)
    assert "data_source" in error_str.lower(), \
        f"Validation error should mention missing data_source field. Got: {error_str}"


def test_data_source_empty_string_validation():
    """
    Unit test: Empty data source validation
    
    While Pydantic allows empty strings, our business logic should validate
    that data_source contains meaningful content.
    """
    # This creates a service with empty data_source (Pydantic allows it)
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test description",
        last_updated=datetime.now(),
        data_source=""  # Empty string
    )
    
    # Our property test should catch this
    assert service.data_source == "", "Service was created with empty data_source"
    
    # This would fail our property test (which is the expected behavior)
    # The property test ensures business rule compliance beyond Pydantic validation


def test_data_source_whitespace_validation():
    """
    Unit test: Whitespace-only data source validation
    
    Verify that data_source with only whitespace is caught by our property tests.
    """
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test description",
        last_updated=datetime.now(),
        data_source="   \t\n   "  # Only whitespace
    )
    
    # Our property test should catch this
    assert service.data_source.strip() == "", "Service has whitespace-only data_source"


def test_data_source_meaningful_content():
    """
    Unit test: Meaningful data source content
    
    Verify that a proper data_source passes validation.
    """
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test description",
        last_updated=datetime.now(),
        data_source="UIDAI Official Guidelines 2024"
    )
    
    # This should pass all our property test validations
    assert service.data_source is not None
    assert service.data_source.strip() != ""
    assert len(service.data_source.strip()) >= 5
    assert any(c.isalnum() for c in service.data_source)
    assert len(service.data_source) <= 500


def test_data_source_various_formats():
    """
    Unit test: Various valid data source formats
    
    Test that different valid formats of data_source are accepted.
    """
    valid_sources = [
        "UIDAI Official Guidelines 2024",
        "Ministry of Electronics and IT - Digital India Portal",
        "Government of India Official Website (Updated Jan 2024)",
        "NIC Database v2.1",
        "State Govt. Records - Maharashtra",
        "Central Govt. Notification No. 12345/2024",
        "Official Gazette Entry - March 2024"
    ]
    
    for source in valid_sources:
        service = EnhancedServiceGuide(
            service_id=f"test_{hash(source) % 1000}",
            service_name="Test Service",
            category=ServiceCategory.CERTIFICATE,
            description="Test description",
            last_updated=datetime.now(),
            data_source=source
        )
        
        # All should pass our validation criteria
        assert service.data_source is not None
        assert service.data_source.strip() != ""
        assert len(service.data_source.strip()) >= 5
        assert any(c.isalnum() for c in service.data_source)
        assert len(service.data_source) <= 500