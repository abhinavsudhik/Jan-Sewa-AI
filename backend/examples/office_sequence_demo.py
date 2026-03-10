"""Demonstration of office visit sequence formatting.

This example shows how the _format_office_sequence() method handles:
1. Single office visit (no numbering)
2. Multiple office visits (numbered sequence)
3. Optional steps
4. Conditional steps
"""

from datetime import datetime
from app.services.response_formatter import ResponseFormatter
from app.models.enhanced_service import (
    EnhancedServiceGuide,
    OfficeVisitStep
)
from app.models.schemas import ServiceCategory


def create_demo_service(name, description, sequence):
    """Helper to create a demo service."""
    return EnhancedServiceGuide(
        service_id=name.lower().replace(" ", "_"),
        service_name=name,
        category=ServiceCategory.CERTIFICATE,
        description=description,
        office_locations=[],
        required_documents=[],
        office_visit_sequence=sequence,
        official_websites=[],
        processing_timelines=[],
        last_updated=datetime.now(),
        data_source="demo"
    )


def demo_single_office():
    """Demonstrate single office visit formatting (no numbering)."""
    print("=" * 70)
    print("DEMO 1: Single Office Visit (No Numbering)")
    print("=" * 70)
    
    service = create_demo_service(
        "Simple Certificate Request",
        "A service requiring only one office visit",
        [
            OfficeVisitStep(
                sequence_number=1,
                office_name="Main Office",
                purpose="Submit application and documents",
                estimated_duration="30 minutes"
            )
        ]
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    print(f"\nService: {response.service_name}")
    print(f"Description: {response.description}\n")
    print(response.sections[2].header)
    print(response.sections[2].content)
    print()


def demo_multiple_offices():
    """Demonstrate multiple office visits with numbering."""
    print("=" * 70)
    print("DEMO 2: Multiple Office Visits (Numbered Sequence)")
    print("=" * 70)
    
    service = create_demo_service(
        "Aadhaar Name Change",
        "Update name in Aadhaar card",
        [
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
        ]
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    print(f"\nService: {response.service_name}")
    print(f"Description: {response.description}\n")
    print(response.sections[2].header)
    print(response.sections[2].content)
    print()


def demo_optional_steps():
    """Demonstrate optional step marking."""
    print("=" * 70)
    print("DEMO 3: Office Sequence with Optional Step")
    print("=" * 70)
    
    service = create_demo_service(
        "Passport Application",
        "Apply for new passport",
        [
            OfficeVisitStep(
                sequence_number=1,
                office_name="Passport Seva Kendra",
                purpose="Submit application and biometric data",
                estimated_duration="60 minutes"
            ),
            OfficeVisitStep(
                sequence_number=2,
                office_name="Police Verification Office",
                purpose="Police verification (if required)",
                estimated_duration="30 minutes",
                is_optional=True
            ),
            OfficeVisitStep(
                sequence_number=3,
                office_name="Collection Center",
                purpose="Collect passport",
                estimated_duration="15 minutes"
            )
        ]
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    print(f"\nService: {response.service_name}")
    print(f"Description: {response.description}\n")
    print(response.sections[2].header)
    print(response.sections[2].content)
    print()


def demo_conditional_steps():
    """Demonstrate conditional step marking."""
    print("=" * 70)
    print("DEMO 4: Office Sequence with Conditional Step")
    print("=" * 70)
    
    service = create_demo_service(
        "Driving License Renewal",
        "Renew existing driving license",
        [
            OfficeVisitStep(
                sequence_number=1,
                office_name="RTO Office",
                purpose="Submit renewal application and documents",
                estimated_duration="45 minutes"
            ),
            OfficeVisitStep(
                sequence_number=2,
                office_name="Medical Examination Center",
                purpose="Medical fitness test",
                estimated_duration="30 minutes",
                is_conditional=True,
                condition="Only if license is expired for more than 5 years"
            ),
            OfficeVisitStep(
                sequence_number=3,
                office_name="RTO Collection Counter",
                purpose="Collect renewed license",
                estimated_duration="20 minutes"
            )
        ]
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    print(f"\nService: {response.service_name}")
    print(f"Description: {response.description}\n")
    print(response.sections[2].header)
    print(response.sections[2].content)
    print()


def demo_optional_and_conditional():
    """Demonstrate step that is both optional and conditional."""
    print("=" * 70)
    print("DEMO 5: Office Sequence with Optional AND Conditional Step")
    print("=" * 70)
    
    service = create_demo_service(
        "Property Registration",
        "Register property ownership",
        [
            OfficeVisitStep(
                sequence_number=1,
                office_name="Sub-Registrar Office",
                purpose="Submit property documents and pay stamp duty",
                estimated_duration="90 minutes"
            ),
            OfficeVisitStep(
                sequence_number=2,
                office_name="Notary Office",
                purpose="Get documents notarized",
                estimated_duration="30 minutes",
                is_optional=True,
                is_conditional=True,
                condition="Only if physical card is requested"
            ),
            OfficeVisitStep(
                sequence_number=3,
                office_name="Sub-Registrar Office",
                purpose="Collect registered documents",
                estimated_duration="30 minutes"
            )
        ]
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    print(f"\nService: {response.service_name}")
    print(f"Description: {response.description}\n")
    print(response.sections[2].header)
    print(response.sections[2].content)
    print()


def demo_unsorted_sequence():
    """Demonstrate automatic sorting by sequence_number."""
    print("=" * 70)
    print("DEMO 6: Automatic Sorting by Sequence Number")
    print("=" * 70)
    print("(Steps provided in non-sequential order: 3, 1, 2)")
    print()
    
    # Create steps in non-sequential order
    service = create_demo_service(
        "Vehicle Registration",
        "Register new vehicle",
        [
            OfficeVisitStep(
                sequence_number=3,
                office_name="Number Plate Office",
                purpose="Collect number plates",
                estimated_duration="20 minutes"
            ),
            OfficeVisitStep(
                sequence_number=1,
                office_name="RTO Office",
                purpose="Submit vehicle documents and pay fees",
                estimated_duration="60 minutes"
            ),
            OfficeVisitStep(
                sequence_number=2,
                office_name="Inspection Center",
                purpose="Vehicle inspection and verification",
                estimated_duration="45 minutes"
            )
        ]
    )
    
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    print(f"Service: {response.service_name}")
    print(f"Description: {response.description}\n")
    print(response.sections[2].header)
    print(response.sections[2].content)
    print("\nNote: Steps are automatically sorted by sequence_number!")
    print()


if __name__ == "__main__":
    demo_single_office()
    demo_multiple_offices()
    demo_optional_steps()
    demo_conditional_steps()
    demo_optional_and_conditional()
    demo_unsorted_sequence()
    
    print("=" * 70)
    print("All demonstrations completed!")
    print("=" * 70)
