"""Example demonstrating the ResponseFormatter service.

This example shows how the ResponseFormatter structures service information
into a consistent format with all five categories.
"""

from datetime import datetime
from app.services.response_formatter import ResponseFormatter
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


def main():
    """Demonstrate ResponseFormatter with a sample service."""
    
    # Create a sample service with all categories populated
    service = EnhancedServiceGuide(
        service_id="aadhaar_name_change",
        service_name="Aadhaar Name Change",
        category=ServiceCategory.AADHAAR,
        description="Update your name in the Aadhaar database",
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
                name="Regional Aadhaar Office",
                address="456 Park Road",
                city="Mumbai",
                state="Maharashtra",
                postal_code="400002",
                operating_hours="10:00 AM - 4:00 PM"
            )
        ],
        required_documents=[
            RequiredDocument(
                document_name="Existing Aadhaar Card",
                description="Your current Aadhaar card",
                copies_required=1,
                is_mandatory=True
            ),
            RequiredDocument(
                document_name="Proof of Name Change",
                description="Marriage certificate, gazette notification, or court order",
                copies_required=2,
                format_requirements="Original + 1 photocopy",
                is_mandatory=True
            ),
            RequiredDocument(
                document_name="Passport Size Photo",
                copies_required=2,
                is_mandatory=True
            )
        ],
        office_visit_sequence=[
            OfficeVisitStep(
                sequence_number=1,
                office_name="District Aadhaar Center",
                purpose="Submit application and documents",
                estimated_duration="30 minutes"
            ),
            OfficeVisitStep(
                sequence_number=2,
                office_name="District Aadhaar Center",
                purpose="Biometric verification (if required)",
                estimated_duration="15 minutes",
                is_conditional=True,
                condition="Only if requested by officer"
            )
        ],
        official_websites=[
            OfficialWebsiteLink(
                url="https://uidai.gov.in",
                purpose="UIDAI Official Portal",
                description="Main website for Aadhaar services"
            ),
            OfficialWebsiteLink(
                url="https://myaadhaar.uidai.gov.in",
                purpose="Online Update Portal",
                description="Portal for online Aadhaar updates"
            )
        ],
        processing_timelines=[
            ProcessingTimeline(
                minimum_days=7,
                maximum_days=30,
                typical_days=14,
                time_unit="days",
                processing_type="standard",
                notes="Processing time may vary based on verification requirements",
                factors_affecting_time=[
                    "Document verification complexity",
                    "Biometric verification requirement",
                    "Regional office workload"
                ]
            )
        ],
        last_updated=datetime.now(),
        data_source="official_uidai_guidelines"
    )
    
    # Format the service response
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Display the formatted response
    print("=" * 80)
    print(f"SERVICE: {response.service_name}")
    print("=" * 80)
    print(f"\n{response.description}\n")
    print(f"Last Updated: {response.last_updated.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for section in response.sections:
        print("-" * 80)
        print(f"\n{section.header}\n")
        print(section.content)
        print()
    
    print("=" * 80)
    
    # Also demonstrate with a service that has empty categories
    print("\n\n")
    print("=" * 80)
    print("EXAMPLE WITH EMPTY CATEGORIES")
    print("=" * 80)
    
    minimal_service = EnhancedServiceGuide(
        service_id="test_service",
        service_name="Test Service",
        category=ServiceCategory.CERTIFICATE,
        description="A service with minimal information",
        office_locations=[
            OfficeLocation(
                name="Main Office",
                address="789 Test Street",
                city="Delhi",
                state="Delhi",
                postal_code="110001"
            )
        ],
        required_documents=[],  # Empty
        office_visit_sequence=[],  # Empty
        official_websites=[],  # Empty
        processing_timelines=[],  # Empty
        last_updated=datetime.now(),
        data_source="test"
    )
    
    minimal_response = formatter.format_service_response(minimal_service)
    
    print(f"\nSERVICE: {minimal_response.service_name}\n")
    
    for section in minimal_response.sections:
        print(f"{section.header}")
        if section.is_empty:
            print(f"  → {section.content}")
        else:
            print(f"  ✓ Data available")
        print()


if __name__ == "__main__":
    main()
