"""Unit tests for ServiceRepository class.

Tests CRUD operations, timestamp-based version selection,
and integration with enhanced mock data.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app.repositories.service_repository import ServiceRepository
from app.models.enhanced_service import EnhancedServiceGuide
from app.models.schemas import ServiceCategory


class TestServiceRepository:
    """Test cases for ServiceRepository functionality."""
    
    def test_initialization_loads_services(self):
        """Test that repository initializes and loads services."""
        repo = ServiceRepository()
        
        # Should have loaded services from mock data
        assert repo.get_service_count() > 0
        assert len(repo.services) > 0
        assert len(repo.service_versions) > 0
    
    def test_get_service_existing(self):
        """Test retrieving an existing service."""
        repo = ServiceRepository()
        
        # Get a service that should exist in mock data
        service = repo.get_service("aadhaar_name_change")
        
        assert service is not None
        assert service.service_id == "aadhaar_name_change"
        assert service.service_name == "Aadhaar Name Change"
        assert isinstance(service, EnhancedServiceGuide)
    
    def test_get_service_nonexistent(self):
        """Test retrieving a non-existent service."""
        repo = ServiceRepository()
        
        service = repo.get_service("nonexistent_service")
        
        assert service is None
    
    def test_get_all_services(self):
        """Test retrieving all services."""
        repo = ServiceRepository()
        
        services = repo.get_all_services()
        
        assert isinstance(services, list)
        assert len(services) > 0
        
        # All items should be EnhancedServiceGuide instances
        for service in services:
            assert isinstance(service, EnhancedServiceGuide)
    
    def test_update_service_new(self):
        """Test updating a service (adding new service)."""
        repo = ServiceRepository()
        
        # Create a new service
        new_service = EnhancedServiceGuide(
            service_id="test_service",
            service_name="Test Service",
            category=ServiceCategory.CERTIFICATE,
            description="Test service for unit testing",
            last_updated=datetime.now(),
            data_source="unit_test"
        )
        
        # Update repository
        repo.update_service(new_service)
        
        # Verify service was added
        retrieved = repo.get_service("test_service")
        assert retrieved is not None
        assert retrieved.service_id == "test_service"
        assert retrieved.service_name == "Test Service"
    
    def test_update_service_existing_with_newer_timestamp(self):
        """Test updating existing service with newer timestamp."""
        repo = ServiceRepository()
        
        # Get existing service
        original_service = repo.get_service("aadhaar_name_change")
        assert original_service is not None
        original_timestamp = original_service.last_updated
        
        # Create updated version with newer timestamp
        updated_service = EnhancedServiceGuide(
            service_id="aadhaar_name_change",
            service_name="Updated Aadhaar Name Change",
            category=ServiceCategory.AADHAAR,
            description="Updated description",
            last_updated=original_timestamp + timedelta(days=1),
            data_source="unit_test_update"
        )
        
        # Update repository
        repo.update_service(updated_service)
        
        # Verify latest version is returned
        retrieved = repo.get_service("aadhaar_name_change")
        assert retrieved is not None
        assert retrieved.service_name == "Updated Aadhaar Name Change"
        assert retrieved.last_updated == updated_service.last_updated
        
        # Verify version history
        versions = repo.get_service_versions("aadhaar_name_change")
        assert len(versions) >= 2
        assert versions[0].last_updated == updated_service.last_updated  # Newest first
    
    def test_update_service_existing_with_older_timestamp(self):
        """Test updating existing service with older timestamp still stores but doesn't become current."""
        repo = ServiceRepository()
        
        # Get existing service
        original_service = repo.get_service("aadhaar_name_change")
        assert original_service is not None
        original_timestamp = original_service.last_updated
        
        # Create version with older timestamp
        older_service = EnhancedServiceGuide(
            service_id="aadhaar_name_change",
            service_name="Older Aadhaar Name Change",
            category=ServiceCategory.AADHAAR,
            description="Older description",
            last_updated=original_timestamp - timedelta(days=1),
            data_source="unit_test_older"
        )
        
        # Update repository
        repo.update_service(older_service)
        
        # Verify original (newer) version is still returned
        retrieved = repo.get_service("aadhaar_name_change")
        assert retrieved is not None
        assert retrieved.last_updated == original_timestamp
        
        # Verify version history includes both
        versions = repo.get_service_versions("aadhaar_name_change")
        assert len(versions) >= 2
        timestamps = [v.last_updated for v in versions]
        assert original_timestamp in timestamps
        assert older_service.last_updated in timestamps
    
    def test_get_service_versions(self):
        """Test retrieving service version history."""
        repo = ServiceRepository()
        
        # Get versions for existing service
        versions = repo.get_service_versions("aadhaar_name_change")
        
        assert isinstance(versions, list)
        assert len(versions) >= 1
        
        # Should be sorted by timestamp (newest first)
        if len(versions) > 1:
            for i in range(len(versions) - 1):
                assert versions[i].last_updated >= versions[i + 1].last_updated
    
    def test_get_service_versions_nonexistent(self):
        """Test getting versions for non-existent service."""
        repo = ServiceRepository()
        
        versions = repo.get_service_versions("nonexistent_service")
        
        assert versions == []
    
    def test_get_services_by_category(self):
        """Test filtering services by category."""
        repo = ServiceRepository()
        
        # Get services in AADHAAR category
        aadhaar_services = repo.get_services_by_category("AADHAAR")
        
        assert isinstance(aadhaar_services, list)
        
        # All returned services should be in AADHAAR category
        for service in aadhaar_services:
            assert service.category == ServiceCategory.AADHAAR
    
    def test_service_exists(self):
        """Test checking service existence."""
        repo = ServiceRepository()
        
        # Existing service
        assert repo.service_exists("aadhaar_name_change") is True
        
        # Non-existent service
        assert repo.service_exists("nonexistent_service") is False
    
    def test_get_service_count(self):
        """Test getting service count."""
        repo = ServiceRepository()
        
        count = repo.get_service_count()
        
        assert isinstance(count, int)
        assert count > 0
        assert count == len(repo.services)
    
    @patch('app.repositories.service_repository.get_enhanced_mock_services')
    def test_load_mock_services_failure(self, mock_get_services):
        """Test handling of mock data loading failure."""
        # Mock failure in loading mock services
        mock_get_services.side_effect = Exception("Mock loading failed")
        
        repo = ServiceRepository()
        
        # Should handle failure gracefully
        assert repo.get_service_count() == 0
        assert len(repo.services) == 0
    
    @patch('app.repositories.service_repository.get_enhanced_mock_services')
    def test_load_mock_services_invalid_data(self, mock_get_services):
        """Test handling of invalid mock data."""
        # Mock invalid data
        mock_get_services.return_value = {
            "invalid_service": "not_a_service_object"
        }
        
        repo = ServiceRepository()
        
        # Should handle invalid data gracefully
        assert repo.get_service_count() == 0
    
    def test_get_latest_version_no_versions(self):
        """Test _get_latest_version with no versions."""
        repo = ServiceRepository()
        
        with pytest.raises(ValueError, match="No versions found"):
            repo._get_latest_version("nonexistent_service")
    
    def test_timestamp_based_version_selection(self):
        """Test that the latest timestamp is always selected."""
        repo = ServiceRepository()
        
        # Create multiple versions with different timestamps
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        
        service_v1 = EnhancedServiceGuide(
            service_id="version_test",
            service_name="Version 1",
            category=ServiceCategory.CERTIFICATE,
            description="First version",
            last_updated=base_time,
            data_source="test"
        )
        
        service_v2 = EnhancedServiceGuide(
            service_id="version_test",
            service_name="Version 2",
            category=ServiceCategory.CERTIFICATE,
            description="Second version",
            last_updated=base_time + timedelta(hours=1),
            data_source="test"
        )
        
        service_v3 = EnhancedServiceGuide(
            service_id="version_test",
            service_name="Version 3",
            category=ServiceCategory.CERTIFICATE,
            description="Third version",
            last_updated=base_time + timedelta(hours=2),
            data_source="test"
        )
        
        # Add versions in non-chronological order
        repo.update_service(service_v2)
        repo.update_service(service_v1)
        repo.update_service(service_v3)
        
        # Should always return the latest version (v3)
        current = repo.get_service("version_test")
        assert current is not None
        assert current.service_name == "Version 3"
        assert current.last_updated == service_v3.last_updated
        
        # Version history should contain all versions
        versions = repo.get_service_versions("version_test")
        assert len(versions) == 3
        assert versions[0].service_name == "Version 3"  # Newest first
        assert versions[1].service_name == "Version 2"
        assert versions[2].service_name == "Version 1"  # Oldest last


