"""Demo script to showcase the enhanced mock service data.

This script demonstrates the three different service scenarios:
1. Service with all categories fully populated (Aadhaar Name Change)
2. Service with some empty categories (Data Access Request)
3. Service with single items (Birth Certificate)
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.query_processor import ServiceRepository


def print_service_summary(service):
    """Print a summary of a service's data."""
    print(f"\n{'='*70}")
    print(f"Service: {service.service_name}")
    print(f"ID: {service.service_id}")
    print(f"Category: {service.category.value}")
    print(f"{'='*70}")
    print(f"\nDescription: {service.description}")
    
    print(f"\n📍 Office Locations: {len(service.office_locations)}")
    if service.office_locations:
        for loc in service.office_locations:
            print(f"  • {loc.name}")
            print(f"    {loc.address}, {loc.city}, {loc.state} {loc.postal_code}")
            if loc.coordinates:
                print(f"    Coordinates: ({loc.coordinates.latitude}, {loc.coordinates.longitude})")
            if loc.operating_hours:
                print(f"    Hours: {loc.operating_hours}")
            if loc.contact_phone:
                print(f"    Phone: {loc.contact_phone}")
    else:
        print("  (No office locations - online service)")
    
    print(f"\n📄 Required Documents: {len(service.required_documents)}")
    if service.required_documents:
        for doc in service.required_documents:
            print(f"  • {doc.document_name}")
            if doc.description:
                print(f"    {doc.description}")
            if doc.copies_required > 1:
                print(f"    Copies: {doc.copies_required}")
            if doc.format_requirements:
                print(f"    Format: {doc.format_requirements}")
            if doc.alternatives:
                print(f"    Alternatives: {', '.join(doc.alternatives[:2])}...")
    else:
        print("  (No documents required)")
    
    print(f"\n🏢 Office Visit Sequence: {len(service.office_visit_sequence)}")
    if service.office_visit_sequence:
        for step in service.office_visit_sequence:
            if len(service.office_visit_sequence) == 1:
                print(f"  • {step.office_name}")
            else:
                print(f"  {step.sequence_number}. {step.office_name}")
            print(f"     {step.purpose}")
            print(f"     Duration: {step.estimated_duration}")
            if step.is_optional:
                print(f"     (Optional)")
            if step.is_conditional:
                print(f"     Condition: {step.condition}")
    else:
        print("  (No office visits required)")
    
    print(f"\n🔗 Official Websites: {len(service.official_websites)}")
    if service.official_websites:
        for website in service.official_websites:
            print(f"  • {website.purpose}: {website.url}")
            if website.description:
                print(f"    {website.description}")
    else:
        print("  (No official websites)")
    
    print(f"\n⏱️  Processing Timelines: {len(service.processing_timelines)}")
    if service.processing_timelines:
        for timeline in service.processing_timelines:
            print(f"  • {timeline.processing_type.title()} Processing")
            print(f"    Typical: {timeline.typical_days} {timeline.time_unit}")
            print(f"    Range: {timeline.as_range_string()}")
            if timeline.notes:
                print(f"    Note: {timeline.notes}")
    else:
        print("  (No timeline information)")
    
    print(f"\n📅 Metadata:")
    print(f"  • Last Updated: {service.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  • Data Source: {service.data_source}")
    print(f"  • Languages: {', '.join(service.available_languages)}")


def main():
    """Main demo function."""
    print("\n" + "="*70)
    print("ENHANCED MOCK SERVICE DATA DEMONSTRATION")
    print("="*70)
    
    repo = ServiceRepository()
    
    print(f"\nTotal services loaded: {len(repo.get_all_services())}")
    
    # Scenario 1: All categories fully populated
    print("\n\n" + "="*70)
    print("SCENARIO 1: Service with ALL categories fully populated")
    print("="*70)
    aadhaar = repo.get_service("aadhaar_name_change")
    print_service_summary(aadhaar)
    
    # Scenario 2: Some empty categories
    print("\n\n" + "="*70)
    print("SCENARIO 2: Service with SOME empty categories")
    print("="*70)
    data_access = repo.get_service("data_access_request")
    print_service_summary(data_access)
    
    # Scenario 3: Single items
    print("\n\n" + "="*70)
    print("SCENARIO 3: Service with SINGLE items in each category")
    print("="*70)
    birth_cert = repo.get_service("birth_certificate")
    print_service_summary(birth_cert)
    
    # Scenario 4: Mixed categories
    print("\n\n" + "="*70)
    print("SCENARIO 4: Service with MIXED category population")
    print("="*70)
    status_tracking = repo.get_service("service_status_tracking")
    print_service_summary(status_tracking)
    
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
