"""Unit tests for enhanced service data models.

Tests validation logic for all five category models and EnhancedServiceGuide.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError, HttpUrl

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


class TestCoordinates:
    """Test Coordinates model validation."""
    
    def test_valid_coordinates(self):
        """Test valid latitude and longitude."""
        coords = Coordinates(latitude=19.0760, longitude=72.8777)
        assert coords.latitude == 19.0760
        assert coords.longitude == 72.8777
    
    def test_latitude_out_of_range_high(self):
        """Test latitude validation fails for values > 90."""
        with pytest.raises(ValidationError) as exc_info:
            Coordinates(latitude=91.0, longitude=0.0)
        assert "Latitude must be between -90 and 90" in str(exc_info.value)
    
    def test_latitude_out_of_range_low(self):
        """Test latitude validation fails for values < -90."""
        with pytest.raises(ValidationError) as exc_info:
            Coordinates(latitude=-91.0, longitude=0.0)
        assert "Latitude must be between -90 and 90" in str(exc_info.value)
    
    def test_longitude_out_of_range_high(self):
        """Test longitude validation fails for values > 180."""
        with pytest.raises(ValidationError) as exc_info:
            Coordinates(latitude=0.0, longitude=181.0)
        assert "Longitude must be between -180 and 180" in str(exc_info.value)
    
    def test_longitude_out_of_range_low(self):
        """Test longitude validation fails for values < -180."""
        with pytest.raises(ValidationError) as exc_info:
            Coordinates(latitude=0.0, longitude=-181.0)
        assert "Longitude must be between -180 and 180" in str(exc_info.value)
    
    def test_boundary_values(self):
        """Test boundary values are accepted."""
        coords1 = Coordinates(latitude=90.0, longitude=180.0)
        assert coords1.latitude == 90.0
        assert coords1.longitude == 180.0
        
        coords2 = Coordinates(latitude=-90.0, longitude=-180.0)
        assert coords2.latitude == -90.0
        assert coords2.longitude == -180.0


class TestOfficeLocation:
    """Test OfficeLocation model."""
    
    def test_valid_office_location_minimal(self):
        """Test office location with required fields only."""
        location = OfficeLocation(
            name="District Collectorate",
            address="123 Main Street",
            city="Mumbai",
            state="Maharashtra",
            postal_code="400001"
        )
        assert location.name == "District Collectorate"
        assert location.coordinates is None
        assert location.operating_hours is None
        assert location.contact_phone is None
    
    def test_valid_office_location_complete(self):
        """Test office location with all fields."""
        location = OfficeLocation(
            name="District Collectorate",
            address="123 Main Street",
            city="Mumbai",
            state="Maharashtra",
            postal_code="400001",
            coordinates=Coordinates(latitude=19.0760, longitude=72.8777),
            operating_hours="Mon-Fri 9:00 AM - 5:00 PM",
            contact_phone="+91-22-12345678"
        )
        assert location.coordinates is not None
        assert location.coordinates.latitude == 19.0760
        assert location.operating_hours == "Mon-Fri 9:00 AM - 5:00 PM"
    
    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        with pytest.raises(ValidationError):
            OfficeLocation(
                name="Office",
                address="123 Main St"
                # Missing city, state, postal_code
            )


class TestRequiredDocument:
    """Test RequiredDocument model validation."""
    
    def test_valid_document_minimal(self):
        """Test document with required fields only."""
        doc = RequiredDocument(document_name="Aadhaar Card")
        assert doc.document_name == "Aadhaar Card"
        assert doc.copies_required == 1
        assert doc.is_mandatory is True
        assert doc.description is None
    
    def test_valid_document_complete(self):
        """Test document with all fields."""
        doc = RequiredDocument(
            document_name="Aadhaar Card",
            description="Government-issued identity card",
            copies_required=2,
            format_requirements="Original + photocopy",
            is_mandatory=True,
            alternatives=["Passport", "Voter ID"]
        )
        assert doc.copies_required == 2
        assert doc.format_requirements == "Original + photocopy"
        assert len(doc.alternatives) == 2
    
    def test_copies_required_validation_zero(self):
        """Test copies_required validation fails for 0."""
        with pytest.raises(ValidationError) as exc_info:
            RequiredDocument(
                document_name="Test Document",
                copies_required=0
            )
        assert "copies_required must be >= 1" in str(exc_info.value)
    
    def test_copies_required_validation_negative(self):
        """Test copies_required validation fails for negative values."""
        with pytest.raises(ValidationError) as exc_info:
            RequiredDocument(
                document_name="Test Document",
                copies_required=-1
            )
        assert "copies_required must be >= 1" in str(exc_info.value)
    
    def test_optional_document(self):
        """Test optional document (is_mandatory=False)."""
        doc = RequiredDocument(
            document_name="Optional Document",
            is_mandatory=False
        )
        assert doc.is_mandatory is False


class TestOfficeVisitStep:
    """Test OfficeVisitStep model."""
    
    def test_valid_step_minimal(self):
        """Test step with required fields only."""
        step = OfficeVisitStep(
            sequence_number=1,
            office_name="Main Office",
            purpose="Submit application",
            estimated_duration="30 minutes"
        )
        assert step.sequence_number == 1
        assert step.is_optional is False
        assert step.is_conditional is False
        assert step.condition is None
    
    def test_valid_step_optional(self):
        """Test optional step."""
        step = OfficeVisitStep(
            sequence_number=2,
            office_name="Optional Office",
            purpose="Additional verification",
            estimated_duration="15 minutes",
            is_optional=True
        )
        assert step.is_optional is True
    
    def test_valid_step_conditional(self):
        """Test conditional step with condition."""
        step = OfficeVisitStep(
            sequence_number=3,
            office_name="Conditional Office",
            purpose="Special processing",
            estimated_duration="1 hour",
            is_conditional=True,
            condition="If applicant is under 18"
        )
        assert step.is_conditional is True
        assert step.condition == "If applicant is under 18"


class TestOfficialWebsiteLink:
    """Test OfficialWebsiteLink model validation."""
    
    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        link = OfficialWebsiteLink(
            url="https://example.gov.in",
            purpose="Application Portal"
        )
        assert str(link.url) == "https://example.gov.in/"
        assert link.purpose == "Application Portal"
    
    def test_valid_http_url_logs_warning(self, caplog):
        """Test HTTP URL is accepted but logs warning."""
        link = OfficialWebsiteLink(
            url="http://example.gov.in",
            purpose="Legacy Portal"
        )
        assert str(link.url) == "http://example.gov.in/"
        # Warning should be logged
        assert any("HTTP URL detected" in record.message for record in caplog.records)
    
    def test_url_with_description(self):
        """Test URL with optional description."""
        link = OfficialWebsiteLink(
            url="https://example.gov.in",
            purpose="Status Tracking",
            description="Track your application status online"
        )
        assert link.description == "Track your application status online"
    
    def test_invalid_url(self):
        """Test invalid URL format fails validation."""
        with pytest.raises(ValidationError):
            OfficialWebsiteLink(
                url="not-a-valid-url",
                purpose="Test"
            )


class TestProcessingTimeline:
    """Test ProcessingTimeline model validation."""
    
    def test_valid_timeline(self):
        """Test valid timeline with proper range."""
        timeline = ProcessingTimeline(
            minimum_days=7,
            maximum_days=30,
            typical_days=14
        )
        assert timeline.minimum_days == 7
        assert timeline.typical_days == 14
        assert timeline.maximum_days == 30
        assert timeline.time_unit == "days"
        assert timeline.processing_type == "standard"
    
    def test_timeline_range_string(self):
        """Test as_range_string method."""
        timeline = ProcessingTimeline(
            minimum_days=7,
            maximum_days=30,
            typical_days=14
        )
        assert timeline.as_range_string() == "7-30 days"
    
    def test_timeline_with_custom_unit(self):
        """Test timeline with custom time unit."""
        timeline = ProcessingTimeline(
            minimum_days=2,
            maximum_days=8,
            typical_days=4,
            time_unit="weeks"
        )
        assert timeline.time_unit == "weeks"
        assert timeline.as_range_string() == "2-8 weeks"
    
    def test_timeline_with_notes_and_factors(self):
        """Test timeline with notes and affecting factors."""
        timeline = ProcessingTimeline(
            minimum_days=7,
            maximum_days=30,
            typical_days=14,
            notes="Processing time may vary during peak season",
            factors_affecting_time=[
                "Document completeness",
                "Verification requirements",
                "Peak season delays"
            ]
        )
        assert timeline.notes is not None
        assert len(timeline.factors_affecting_time) == 3
    
    def test_timeline_validation_min_greater_than_typical(self):
        """Test validation fails when minimum > typical."""
        with pytest.raises(ValidationError) as exc_info:
            ProcessingTimeline(
                minimum_days=20,
                maximum_days=30,
                typical_days=14
            )
        assert "minimum <= typical <= maximum" in str(exc_info.value)
    
    def test_timeline_validation_typical_greater_than_max(self):
        """Test validation fails when typical > maximum."""
        with pytest.raises(ValidationError) as exc_info:
            ProcessingTimeline(
                minimum_days=7,
                maximum_days=30,
                typical_days=35
            )
        assert "minimum <= typical <= maximum" in str(exc_info.value)
    
    def test_timeline_validation_min_greater_than_max(self):
        """Test validation fails when minimum > maximum."""
        with pytest.raises(ValidationError) as exc_info:
            ProcessingTimeline(
                minimum_days=30,
                maximum_days=7,
                typical_days=14
            )
        assert "minimum <= typical <= maximum" in str(exc_info.value)
    
    def test_expedited_processing(self):
        """Test expedited processing timeline."""
        timeline = ProcessingTimeline(
            minimum_days=1,
            maximum_days=3,
            typical_days=2,
            processing_type="expedited"
        )
        assert timeline.processing_type == "expedited"


class TestEnhancedServiceGuide:
    """Test EnhancedServiceGuide model."""
    
    def test_valid_service_guide_minimal(self):
        """Test service guide with required fields only."""
        guide = EnhancedServiceGuide(
            service_id="test_service",
            service_name="Test Service",
            category=ServiceCategory.CERTIFICATE,
            description="A test service",
            last_updated=datetime.now(),
            data_source="test"
        )
        assert guide.service_id == "test_service"
        assert len(guide.office_locations) == 0
        assert len(guide.required_documents) == 0
        assert len(guide.office_visit_sequence) == 0
        assert len(guide.official_websites) == 0
        assert len(guide.processing_timelines) == 0
        assert guide.available_languages == ["en"]
    
    def test_valid_service_guide_complete(self):
        """Test service guide with all categories populated."""
        guide = EnhancedServiceGuide(
            service_id="aadhaar_name_change",
            service_name="Aadhaar Name Change",
            category=ServiceCategory.AADHAAR,
            description="Update name in Aadhaar card",
            office_locations=[
                OfficeLocation(
                    name="District Office",
                    address="123 Main St",
                    city="Mumbai",
                    state="Maharashtra",
                    postal_code="400001"
                )
            ],
            required_documents=[
                RequiredDocument(
                    document_name="Aadhaar Card",
                    copies_required=1
                )
            ],
            office_visit_sequence=[
                OfficeVisitStep(
                    sequence_number=1,
                    office_name="Main Office",
                    purpose="Submit application",
                    estimated_duration="30 minutes"
                )
            ],
            official_websites=[
                OfficialWebsiteLink(
                    url="https://uidai.gov.in",
                    purpose="Official Portal"
                )
            ],
            processing_timelines=[
                ProcessingTimeline(
                    minimum_days=7,
                    maximum_days=30,
                    typical_days=14
                )
            ],
            last_updated=datetime.now(),
            data_source="mock_data",
            available_languages=["en", "hi"]
        )
        assert len(guide.office_locations) == 1
        assert len(guide.required_documents) == 1
        assert len(guide.office_visit_sequence) == 1
        assert len(guide.official_websites) == 1
        assert len(guide.processing_timelines) == 1
        assert "hi" in guide.available_languages
    
    def test_service_guide_with_legacy_fields(self):
        """Test service guide with legacy compatibility fields."""
        guide = EnhancedServiceGuide(
            service_id="test_service",
            service_name="Test Service",
            category=ServiceCategory.CERTIFICATE,
            description="A test service",
            last_updated=datetime.now(),
            data_source="test",
            steps=[{"step_number": 1, "description": "Legacy step"}],
            processing_time={"minimum": "7 days", "maximum": "30 days"},
            official_portal_url="https://example.gov.in",
            contact_info={"phone": "123-456-7890"}
        )
        assert guide.steps is not None
        assert guide.processing_time is not None
        assert guide.official_portal_url is not None
        assert guide.contact_info is not None
    
    def test_service_guide_multiple_timelines(self):
        """Test service guide with both standard and expedited timelines."""
        guide = EnhancedServiceGuide(
            service_id="test_service",
            service_name="Test Service",
            category=ServiceCategory.CERTIFICATE,
            description="A test service",
            processing_timelines=[
                ProcessingTimeline(
                    minimum_days=7,
                    maximum_days=30,
                    typical_days=14,
                    processing_type="standard"
                ),
                ProcessingTimeline(
                    minimum_days=1,
                    maximum_days=3,
                    typical_days=2,
                    processing_type="expedited"
                )
            ],
            last_updated=datetime.now(),
            data_source="test"
        )
        assert len(guide.processing_timelines) == 2
        assert guide.processing_timelines[0].processing_type == "standard"
        assert guide.processing_timelines[1].processing_type == "expedited"
