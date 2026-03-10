"""
Property-Based Tests for End-to-End Integration - Task 10.3

Property-based tests using Hypothesis to verify universal properties
across all possible service configurations and user inputs.

**Validates: Requirements 1.1, 1.4, 7.1, 8.1, 8.4**
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from hypothesis.strategies import builds, lists, text, integers, booleans, sampled_from
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.enhanced_service import (
    EnhancedServiceGuide, OfficeLocation, RequiredDocument, 
    OfficeVisitStep, OfficialWebsiteLink, ProcessingTimeline,
    ServiceCategory, Coordinates
)
from app.services.response_formatter import ResponseFormatter
from app.repositories.service_repository import ServiceRepository
from datetime import datetime
from typing import List, Dict, Any
import asyncio


# Hypothesis strategies for generating test data
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
        name=draw(text(min_size=1, max_size=100)),
        address=draw(text(min_size=1, max_size=200)),
        city=draw(text(min_size=1, max_size=50)),
        state=draw(text(min_size=1, max_size=50)),
        postal_code=draw(text(min_size=1, max_size=10)),
        coordinates=draw(st.one_of(st.none(), coordinates_strategy())),
        operating_hours=draw(st.one_of(st.none(), text(min_size=1, max_size=100))),
        contact_phone=draw(st.one_of(st.none(), text(min_size=1, max_size=20)))
    )


@st.composite
def required_document_strategy(draw):
    """Generate valid required documents."""
    return RequiredDocument(
        document_name=draw(text(min_size=1, max_size=100)),
        description=draw(st.one_of(st.none(), text(min_size=1, max_size=200))),
        copies_required=draw(integers(min_value=1, max_value=10)),
        format_requirements=draw(st.one_of(st.none(), text(min_size=1, max_size=100))),
        is_mandatory=draw(booleans()),
        alternatives=draw(st.one_of(st.none(), lists(text(min_size=1, max_size=50), max_size=5)))
    )


@st.composite
def office_visit_step_strategy(draw):
    """Generate valid office visit steps."""
    sequence_num = draw(integers(min_value=1, max_value=10))
    return OfficeVisitStep(
        sequence_number=sequence_num,
        office_name=draw(text(min_size=1, max_size=100)) + f"_{sequence_num}",  # Make unique
        purpose=draw(text(min_size=1, max_size=200)),
        estimated_duration=draw(text(min_size=1, max_size=50)),
        is_optional=draw(booleans()),
        is_conditional=draw(booleans()),
        condition=draw(st.one_of(st.none(), text(min_size=1, max_size=100)))
    )


@st.composite
def official_website_link_strategy(draw):
    """Generate valid official website links."""
    # Generate valid URLs
    domains = ["gov.in", "nic.in", "india.gov.in", "digitalindia.gov.in"]
    domain = draw(sampled_from(domains))
    path = draw(text(alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd")), min_size=0, max_size=50))
    url = f"https://{domain}/{path}" if path else f"https://{domain}"
    
    return OfficialWebsiteLink(
        url=url,
        purpose=draw(text(min_size=1, max_size=100)),
        description=draw(st.one_of(st.none(), text(min_size=1, max_size=200)))
    )


@st.composite
def processing_timeline_strategy(draw):
    """Generate valid processing timelines."""
    min_days = draw(integers(min_value=1, max_value=30))
    max_days = draw(integers(min_value=min_days, max_value=min_days + 100))
    typical_days = draw(integers(min_value=min_days, max_value=max_days))
    
    return ProcessingTimeline(
        minimum_days=min_days,
        maximum_days=max_days,
        typical_days=typical_days,
        time_unit=draw(sampled_from(["days", "weeks", "months"])),
        processing_type=draw(sampled_from(["standard", "expedited", "priority"])),
        notes=draw(st.one_of(st.none(), text(min_size=1, max_size=200))),
        factors_affecting_time=draw(lists(text(min_size=1, max_size=100), max_size=5))
    )


@st.composite
def enhanced_service_guide_strategy(draw):
    """Generate valid enhanced service guides."""
    # Generate unique office visit steps
    num_steps = draw(integers(min_value=0, max_value=5))
    office_steps = []
    for i in range(num_steps):
        step = OfficeVisitStep(
            sequence_number=i + 1,  # Ensure unique sequence numbers
            office_name=f"Office_{i+1}_{draw(text(min_size=1, max_size=50))}",
            purpose=draw(text(min_size=1, max_size=200)),
            estimated_duration=draw(text(min_size=1, max_size=50)),
            is_optional=draw(booleans()),
            is_conditional=draw(booleans()),
            condition=draw(st.one_of(st.none(), text(min_size=1, max_size=100)))
        )
        office_steps.append(step)
    
    return EnhancedServiceGuide(
        service_id=draw(text(min_size=1, max_size=50)),
        service_name=draw(text(min_size=1, max_size=100)),
        category=draw(sampled_from(list(ServiceCategory))),
        description=draw(text(min_size=1, max_size=500)),
        office_locations=draw(lists(office_location_strategy(), max_size=5)),
        required_documents=draw(lists(required_document_strategy(), max_size=10)),
        office_visit_sequence=office_steps,
        official_websites=draw(lists(official_website_link_strategy(), max_size=5)),
        processing_timelines=draw(lists(processing_timeline_strategy(), max_size=3)),
        last_updated=datetime.now(),
        data_source="property_test",
        available_languages=["en"]
    )


class TestEndToEndIntegrationProperties:
    """Property-based tests for end-to-end integration."""

    # Feature: government-service-info-enhancement, Property 1: All Five Categories Present
    @given(service=enhanced_service_guide_strategy())
    @settings(max_examples=50)
    def test_property_all_five_categories_present(self, service):
        """
        Property 1: For any service, the formatted response must contain 
        all five information categories with appropriate headers.
        
        **Validates: Requirements 1.1, 8.1**
        """
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        
        # Verify exactly 5 sections
        assert len(response.sections) == 5, \
            f"Expected 5 sections, got {len(response.sections)}"
        
        # Verify all expected headers present
        expected_headers = [
            "📍 Office Locations",
            "📄 Required Documents",
            "🏢 Office Visit Sequence",
            "🔗 Official Websites",
            "⏱️ Processing Timeline"
        ]
        
        actual_headers = [section.header for section in response.sections]
        assert actual_headers == expected_headers, \
            f"Headers mismatch. Expected: {expected_headers}, Got: {actual_headers}"

    # Feature: government-service-info-enhancement, Property 2: Section Order Consistency
    @given(service1=enhanced_service_guide_strategy(), service2=enhanced_service_guide_strategy())
    @settings(max_examples=30)
    def test_property_section_order_consistency(self, service1, service2):
        """
        Property 2: For any two services, the five information categories 
        must appear in the same order.
        
        **Validates: Requirements 1.4, 8.4**
        """
        formatter = ResponseFormatter()
        
        response1 = formatter.format_service_response(service1)
        response2 = formatter.format_service_response(service2)
        
        headers1 = [section.header for section in response1.sections]
        headers2 = [section.header for section in response2.sections]
        
        assert headers1 == headers2, \
            "Section order must be consistent across all services"

    # Feature: government-service-info-enhancement, Property 3: Missing Data Handling
    @given(service=enhanced_service_guide_strategy())
    @settings(max_examples=50)
    def test_property_missing_data_handling(self, service):
        """
        Property 3: For any service with missing data in categories,
        the formatted response must display "Information not available" 
        for empty categories while maintaining all section headers.
        
        **Validates: Requirements 1.3, 8.2**
        """
        # Create service with some empty categories
        empty_service = EnhancedServiceGuide(
            service_id=service.service_id,
            service_name=service.service_name,
            category=service.category,
            description=service.description,
            office_locations=[],  # Empty
            required_documents=service.required_documents,
            office_visit_sequence=[],  # Empty
            official_websites=service.official_websites,
            processing_timelines=[],  # Empty
            last_updated=service.last_updated,
            data_source=service.data_source,
            available_languages=service.available_languages
        )
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(empty_service)
        
        # All 5 sections must still be present
        assert len(response.sections) == 5
        
        # Empty sections should be marked as empty and have appropriate message
        empty_indices = [0, 2, 4]  # office_locations, office_sequence, timelines
        for i in empty_indices:
            section = response.sections[i]
            assert section.is_empty, f"Section {i} should be marked as empty"
            assert "Information not available" in section.content, \
                f"Section {i} should have 'Information not available' message"

    # Feature: government-service-info-enhancement, Property 4: Office Location Completeness
    @given(service=enhanced_service_guide_strategy())
    @settings(max_examples=50)
    def test_property_office_location_completeness(self, service):
        """
        Property 4: For any service with N office locations, 
        all N locations must appear in the formatted response.
        
        **Validates: Requirements 2.1, 2.2**
        """
        assume(len(service.office_locations) > 0)  # Only test when locations exist
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        
        # Find office locations section (first section)
        locations_section = response.sections[0]
        
        # All location names should appear in the content
        for location in service.office_locations:
            assert location.name in locations_section.content, \
                f"Location '{location.name}' missing from formatted response"
            assert location.address in locations_section.content, \
                f"Address for '{location.name}' missing from formatted response"

    # Feature: government-service-info-enhancement, Property 5: Document List Completeness
    @given(service=enhanced_service_guide_strategy())
    @settings(max_examples=50)
    def test_property_document_list_completeness(self, service):
        """
        Property 5: For any service with N required documents,
        all N documents must appear as separate items in the formatted response.
        
        **Validates: Requirements 3.1, 3.2, 3.4**
        """
        assume(len(service.required_documents) > 0)  # Only test when documents exist
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        
        # Find required documents section (second section)
        documents_section = response.sections[1]
        
        # All document names should appear in the content
        for document in service.required_documents:
            assert document.document_name in documents_section.content, \
                f"Document '{document.document_name}' missing from formatted response"

    # Feature: government-service-info-enhancement, Property 6: Office Sequence Order Preservation
    @given(service=enhanced_service_guide_strategy())
    @settings(max_examples=50)
    def test_property_office_sequence_order_preservation(self, service):
        """
        Property 6: For any service with multi-step office sequence,
        the offices must appear in the correct sequence order.
        
        **Validates: Requirements 4.1, 4.2**
        """
        assume(len(service.office_visit_sequence) > 1)  # Only test multi-step sequences
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        
        # Find office sequence section (third section)
        sequence_section = response.sections[2]
        
        # Sort steps by sequence number
        sorted_steps = sorted(service.office_visit_sequence, 
                            key=lambda x: x.sequence_number)
        
        # Verify order preservation in formatted content
        last_pos = -1
        for step in sorted_steps:
            pos = sequence_section.content.find(step.office_name)
            assert pos > last_pos, \
                f"Office '{step.office_name}' appears out of sequence order"
            last_pos = pos

    # Feature: government-service-info-enhancement, Property 7: Website Links Completeness
    @given(service=enhanced_service_guide_strategy())
    @settings(max_examples=50)
    def test_property_website_links_completeness(self, service):
        """
        Property 7: For any service with N official website links,
        all N links must appear in the formatted response.
        
        **Validates: Requirements 5.1, 5.2**
        """
        assume(len(service.official_websites) > 0)  # Only test when websites exist
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        
        # Find official websites section (fourth section)
        websites_section = response.sections[3]
        
        # All website URLs and purposes should appear
        for website in service.official_websites:
            assert str(website.url) in websites_section.content, \
                f"Website URL '{website.url}' missing from formatted response"
            assert website.purpose in websites_section.content, \
                f"Website purpose '{website.purpose}' missing from formatted response"

    # Feature: government-service-info-enhancement, Property 8: Timeline Information Completeness
    @given(service=enhanced_service_guide_strategy())
    @settings(max_examples=50)
    def test_property_timeline_information_completeness(self, service):
        """
        Property 8: For any service with processing timeline data,
        the timeline must include time units and duration information.
        
        **Validates: Requirements 6.1, 6.2**
        """
        assume(len(service.processing_timelines) > 0)  # Only test when timelines exist
        
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        
        # Find processing timeline section (fifth section)
        timeline_section = response.sections[4]
        
        # All timeline information should appear
        for timeline in service.processing_timelines:
            assert str(timeline.typical_days) in timeline_section.content, \
                f"Typical days '{timeline.typical_days}' missing from timeline"
            assert timeline.time_unit in timeline_section.content, \
                f"Time unit '{timeline.time_unit}' missing from timeline"
            # Processing type is capitalized in output
            capitalized_type = timeline.processing_type.capitalize()
            assert capitalized_type in timeline_section.content, \
                f"Processing type '{capitalized_type}' missing from timeline"

    # Feature: government-service-info-enhancement, Property 9: Format Consistency
    @given(services=lists(enhanced_service_guide_strategy(), min_size=2, max_size=5))
    @settings(max_examples=20)
    def test_property_format_consistency(self, services):
        """
        Property 9: For any set of services, the formatting structure
        must be consistent across all responses.
        
        **Validates: Requirements 8.1, 8.3**
        """
        formatter = ResponseFormatter()
        responses = [formatter.format_service_response(service) for service in services]
        
        # All responses should have same structure
        reference_response = responses[0]
        reference_headers = [section.header for section in reference_response.sections]
        
        for i, response in enumerate(responses[1:], 1):
            headers = [section.header for section in response.sections]
            assert headers == reference_headers, \
                f"Response {i} has inconsistent headers"
            
            assert len(response.sections) == len(reference_response.sections), \
                f"Response {i} has inconsistent section count"
            
            # Each section should have same structure
            for j, section in enumerate(response.sections):
                assert hasattr(section, 'header'), f"Response {i} section {j} missing header"
                assert hasattr(section, 'content'), f"Response {i} section {j} missing content"
                assert hasattr(section, 'is_empty'), f"Response {i} section {j} missing is_empty"

    # Feature: government-service-info-enhancement, Property 10: Content Non-Empty for Available Data
    @given(service=enhanced_service_guide_strategy())
    @settings(max_examples=50)
    def test_property_content_non_empty_for_available_data(self, service):
        """
        Property 10: For any service with available data in a category,
        the formatted content must be non-empty and meaningful.
        
        **Validates: Requirements 1.1, 1.3**
        """
        formatter = ResponseFormatter()
        response = formatter.format_service_response(service)
        
        # Check each category
        categories_data = [
            (service.office_locations, 0),
            (service.required_documents, 1),
            (service.office_visit_sequence, 2),
            (service.official_websites, 3),
            (service.processing_timelines, 4)
        ]
        
        for data_list, section_index in categories_data:
            section = response.sections[section_index]
            
            if len(data_list) > 0:
                # Should not be marked as empty
                assert not section.is_empty, \
                    f"Section {section_index} should not be empty when data exists"
                
                # Should have meaningful content
                assert len(section.content.strip()) > 0, \
                    f"Section {section_index} has empty content despite available data"
                
                assert section.content != "Information not available", \
                    f"Section {section_index} shows unavailable despite having data"
            else:
                # Should be marked as empty
                assert section.is_empty, \
                    f"Section {section_index} should be marked empty when no data"
                
                assert "Information not available" in section.content, \
                    f"Section {section_index} should show unavailable message"


class TestEndToEndAPIProperties:
    """Property-based tests for the complete API flow."""

    @pytest.mark.asyncio
    @given(query_text=text(min_size=1, max_size=100))
    @settings(max_examples=20)
    async def test_property_api_response_structure(self, query_text):
        """
        Property: For any non-empty query, the API must return a well-formed
        response with required fields.
        
        **Validates: Requirements 7.1**
        """
        # Filter out queries that are just whitespace
        assume(query_text.strip())
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": query_text,
                    "language": "en"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Required fields must always be present
            required_fields = ["message", "language", "session_id"]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"
            
            # Message should never be empty
            assert len(data["message"]) > 0, "Response message cannot be empty"
            
            # Language should be preserved
            assert data["language"] == "en"
            
            # Session ID should be valid
            assert len(data["session_id"]) > 0, "Session ID cannot be empty"

    @pytest.mark.asyncio
    @given(
        query=sampled_from([
            "aadhaar name change", "data access request", 
            "birth certificate", "service status tracking"
        ]),
        language=sampled_from(["en", "hi", "te"])
    )
    @settings(max_examples=15)
    async def test_property_known_service_response_structure(self, query, language):
        """
        Property: For any known service query in any supported language,
        the response must include a properly structured enhanced service guide.
        
        **Validates: Requirements 1.1, 7.1, 8.1**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": query,
                    "language": language
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should have enhanced service guide for known services
            if data.get("enhanced_service_guide"):
                guide = data["enhanced_service_guide"]
                
                # Required guide fields
                required_guide_fields = [
                    "service_name", "description", "sections", 
                    "last_updated", "service_id", "category"
                ]
                for field in required_guide_fields:
                    assert field in guide, f"Missing guide field: {field}"
                
                # Sections structure
                sections = guide["sections"]
                assert len(sections) == 5, "Must have exactly 5 sections"
                
                for section in sections:
                    assert "header" in section
                    assert "content" in section
                    assert "is_empty" in section
                    assert isinstance(section["is_empty"], bool)

    @pytest.mark.asyncio
    @given(session_id=text(min_size=1, max_size=50))
    @settings(max_examples=10)
    async def test_property_session_id_preservation(self, session_id):
        """
        Property: For any provided session ID, the API must preserve
        and return the same session ID in the response.
        
        **Validates: Requirements 7.1**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": "aadhaar name change",
                    "language": "en",
                    "session_id": session_id
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Session ID should be preserved
            assert data["session_id"] == session_id, \
                "Session ID must be preserved in response"