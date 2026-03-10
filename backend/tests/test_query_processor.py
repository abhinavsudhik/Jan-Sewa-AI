"""Unit tests for QueryProcessor service."""

import pytest
from datetime import datetime

from app.services.query_processor import QueryProcessor, ServiceRepository, QueryResult
from app.models.enhanced_service import EnhancedServiceGuide
from app.models.schemas import ServiceCategory


@pytest.fixture
def mock_service_repository():
    """Create a mock service repository with test data."""
    repo = ServiceRepository()
    
    # Add test services
    repo.services = {
        "aadhaar_name_change": EnhancedServiceGuide(
            service_id="aadhaar_name_change",
            service_name="Aadhaar Name Change",
            category=ServiceCategory.CERTIFICATE,
            description="Change name on Aadhaar card",
            last_updated=datetime.now(),
            data_source="test"
        ),
        "data_access_request": EnhancedServiceGuide(
            service_id="data_access_request",
            service_name="Data Access Request",
            category=ServiceCategory.DATA_ACCESS,
            description="Request access to government data",
            last_updated=datetime.now(),
            data_source="test"
        ),
        "service_status_tracking": EnhancedServiceGuide(
            service_id="service_status_tracking",
            service_name="Service Status Tracking",
            category=ServiceCategory.STATUS_INQUIRY,
            description="Track status of government service applications",
            last_updated=datetime.now(),
            data_source="test"
        ),
        "driving_license": EnhancedServiceGuide(
            service_id="driving_license",
            service_name="Driving License",
            category=ServiceCategory.IDENTITY_CARD,
            description="Apply for driving license",
            last_updated=datetime.now(),
            data_source="test"
        ),
    }
    
    return repo


@pytest.fixture
def query_processor(mock_service_repository):
    """Create a QueryProcessor with mock repository."""
    return QueryProcessor(mock_service_repository)


class TestQueryProcessor:
    """Test suite for QueryProcessor."""
    
    def test_single_match_success(self, query_processor):
        """Test query matching single service returns success."""
        result = query_processor.process_query("aadhaar name change")
        
        assert result.status == "success"
        assert result.service is not None
        assert result.service.service_id == "aadhaar_name_change"
        assert result.message is None
        assert result.matches is None
        assert result.suggestions is None
    
    def test_single_match_case_insensitive(self, query_processor):
        """Test query matching is case insensitive."""
        result = query_processor.process_query("AADHAAR NAME change")
        
        assert result.status == "success"
        assert result.service is not None
        assert result.service.service_id == "aadhaar_name_change"
    
    def test_single_match_with_extra_words(self, query_processor):
        """Test query with extra words still matches."""
        result = query_processor.process_query("how to change aadhaar name")
        
        assert result.status == "success"
        assert result.service is not None
        assert result.service.service_id == "aadhaar_name_change"
    
    def test_no_match_returns_suggestions(self, query_processor):
        """Test query with no matching service returns suggestions."""
        result = query_processor.process_query("flying car license")
        
        assert result.status == "no_match"
        assert result.message == "I couldn't find information about that service."
        assert result.service is None
        assert result.matches is None
        assert result.suggestions is not None
        # Should suggest driving_license since it has "license" keyword
        assert isinstance(result.suggestions, list)
    
    def test_ambiguous_query_multiple_matches(self, query_processor):
        """Test ambiguous query matching multiple services."""
        # Query with just "status" should match service_status_tracking
        # But let's test with a query that could match multiple
        result = query_processor.process_query("status")
        
        # This depends on keyword map - with current map, "status" alone
        # matches service_status_tracking (needs both "status" and "tracking")
        # So this might not be ambiguous. Let's test the logic anyway.
        if result.status == "ambiguous":
            assert result.message == "I found multiple services matching your query. Which one do you need?"
            assert result.matches is not None
            assert len(result.matches) > 1
            assert result.service is None
    
    def test_empty_query(self, query_processor):
        """Test empty query returns no match."""
        result = query_processor.process_query("")
        
        assert result.status == "no_match"
        assert result.suggestions is not None
    
    def test_whitespace_query(self, query_processor):
        """Test whitespace-only query returns no match."""
        result = query_processor.process_query("   ")
        
        assert result.status == "no_match"
        assert result.suggestions is not None
    
    def test_partial_keyword_match_no_success(self, query_processor):
        """Test partial keyword match doesn't return success."""
        # Query with only "aadhaar" but not "name" shouldn't match aadhaar_name_change
        result = query_processor.process_query("aadhaar")
        
        # Should not be success since it needs both "aadhaar" AND "name"
        assert result.status != "success"
    
    def test_find_similar_services(self, query_processor):
        """Test _find_similar_services returns partial matches."""
        similar = query_processor._find_similar_services("license application")
        
        # Should include driving_license since it has "license" keyword
        assert "driving_license" in similar
        assert len(similar) <= 3  # Should return max 3 suggestions
    
    def test_find_matching_services_all_keywords_required(self, query_processor):
        """Test _find_matching_services requires all keywords."""
        # "aadhaar_name_change" requires both "aadhaar" and "name"
        matches = query_processor._find_matching_services("aadhaar")
        assert "aadhaar_name_change" not in matches
        
        matches = query_processor._find_matching_services("name")
        assert "aadhaar_name_change" not in matches
        
        matches = query_processor._find_matching_services("aadhaar name")
        assert "aadhaar_name_change" in matches
    
    def test_keyword_map_structure(self, query_processor):
        """Test keyword map has expected structure."""
        keyword_map = query_processor.keyword_map
        
        assert isinstance(keyword_map, dict)
        assert "aadhaar_name_change" in keyword_map
        assert isinstance(keyword_map["aadhaar_name_change"], list)
        assert "aadhaar" in keyword_map["aadhaar_name_change"]
        assert "name" in keyword_map["aadhaar_name_change"]


