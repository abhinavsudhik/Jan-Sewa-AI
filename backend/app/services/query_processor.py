"""Query processing service for identifying government services from user queries.

This module handles:
- Parsing user queries
- Identifying requested services using keyword matching
- Handling ambiguous queries
- Suggesting similar services for unknown queries
"""

from typing import Dict, List, Optional
from pydantic import BaseModel

from ..models.enhanced_service import EnhancedServiceGuide


class QueryResult(BaseModel):
    """Result of query processing."""
    status: str  # success, no_match, ambiguous
    message: Optional[str] = None
    service: Optional[EnhancedServiceGuide] = None
    matches: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None


class ServiceRepository:
    """Repository for service data access.
    
    This is a simple in-memory implementation. In production, this would
    connect to a database or external service.
    """
    
    def __init__(self):
        self.services: Dict[str, EnhancedServiceGuide] = {}
        self._load_services()
    
    def get_service(self, service_id: str) -> Optional[EnhancedServiceGuide]:
        """Retrieve service by ID."""
        return self.services.get(service_id)
    
    def get_all_services(self) -> List[EnhancedServiceGuide]:
        """Retrieve all services."""
        return list(self.services.values())
    
    def update_service(self, service: EnhancedServiceGuide) -> None:
        """Update service data."""
        self.services[service.service_id] = service
    
    def _load_services(self) -> None:
        """Load services from data source."""
        # Current implementation: load from mock data
        # Future: load from database
        self.services = self._load_mock_services()
    
    def _load_mock_services(self) -> Dict[str, EnhancedServiceGuide]:
        """Load mock service data.
        
        Loads comprehensive mock data from the data module.
        """
        from ..data.enhanced_mock_services import get_enhanced_mock_services
        return get_enhanced_mock_services()


class QueryProcessor:
    """Processes user queries and identifies requested services."""
    
    def __init__(self, service_repository: ServiceRepository):
        """Initialize QueryProcessor with a service repository.
        
        Args:
            service_repository: Repository for accessing service data
        """
        self.service_repository = service_repository
        self.keyword_map = self._build_keyword_map()
    
    def process_query(self, query: str) -> QueryResult:
        """Process user query and identify requested service.
        
        Args:
            query: User's query string
            
        Returns:
            QueryResult with identified service(s), or error information
            
        Handles:
        - Single match: Returns service with status="success"
        - No matches: Returns suggestions with status="no_match"
        - Multiple matches: Returns matches with status="ambiguous"
        """
        normalized_query = query.lower().strip()
        
        # Find matching services
        matches = self._find_matching_services(normalized_query)
        
        if len(matches) == 0:
            # No matches - suggest similar services
            suggestions = self._find_similar_services(normalized_query)
            return QueryResult(
                status="no_match",
                message="I couldn't find information about that service.",
                suggestions=suggestions
            )
        elif len(matches) == 1:
            # Single match - return service
            service = self.service_repository.get_service(matches[0])
            return QueryResult(
                status="success",
                service=service
            )
        else:
            # Multiple matches - request clarification
            return QueryResult(
                status="ambiguous",
                message="I found multiple services matching your query. "
                        "Which one do you need?",
                matches=matches
            )
    
    def _find_matching_services(self, query: str) -> List[str]:
        """Find services matching the query.
        
        A service matches if ALL of its keywords appear in the query.
        
        Args:
            query: Normalized query string (lowercase)
            
        Returns:
            List of matching service IDs
        """
        matches = []
        for service_id, keywords in self.keyword_map.items():
            if all(keyword in query for keyword in keywords):
                # Handle alternative patterns that map to existing services
                if service_id == "service_status_tracking_alt1":
                    matches.append("service_status_tracking")
                else:
                    matches.append(service_id)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(matches))
    
    def _find_similar_services(self, query: str) -> List[str]:
        """Find services with partial keyword matches.
        
        Returns services that have at least one keyword matching the query.
        Used for suggesting alternatives when no exact match is found.
        
        Args:
            query: Normalized query string (lowercase)
            
        Returns:
            List of up to 3 similar service IDs
        """
        similar = []
        query_words = set(query.split())
        
        for service_id, keywords in self.keyword_map.items():
            keyword_set = set(keywords)
            # Check if there's any overlap between query words and keywords
            if len(query_words & keyword_set) > 0:
                similar.append(service_id)
        
        return similar[:3]  # Return top 3 suggestions
    
    def _build_keyword_map(self) -> Dict[str, List[str]]:
        """Build keyword mapping for service identification.
        
        Maps service IDs to lists of keywords that identify them.
        A query must contain ALL keywords for a service to match.
        
        Returns:
            Dictionary mapping service_id to list of keywords
            
        Note:
            This would typically be loaded from configuration or database.
            For now, using hardcoded examples with flexible matching.
        """
        return {
            "aadhaar_name_change": ["aadhaar", "name"],
            "data_access_request": ["data", "access"],
            "birth_certificate": ["birth", "certificate"],
            "service_status_tracking": ["status", "tracking"],
            # Alternative patterns for more flexible matching
            "service_status_tracking_alt1": ["service", "status"],  # Maps to service_status_tracking
            "driving_license": ["driving", "license"],
        }
