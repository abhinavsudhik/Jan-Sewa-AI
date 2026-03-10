"""Tests for office visit sequence formatting logic.

This module tests the _format_office_sequence() method to ensure:
1. Single office visit displays without numbering (bullet point)
2. Multiple office visits display with numbered sequence
3. Purpose and estimated duration are included
4. Optional steps are marked with "(Optional)"
5. Conditional steps are marked with "Condition: {condition}"
6. Steps are sorted by sequence_number
"""

import pytest
from datetime import datetime

from app.services.response_formatter import ResponseFormatter
from app.models.enhanced_service import (
    EnhancedServiceGuide,
    OfficeVisitStep
)
from app.models.schemas import ServiceCategory


def create_test_service(office_visit_sequence):
    """Helper to create a test service with given office visit sequence."""
    return EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test description",
        office_locations=[],
        required_documents=[],
        office_visit_sequence=office_visit_sequence,
        official_websites=[],
        processing_timelines=[],
        last_updated=datetime.now(),
        data_source="test"
    )


def test_single_office_no_numbering():
    """Test single office visit displays without sequence numbering."""
    service = create_test_service([
        OfficeVisitStep(
            sequence_number=1,
            office_name="Main Office",
            purpose="Submit application and documents",
            estimated_duration="30 minutes"
        )
    ])
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Get office sequence section (3rd section, index 2)
    sequence_section = response.sections[2]
    content = sequence_section.content
    
    # Should start with bullet point, not "1."
    assert content.startswith("• Main Office")
    assert "1. Main Office" not in content
    
    # Should contain purpose and duration
    assert "Submit application and documents" in content
    assert "Duration: 30 minutes" in content


def test_multiple_offices_with_numbering():
    """Test multiple office visits display with numbered sequence."""
    service = create_test_service([
        OfficeVisitStep(
            sequence_number=1,
            office_name="District Collectorate",
            purpose="Submit application form and documents",
            estimated_duration="45 minutes"
        ),
        OfficeVisitStep(
            sequence_number=2,
            office_name="Verification Office",
            purpose="Biometric verification and document verification",
            estimated_duration="30 minutes"
        ),
        OfficeVisitStep(
            sequence_number=3,
            office_name="Collection Center",
            purpose="Collect updated Aadhaar card",
            estimated_duration="15 minutes"
        )
    ])
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    sequence_section = response.sections[2]
    content = sequence_section.content
    
    # Should contain numbered sequence
    assert "1. District Collectorate" in content
    assert "2. Verification Office" in content
    assert "3. Collection Center" in content
    
    # Should contain purposes
    assert "Submit application form and documents" in content
    assert "Biometric verification and document verification" in content
    assert "Collect updated Aadhaar card" in content
    
    # Should contain durations
    assert "Duration: 45 minutes" in content
    assert "Duration: 30 minutes" in content
    assert "Duration: 15 minutes" in content


def test_optional_step_indicator():
    """Test optional steps are marked with (Optional)."""
    service = create_test_service([
        OfficeVisitStep(
            sequence_number=1,
            office_name="Main Office",
            purpose="Submit application",
            estimated_duration="30 minutes",
            is_optional=False
        ),
        OfficeVisitStep(
            sequence_number=2,
            office_name="Collection Center",
            purpose="Collect physical card",
            estimated_duration="15 minutes",
            is_optional=True
        )
    ])
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    sequence_section = response.sections[2]
    content = sequence_section.content
    
    # Should contain (Optional) indicator for step 2
    assert "(Optional)" in content
    
    # Verify it appears after the Collection Center step
    collection_center_pos = content.find("Collection Center")
    optional_pos = content.find("(Optional)")
    assert optional_pos > collection_center_pos