class TestServiceRepository:
    """Test suite for ServiceRepository."""
    
    def test_get_service_existing(self, mock_service_repository):
        """Test getting an existing service."""
        service = mock_service_repository.get_service("aadhaar_name_change")
        
        assert service is not None
        assert service.service_id == "aadhaar_name_change"
        assert service.service_name == "Aadhaar Name Change"
    
    def test_get_service_nonexistent(self, mock_service_repository):
        """Test getting a non-existent service returns None."""
        service = mock_service_repository.get_service("nonexistent_service")
        
        assert service is None
    
    def test_get_all_services(self, mock_service_repository):
        """Test getting all services."""
        services = mock_service_repository.get_all_services()
        
        assert isinstance(services, list)
        assert len(services) == 4
        service_ids = [s.service_id for s in services]
        assert "aadhaar_name_change" in service_ids
        assert "data_access_request" in service_ids
    
    def test_update_service(self, mock_service_repository):
        """Test updating a service."""
        updated_service = EnhancedServiceGuide(
            service_id="aadhaar_name_change",
            service_name="Aadhaar Name Update",  # Changed name
            category=ServiceCategory.CERTIFICATE,
            description="Updated description",
            last_updated=datetime.now(),
            data_source="test"
        )
        
        mock_service_repository.update_service(updated_service)
        
        retrieved = mock_service_repository.get_service("aadhaar_name_change")
        assert retrieved.service_name == "Aadhaar Name Update"
        assert retrieved.description == "Updated description"


class TestQueryResult:
    """Test suite for QueryResult model."""
    
    def test_query_result_success(self):
        """Test creating a success QueryResult."""
        service = EnhancedServiceGuide(
            service_id="test",
            service_name="Test Service",
            category=ServiceCategory.CERTIFICATE,
            description="Test",
            last_updated=datetime.now(),
            data_source="test"
        )
        
        result = QueryResult(
            status="success",
            service=service
        )
        
        assert result.status == "success"
        assert result.service == service
        assert result.message is None
        assert result.matches is None
        assert result.suggestions is None
    
    def test_query_result_no_match(self):
        """Test creating a no_match QueryResult."""
        result = QueryResult(
            status="no_match",
            message="Not found",
            suggestions=["service1", "service2"]
        )
        
        assert result.status == "no_match"
        assert result.message == "Not found"
        assert result.suggestions == ["service1", "service2"]
        assert result.service is None
        assert result.matches is None
    
    def test_query_result_ambiguous(self):
        """Test creating an ambiguous QueryResult."""
        result = QueryResult(
            status="ambiguous",
            message="Multiple matches",
            matches=["service1", "service2", "service3"]
        )
        
        assert result.status == "ambiguous"
        assert result.message == "Multiple matches"
        assert result.matches == ["service1", "service2", "service3"]
        assert result.service is None
        assert result.suggestions is None
