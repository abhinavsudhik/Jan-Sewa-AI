"""Enhanced mock service data for testing and development.

This module provides comprehensive mock data for at least 3 government services,
demonstrating different scenarios:

1. Service with all categories fully populated (Aadhaar Name Change)
2. Service with some empty categories (Data Access Request)
3. Service with single items (Birth Certificate)

Each service includes realistic Indian government service examples with proper
addresses, websites, and timelines.
"""

from datetime import datetime
from typing import Dict
from app.models.enhanced_service import (
    EnhancedServiceGuide,
    OfficeLocation,
    RequiredDocument,
    OfficeVisitStep,
    OfficialWebsiteLink,
    ProcessingTimeline,
    Coordinates,
)
from app.models.schemas import ServiceCategory


def get_enhanced_mock_services() -> Dict[str, EnhancedServiceGuide]:
    """
    Get comprehensive mock service data.
    
    Returns:
        Dictionary mapping service_id to EnhancedServiceGuide
    """
    return {
        "aadhaar_name_change": _create_aadhaar_name_change_service(),
        "data_access_request": _create_data_access_request_service(),
        "birth_certificate": _create_birth_certificate_service(),
        "service_status_tracking": _create_service_status_tracking_service(),
    }


def _create_aadhaar_name_change_service() -> EnhancedServiceGuide:
    """
    Service with all categories fully populated.
    
    Demonstrates:
    - Multiple office locations with coordinates
    - Multiple required documents with specifications
    - Multi-step office visit sequence
    - Multiple official websites
    - Both standard and expedited processing timelines
    """
    return EnhancedServiceGuide(
        # Basic information
        service_id="aadhaar_name_change",
        service_name="Aadhaar Name Change",
        category=ServiceCategory.AADHAAR,
        description="Update your name in the Aadhaar database due to marriage, legal name change, or correction of errors.",
        
        # Office locations - multiple with full details
        office_locations=[
            OfficeLocation(
                name="UIDAI Regional Office - Delhi",
                address="2nd Floor, MTNL Building, Kidwai Nagar East",
                city="New Delhi",
                state="Delhi",
                postal_code="110023",
                coordinates=Coordinates(latitude=28.5672, longitude=77.2100),
                operating_hours="Monday-Friday: 9:30 AM - 5:30 PM",
                contact_phone="+91-11-23466868"
            ),
            OfficeLocation(
                name="Aadhaar Seva Kendra - Connaught Place",
                address="Block A, Connaught Place, Inner Circle",
                city="New Delhi",
                state="Delhi",
                postal_code="110001",
                coordinates=Coordinates(latitude=28.6315, longitude=77.2167),
                operating_hours="Monday-Saturday: 10:00 AM - 6:00 PM",
                contact_phone="+91-11-23417777"
            ),
            OfficeLocation(
                name="Common Service Centre - Rohini",
                address="Sector 7, Rohini",
                city="New Delhi",
                state="Delhi",
                postal_code="110085",
                coordinates=Coordinates(latitude=28.7041, longitude=77.1025),
                operating_hours="Monday-Saturday: 9:00 AM - 7:00 PM",
                contact_phone="+91-11-27555444"
            ),
        ],
        
        # Required documents - multiple with specifications
        required_documents=[
            RequiredDocument(
                document_name="Aadhaar Card",
                description="Original Aadhaar card or e-Aadhaar printout",
                copies_required=2,
                format_requirements="Original + 1 photocopy",
                is_mandatory=True,
            ),
            RequiredDocument(
                document_name="Proof of Identity (PoI)",
                description="Document showing your new name",
                copies_required=1,
                format_requirements="Self-attested photocopy",
                is_mandatory=True,
                alternatives=[
                    "Passport",
                    "PAN Card",
                    "Driving License",
                    "Marriage Certificate (for name change after marriage)",
                    "Gazette notification (for legal name change)"
                ]
            ),
            RequiredDocument(
                document_name="Proof of Address (PoA)",
                description="Current address verification",
                copies_required=1,
                format_requirements="Self-attested photocopy",
                is_mandatory=True,
                alternatives=[
                    "Passport",
                    "Bank Statement",
                    "Electricity Bill",
                    "Telephone Bill",
                    "Ration Card"
                ]
            ),
            RequiredDocument(
                document_name="Supporting Document for Name Change",
                description="Legal document justifying the name change",
                copies_required=1,
                format_requirements="Original + self-attested photocopy",
                is_mandatory=True,
                alternatives=[
                    "Marriage Certificate (for post-marriage name change)",
                    "Gazette Notification (for legal name change)",
                    "Court Order (for court-ordered name change)",
                    "Affidavit on stamp paper (for minor corrections)"
                ]
            ),
        ],
        
        # Office visit sequence - multi-step process
        office_visit_sequence=[
            OfficeVisitStep(
                sequence_number=1,
                office_name="Aadhaar Seva Kendra or CSC",
                purpose="Submit name change request with documents and biometric verification",
                estimated_duration="45-60 minutes",
                is_optional=False,
                is_conditional=False,
            ),
            OfficeVisitStep(
                sequence_number=2,
                office_name="Document Verification Center",
                purpose="Additional document verification if requested by UIDAI",
                estimated_duration="30 minutes",
                is_optional=False,
                is_conditional=True,
                condition="Only if UIDAI requests additional verification"
            ),
            OfficeVisitStep(
                sequence_number=3,
                office_name="Aadhaar Seva Kendra",
                purpose="Collect updated Aadhaar card (if opted for physical card)",
                estimated_duration="15 minutes",
                is_optional=True,
                is_conditional=False,
            ),
        ],
        
        # Official websites - multiple with purposes
        official_websites=[
            OfficialWebsiteLink(
                url="https://uidai.gov.in/",
                purpose="UIDAI Official Website",
                description="Main portal for Aadhaar information and services"
            ),
            OfficialWebsiteLink(
                url="https://ssup.uidai.gov.in/",
                purpose="Self Service Update Portal",
                description="Online portal to initiate Aadhaar update requests"
            ),
            OfficialWebsiteLink(
                url="https://resident.uidai.gov.in/check-aadhaar-status",
                purpose="Status Tracking",
                description="Check the status of your Aadhaar update request"
            ),
            OfficialWebsiteLink(
                url="https://appointments.uidai.gov.in/",
                purpose="Appointment Booking",
                description="Book appointment at Aadhaar Seva Kendra"
            ),
        ],
        
        # Processing timelines - both standard and expedited
        processing_timelines=[
            ProcessingTimeline(
                minimum_days=15,
                maximum_days=90,
                typical_days=30,
                time_unit="days",
                processing_type="standard",
                notes="Processing time starts after successful biometric verification",
                factors_affecting_time=[
                    "Document verification complexity",
                    "UIDAI workload at the time of submission",
                    "Completeness of submitted documents",
                    "Need for additional verification"
                ]
            ),
            ProcessingTimeline(
                minimum_days=7,
                maximum_days=15,
                typical_days=10,
                time_unit="days",
                processing_type="expedited",
                notes="Available for urgent cases with additional fee of ₹100",
                factors_affecting_time=[
                    "Availability of expedited service at the center",
                    "Document completeness"
                ]
            ),
        ],
        
        # Metadata
        last_updated=datetime(2024, 1, 15, 10, 30, 0),
        data_source="UIDAI Official Guidelines 2024",
        available_languages=["en", "hi"],
    )


