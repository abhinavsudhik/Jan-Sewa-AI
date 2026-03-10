"""Demonstration of website links and timeline formatting.

This example shows the enhanced formatting for:
- Official website links with descriptions
- Processing timelines with ranges, notes, and factors
"""

from datetime import datetime
from app.services.response_formatter import ResponseFormatter
from app.models.enhanced_service import (
    EnhancedServiceGuide,
    OfficialWebsiteLink,
    ProcessingTimeline
)
from app.models.schemas import ServiceCategory


def main():
    """Demonstrate website and timeline formatting."""
    
    # Create a service with comprehensive website and timeline data
    service = EnhancedServiceGuide(
        service_id="aadhaar_name_change",
        service_name="Aadhaar Name Change",
        category=ServiceCategory.IDENTITY_CARD,
        description="Update your name in Aadhaar card",
        
        # Official websites with descriptions
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
            ),
            OfficialWebsiteLink(
                url="https://resident.uidai.gov.in/check-aadhaar",
                purpose="Status Tracking",
                description="Check the status of your update request"
            )
        ],
        
        # Processing timelines with standard and expedited options
        processing_timelines=[
            ProcessingTimeline(
                minimum_days=7,
                maximum_days=30,
                typical_days=14,
                processing_type="standard",
                notes="Processing time may vary based on verification requirements",
                factors_affecting_time=[
                    "Document verification complexity",
                    "Biometric verification requirement",
                    "Regional office workload"
                ]
            ),
            ProcessingTimeline(
                minimum_days=1,
                maximum_days=3,
                typical_days=2,
                processing_type="expedited",
                notes="Available for urgent cases with additional fee"
            )
        ],
        
        last_updated=datetime.now(),
        data_source="demo"
    )
    
    # Format the service response
    formatter = ResponseFormatter()
    response = formatter.format_service_response(service)
    
    # Display the formatted response
    print("=" * 70)
    print(f"SERVICE: {response.service_name}")
    print(f"DESCRIPTION: {response.description}")
    print("=" * 70)
    print()
    
    for section in response.sections:
        print(section.header)
        print("-" * 70)
        print(section.content)
        print()
    
    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    
    # Show specific sections
    print("\n\n")
    print("DETAILED VIEW OF WEBSITE LINKS SECTION:")
    print("=" * 70)
    websites_section = response.sections[3]  # Official websites is 4th section
    print(websites_section.header)
    print("-" * 70)
    print(websites_section.content)
    print()
    
    print("\n\n")
    print("DETAILED VIEW OF PROCESSING TIMELINE SECTION:")
    print("=" * 70)
    timeline_section = response.sections[4]  # Processing timeline is 5th section
    print(timeline_section.header)
    print("-" * 70)
    print(timeline_section.content)
    print()


if __name__ == "__main__":
    main()
