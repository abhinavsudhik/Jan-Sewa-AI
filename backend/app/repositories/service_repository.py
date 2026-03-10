"""Service repository for managing government service data access.

This repository provides CRUD operations for government service data,
including loading enhanced mock data and supporting timestamp-based
version selection for the latest data.

Key features:
- CRUD operations: get_service(), get_all_services(), update_service()
- Data loading: _load_services() and _load_mock_services()
- Timestamp-based version selection (requirement 9.1)
- Update propagation (requirement 9.3)
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.models.enhanced_service import EnhancedServiceGuide
from app.data.enhanced_mock_services import get_enhanced_mock_services

logger = logging.getLogger(__name__)


class ServiceRepository:
    """Repository for service data access with enhanced mock data integration."""
    
    def __init__(self):
        """Initialize repository and load services."""
        self.services: Dict[str, EnhancedServiceGuide] = {}
        self.service_versions: Dict[str, List[EnhancedServiceGuide]] = {}
        self._load_services()
        logger.info(f"ServiceRepository initialized with {len(self.services)} services")
    
    def get_service(self, service_id: str) -> Optional[EnhancedServiceGuide]:
        """
        Retrieve service by ID with timestamp-based version selection.
        
        For requirement 9.1: If multiple versions exist, returns the one
        with the latest last_updated timestamp.
        
        Args:
            service_id: Unique identifier for the service
            
        Returns:
            EnhancedServiceGuide if found, None otherwise
        """
        if service_id not in self.services:
            logger.warning(f"Service not found: {service_id}")
            return None
        
        service = self.services[service_id]
        logger.debug(f"Retrieved service: {service_id}, last_updated: {service.last_updated}")
        return service
    
    def get_all_services(self) -> List[EnhancedServiceGuide]:
        """
        Retrieve all services.
        
        Returns the latest version of each service based on timestamp.
        
        Returns:
            List of all EnhancedServiceGuide objects
        """
        services = list(self.services.values())
        logger.debug(f"Retrieved {len(services)} services")
        return services
    
    def update_service(self, service: EnhancedServiceGuide) -> None:
        """
        Update service data with timestamp-based versioning.
        
        For requirement 9.3: Ensures updates are reflected in subsequent queries
        by maintaining version history and selecting the latest version.
        
        Args:
            service: Updated EnhancedServiceGuide object
        """
        service_id = service.service_id
        
        # Initialize version list if this is the first version
        if service_id not in self.service_versions:
            self.service_versions[service_id] = []
        
        # Add to version history
        self.service_versions[service_id].append(service)
        
        # Update main services dict with latest version
        self.services[service_id] = self._get_latest_version(service_id)
        
        logger.info(
            f"Updated service: {service_id}, "
            f"new timestamp: {service.last_updated}, "
            f"total versions: {len(self.service_versions[service_id])}"
        )
    
    def _load_services(self) -> None:
        """
        Load services from data source.
        
        Current implementation loads from enhanced mock data.
        Future implementations can load from database or external APIs.
        """
        try:
            mock_services = self._load_mock_services()
            
            # Initialize both services dict and version history
            for service_id, service in mock_services.items():
                self.services[service_id] = service
                self.service_versions[service_id] = [service]
            
            logger.info(f"Loaded {len(mock_services)} services from mock data")
            
        except Exception as e:
            logger.error(f"Failed to load services: {e}")
            # Initialize empty collections on failure
            self.services = {}
            self.service_versions = {}
    
    def _load_mock_services(self) -> Dict[str, EnhancedServiceGuide]:
        """
        Load enhanced mock service data.
        
        Integrates with the enhanced mock data created in Task 5.3,
        which includes comprehensive mock services with all five categories
        and edge cases.
        
        Returns:
            Dictionary mapping service_id to EnhancedServiceGuide
        """
        try:
            mock_services = get_enhanced_mock_services()
            
            # Validate that all services have required fields
            for service_id, service in mock_services.items():
                if not isinstance(service, EnhancedServiceGuide):
                    raise ValueError(f"Invalid service type for {service_id}: {type(service)}")
                
                if service.service_id != service_id:
                    raise ValueError(
                        f"Service ID mismatch: key={service_id}, "
                        f"service.service_id={service.service_id}"
                    )
            
            logger.info(f"Successfully loaded {len(mock_services)} mock services")
            return mock_services
            
        except Exception as e:
            logger.error(f"Failed to load mock services: {e}")
            return {}
    
    def _get_latest_version(self, service_id: str) -> EnhancedServiceGuide:
        """
        Get the latest version of a service based on last_updated timestamp.
        
        Implements requirement 9.1: timestamp-based version selection.
        
        Args:
            service_id: Service identifier
            
        Returns:
            Latest version of the service
            
        Raises:
            ValueError: If no versions exist for the service
        """
        if service_id not in self.service_versions:
            raise ValueError(f"No versions found for service: {service_id}")
        
        versions = self.service_versions[service_id]
        if not versions:
            raise ValueError(f"Empty version list for service: {service_id}")
        
        # Sort by last_updated timestamp (descending) and return the latest
        latest_version = max(versions, key=lambda s: s.last_updated)
        
        logger.debug(
            f"Selected latest version for {service_id}: "
            f"{latest_version.last_updated} from {len(versions)} versions"
        )
        
        return latest_version
    
    def get_service_versions(self, service_id: str) -> List[EnhancedServiceGuide]:
        """
        Get all versions of a service sorted by timestamp (newest first).
        
        Useful for debugging and auditing service changes.
        
        Args:
            service_id: Service identifier
            
        Returns:
            List of service versions sorted by last_updated (descending)
        """
        if service_id not in self.service_versions:
            return []
        
        versions = self.service_versions[service_id]
        return sorted(versions, key=lambda s: s.last_updated, reverse=True)
    
    def get_service_count(self) -> int:
        """
        Get total number of services.
        
        Returns:
            Number of unique services in the repository
        """
        return len(self.services)
    
    def get_services_by_category(self, category: str) -> List[EnhancedServiceGuide]:
        """
        Get all services in a specific category.
        
        Args:
            category: Service category to filter by
            
        Returns:
            List of services in the specified category
        """
        matching_services = [
            service for service in self.services.values()
            if service.category.value == category
        ]
        
        logger.debug(f"Found {len(matching_services)} services in category: {category}")
        return matching_services
    
    def service_exists(self, service_id: str) -> bool:
        """
        Check if a service exists in the repository.
        
        Args:
            service_id: Service identifier to check
            
        Returns:
            True if service exists, False otherwise
        """
        return service_id in self.services