def _create_data_access_request_service() -> EnhancedServiceGuide:
    """
    Service with some empty categories.
    
    Demonstrates:
    - Some categories populated, others empty
    - "Information not available" handling for empty categories
    - Realistic scenario where not all information is available
    """
    return EnhancedServiceGuide(
        # Basic information
        service_id="data_access_request",
        service_name="Personal Data Access Request",
        category=ServiceCategory.DATA_ACCESS,
        description="Request access to your personal data held by government departments under the Right to Information Act.",
        
        # Office locations - empty (online-only service)
        office_locations=[],
        
        # Required documents - populated
        required_documents=[
            RequiredDocument(
                document_name="Identity Proof",
                description="Government-issued photo ID",
                copies_required=1,
                format_requirements="Scanned copy in PDF format",
                is_mandatory=True,
                alternatives=[
                    "Aadhaar Card",
                    "Passport",
                    "Driving License",
                    "Voter ID"
                ]
            ),
            RequiredDocument(
                document_name="Address Proof",
                description="Current residential address verification",
                copies_required=1,
                format_requirements="Scanned copy in PDF format",
                is_mandatory=True,
                alternatives=[
                    "Utility Bill (not older than 3 months)",
                    "Bank Statement",
                    "Aadhaar Card"
                ]
            ),
        ],
        
        # Office visit sequence - empty (online-only)
        office_visit_sequence=[],
        
        # Official websites - populated
        official_websites=[
            OfficialWebsiteLink(
                url="https://rtionline.gov.in/",
                purpose="RTI Online Portal",
                description="Submit and track RTI applications online"
            ),
            OfficialWebsiteLink(
                url="https://dsci.in/data-protection",
                purpose="Data Protection Guidelines",
                description="Information about data protection rights in India"
            ),
        ],
        
        # Processing timelines - populated
        processing_timelines=[
            ProcessingTimeline(
                minimum_days=30,
                maximum_days=60,
                typical_days=45,
                time_unit="days",
                processing_type="standard",
                notes="As per RTI Act, response must be provided within 30 days",
                factors_affecting_time=[
                    "Complexity of data request",
                    "Number of departments involved",
                    "Volume of data requested"
                ]
            ),
        ],
        
        # Metadata
        last_updated=datetime(2024, 1, 10, 14, 0, 0),
        data_source="RTI Act 2005 and Digital Personal Data Protection Act 2023",
        available_languages=["en", "hi"],
    )


