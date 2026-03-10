"""Demonstration of document list formatting.

This example shows how the ResponseFormatter handles various document
configurations including optional documents, alternatives, and format requirements.
"""

from datetime import datetime
from app.services.response_formatter import ResponseFormatter
from app.models.enhanced_service import (
    EnhancedServiceGuide,
    RequiredDocument
)
from app.models.schemas import ServiceCategory


def main():
    """Demonstrate document formatting with various configurations."""
    
    # Create a service with comprehensive document requirements
    service = EnhancedServiceGuide(
        service_id="demo_service",
        service_name="Document Formatting Demo",
        category=ServiceCategory.CERTIFICATE,
        description="Demonstrates all document formatting features",
        required_documents=[
            # Document with all fields
            RequiredDocument(
                document_name="Aadhaar Card",
                description="Government-issued identity card",
                copies_required=2,
                format_requirements="Original + photocopy",
                is_mandatory=True
            ),
            # Document with alternatives
            RequiredDocument(
                document_name="Proof of Address Change",
                description="Document showing new address",
                alternatives=["Electricity Bill", "Rent Agreement", "Bank Statement"],
                is_mandatory=True
            ),
            # Optional document
            RequiredDocument(
                document_name="Passport Size Photo",
                description="Recent passport size photograph",
                copies_required=2,
                is_mandatory=False
            ),
            # Minimal document (only name)
            RequiredDocument(
                document_name="PAN Card",
                is_mandatory=True
            ),
            # Document with format requirements only
            RequiredDocument(
                document_name="Birth Certificate",
                format_requirements="Self-attested copy",
                is_mandatory=True
            ),
            # Optional document with alternatives
            RequiredDocument(
                document_name="Income Proof",
                description="Document showing annual income",
                alternatives=["Salary Slip", "ITR", "Form 16"],
                is_mandatory=False
            )
        ],
        last_updated=datetime.now(),
        data_source="demo"
    )
    
    # Format the service response
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Display the formatted documents section
    print("=" * 80)
    print("DOCUMENT FORMATTING DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Get the required documents section (index 1)
    doc_section = response.sections[1]
    
    print(doc_section.header)
    print()
    print(doc_section.content)
    print()
    print("=" * 80)
    
    # Show feature breakdown
    print("\nFEATURES DEMONSTRATED:")
    print("-" * 80)
    print("✓ Document name as bullet point")
    print("✓ Description indented below name")
    print("✓ Copies required (when > 1)")
    print("✓ Format requirements")
    print("✓ Optional indicator for non-mandatory documents")
    print("✓ Alternatives list")
    print("✓ Proper spacing between documents")
    print("✓ Minimal documents (name only)")
    print()


if __name__ == "__main__":
    main()
