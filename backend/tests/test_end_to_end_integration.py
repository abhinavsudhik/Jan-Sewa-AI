"""
End-to-End Integration Tests - Task 10.3

Tests complete user flow: query → API → formatted response → display
Tests with various service types and data completeness levels
Tests error flows (unknown service, ambiguous query)
Verifies consistent structure across all services

**Validates: Requirements 1.1, 1.4, 7.1, 8.1, 8.4**
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.enhanced_service import EnhancedServiceGuide
from app.services.response_formatter import ResponseFormatter
from app.repositories.service_repository import ServiceRepository
from app.services.query_processor import QueryProcessor
from datetime import datetime
from typing import Dict, Any, List
import json


class TestEndToEndIntegration:
    """
    Comprehensive end-to-end integration tests for the complete system flow.
    
    Tests the entire pipeline from user query through backend processing
    to structured response formatting, ensuring consistent behavior across
    all service types and data completeness levels.
    """

    @pytest.mark.asyncio
    async def test_complete_user_flow_aadhaar_service(self):
        """
        Test complete flow: query → API → formatted response → display structure
        for Aadhaar name change service with full data.
        
        **Validates: Requirements 1.1, 7.1, 8.1**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Step 1: User submits query
            user_query = "I need to change my name in Aadhaar card"
            
            # Step 2: API processes query
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": user_query,
                    "language": "en"
                }
            )
            
            # Step 3: Verify API response structure
            assert response.status_code == 200
            data = response.json()
            
            # Verify complete response structure
            assert "message" in data
            assert "enhanced_service_guide" in data
            assert "session_id" in data
            assert "language" in data
            
            # Step 4: Verify enhanced service guide structure
            enhanced_guide = data["enhanced_service_guide"]
            assert enhanced_guide is not None
            
            # Verify all required fields for display
            required_fields = [
                "service_name", "description", "sections", 
                "last_updated", "service_id", "category"
            ]
            for field in required_fields:
                assert field in enhanced_guide, f"Missing field: {field}"
            
            # Step 5: Verify all five categories present in correct order
            sections = enhanced_guide["sections"]
            assert len(sections) == 5, "Must have exactly 5 sections"
            
            expected_headers = [
                "📍 Office Locations",
                "📄 Required Documents", 
                "🏢 Office Visit Sequence",
                "🔗 Official Websites",
                "⏱️ Processing Timeline"
            ]
            
            actual_headers = [section["header"] for section in sections]
            assert actual_headers == expected_headers, \
                f"Section order mismatch. Expected: {expected_headers}, Got: {actual_headers}"
            
            # Step 6: Verify each section has display-ready structure
            for i, section in enumerate(sections):
                assert "header" in section
                assert "content" in section
                assert "is_empty" in section
                assert isinstance(section["is_empty"], bool)
                assert isinstance(section["content"], str)
                assert len(section["content"]) > 0, f"Section {i} has empty content"

    @pytest.mark.asyncio
    async def test_various_service_types_consistency(self):
        """
        Test complete flow with various service types to ensure consistent
        structure and formatting across all government services.
        
        **Validates: Requirements 1.4, 8.1, 8.4**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            
            # Test different service categories
            test_services = [
                {
                    "query": "aadhaar name change",
                    "expected_service": "aadhaar_name_change",
                    "category": "identity_document"
                },
                {
                    "query": "data access request",
                    "expected_service": "data_access_request", 
                    "category": "data_request"
                },
                {
                    "query": "birth certificate",
                    "expected_service": "birth_certificate",
                    "category": "certificate"
                },
                {
                    "query": "service status tracking",
                    "expected_service": "service_status_tracking",
                    "category": "tracking"
                }
            ]
            
            responses = []
            
            for service_test in test_services:
                response = await client.post(
                    "/api/v1/chat/",
                    json={
                        "message": service_test["query"],
                        "language": "en"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                if data.get("enhanced_service_guide"):
                    responses.append({
                        "query": service_test["query"],
                        "guide": data["enhanced_service_guide"],
                        "expected_service": service_test["expected_service"]
                    })
            
            # Verify consistency across all services
            assert len(responses) > 0, "No valid service responses received"
            
            # Check structure consistency
            first_guide = responses[0]["guide"]
            first_sections = first_guide["sections"]
            first_headers = [section["header"] for section in first_sections]
            
            for response_data in responses[1:]:
                guide = response_data["guide"]
                sections = guide["sections"]
                headers = [section["header"] for section in sections]
                
                # Verify same number of sections
                assert len(sections) == len(first_sections), \
                    f"Inconsistent section count for {response_data['query']}"
                
                # Verify same headers in same order
                assert headers == first_headers, \
                    f"Inconsistent headers for {response_data['query']}"
                
                # Verify all required fields present
                for field in ["service_name", "description", "sections", "last_updated"]:
                    assert field in guide, \
                        f"Missing field {field} in {response_data['query']}"

    @pytest.mark.asyncio
    async def test_data_completeness_levels(self):
        """
        Test services with different data completeness levels to ensure
        graceful handling of missing information.
        
        **Validates: Requirements 1.1, 1.3, 8.2**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            
            # Test services that might have varying data completeness
            test_queries = [
                "aadhaar name change",  # Should have comprehensive data
                "data access request",  # May have limited data
                "birth certificate",    # Standard certificate process
            ]
            
            for query in test_queries:
                response = await client.post(
                    "/api/v1/chat/",
                    json={
                        "message": query,
                        "language": "en"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                if data.get("enhanced_service_guide"):
                    guide = data["enhanced_service_guide"]
                    sections = guide["sections"]
                    
                    # Verify all 5 sections present regardless of data availability
                    assert len(sections) == 5, f"Missing sections for query: {query}"
                    
                    for section in sections:
                        # Each section must have header and content
                        assert section["header"], f"Missing header for {query}"
                        assert section["content"], f"Missing content for {query}"
                        
                        # Empty sections should be properly marked
                        if section["is_empty"]:
                            assert "Information not available" in section["content"], \
                                f"Empty section not properly marked for {query}"
                        else:
                            # Non-empty sections should have meaningful content
                            assert len(section["content"].strip()) > 20, \
                                f"Non-empty section has minimal content for {query}"

    @pytest.mark.asyncio
    async def test_error_flows_unknown_service(self):
        """
        Test error flow for unknown service queries to ensure graceful
        handling and appropriate user feedback.
        
        **Validates: Requirements 7.4**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            
            unknown_queries = [
                "quantum physics research permit",
                "alien registration certificate", 
                "time travel license application",
                "unicorn breeding permit",
                "completely unknown government service"
            ]
            
            for query in unknown_queries:
                response = await client.post(
                    "/api/v1/chat/",
                    json={
                        "message": query,
                        "language": "en"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Should return helpful message for unknown service
                assert "message" in data
                assert len(data["message"]) > 0
                
                # Should not have enhanced_service_guide for unknown service
                assert data.get("enhanced_service_guide") is None, \
                    f"Unexpected service guide for unknown query: {query}"
                
                # Message should be helpful and professional
                message = data["message"].lower()
                # Should contain helpful keywords or be a welcome message or suggestions
                helpful_indicators = [
                    "government", "services", "assistant", "help", 
                    "hello", "can help", "what would you like",
                    "couldn't find", "did you mean", "suggestions"
                ]
                assert any(indicator in message for indicator in helpful_indicators), \
                    f"Unhelpful message for unknown query: {query}. Message: {data['message']}"

    @pytest.mark.asyncio
    async def test_error_flows_ambiguous_query(self):
        """
        Test error flow for ambiguous queries that could match multiple services.
        
        **Validates: Requirements 7.3**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            
            # Queries that might be ambiguous
            ambiguous_queries = [
                "status",           # Could match status tracking
                "certificate",      # Could match multiple certificates
                "document",         # Could match document services
                "application",      # Could match various applications
            ]
            
            for query in ambiguous_queries:
                response = await client.post(
                    "/api/v1/chat/",
                    json={
                        "message": query,
                        "language": "en"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Should return some response
                assert "message" in data
                assert len(data["message"]) > 0
                
                # Response should be helpful regardless of ambiguity
                message = data["message"]
                assert len(message.strip()) > 10, \
                    f"Too brief response for ambiguous query: {query}"

    @pytest.mark.asyncio
    async def test_consistent_structure_validation(self):
        """
        Test that all service responses maintain consistent structure
        across different queries and service types.
        
        **Validates: Requirements 8.1, 8.4**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            
            # Comprehensive set of service queries
            service_queries = [
                "aadhaar name change",
                "data access request", 
                "birth certificate",
                "service status tracking"
            ]
            
            all_responses = []
            
            for query in service_queries:
                response = await client.post(
                    "/api/v1/chat/",
                    json={
                        "message": query,
                        "language": "en"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                if data.get("enhanced_service_guide"):
                    all_responses.append({
                        "query": query,
                        "guide": data["enhanced_service_guide"]
                    })
            
            assert len(all_responses) >= 2, "Need at least 2 services for consistency testing"
            
            # Define the expected structure template
            expected_structure = {
                "service_name": str,
                "description": str,
                "sections": list,
                "last_updated": str,
                "service_id": str,
                "category": str
            }
            
            expected_section_structure = {
                "header": str,
                "content": str,
                "is_empty": bool
            }
            
            # Validate structure consistency
            for response_data in all_responses:
                guide = response_data["guide"]
                query = response_data["query"]
                
                # Validate top-level structure
                for field, expected_type in expected_structure.items():
                    assert field in guide, f"Missing field {field} in {query}"
                    assert isinstance(guide[field], expected_type), \
                        f"Wrong type for {field} in {query}"
                
                # Validate sections structure
                sections = guide["sections"]
                assert len(sections) == 5, f"Wrong section count in {query}"
                
                for i, section in enumerate(sections):
                    for field, expected_type in expected_section_structure.items():
                        assert field in section, \
                            f"Missing section field {field} in {query} section {i}"
                        assert isinstance(section[field], expected_type), \
                            f"Wrong section field type {field} in {query} section {i}"
            
            # Validate header consistency across all services
            reference_headers = [s["header"] for s in all_responses[0]["guide"]["sections"]]
            
            for response_data in all_responses[1:]:
                headers = [s["header"] for s in response_data["guide"]["sections"]]
                assert headers == reference_headers, \
                    f"Inconsistent headers in {response_data['query']}"

    @pytest.mark.asyncio
    async def test_frontend_display_readiness(self):
        """
        Test that API responses are properly structured for frontend display
        with all necessary data for rendering components.
        
        **Validates: Requirements 1.1, 10.1, 10.3**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": "aadhaar name change",
                    "language": "en"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            enhanced_guide = data["enhanced_service_guide"]
            assert enhanced_guide is not None
            
            # Verify data is ready for frontend component rendering
            
            # 1. Service header information
            assert enhanced_guide["service_name"]
            assert enhanced_guide["description"]
            assert enhanced_guide["last_updated"]
            
            # 2. Sections ready for iteration
            sections = enhanced_guide["sections"]
            assert isinstance(sections, list)
            assert len(sections) == 5
            
            # 3. Each section has display-ready content
            for section in sections:
                # Header for section titles
                assert section["header"]
                assert isinstance(section["header"], str)
                assert len(section["header"]) > 0
                
                # Content for section body
                assert section["content"] is not None
                assert isinstance(section["content"], str)
                
                # Empty flag for conditional rendering
                assert "is_empty" in section
                assert isinstance(section["is_empty"], bool)
                
                # Content should be non-empty string
                assert len(section["content"]) > 0
            
            # 4. Verify accessibility-ready structure
            # Headers should have emoji icons for visual distinction
            headers = [section["header"] for section in sections]
            expected_icons = ["📍", "📄", "🏢", "🔗", "⏱️"]
            
            for i, header in enumerate(headers):
                assert expected_icons[i] in header, \
                    f"Missing icon in header: {header}"

    @pytest.mark.asyncio
    async def test_session_and_language_handling(self):
        """
        Test session ID generation and language parameter handling
        across the complete flow.
        
        **Validates: Requirements 7.1**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            
            # Test 1: Session ID generation
            response1 = await client.post(
                "/api/v1/chat/",
                json={
                    "message": "aadhaar name change",
                    "language": "en"
                }
            )
            
            assert response1.status_code == 200
            data1 = response1.json()
            assert "session_id" in data1
            session_id = data1["session_id"]
            assert len(session_id) > 0
            
            # Test 2: Session ID preservation
            response2 = await client.post(
                "/api/v1/chat/",
                json={
                    "message": "data access request",
                    "language": "en",
                    "session_id": session_id
                }
            )
            
            assert response2.status_code == 200
            data2 = response2.json()
            assert data2["session_id"] == session_id
            
            # Test 3: Language parameter handling
            languages = ["en", "hi", "te"]
            
            for lang in languages:
                response = await client.post(
                    "/api/v1/chat/",
                    json={
                        "message": "birth certificate",
                        "language": lang
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["language"] == lang

    @pytest.mark.asyncio
    async def test_performance_and_response_time(self):
        """
        Test that the complete flow performs within acceptable time limits
        for good user experience.
        
        **Validates: Requirements 7.1, 7.2**
        """
        import time
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            
            test_queries = [
                "aadhaar name change",
                "data access request",
                "birth certificate"
            ]
            
            response_times = []
            
            for query in test_queries:
                start_time = time.time()
                
                response = await client.post(
                    "/api/v1/chat/",
                    json={
                        "message": query,
                        "language": "en"
                    }
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                assert response.status_code == 200
                
                # Response should be under 2 seconds for good UX
                assert response_time < 2.0, \
                    f"Response too slow for '{query}': {response_time:.2f}s"
            
            # Average response time should be reasonable
            avg_response_time = sum(response_times) / len(response_times)
            assert avg_response_time < 1.0, \
                f"Average response time too slow: {avg_response_time:.2f}s"

    @pytest.mark.asyncio
    async def test_edge_cases_and_robustness(self):
        """
        Test edge cases and system robustness with various input scenarios.
        
        **Validates: Requirements 7.1, 7.4**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            
            edge_cases = [
                # Case variations
                "AADHAAR NAME CHANGE",
                "aadhaar name change",
                "Aadhaar Name Change",
                
                # Extra whitespace
                "  aadhaar name change  ",
                "\n\taadhaar name change\n\t",
                
                # Punctuation
                "aadhaar name change!",
                "aadhaar name change?",
                "aadhaar, name change.",
                
                # Partial matches
                "aadhaar name",
                "name change aadhaar",
                
                # Common variations
                "aadhar name change",  # Common misspelling
                "adhaar name change",  # Another misspelling
            ]
            
            for test_input in edge_cases:
                response = await client.post(
                    "/api/v1/chat/",
                    json={
                        "message": test_input,
                        "language": "en"
                    }
                )
                
                assert response.status_code == 200, \
                    f"Failed for input: '{test_input}'"
                
                data = response.json()
                assert "message" in data, \
                    f"Missing message for input: '{test_input}'"
                
                # Should return either service guide or helpful message
                assert len(data["message"]) > 0, \
                    f"Empty message for input: '{test_input}'"


class TestEndToEndErrorHandling:
    """Test error scenarios in the complete end-to-end flow."""

    @pytest.mark.asyncio
    async def test_malformed_requests(self):
        """Test handling of malformed requests."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            
            # Test empty message
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": "",
                    "language": "en"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "Government Services Assistant" in data["message"]
            
            # Test missing message field
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "language": "en"
                }
            )
            assert response.status_code == 422  # Validation error
            
            # Test invalid JSON
            response = await client.post(
                "/api/v1/chat/",
                content="invalid json",
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_system_resilience(self):
        """Test system resilience under various conditions."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            
            # Test very long message
            long_message = "aadhaar name change " * 100
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": long_message,
                    "language": "en"
                }
            )
            assert response.status_code == 200
            
            # Test special characters
            special_message = "aadhaar name change @#$%^&*()"
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": special_message,
                    "language": "en"
                }
            )
            assert response.status_code == 200
            
            # Test unicode characters
            unicode_message = "aadhaar name change आधार नाम परिवर्तन"
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": unicode_message,
                    "language": "en"
                }
            )
            assert response.status_code == 200


