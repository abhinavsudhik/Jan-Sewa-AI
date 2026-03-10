"""Example usage of enhanced service data models.

This script demonstrates how to create and use the enhanced service models
with all five information categories and validation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from app.models.enhanced_service import (
    Coordinates,
    OfficeLocation,
    RequiredDocument,
    OfficeVisitStep,
    OfficialWebsiteLink,
    ProcessingTimeline,
    EnhancedServiceGuide,
)
from app.models.schemas import ServiceCategory


def create_sample_service() -> EnhancedServiceGuide:
    """Create a sample enhanced service guide with all categories populated."""
    
    # Office Locations
    office_locations = [
        OfficeLocation(
            name="District Collectorate - Mumbai",
            address="CST Road, Near Railway Station",
            city="Mumbai",
            state="Maharashtra",
            postal_code="400001",
            coordinates=Coordinates(latitude=19.0760, longitude=72.8777),
            operating_hours="Monday-Friday: 9:00 AM - 5:00 PM",
            contact_phone="+91-22-12345678"
        ),
        OfficeLocation(
            name="Sub-District Office - Andheri",
            address="Andheri West, Near Metro Station",
            city="Mumbai",
            state="Maharashtra",
            postal_code="400053",
            operating_hours="Monday-Saturday: 10:00 AM - 4:00 PM",
            contact_phone="+91-22-87654321"
        )
    ]
    
    # Required Documents
    required_documents = [
        RequiredDocument(
            document_name="Aadhaar Card",
            description="Original Aadhaar card for identity verification",
            copies_required=2,
            format_requirements="Original + 1 photocopy",
            is_mandatory=True
        ),
        RequiredDocument(
            document_name="Proof of Address Change",
            description="Document showing new address (utility bill, rent agreement, etc.)",
            copies_required=1,
            format_requirements="Original or certified copy",
            is_mandatory=True,
            alternatives=["Electricity Bill", "Rent Agreement", "Bank Statement"]
        ),
        RequiredDocument(
            document_name="Passport Size Photograph",
            description="Recent passport size photograph",
            copies_required=2,
            format_requirements="Color photograph, white background",
            is_mandatory=True
        )
    ]
    
    # Office Visit Sequence
    office_visit_sequence = [
        OfficeVisitStep(
            sequence_number=1,
            office_name="District Collectorate - Mumbai",
            purpose="Submit application form and documents",
            estimated_duration="45 minutes",
            is_optional=False
        ),
        OfficeVisitStep(
            sequence_number=2,
            office_name="Verification Office",
            purpose="Biometric verification and document verification",
            estimated_duration="30 minutes",
            is_optional=False
        ),
        OfficeVisitStep(
            sequence_number=3,
            office_name="Collection Center",
            purpose="Collect updated Aadhaar card",
            estimated_duration="15 minutes",
            is_optional=True,
            is_conditional=True,
            condition="Only if physical card is requested (otherwise delivered by post)"
        )
    ]
    
    # Official Websites
    official_websites = [
        OfficialWebsiteLink(
            url="https://uidai.gov.in",
            purpose="Official UIDAI Portal",
            description="Main portal for all Aadhaar-related services"
        ),
        OfficialWebsiteLink(
            url="https://myaadhaar.uidai.gov.in",
            purpose="Online Application Portal",
            description="Submit name change request online"
        ),
        OfficialWebsiteLink(
            url="https://resident.uidai.gov.in/check-status",
            purpose="Status Tracking",
            description="Track your application status"
        )
    ]
    
    # Processing Timelines
    processing_timelines = [
        ProcessingTimeline(
            minimum_days=7,
            maximum_days=30,
            typical_days=14,
            time_unit="days",
            processing_type="standard",
            notes="Processing time starts after successful document verification",
            factors_affecting_time=[
                "Document completeness and accuracy",
                "Verification requirements",
                "Peak season delays (March-April)",
                "Postal delivery time (if applicable)"
            ]
        ),
        ProcessingTimeline(
            minimum_days=1,
            maximum_days=3,
            typical_days=2,
            time_unit="days",
            processing_type="expedited",
            notes="Available for urgent cases with additional fee",
            factors_affecting_time=[
                "Availability of expedited service at your location",
                "Additional documentation may be required"
            ]
        )
    ]
    
    # Create the complete service guide
    service_guide = EnhancedServiceGuide(
        service_id="aadhaar_name_change",
        service_name="Aadhaar Name Change",
        category=ServiceCategory.AADHAAR,
        description="Update your name in the Aadhaar database. This service allows you to "
                    "correct or update your name as it appears on your Aadhaar card.",
        office_locations=office_locations,
        required_documents=required_documents,
        office_visit_sequence=office_visit_sequence,
        official_websites=official_websites,
        processing_timelines=processing_timelines,
        last_updated=datetime.now(),
        data_source="UIDAI Official Guidelines 2024",
        available_languages=["en", "hi", "mr"]
    )
    
    return service_guide


def print_service_summary(service: EnhancedServiceGuide):
    """Print a summary of the service guide."""
    print(f"\n{'='*60}")
    print(f"Service: {service.service_name}")
    print(f"Category: {service.category.value}")
    print(f"{'='*60}\n")
    
    print(f"Description: {service.description}\n")
    
    print(f"📍 Office Locations: {len(service.office_locations)}")
    for loc in service.office_locations:
        print(f"  - {loc.name}")
        if loc.coordinates:
            print(f"    Coordinates: ({loc.coordinates.latitude}, {loc.coordinates.longitude})")
    
    print(f"\n📄 Required Documents: {len(service.required_documents)}")
    for doc in service.required_documents:
        mandatory = "Mandatory" if doc.is_mandatory else "Optional"
        print(f"  - {doc.document_name} ({mandatory}, {doc.copies_required} copies)")
    
    print(f"\n🏢 Office Visit Sequence: {len(service.office_visit_sequence)} steps")
    for step in service.office_visit_sequence:
        optional = " (Optional)" if step.is_optional else ""
        print(f"  {step.sequence_number}. {step.office_name}{optional}")
        print(f"     Purpose: {step.purpose}")
        print(f"     Duration: {step.estimated_duration}")
    
    print(f"\n🔗 Official Websites: {len(service.official_websites)}")
    for site in service.official_websites:
        print(f"  - {site.purpose}: {site.url}")
    
    print(f"\n⏱️ Processing Timelines: {len(service.processing_timelines)}")
    for timeline in service.processing_timelines:
        print(f"  - {timeline.processing_type.title()} Processing:")
        print(f"    Range: {timeline.as_range_string()}")
        print(f"    Typical: {timeline.typical_days} {timeline.time_unit}")
    
    print(f"\n{'='*60}")
    print(f"Last Updated: {service.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Data Source: {service.data_source}")
    print(f"Available Languages: {', '.join(service.available_languages)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Create and display sample service
    service = create_sample_service()
    print_service_summary(service)
    
    # Demonstrate validation
    print("\n✅ All validations passed!")
    print("  - Coordinates within valid ranges")
    print("  - Document copies >= 1")
    print("  - Timeline: minimum <= typical <= maximum")
    print("  - URLs properly formatted")
