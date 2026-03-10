"""Tests for document list formatting in ResponseFormatter."""

import pytest
from datetime import datetime

from app.services.response_formatter import ResponseFormatter
from app.models.enhanced_service import (
    EnhancedServiceGuide,
    RequiredDocument
)
from app.models.schemas import ServiceCategory


def test_format_document_with_all_fields():
    """Test formatting a document with all optional fields populated."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test",
        required_documents=[
            RequiredDocument(
                document_name="Proof of Address",
                description="Document showing current address",
                copies_required=3,
                format_requirements="Original + 2 photocopies",
                is_mandatory=True,
                alternatives=["Electricity Bill", "Rent Agreement", "Bank Statement"]
            )
        ],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Get the required documents section
    doc_section = response.sections[1]
    
    # Verify all fields are present
    assert "Proof of Address" in doc_section.content
    assert "Document showing current address" in doc_section.content
    assert "Copies required: 3" in doc_section.content
    assert "Format: Original + 2 photocopies" in doc_section.content
    assert "Alternatives: Electricity Bill, Rent Agreement, Bank Statement" in doc_section.content
    assert "(Optional)" not in doc_section.content  # Should not be marked optional


def test_format_optional_document():
    """Test formatting an optional document."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test",
        required_documents=[
            RequiredDocument(
                document_name="Passport Size Photo",
                description="Recent passport size photograph",
                copies_required=2,
                is_mandatory=False
            )
        ],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    doc_section = response.sections[1]
    
    # Verify optional indicator is present
    assert "Passport Size Photo (Optional)" in doc_section.content
    assert "Recent passport size photograph" in doc_section.content
    assert "Copies required: 2" in doc_section.content


def test_format_document_with_minimal_fields():
    """Test formatting a document with only required fields."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test",
        required_documents=[
            RequiredDocument(
                document_name="Aadhaar Card"
            )
        ],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    doc_section = response.sections[1]
    
    # Verify only document name is present
    assert "• Aadhaar Card" in doc_section.content
    assert "Copies required:" not in doc_section.content  # Should not show for 1 copy
    assert "Format:" not in doc_section.content
    assert "Alternatives:" not in doc_section.content


def test_format_multiple_documents():
    """Test formatting multiple documents with proper spacing."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test",
        required_documents=[
            RequiredDocument(
                document_name="Aadhaar Card",
                description="Government-issued identity card",
                copies_required=2,
                format_requirements="Original + photocopy"
            ),
            RequiredDocument(
                document_name="Proof of Address Change",
                description="Document showing new address",
                alternatives=["Electricity Bill", "Rent Agreement", "Bank Statement"]
            ),
            RequiredDocument(
                document_name="Passport Size Photo",
                description="Recent passport size photograph",
                copies_required=2,
                is_mandatory=False
            )
        ],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    doc_section = response.sections[1]
    
    # Verify all three documents are present
    assert "Aadhaar Card" in doc_section.content
    assert "Proof of Address Change" in doc_section.content
    assert "Passport Size Photo (Optional)" in doc_section.content
    
    # Verify proper spacing (double newline between documents)
    assert "\n\n" in doc_section.content
    
    # Verify specific details for each document
    assert "Government-issued identity card" in doc_section.content
    assert "Copies required: 2" in doc_section.content
    assert "Format: Original + photocopy" in doc_section.content
    assert "Alternatives: Electricity Bill, Rent Agreement, Bank Statement" in doc_section.content


def test_format_document_copies_required_one():
    """Test that copies_required is not shown when it's 1."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test",
        required_documents=[
            RequiredDocument(
                document_name="Test Document",
                copies_required=1
            )
        ],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    doc_section = response.sections[1]
    
    # Verify copies_required is not shown for 1 copy
    assert "Test Document" in doc_section.content
    assert "Copies required:" not in doc_section.content


def test_format_document_empty_alternatives():
    """Test that empty alternatives list is not shown."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test",
        required_documents=[
            RequiredDocument(
                document_name="Test Document",
                alternatives=[]
            )
        ],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    doc_section = response.sections[1]
    
    # Verify alternatives is not shown for empty list
    assert "Test Document" in doc_section.content
    assert "Alternatives:" not in doc_section.content


def test_format_document_matches_expected_format():
    """Test that the output matches the expected format from the task description."""
    service = EnhancedServiceGuide(
        service_id="test",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="Test",
        required_documents=[
            RequiredDocument(
                document_name="Aadhaar Card",
                description="Government-issued identity card",
                copies_required=2,
                format_requirements="Original + photocopy"
            ),
            RequiredDocument(
                document_name="Proof of Address Change",
                description="Document showing new address",
                alternatives=["Electricity Bill", "Rent Agreement", "Bank Statement"]
            ),
            RequiredDocument(
                document_name="Passport Size Photo",
                description="Recent passport size photograph",
                copies_required=2,
                is_mandatory=False
            )
        ],
        last_updated=datetime.now(),
        data_source="test"
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    doc_section = response.sections[1]
    
    # Expected format from task description:
    # • Aadhaar Card
    #   Government-issued identity card
    #   Copies required: 2
    #   Format: Original + photocopy
    #
    # • Proof of Address Change
    #   Document showing new address
    #   Alternatives: Electricity Bill, Rent Agreement, Bank Statement
    #
    # • Passport Size Photo (Optional)
    #   Recent passport size photograph
    #   Copies required: 2
    
    expected_lines = [
        "• Aadhaar Card",
        "  Government-issued identity card",
        "  Copies required: 2",
        "  Format: Original + photocopy",
        "",
        "• Proof of Address Change",
        "  Document showing new address",
        "  Alternatives: Electricity Bill, Rent Agreement, Bank Statement",
        "",
        "• Passport Size Photo (Optional)",
        "  Recent passport size photograph",
        "  Copies required: 2"
    ]
    
    expected_content = "\n".join(expected_lines)
    assert doc_section.content == expected_content