class TestEndToEndDataIntegrity:
    """Test data integrity throughout the complete flow."""

    @pytest.mark.asyncio
    async def test_data_preservation_through_pipeline(self):
        """
        Test that service data is preserved correctly through the entire
        processing pipeline from repository to formatted response.
        
        **Validates: Requirements 9.1, 9.4**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": "aadhaar name change",
                    "language": "en"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            enhanced_guide = data["enhanced_service_guide"]
            assert enhanced_guide is not None
            
            # Verify data source tracking
            assert "service_id" in enhanced_guide
            assert enhanced_guide["service_id"] == "aadhaar_name_change"
            
            # Verify timestamp preservation
            assert "last_updated" in enhanced_guide
            last_updated = enhanced_guide["last_updated"]
            
            # Should be valid ISO datetime
            try:
                datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            except ValueError:
                pytest.fail(f"Invalid timestamp format: {last_updated}")
            
            # Verify category preservation
            assert "category" in enhanced_guide
            assert enhanced_guide["category"] in [
                "aadhaar", "data_access", "record_modification", "status_inquiry", 
                "identity_card", "certificate"
            ]

    @pytest.mark.asyncio
    async def test_content_formatting_integrity(self):
        """
        Test that content formatting maintains data integrity while
        providing display-ready structure.
        
        **Validates: Requirements 1.2, 8.3**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": "aadhaar name change",
                    "language": "en"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            enhanced_guide = data["enhanced_service_guide"]
            sections = enhanced_guide["sections"]
            
            # Test each section for formatting integrity
            for section in sections:
                content = section["content"]
                
                if not section["is_empty"]:
                    # Non-empty content should be properly formatted
                    assert len(content.strip()) > 0
                    assert content != "Information not available"
                    
                    # Should contain meaningful information
                    assert len(content) > 10, \
                        f"Content too brief in section: {section['header']}"
                else:
                    # Empty sections should have standard message
                    assert "Information not available" in content