def _create_birth_certificate_service() -> EnhancedServiceGuide:
    """
    Service with single items in each category.
    
    Demonstrates:
    - Single office location
    - Single document
    - Single office visit (no numbering)
    - Single website
    - Single timeline
    """
    return EnhancedServiceGuide(
        # Basic information
        service_id="birth_certificate",
        service_name="Birth Certificate Issuance",
        category=ServiceCategory.CERTIFICATE,
        description="Obtain an official birth certificate from the Municipal Corporation for births registered in the city.",
        
        # Office locations - single location
        office_locations=[
            OfficeLocation(
                name="Municipal Corporation Office - Birth & Death Registration",
                address="Town Hall, Chandni Chowk",
                city="New Delhi",
                state="Delhi",
                postal_code="110006",
                coordinates=Coordinates(latitude=28.6507, longitude=77.2334),
                operating_hours="Monday-Friday: 10:00 AM - 4:00 PM",
                contact_phone="+91-11-23941234"
            ),
        ],
        
        # Required documents - single document
        required_documents=[
            RequiredDocument(
                document_name="Birth Registration Acknowledgment",
                description="Hospital-issued birth registration form or acknowledgment slip",
                copies_required=1,
                format_requirements="Original document",
                is_mandatory=True,
            ),
        ],
        
        # Office visit sequence - single visit (no numbering per requirement 4.4)
        office_visit_sequence=[
            OfficeVisitStep(
                sequence_number=1,
                office_name="Municipal Corporation Office",
                purpose="Submit birth registration acknowledgment and collect certificate",
                estimated_duration="30 minutes",
                is_optional=False,
                is_conditional=False,
            ),
        ],
        
        # Official websites - single website
        official_websites=[
            OfficialWebsiteLink(
                url="https://mcdonline.nic.in/",
                purpose="Municipal Corporation Portal",
                description="Online services for birth and death certificates"
            ),
        ],
        
        # Processing timelines - single timeline
        processing_timelines=[
            ProcessingTimeline(
                minimum_days=1,
                maximum_days=7,
                typical_days=3,
                time_unit="days",
                processing_type="standard",
                notes="Instant issuance available for births registered within 21 days",
                factors_affecting_time=[
                    "Time elapsed since birth registration",
                    "Completeness of hospital records"
                ]
            ),
        ],
        
        # Metadata
        last_updated=datetime(2024, 1, 20, 9, 0, 0),
        data_source="Municipal Corporation of Delhi - Birth Registration Guidelines",
        available_languages=["en", "hi"],
    )


