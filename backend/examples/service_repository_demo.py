"""Demo script showing ServiceRepository functionality.

This script demonstrates:
1. Loading services from enhanced mock data
2. CRUD operations
3. Timestamp-based version selection
4. Integration with enhanced mock data
"""

from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.repositories.service_repository import ServiceRepository
from app.models.enhanced_service import EnhancedServiceGuide
from app.models.schemas import ServiceCategory


def main():
    """Demonstrate ServiceRepository functionality."""
    print("=== ServiceRepository Demo ===\n")
    
    # Initialize repository
    print("1. Initializing ServiceRepository...")
    repo = ServiceRepository()
    print(f"   Loaded {repo.get_service_count()} services\n")
    
    # Show all available services
    print("2. Available services:")
    services = repo.get_all_services()
    for service in services:
        print(f"   - {service.service_id}: {service.service_name}")
        print(f"     Category: {service.category.value}")
        print(f"     Last updated: {service.last_updated}")
        print(f"     Data source: {service.data_source}")
        print()
    
    # Demonstrate getting a specific service
    print("3. Getting specific service (Aadhaar Name Change):")
    aadhaar_service = repo.get_service("aadhaar_name_change")
    if aadhaar_service:
        print(f"   Service: {aadhaar_service.service_name}")
        print(f"   Description: {aadhaar_service.description}")
        print(f"   Office locations: {len(aadhaar_service.office_locations)}")
        print(f"   Required documents: {len(aadhaar_service.required_documents)}")
        print(f"   Office visit steps: {len(aadhaar_service.office_visit_sequence)}")
        print(f"   Official websites: {len(aadhaar_service.official_websites)}")
        print(f"   Processing timelines: {len(aadhaar_service.processing_timelines)}")
        print()
    
    # Demonstrate services by category
    print("4. Services by category (aadhaar):")
    aadhaar_services = repo.get_services_by_category("aadhaar")
    for service in aadhaar_services:
        print(f"   - {service.service_name}")
    print()
    
    # Demonstrate service updates and version management
    print("5. Demonstrating service updates and version management:")
    
    # Create an updated version of an existing service
    if aadhaar_service:
        original_timestamp = aadhaar_service.last_updated
        print(f"   Original timestamp: {original_timestamp}")
        
        # Create updated version
        updated_service = EnhancedServiceGuide(
            service_id="aadhaar_name_change",
            service_name="Aadhaar Name Change (Updated)",
            category=ServiceCategory.AADHAAR,
            description="Updated process for Aadhaar name changes with new requirements",
            office_locations=aadhaar_service.office_locations,
            required_documents=aadhaar_service.required_documents,
            office_visit_sequence=aadhaar_service.office_visit_sequence,
            official_websites=aadhaar_service.official_websites,
            processing_timelines=aadhaar_service.processing_timelines,
            last_updated=original_timestamp + timedelta(days=1),
            data_source="Updated Guidelines 2024",
            available_languages=["en", "hi"]
        )
        
        # Update the service
        repo.update_service(updated_service)
        print(f"   Updated timestamp: {updated_service.last_updated}")
        
        # Verify latest version is returned
        current_service = repo.get_service("aadhaar_name_change")
        print(f"   Current service name: {current_service.service_name}")
        print(f"   Current timestamp: {current_service.last_updated}")
        
        # Show version history
        versions = repo.get_service_versions("aadhaar_name_change")
        print(f"   Total versions: {len(versions)}")
        for i, version in enumerate(versions):
            print(f"     Version {i+1}: {version.last_updated} - {version.service_name}")
        print()
    
    # Demonstrate adding a new service
    print("6. Adding a new service:")
    new_service = EnhancedServiceGuide(
        service_id="demo_service",
        service_name="Demo Service",
        category=ServiceCategory.CERTIFICATE,
        description="A demo service for testing purposes",
        last_updated=datetime.now(),
        data_source="Demo Script"
    )
    
    repo.update_service(new_service)
    print(f"   Added service: {new_service.service_name}")
    print(f"   Total services now: {repo.get_service_count()}")
    
    # Verify the new service exists
    retrieved_demo = repo.get_service("demo_service")
    if retrieved_demo:
        print(f"   Successfully retrieved: {retrieved_demo.service_name}")
    print()
    
    # Demonstrate empty categories handling
    print("7. Service with empty categories (Data Access Request):")
    data_service = repo.get_service("data_access_request")
    if data_service:
        print(f"   Service: {data_service.service_name}")
        print(f"   Office locations (empty): {len(data_service.office_locations)}")
        print(f"   Office visit sequence (empty): {len(data_service.office_visit_sequence)}")
        print(f"   Required documents (populated): {len(data_service.required_documents)}")
        print(f"   Official websites (populated): {len(data_service.official_websites)}")
        print()
    
    # Demonstrate single item categories
    print("8. Service with single items (Birth Certificate):")
    birth_service = repo.get_service("birth_certificate")
    if birth_service:
        print(f"   Service: {birth_service.service_name}")
        print(f"   Office locations: {len(birth_service.office_locations)}")
        print(f"   Required documents: {len(birth_service.required_documents)}")
        print(f"   Office visit sequence: {len(birth_service.office_visit_sequence)}")
        print(f"   Official websites: {len(birth_service.official_websites)}")
        print(f"   Processing timelines: {len(birth_service.processing_timelines)}")
        
        # Show the single office visit step (should not be numbered per requirement 4.4)
        if birth_service.office_visit_sequence:
            step = birth_service.office_visit_sequence[0]
            print(f"   Single office visit: {step.office_name} - {step.purpose}")
        print()
    
    print("=== Demo Complete ===")


if __name__ == "__main__":
    main()