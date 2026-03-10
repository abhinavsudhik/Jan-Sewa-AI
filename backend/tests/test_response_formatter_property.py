"""
Property Tests for ResponseFormatter

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 8.1, 8.2, 8.4**

This module contains property-based tests for the ResponseFormatter service to ensure
it consistently structures service information into the standardized format with all
five categories present and properly ordered.

Property Tests:
- Property 1: All Five Categories Present - Verify all categories appear in every response
- Property 2: Section Order Consistency - Verify consistent category ordering
- Property 3: Section Headers Present - Verify all headers are labeled
- Property 4: Missing Data Handling - Verify "Information not available" for empty categories

Requirements Reference:
- Requirement 1.1: Structured Service Response Format with all five information categories
- Requirement 1.2: Organize information into clearly labeled sections with consistent formatting
- Requirement 1.3: Indicate "Information not available" for unavailable categories
- Requirement 1.4: Maintain same section order for all government service queries
- Requirement 8.1: Apply standardized format to all government service responses
- Requirement 8.2: Display category header with appropriate message when information is missing
- Requirement 8.4: Five information categories appear in same order and format
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase
from datetime import datetime, timedelta
from typing import List, Optional

from app.services.response_formatter import ResponseFormatter, ResponseSection, FormattedServiceResponse
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
    # Generate more realistic office names (no whitespace-only strings)
    name = draw(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=("Cc", "Cf", "Cs"))))
    # Ensure name is not just whitespace
    if not name.strip():
        name = "Office"
    
    return OfficeLocation(
        name=name,
        address=draw(st.text(min_size=1, max_size=200)),
        city=draw(st.text(min_size=1, max_size=50)),
        state=draw(st.text(min_size=1, max_size=50)),
        postal_code=draw(st.text(min_size=1, max_size=20)),
        coordinates=draw(st.one_of(st.none(), coordinates_strategy())),
        operating_hours=draw(st.one_of(st.none(), st.text(min_size=1, max_size=100))),
        contact_phone=draw(st.one_of(st.none(), st.text(min_size=1, max_size=20)))
    )


@st.composite
def required_document_strategy(draw):
    """Generate valid required documents."""
    # Generate document names without bullet characters or problematic characters
    document_name = draw(st.text(
        min_size=1, 
        max_size=100,
        alphabet=st.characters(
            blacklist_categories=("Cc", "Cf", "Cs"),
            blacklist_characters="•"
        )
    ))
    # Ensure name is not just whitespace
    if not document_name.strip():
        document_name = "Document"
    
    # Generate format requirements without bullet characters
    format_requirements = draw(st.one_of(
        st.none(), 
        st.text(
            min_size=1, 
            max_size=100,
            alphabet=st.characters(
                blacklist_categories=("Cc", "Cf", "Cs"),
                blacklist_characters="•"
            )
        )
    ))
    
    return RequiredDocument(
        document_name=document_name,
        description=draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        copies_required=draw(st.integers(min_value=1, max_value=10)),
        format_requirements=format_requirements,
        is_mandatory=draw(st.booleans()),
        alternatives=draw(st.one_of(st.none(), st.lists(st.text(min_size=1, max_size=50), max_size=5)))
    )


@st.composite
def office_visit_step_strategy(draw):
    """Generate valid office visit steps."""
    # Generate more realistic office names to avoid duplicates
    office_names = [
        "District Collectorate", "Verification Office", "Collection Center",
        "Main Office", "Registration Office", "Document Center",
        "Service Center", "Administrative Office", "Processing Center"
    ]
    
    return OfficeVisitStep(
        sequence_number=draw(st.integers(min_value=1, max_value=10)),
        office_name=draw(st.sampled_from(office_names)),
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
    protocols = ["https", "http"]
    domains = ["gov.in", "nic.in", "example.gov.in", "portal.gov.in"]
    
    protocol = draw(st.sampled_from(protocols))
    domain = draw(st.sampled_from(domains))
    path = draw(st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc")), min_size=0, max_size=50))
    
    url = f"{protocol}://{domain}"
    if path:
        url += f"/{path}"
    
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
        processing_type=draw(st.sampled_from(["standard", "expedited", "priority"])),
        notes=draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        factors_affecting_time=draw(st.lists(st.text(min_size=1, max_size=100), max_size=5))
    )


@st.composite
def enhanced_service_guide_strategy(draw):
    """Generate valid EnhancedServiceGuide instances."""
    return EnhancedServiceGuide(
        service_id=draw(st.text(min_size=1, max_size=50)),
        service_name=draw(st.text(min_size=1, max_size=100)),
        category=draw(st.sampled_from(ServiceCategory)),
        description=draw(st.text(min_size=1, max_size=500)),
        office_locations=draw(st.lists(office_location_strategy(), max_size=5)),
        required_documents=draw(st.lists(required_document_strategy(), max_size=10)),
        office_visit_sequence=draw(st.lists(office_visit_step_strategy(), max_size=5)),
        official_websites=draw(st.lists(official_website_link_strategy(), max_size=5)),
        processing_timelines=draw(st.lists(processing_timeline_strategy(), max_size=3)),
        last_updated=draw(st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2024, 12, 31)
        )),
        data_source=draw(st.text(min_size=1, max_size=100)),
        available_languages=draw(st.lists(st.sampled_from(["en", "hi", "ta", "te", "bn"]), min_size=1, max_size=3))
    )


# Property Tests

@settings(max_examples=100, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(service=enhanced_service_guide_strategy())
def test_property_1_all_five_categories_present(service):
    """
    **Validates: Requirements 1.1, 8.1**
    
    Property 1: All Five Categories Present
    
    For any service query that is successfully processed, the formatted response must 
    contain all five information categories (office locations, required documents, 
    office visit sequence, official websites, processing timeline) with appropriate 
    headers, regardless of whether data is available for each category.
    """
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Verify exactly 5 sections are present
    assert len(response.sections) == 5, f"Expected 5 sections, got {len(response.sections)}"
    
    # Verify all expected category headers are present
    expected_headers = [
        "📍 Office Locations",
        "📄 Required Documents", 
        "🏢 Office Visit Sequence",
        "🔗 Official Websites",
        "⏱️ Processing Timeline"
    ]
    
    actual_headers = [section.header for section in response.sections]
    assert actual_headers == expected_headers, \
        f"Expected headers {expected_headers}, got {actual_headers}"


@settings(max_examples=100, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(service1=enhanced_service_guide_strategy(), service2=enhanced_service_guide_strategy())
def test_property_2_section_order_consistency(service1, service2):
    """
    **Validates: Requirements 1.4, 8.4**
    
    Property 2: Section Order Consistency
    
    For any two service responses, the five information categories must appear in 
    the same order: office locations, required documents, office visit sequence, 
    official websites, processing timeline.
    """
    formatter = ResponseFormatter()
    
    response1 = formatter.format_service_response(service1)
    response2 = formatter.format_service_response(service2)
    
    # Extract headers from both responses
    headers1 = [section.header for section in response1.sections]
    headers2 = [section.header for section in response2.sections]
    
    # Verify headers are identical in order
    assert headers1 == headers2, \
        f"Section order inconsistent: Service1 headers {headers1}, Service2 headers {headers2}"
    
    # Verify the specific expected order
    expected_order = [
        "📍 Office Locations",
        "📄 Required Documents",
        "🏢 Office Visit Sequence", 
        "🔗 Official Websites",
        "⏱️ Processing Timeline"
    ]
    
    assert headers1 == expected_order, \
        f"Headers not in expected order. Expected {expected_order}, got {headers1}"


@settings(max_examples=100, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(service=enhanced_service_guide_strategy())
def test_property_3_section_headers_present(service):
    """
    **Validates: Requirements 1.2**
    
    Property 3: Section Headers Present
    
    For any formatted service response, each of the five information categories 
    must have a clearly labeled section header.
    """
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Verify all sections have non-empty headers
    for i, section in enumerate(response.sections):
        assert section.header is not None, f"Section {i} has None header"
        assert section.header.strip() != "", f"Section {i} has empty header"
        assert len(section.header) > 0, f"Section {i} has zero-length header"
    
    # Verify headers contain expected emoji/text patterns
    expected_patterns = [
        ("📍", "Office Locations"),
        ("📄", "Required Documents"),
        ("🏢", "Office Visit Sequence"),
        ("🔗", "Official Websites"),
        ("⏱️", "Processing Timeline")
    ]
    
    for i, (emoji, text) in enumerate(expected_patterns):
        section = response.sections[i]
        assert emoji in section.header, f"Section {i} header missing emoji {emoji}: {section.header}"
        assert text in section.header, f"Section {i} header missing text {text}: {section.header}"


@settings(max_examples=100, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(service=enhanced_service_guide_strategy())
def test_property_4_missing_data_handling(service):
    """
    **Validates: Requirements 1.3, 8.2**
    
    Property 4: Missing Data Handling
    
    For any service with missing data in one or more categories, the formatted 
    response must display the category header with "Information not available" 
    message for each missing category.
    """
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Check each category for proper handling of empty data
    categories_data = [
        (service.office_locations, "office locations"),
        (service.required_documents, "required documents"),
        (service.office_visit_sequence, "office visit sequence"),
        (service.official_websites, "official websites"),
        (service.processing_timelines, "processing timelines")
    ]
    
    for i, (category_data, category_name) in enumerate(categories_data):
        section = response.sections[i]
        
        if not category_data or len(category_data) == 0:
            # Category is empty - should show "Information not available"
            assert section.is_empty, \
                f"Section {i} ({category_name}) should be marked as empty when data is missing"
            assert section.content == "Information not available", \
                f"Section {i} ({category_name}) should show 'Information not available' when empty, got: {section.content}"
        else:
            # Category has data - should not be marked as empty
            assert not section.is_empty, \
                f"Section {i} ({category_name}) should not be marked as empty when data is present"
            assert section.content != "Information not available", \
                f"Section {i} ({category_name}) should not show 'Information not available' when data is present"


# Property Tests for Office Location Formatting (Task 2.4)

@settings(max_examples=100, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(service=enhanced_service_guide_strategy())
def test_property_5_office_location_completeness(service):
    """
    **Validates: Requirements 2.1, 2.2**
    
    Property 5: Office Location Completeness
    
    For any service with N office locations, the formatted response must display 
    all N locations with complete address details. When multiple locations exist,
    all must be listed.
    """
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Get the office locations section (first section)
    office_section = response.sections[0]
    assert office_section.header == "📍 Office Locations"
    
    if not service.office_locations or len(service.office_locations) == 0:
        # No locations - should show "Information not available"
        assert office_section.is_empty
        assert office_section.content == "Information not available"
    else:
        # Has locations - should display all of them
        assert not office_section.is_empty
        assert office_section.content != "Information not available"
        
        # Count bullet points to verify all locations are displayed
        bullet_count = office_section.content.count("•")
        assert bullet_count == len(service.office_locations), \
            f"Expected {len(service.office_locations)} locations, found {bullet_count} bullet points"
        
        # Verify each location's required fields are present
        for location in service.office_locations:
            # Office name should be present
            assert location.name in office_section.content, \
                f"Office name '{location.name}' not found in formatted output"
            
            # Complete address should be present
            expected_address = f"{location.address}, {location.city}, {location.state} {location.postal_code}"
            assert location.address in office_section.content, \
                f"Address '{location.address}' not found in formatted output"
            assert location.city in office_section.content, \
                f"City '{location.city}' not found in formatted output"
            assert location.state in office_section.content, \
                f"State '{location.state}' not found in formatted output"
            assert location.postal_code in office_section.content, \
                f"Postal code '{location.postal_code}' not found in formatted output"


@settings(max_examples=100, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(service=enhanced_service_guide_strategy())
def test_property_6_coordinates_inclusion(service):
    """
    **Validates: Requirements 2.3**
    
    Property 6: Coordinates Inclusion
    
    For any office location with geographic coordinates available, the formatted 
    response must include the coordinates. When coordinates are not available,
    they should not appear in the output.
    """
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Get the office locations section
    office_section = response.sections[0]
    
    if not service.office_locations or len(service.office_locations) == 0:
        # No locations to check
        return
    
    for location in service.office_locations:
        if location.coordinates:
            # Coordinates available - should be included
            coord_text = f"Coordinates: {location.coordinates.latitude}, {location.coordinates.longitude}"
            assert coord_text in office_section.content, \
                f"Coordinates for '{location.name}' not found in output. Expected: {coord_text}"
            
            # Verify individual coordinate values are present
            assert str(location.coordinates.latitude) in office_section.content, \
                f"Latitude {location.coordinates.latitude} not found in output"
            assert str(location.coordinates.longitude) in office_section.content, \
                f"Longitude {location.coordinates.longitude} not found in output"
        else:
            # No coordinates - should not have coordinate text for this location
            # We can't easily verify absence without more complex parsing,
            # but we can check that if "Coordinates:" appears, it's for other locations
            pass


@settings(max_examples=100, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(service=enhanced_service_guide_strategy())
def test_property_7_office_location_list_format(service):
    """
    **Validates: Requirements 2.4**
    
    Property 7: Office Location List Format
    
    For any service with office locations, the formatted response must display 
    locations in list format with each location on a separate line, using 
    bullet points and proper indentation.
    """
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Get the office locations section
    office_section = response.sections[0]
    
    if not service.office_locations or len(service.office_locations) == 0:
        # No locations to check formatting
        return
    
    # Verify list formatting structure
    content = office_section.content
    
    # Each location should start with a bullet point
    bullet_count = content.count("•")
    assert bullet_count == len(service.office_locations), \
        f"Expected {len(service.office_locations)} bullet points, found {bullet_count}"
    
    # Verify proper line structure
    lines = content.split('\n')
    bullet_lines = [line for line in lines if line.strip().startswith("•")]
    assert len(bullet_lines) == len(service.office_locations), \
        f"Expected {len(service.office_locations)} bullet lines, found {len(bullet_lines)}"
    
    # Verify each bullet line contains the office name
    for location in service.office_locations:
        found_bullet_line = False
        for line in bullet_lines:
            if location.name.strip() in line:
                found_bullet_line = True
                # Verify bullet line format: "• {office_name}"
                expected_start = f"• {location.name.strip()}"
                assert line.strip().startswith(expected_start), \
                    f"Bullet line should start with '{expected_start}', got: {line.strip()}"
                break
        assert found_bullet_line, \
            f"No bullet line found for office '{location.name.strip()}'"
    
    # Verify indentation for sub-items (address, coordinates, etc.)
    indented_lines = [line for line in lines if line.startswith("  ") and not line.strip().startswith("•")]
    
    # Should have at least one indented line per location (for address)
    assert len(indented_lines) >= len(service.office_locations), \
        f"Expected at least {len(service.office_locations)} indented lines for addresses, found {len(indented_lines)}"
    
    # If multiple locations, verify they are separated by blank lines
    if len(service.office_locations) > 1:
        # Should have blank lines between location blocks
        blank_lines = [i for i, line in enumerate(lines) if line.strip() == ""]
        # Should have at least (N-1) blank lines for N locations
        assert len(blank_lines) >= len(service.office_locations) - 1, \
            f"Expected at least {len(service.office_locations) - 1} blank lines between locations, found {len(blank_lines)}"


# Property Tests for Document Formatting (Task 2.6)

@settings(max_examples=100, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(service=enhanced_service_guide_strategy())
def test_property_8_document_list_completeness(service):
    """
    **Validates: Requirements 3.1, 3.2, 3.4**
    
    Property 8: Document List Completeness
    
    For any service with N required documents in the data model, the formatted 
    response must display all N documents as separate items in a list format.
    """
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Get the required documents section (second section)
    doc_section = response.sections[1]
    assert doc_section.header == "📄 Required Documents"
    
    if not service.required_documents or len(service.required_documents) == 0:
        # No documents - should show "Information not available"
        assert doc_section.is_empty
        assert doc_section.content == "Information not available"
    else:
        # Has documents - should display all of them
        assert not doc_section.is_empty
        assert doc_section.content != "Information not available"
        
        # Count bullet points at the start of lines to verify all documents are displayed
        lines = doc_section.content.split('\n')
        bullet_lines = [line for line in lines if line.strip().startswith("•")]
        assert len(bullet_lines) == len(service.required_documents), \
            f"Expected {len(service.required_documents)} documents, found {len(bullet_lines)} bullet points"
        
        # Verify each document name appears in the formatted output
        for doc in service.required_documents:
            assert doc.document_name in doc_section.content, \
                f"Document '{doc.document_name}' not found in formatted output"
        
        # Verify list format - each document should start with bullet point
        lines = doc_section.content.split('\n')
        bullet_lines = [line for line in lines if line.strip().startswith("•")]
        assert len(bullet_lines) == len(service.required_documents), \
            f"Expected {len(service.required_documents)} bullet lines, found {len(bullet_lines)}"
        
        # Verify each document appears as separate item
        document_names = [doc.document_name for doc in service.required_documents]
        
        # For each unique document name, verify it appears the correct number of times
        from collections import Counter
        name_counts = Counter(document_names)
        
        for doc_name, expected_count in name_counts.items():
            # Count how many bullet lines start with this exact document name
            matching_lines = []
            for line in bullet_lines:
                # Check if line starts with "• {doc_name}" (exact match at start)
                expected_prefix = f"• {doc_name}"
                if line.strip().startswith(expected_prefix):
                    # Ensure it's an exact match by checking the next character
                    remaining = line.strip()[len(expected_prefix):]
                    if not remaining or remaining.startswith(" ") or remaining.startswith("("):
                        matching_lines.append(line)
            
            assert len(matching_lines) == expected_count, \
                f"Document '{doc_name}' should appear {expected_count} times, found {len(matching_lines)} times"
        
        # If multiple documents, verify they are separated by blank lines
        if len(service.required_documents) > 1:
            blank_lines = [i for i, line in enumerate(lines) if line.strip() == ""]
            # Should have at least (N-1) blank lines for N documents
            assert len(blank_lines) >= len(service.required_documents) - 1, \
                f"Expected at least {len(service.required_documents) - 1} blank lines between documents, found {len(blank_lines)}"


@settings(max_examples=100, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(service=enhanced_service_guide_strategy())
def test_property_9_document_specifications_inclusion(service):
    """
    **Validates: Requirements 3.3**
    
    Property 9: Document Specifications Inclusion
    
    For any required document with specifications (copies required, format 
    requirements) in the data model, the formatted response must include 
    these specifications with that document.
    """
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Get the required documents section
    doc_section = response.sections[1]
    
    if not service.required_documents or len(service.required_documents) == 0:
        # No documents to check specifications
        return
    
    for doc in service.required_documents:
        # Find the document in the formatted output
        doc_found = doc.document_name in doc_section.content
        assert doc_found, f"Document '{doc.document_name}' not found in formatted output"
        
        # Find the specific document block in the formatted output
        lines = doc_section.content.split('\n')
        doc_block_lines = []
        in_doc_block = False
        
        for line in lines:
            if line.strip().startswith(f"• {doc.document_name}"):
                in_doc_block = True
                doc_block_lines = [line]
            elif in_doc_block:
                if line.strip().startswith("•"):
                    # Start of next document, stop collecting
                    break
                else:
                    doc_block_lines.append(line)
        
        doc_block_content = '\n'.join(doc_block_lines)
        
        # Check copies required specification within this document's block
        if doc.copies_required > 1:
            copies_text = f"Copies required: {doc.copies_required}"
            assert copies_text in doc_block_content, \
                f"Copies specification '{copies_text}' not found for document '{doc.document_name}'"
        else:
            # Should not show "Copies required: 1" (default case) in this document's block
            copies_text = f"Copies required: {doc.copies_required}"
            assert copies_text not in doc_block_content, \
                f"Should not show '{copies_text}' for default single copy requirement"
        
        # Check format requirements specification within this document's block
        if doc.format_requirements:
            format_text = f"Format: {doc.format_requirements}"
            assert format_text in doc_block_content, \
                f"Format specification '{format_text}' not found for document '{doc.document_name}'"
        
        # Check alternatives specification within this document's block
        if doc.alternatives and len(doc.alternatives) > 0:
            alternatives_text = f"Alternatives: {', '.join(doc.alternatives)}"
            assert alternatives_text in doc_block_content, \
                f"Alternatives specification '{alternatives_text}' not found for document '{doc.document_name}'"
        
        # Check description specification within this document's block
        if doc.description:
            assert doc.description in doc_block_content, \
                f"Description '{doc.description}' not found for document '{doc.document_name}'"
        
        # Check optional marking within this document's block
        if not doc.is_mandatory:
            optional_text = f"{doc.document_name} (Optional)"
            assert optional_text in doc_block_content, \
                f"Optional marking not found for document '{doc.document_name}'"
        else:
            # Should not have (Optional) marking for mandatory documents
            optional_text = f"{doc.document_name} (Optional)"
            assert optional_text not in doc_block_content, \
                f"Should not have optional marking for mandatory document '{doc.document_name}'"


# Property Tests for Office Sequence Formatting (Task 2.8)

@settings(max_examples=100, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(service=enhanced_service_guide_strategy())
def test_property_10_office_sequence_order_preservation(service):
    """
    **Validates: Requirements 4.1**
    
    Property 10: Office Sequence Order Preservation
    
    For any service with a multi-step office visit sequence, the formatted 
    response must display the offices in the correct sequence order as 
    specified in the data model.
    """
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Get the office visit sequence section (third section)
    sequence_section = response.sections[2]
    assert sequence_section.header == "🏢 Office Visit Sequence"
    
    if not service.office_visit_sequence or len(service.office_visit_sequence) == 0:
        # No sequence - should show "Information not available"
        assert sequence_section.is_empty
        assert sequence_section.content == "Information not available"
        return
    
    if len(service.office_visit_sequence) < 2:
        # Single office - order preservation not applicable
        return
    
    # Multiple offices - verify order preservation
    assert not sequence_section.is_empty
    assert sequence_section.content != "Information not available"
    
    # Sort the steps by sequence_number (same as formatter does)
    sorted_steps = sorted(service.office_visit_sequence, key=lambda x: x.sequence_number)
    
    # Verify the sequence numbers appear in order in the formatted content
    content = sequence_section.content
    lines = content.split('\n')
    
    # Find lines that start with sequence numbers
    numbered_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and stripped[0].isdigit() and '.' in stripped:
            numbered_lines.append(stripped)
    
    # Extract sequence numbers from the formatted content
    import re
    found_numbers = []
    for line in numbered_lines:
        match = re.match(r'^(\d+)\.', line)
        if match:
            found_numbers.append(int(match.group(1)))
    
    # Verify the numbers appear in ascending order
    if len(found_numbers) > 1:
        for i in range(1, len(found_numbers)):
            assert found_numbers[i] >= found_numbers[i-1], \
                f"Sequence numbers not in order: {found_numbers}"
    
    # Verify each step appears in the formatted content with correct numbering
    for step in sorted_steps:
        # Check that the step appears with its sequence number
        number_pattern = f"{step.sequence_number}. {step.office_name}"
        assert number_pattern in content, \
            f"Expected numbered sequence '{number_pattern}' not found in formatted output"


@settings(max_examples=100, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(service=enhanced_service_guide_strategy())
def test_property_11_office_sequence_numbering(service):
    """
    **Validates: Requirements 4.2**
    
    Property 11: Office Sequence Numbering
    
    For any service requiring multiple office visits, each office in the 
    formatted response must be numbered to indicate the visit order.
    """
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Get the office visit sequence section
    sequence_section = response.sections[2]
    
    if not service.office_visit_sequence or len(service.office_visit_sequence) == 0:
        # No sequence to check numbering
        return
    
    if len(service.office_visit_sequence) == 1:
        # Single office - should NOT have numbering (covered by Property 13)
        return
    
    # Multiple offices - should have numbering
    assert not sequence_section.is_empty
    content = sequence_section.content
    
    # Sort steps by sequence_number
    sorted_steps = sorted(service.office_visit_sequence, key=lambda x: x.sequence_number)
    
    # Verify each office has proper numbering
    for step in sorted_steps:
        expected_number_format = f"{step.sequence_number}. {step.office_name}"
        assert expected_number_format in content, \
            f"Expected numbered format '{expected_number_format}' not found in output"
    
    # Verify no bullet points are used for multiple offices
    lines = content.split('\n')
    office_lines = [line for line in lines if any(step.office_name in line for step in sorted_steps)]
    
    for line in office_lines:
        # Office lines should start with numbers, not bullets
        stripped_line = line.strip()
        if any(step.office_name in stripped_line for step in sorted_steps):
            # This line contains an office name, verify it starts with a number
            assert not stripped_line.startswith("•"), \
                f"Multiple office sequence should not use bullet points, found: {stripped_line}"
            
            # Verify it starts with a number followed by a dot
            import re
            number_pattern = r'^\d+\.'
            assert re.match(number_pattern, stripped_line), \
                f"Office line should start with number and dot, got: {stripped_line}"


@settings(max_examples=100, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(service=enhanced_service_guide_strategy())
def test_property_12_optional_visit_indication(service):
    """
    **Validates: Requirements 4.3**
    
    Property 12: Optional Visit Indication
    
    For any office visit step marked as optional or conditional in the data 
    model, the formatted response must clearly indicate this status.
    """
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Get the office visit sequence section
    sequence_section = response.sections[2]
    
    if not service.office_visit_sequence or len(service.office_visit_sequence) == 0:
        # No sequence to check optional/conditional status
        return
    
    assert not sequence_section.is_empty
    content = sequence_section.content
    
    # Count optional and conditional steps in the data
    optional_steps = [step for step in service.office_visit_sequence if step.is_optional]
    conditional_steps = [step for step in service.office_visit_sequence if step.is_conditional and step.condition]
    
    # Check that optional indicators appear the correct number of times
    optional_count_in_content = content.count("(Optional)")
    assert optional_count_in_content == len(optional_steps), \
        f"Expected {len(optional_steps)} '(Optional)' indicators, found {optional_count_in_content}"
    
    # Check that condition indicators appear for conditional steps
    condition_count_in_content = content.count("Condition:")
    assert condition_count_in_content == len(conditional_steps), \
        f"Expected {len(conditional_steps)} 'Condition:' indicators, found {condition_count_in_content}"
    
    # Verify each conditional step's condition text appears
    for step in conditional_steps:
        condition_text = f"Condition: {step.condition}"
        assert condition_text in content, \
            f"Condition text '{condition_text}' not found for conditional step"


@settings(max_examples=100, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(service=enhanced_service_guide_strategy())
def test_property_13_single_office_no_numbering(service):
    """
    **Validates: Requirements 4.4**
    
    Property 13: Single Office No Numbering
    
    For any service requiring exactly one office visit, the formatted response 
    must display that office without sequence numbering.
    """
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Get the office visit sequence section
    sequence_section = response.sections[2]
    
    if not service.office_visit_sequence or len(service.office_visit_sequence) == 0:
        # No sequence to check
        return
    
    if len(service.office_visit_sequence) != 1:
        # Not a single office case
        return
    
    # Exactly one office visit
    assert not sequence_section.is_empty
    content = sequence_section.content
    
    single_step = service.office_visit_sequence[0]
    
    # Should use bullet point format, not numbered format
    expected_bullet_format = f"• {single_step.office_name}"
    assert expected_bullet_format in content, \
        f"Single office should use bullet format '• {single_step.office_name}', not found in: {content}"
    
    # Should NOT use numbered format
    numbered_format = f"1. {single_step.office_name}"
    assert numbered_format not in content, \
        f"Single office should not use numbered format '1. {single_step.office_name}', but found in: {content}"
    
    # Should NOT use any other number format
    import re
    lines = content.split('\n')
    for line in lines:
        if single_step.office_name in line:
            stripped_line = line.strip()
            # This line contains the office name
            number_pattern = r'^\d+\.'
            assert not re.match(number_pattern, stripped_line), \
                f"Single office line should not start with number, got: {stripped_line}"
            
            # Should start with bullet point
            assert stripped_line.startswith("•"), \
                f"Single office line should start with bullet point, got: {stripped_line}"
    
    # Verify the office details are still included
    assert single_step.office_name in content, \
        f"Office name '{single_step.office_name}' should be present"
    assert single_step.purpose in content, \
        f"Office purpose '{single_step.purpose}' should be present"
    assert f"Duration: {single_step.estimated_duration}" in content, \
        f"Duration '{single_step.estimated_duration}' should be present"


# Additional property tests for comprehensive coverage

@settings(max_examples=50, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(service=enhanced_service_guide_strategy())
def test_property_response_structure_integrity(service):
    """
    Verify that the response structure maintains integrity across all inputs.
    
    This property ensures that:
    - Response always has the correct basic structure
    - Service metadata is preserved
    - No sections are None or malformed
    """
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Verify response structure
    assert isinstance(response, FormattedServiceResponse), \
        f"Response should be FormattedServiceResponse, got {type(response)}"
    
    # Verify service metadata preservation
    assert response.service_name == service.service_name, \
        "Service name should be preserved in response"
    assert response.description == service.description, \
        "Service description should be preserved in response"
    assert response.last_updated == service.last_updated, \
        "Last updated timestamp should be preserved in response"
    
    # Verify all sections are valid ResponseSection objects
    for i, section in enumerate(response.sections):
        assert isinstance(section, ResponseSection), \
            f"Section {i} should be ResponseSection, got {type(section)}"
        assert section.header is not None, f"Section {i} header should not be None"
        assert section.content is not None, f"Section {i} content should not be None"
        assert isinstance(section.is_empty, bool), \
            f"Section {i} is_empty should be boolean, got {type(section.is_empty)}"


@settings(max_examples=50, phases=[Phase.generate, Phase.target, Phase.shrink])
@given(services=st.lists(enhanced_service_guide_strategy(), min_size=2, max_size=5))
def test_property_format_consistency_across_services(services):
    """
    Verify that formatting is consistent across multiple different services.
    
    This property ensures that the formatter produces consistent output
    structure regardless of the input service variations.
    """
    formatter = ResponseFormatter()
    responses = [formatter.format_service_response(service) for service in services]
    
    # All responses should have the same number of sections
    section_counts = [len(response.sections) for response in responses]
    assert all(count == 5 for count in section_counts), \
        f"All responses should have 5 sections, got counts: {section_counts}"
    
    # All responses should have the same header order
    first_headers = [section.header for section in responses[0].sections]
    for i, response in enumerate(responses[1:], 1):
        headers = [section.header for section in response.sections]
        assert headers == first_headers, \
            f"Response {i} headers {headers} don't match first response headers {first_headers}"
    
    # All responses should follow the same empty/non-empty logic
    for response in responses:
        for section in response.sections:
            if section.is_empty:
                assert section.content == "Information not available", \
                    f"Empty section should have standard message, got: {section.content}"
            else:
                assert section.content != "Information not available", \
                    f"Non-empty section should not have 'Information not available' message"