class TestServiceRepositoryIntegration:
    """Integration tests with enhanced mock data."""
    
    def test_integration_with_enhanced_mock_data(self):
        """Test that repository correctly integrates with enhanced mock data."""
        repo = ServiceRepository()
        
        # Should load all services from enhanced mock data
        expected_services = [
            "aadhaar_name_change",
            "data_access_request", 
            "birth_certificate",
            "service_status_tracking"
        ]
        
        for service_id in expected_services:
            service = repo.get_service(service_id)
            assert service is not None, f"Service {service_id} should be loaded"
            assert service.service_id == service_id
            
            # Verify all five categories are present (even if empty)
            assert hasattr(service, 'office_locations')
            assert hasattr(service, 'required_documents')
            assert hasattr(service, 'office_visit_sequence')
            assert hasattr(service, 'official_websites')
            assert hasattr(service, 'processing_timelines')
    
    def test_aadhaar_service_has_all_categories_populated(self):
        """Test that Aadhaar service has all categories populated."""
        repo = ServiceRepository()
        
        service = repo.get_service("aadhaar_name_change")
        assert service is not None
        
        # Should have multiple items in each category
        assert len(service.office_locations) > 0
        assert len(service.required_documents) > 0
        assert len(service.office_visit_sequence) > 0
        assert len(service.official_websites) > 0
        assert len(service.processing_timelines) > 0
    
    def test_data_access_service_has_empty_categories(self):
        """Test that data access service demonstrates empty categories."""
        repo = ServiceRepository()
        
        service = repo.get_service("data_access_request")
        assert service is not None
        
        # Should have some empty categories (office locations, office sequence)
        assert len(service.office_locations) == 0
        assert len(service.office_visit_sequence) == 0
        
        # But should have populated categories
        assert len(service.required_documents) > 0
        assert len(service.official_websites) > 0
        assert len(service.processing_timelines) > 0
    
    def test_birth_certificate_single_items(self):
        """Test that birth certificate service has single items."""
        repo = ServiceRepository()
        
        service = repo.get_service("birth_certificate")
        assert service is not None
        
        # Should have single items in each populated category
        assert len(service.office_locations) == 1
        assert len(service.required_documents) == 1
        assert len(service.office_visit_sequence) == 1
        assert len(service.official_websites) == 1
        assert len(service.processing_timelines) == 1