def _create_service_status_tracking_service() -> EnhancedServiceGuide:
    """
    Service with mixed categories (some populated, some with multiple items).
    
    Demonstrates:
    - Mixed scenario with varying data completeness
    - Some categories with multiple items, others with single items
    - Realistic government service tracking scenario
    """
    return EnhancedServiceGuide(
        # Basic information
        service_id="service_status_tracking",
        service_name="Government Service Status Tracking",
        category=ServiceCategory.STATUS_INQUIRY,
        description="Track the status of your government service applications and requests across various departments.",
        
        # Office locations - multiple locations
        office_locations=[
            OfficeLocation(
                name="Citizen Service Center - Central Delhi",
                address="Vikas Bhawan, INA Market",
                city="New Delhi",
                state="Delhi",
                postal_code="110023",
                coordinates=Coordinates(latitude=28.5706, longitude=77.2144),
                operating_hours="Monday-Friday: 9:00 AM - 6:00 PM",
                contact_phone="+91-11-24651234"
            ),
            OfficeLocation(
                name="District Collectorate - Help Desk",
                address="District Collectorate Complex, Rajouri Garden",
                city="New Delhi",
                state="Delhi",
                postal_code="110027",
                coordinates=Coordinates(latitude=28.6469, longitude=77.1200),
                operating_hours="Monday-Saturday: 10:00 AM - 5:00 PM",
                contact_phone="+91-11-25555678"
            ),
        ],
        
        # Required documents - single document
        required_documents=[
            RequiredDocument(
                document_name="Application Reference Number",
                description="Reference number or acknowledgment receipt from original application",
                copies_required=1,
                format_requirements="Original receipt or printed confirmation",
                is_mandatory=True,
                alternatives=[
                    "SMS confirmation with reference number",
                    "Email confirmation from department",
                    "Online application dashboard screenshot"
                ]
            ),
        ],
        
        # Office visit sequence - empty (online service primarily)
        office_visit_sequence=[],
        
        # Official websites - multiple websites
        official_websites=[
            OfficialWebsiteLink(
                url="https://serviceonline.gov.in/",
                purpose="Unified Service Portal",
                description="Track applications across all government departments"
            ),
            OfficialWebsiteLink(
                url="https://pgportal.gov.in/",
                purpose="Public Grievance Portal",
                description="File complaints and track grievance status"
            ),
            OfficialWebsiteLink(
                url="https://digitalindia.gov.in/services",
                purpose="Digital India Services",
                description="Access digital government services and track progress"
            ),
        ],
        
        # Processing timelines - multiple timelines for different service types
        processing_timelines=[
            ProcessingTimeline(
                minimum_days=1,
                maximum_days=3,
                typical_days=1,
                time_unit="days",
                processing_type="status_update",
                notes="Status updates are typically available within 24 hours",
                factors_affecting_time=[
                    "Department response time",
                    "System maintenance windows"
                ]
            ),
            ProcessingTimeline(
                minimum_days=7,
                maximum_days=30,
                typical_days=14,
                time_unit="days",
                processing_type="issue_resolution",
                notes="Time to resolve status-related issues or discrepancies",
                factors_affecting_time=[
                    "Complexity of the issue",
                    "Department workload",
                    "Need for manual verification"
                ]
            ),
        ],
        
        # Metadata
        last_updated=datetime(2024, 1, 18, 16, 45, 0),
        data_source="Digital India Initiative - Service Tracking Guidelines 2024",
        available_languages=["en", "hi", "bn"],
    )