def test_conditional_step_with_condition():
    """Test conditional steps are marked with Condition: {condition}."""
    service = create_test_service([
        OfficeVisitStep(
            sequence_number=1,
            office_name="Main Office",
            purpose="Submit application",
            estimated_duration="30 minutes"
        ),
        OfficeVisitStep(
            sequence_number=2,
            office_name="Collection Center",
            purpose="Collect physical card",
            estimated_duration="15 minutes",
            is_conditional=True,
            condition="Only if physical card is requested"
        )
    ])
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    sequence_section = response.sections[2]
    content = sequence_section.content
    
    # Should contain condition text
    assert "Condition: Only if physical card is requested" in content
    
    # Verify it appears after the Collection Center step
    collection_center_pos = content.find("Collection Center")
    condition_pos = content.find("Condition:")
    assert condition_pos > collection_center_pos


def test_optional_and_conditional_step():
    """Test step that is both optional and conditional."""
    service = create_test_service([
        OfficeVisitStep(
            sequence_number=1,
            office_name="Main Office",
            purpose="Submit application",
            estimated_duration="30 minutes"
        ),
        OfficeVisitStep(
            sequence_number=2,
            office_name="Collection Center",
            purpose="Collect physical card",
            estimated_duration="15 minutes",
            is_optional=True,
            is_conditional=True,
            condition="Only if physical card is requested"
        )
    ])
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    sequence_section = response.sections[2]
    content = sequence_section.content
    
    # Should contain both indicators
    assert "(Optional)" in content
    assert "Condition: Only if physical card is requested" in content


def test_sequence_sorting():
    """Test steps are sorted by sequence_number before formatting."""
    # Create steps in non-sequential order
    service = create_test_service([
        OfficeVisitStep(
            sequence_number=3,
            office_name="Third Office",
            purpose="Third step",
            estimated_duration="15 minutes"
        ),
        OfficeVisitStep(
            sequence_number=1,
            office_name="First Office",
            purpose="First step",
            estimated_duration="30 minutes"
        ),
        OfficeVisitStep(
            sequence_number=2,
            office_name="Second Office",
            purpose="Second step",
            estimated_duration="20 minutes"
        )
    ])
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    sequence_section = response.sections[2]
    content = sequence_section.content
    
    # Verify order in formatted content
    first_pos = content.find("First Office")
    second_pos = content.find("Second Office")
    third_pos = content.find("Third Office")
    
    assert first_pos < second_pos < third_pos
    
    # Verify numbering is correct
    assert "1. First Office" in content
    assert "2. Second Office" in content
    assert "3. Third Office" in content


def test_single_optional_office():
    """Test single office that is optional."""
    service = create_test_service([
        OfficeVisitStep(
            sequence_number=1,
            office_name="Main Office",
            purpose="Submit application",
            estimated_duration="30 minutes",
            is_optional=True
        )
    ])
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    sequence_section = response.sections[2]
    content = sequence_section.content
    
    # Should use bullet point (not numbered)
    assert content.startswith("• Main Office")
    
    # Should contain optional indicator
    assert "(Optional)" in content


def test_single_conditional_office():
    """Test single office that is conditional."""
    service = create_test_service([
        OfficeVisitStep(
            sequence_number=1,
            office_name="Main Office",
            purpose="Submit application",
            estimated_duration="30 minutes",
            is_conditional=True,
            condition="Only during business hours"
        )
    ])
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    sequence_section = response.sections[2]
    content = sequence_section.content
    
    # Should use bullet point (not numbered)
    assert content.startswith("• Main Office")
    
    # Should contain condition
    assert "Condition: Only during business hours" in content


def test_formatting_with_blank_lines():
    """Test multiple offices are separated by blank lines."""
    service = create_test_service([
        OfficeVisitStep(
            sequence_number=1,
            office_name="Office A",
            purpose="Step A",
            estimated_duration="30 minutes"
        ),
        OfficeVisitStep(
            sequence_number=2,
            office_name="Office B",
            purpose="Step B",
            estimated_duration="20 minutes"
        )
    ])
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    sequence_section = response.sections[2]
    content = sequence_section.content
    
    # Should contain double newline between steps
    assert "\n\n" in content
