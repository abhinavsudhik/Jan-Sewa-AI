"""Example demonstrating the SchemaAdapter usage.

This script shows how to convert a legacy ServiceGuide to an EnhancedServiceGuide
using the SchemaAdapter.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from app.models.schemas import (
    ServiceGuide,
    ServiceStep,
    ProcessingTime,
    ContactInfo,
    ServiceCategory,
)
from app.services.schema_adapter import SchemaAdapter


def main():
    """Demonstrate schema adapter conversion."""
    print("=" * 60)
    print("Schema Adapter Example")
    print("=" * 60)
    print()
    
    # Create a legacy ServiceGuide
    print("Creating legacy ServiceGuide...")
    legacy_guide = ServiceGuide(
        service_id="aadhaar_name_change",
        service_name="Aadhaar Name Change",
        category=ServiceCategory.AADHAAR,
        description="Update your name in the Aadhaar database",
        steps=[
            ServiceStep(
                step_number=1,
                description="Visit nearest Aadhaar enrollment center",
                requires_in_person=True,
                online_available=False,
                estimated_duration="30 minutes",
            ),
            ServiceStep(
                step_number=2,
                description="Submit name change request with supporting documents",
                requires_in_person=True,
                online_available=False,
                estimated_duration="15 minutes",
            ),
            ServiceStep(
                step_number=3,
                description="Biometric verification",
                requires_in_person=True,
                online_available=False,
                estimated_duration="10 minutes",
            ),
        ],
        processing_time=ProcessingTime(
            minimum="7 days",
            maximum="90 days",
            typical="30 days",
            factors=[
                "Document verification time",
                "System processing load",
                "Completeness of submitted documents",
            ],
        ),
        official_portal_url="https://uidai.gov.in",
        contact_info=ContactInfo(
            phone="+91-1947",
            email="help@uidai.gov.in",
            address="UIDAI Headquarters, 3rd Floor, Tower-I, Jeevan Bharati Building, Connaught Place, New Delhi, Delhi 110001",
            helpline="1947",
        ),
        last_updated=datetime(2024, 1, 15, 10, 30, 0),
        available_languages=["en", "hi"],
    )
    
    print(f"Legacy Service: {legacy_guide.service_name}")
    print(f"Steps: {len(legacy_guide.steps)}")
    print(f"Contact Address: {legacy_guide.contact_info.address}")
    print()
    
    # Convert to enhanced format
    print("Converting to EnhancedServiceGuide...")
    enhanced_guide = SchemaAdapter.legacy_to_enhanced(legacy_guide)
    
    print(f"Enhanced Service: {enhanced_guide.service_name}")
    print(f"Data Source: {enhanced_guide.data_source}")
    print()
    
    # Display converted data
    print("Converted Data:")
    print("-" * 60)
    
    print(f"\n📍 Office Locations: {len(enhanced_guide.office_locations)}")
    for location in enhanced_guide.office_locations:
        print(f"  - {location.name}")
        print(f"    Address: {location.address}")
        print(f"    City: {location.city}, State: {location.state}")
        print(f"    Postal Code: {location.postal_code}")
        print(f"    Phone: {location.contact_phone}")
    
    print(f"\n📄 Required Documents: {len(enhanced_guide.required_documents)}")
    if not enhanced_guide.required_documents:
        print("  (Not available in legacy schema)")
    
    print(f"\n🏢 Office Visit Sequence: {len(enhanced_guide.office_visit_sequence)}")
    for step in enhanced_guide.office_visit_sequence:
        print(f"  {step.sequence_number}. {step.office_name}")
        print(f"     Purpose: {step.purpose}")
        print(f"     Duration: {step.estimated_duration}")
    
    print(f"\n🔗 Official Websites: {len(enhanced_guide.official_websites)}")
    for website in enhanced_guide.official_websites:
        print(f"  - {website.purpose}: {website.url}")
        print(f"    {website.description}")
    
    print(f"\n⏱️ Processing Timelines: {len(enhanced_guide.processing_timelines)}")
    for timeline in enhanced_guide.processing_timelines:
        print(f"  - {timeline.processing_type.title()} Processing")
        print(f"    Typical: {timeline.typical_days} {timeline.time_unit}")
        print(f"    Range: {timeline.as_range_string()}")
        print(f"    Factors affecting time:")
        for factor in timeline.factors_affecting_time:
            print(f"      • {factor}")
    
    print()
    print("=" * 60)
    print("Conversion completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
