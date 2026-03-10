"""
Integration tests for chat endpoint - Task 7.2

Tests the complete flow from user query through QueryProcessor, ServiceRepository,
and ResponseFormatter to return properly structured responses.

**Validates: Requirements 1.1, 7.1, 7.2, 7.3, 7.4**
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.schemas import ChatMessage, ChatResponse, EnhancedServiceResponse, ResponseSection
from datetime import datetime
from typing import Dict, Any


class TestChatEndpointIntegration:
    """Integration tests for the chat endpoint with enhanced services."""

    @pytest.mark.asyncio
    async def test_successful_service_query_full_flow(self):
        """
        Test complete flow from query to formatted response for known service.
        
        **Validates: Requirements 1.1, 7.1, 7.2**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Test Aadhaar name change query
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": "I need to change my name in Aadhaar",
                    "language": "en"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify basic response structure
            assert "message" in data
            assert "enhanced_service_guide" in data
            assert data["enhanced_service_guide"] is not None
            
            # Verify enhanced service guide structure
            enhanced_guide = data["enhanced_service_guide"]
            assert "service_name" in enhanced_guide
            assert "description" in enhanced_guide
            assert "sections" in enhanced_guide
            assert "last_updated" in enhanced_guide
            
            # Verify all five categories are present (Requirement 1.1)
            sections = enhanced_guide["sections"]
            assert len(sections) == 5
            
            expected_headers = [
                "📍 Office Locations",
                "📄 Required Documents", 
                "🏢 Office Visit Sequence",
                "🔗 Official Websites",
                "⏱️ Processing Timeline"
            ]
            
            actual_headers = [section["header"] for section in sections]
            assert actual_headers == expected_headers
            
            # Verify each section has required fields
            for section in sections:
                assert "header" in section
                assert "content" in section
                assert "is_empty" in section
                assert isinstance(section["is_empty"], bool)

    @pytest.mark.asyncio
    async def test_all_five_categories_in_response(self):
        """
        Test that all five information categories are present in API response.
        
        **Validates: Requirements 1.1**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Test with data access request
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": "data access request",
                    "language": "en"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            enhanced_guide = data["enhanced_service_guide"]
            sections = enhanced_guide["sections"]
            
            # Verify exactly 5 sections
            assert len(sections) == 5
            
            # Verify section headers match expected categories
            headers = [section["header"] for section in sections]
            expected_headers = [
                "📍 Office Locations",
                "📄 Required Documents",
                "🏢 Office Visit Sequence", 
                "🔗 Official Websites",
                "⏱️ Processing Timeline"
            ]
            assert headers == expected_headers
            
            # Verify each section has content (even if empty)
            for section in sections:
                assert section["content"] is not None
                assert len(section["content"]) > 0
                # Content should either be actual data or "Information not available"
                assert section["content"] != ""

    @pytest.mark.asyncio
    async def test_response_structure_validation(self):
        """
        Test that response structure matches expected schema.
        
        **Validates: Requirements 1.1**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": "birth certificate",
                    "language": "en"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate top-level response structure
            required_fields = ["message", "language", "session_id"]
            for field in required_fields:
                assert field in data
            
            # Validate enhanced service guide structure
            if "enhanced_service_guide" in data and data["enhanced_service_guide"]:
                enhanced_guide = data["enhanced_service_guide"]
                
                # Required fields in enhanced service guide
                required_enhanced_fields = ["service_name", "description", "sections", "last_updated"]
                for field in required_enhanced_fields:
                    assert field in enhanced_guide
                
                # Validate sections structure
                sections = enhanced_guide["sections"]
                assert isinstance(sections, list)
                
                for section in sections:
                    required_section_fields = ["header", "content", "is_empty"]
                    for field in required_section_fields:
                        assert field in section
                    
                    assert isinstance(section["header"], str)
                    assert isinstance(section["content"], str)
                    assert isinstance(section["is_empty"], bool)

    @pytest.mark.asyncio
    async def test_unknown_service_error_scenario(self):
        """
        Test error handling for unknown service queries.
        
        **Validates: Requirements 7.4**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": "quantum physics research permit",
                    "language": "en"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should return welcome message for unknown service
            assert "message" in data
            assert "Government Services Assistant" in data["message"]
            
            # Should not have enhanced_service_guide for unknown service
            assert data.get("enhanced_service_guide") is None

    @pytest.mark.asyncio
    async def test_ambiguous_query_scenario(self):
        """
        Test handling of ambiguous queries that match multiple services.
        
        **Validates: Requirements 7.3**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Use a query that might match multiple services
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": "status",  # Could match service status tracking
                    "language": "en"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should return a response (either specific service or clarification)
            assert "message" in data
            assert len(data["message"]) > 0

    @pytest.mark.asyncio
    async def test_generic_greeting_handling(self):
        """
        Test handling of generic greetings and welcome messages.
        
        **Validates: Requirements 7.4**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            greetings = ["hello", "hi", "help", "what can you do"]
            
            for greeting in greetings:
                response = await client.post(
                    "/api/v1/chat/",
                    json={
                        "message": greeting,
                        "language": "en"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Should return welcome message
                assert "Government Services Assistant" in data["message"]
                assert "enhanced_service_guide" not in data or data["enhanced_service_guide"] is None

    @pytest.mark.asyncio
    async def test_multiple_services_consistency(self):
        """
        Test that different services all return consistent structure.
        
        **Validates: Requirements 1.1, 8.1**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            
            # Test queries for different services
            test_queries = [
                "aadhaar name change",
                "data access request", 
                "birth certificate",
                "service status tracking"
            ]
            
            responses = []
            for query in test_queries:
                response = await client.post(
                    "/api/v1/chat/",
                    json={
                        "message": query,
                        "language": "en"
                    }
                )
                assert response.status_code == 200
                responses.append(response.json())
            
            # Verify all responses have enhanced service guides
            enhanced_guides = []
            for data in responses:
                assert "enhanced_service_guide" in data
                if data["enhanced_service_guide"]:
                    enhanced_guides.append(data["enhanced_service_guide"])
            
            # Verify consistent structure across all services
            if enhanced_guides:
                first_guide = enhanced_guides[0]
                first_headers = [section["header"] for section in first_guide["sections"]]
                
                for guide in enhanced_guides[1:]:
                    headers = [section["header"] for section in guide["sections"]]
                    assert headers == first_headers, "All services should have same section headers in same order"
                    assert len(guide["sections"]) == 5, "All services should have exactly 5 sections"

    @pytest.mark.asyncio
    async def test_session_id_handling(self):
        """
        Test session ID generation and preservation.
        
        **Validates: Requirements 7.1**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Test without session ID
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
            
            # Test with provided session ID
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

    @pytest.mark.asyncio
    async def test_language_parameter_handling(self):
        """
        Test language parameter is preserved in responses.
        
        **Validates: Requirements 7.1**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            languages = ["en", "hi", "te"]
            
            for lang in languages:
                response = await client.post(
                    "/api/v1/chat/",
                    json={
                        "message": "aadhaar name change",
                        "language": lang
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["language"] == lang

    @pytest.mark.asyncio
    async def test_error_resilience_and_fallback(self):
        """
        Test system resilience and fallback behavior.
        
        **Validates: Requirements 7.1, 7.4**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Test with malformed but processable input
            test_cases = [
                "AADHAAR NAME CHANGE!!!",  # All caps with punctuation
                "   data access request   ",  # Extra whitespace
                "Data Access Request",  # Mixed case
                "aadhaar-name-change",  # Hyphenated
            ]
            
            for test_input in test_cases:
                response = await client.post(
                    "/api/v1/chat/",
                    json={
                        "message": test_input,
                        "language": "en"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "message" in data
                # Should either return service guide or helpful message
                assert len(data["message"]) > 0

    @pytest.mark.asyncio
    async def test_legacy_compatibility(self):
        """
        Test that legacy service_guide is still provided for backward compatibility.
        
        **Validates: Requirements 7.2**
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
            
            # Should have both legacy and enhanced formats
            assert "service_guide" in data
            assert "enhanced_service_guide" in data
            
            if data["service_guide"]:
                # Verify legacy format has expected fields
                legacy_guide = data["service_guide"]
                legacy_fields = ["service_id", "service_name", "category", "description", "steps"]
                for field in legacy_fields:
                    assert field in legacy_guide

    @pytest.mark.asyncio
    async def test_timestamp_in_response(self):
        """
        Test that last_updated timestamp is included in responses.
        
        **Validates: Requirements 9.2**
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": "birth certificate",
                    "language": "en"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            if data.get("enhanced_service_guide"):
                enhanced_guide = data["enhanced_service_guide"]
                assert "last_updated" in enhanced_guide
                
                # Verify timestamp format
                timestamp_str = enhanced_guide["last_updated"]
                # Should be parseable as ISO datetime
                try:
                    datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except ValueError:
                    pytest.fail(f"Invalid timestamp format: {timestamp_str}")

    @pytest.mark.asyncio
    async def test_content_not_empty_for_available_data(self):
        """
        Test that sections with available data have non-empty content.
        
        **Validates: Requirements 1.1, 1.3**
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
            
            if data.get("enhanced_service_guide"):
                enhanced_guide = data["enhanced_service_guide"]
                sections = enhanced_guide["sections"]
                
                for section in sections:
                    if not section["is_empty"]:
                        # Non-empty sections should have meaningful content
                        assert len(section["content"].strip()) > 0
                        assert section["content"] != "Information not available"
                    else:
                        # Empty sections should indicate unavailability
                        assert "Information not available" in section["content"]


class TestChatEndpointErrorScenarios:
    """Test error scenarios and edge cases for the chat endpoint."""

    @pytest.mark.asyncio
    async def test_empty_message_handling(self):
        """Test handling of empty or whitespace-only messages."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            test_cases = ["", "   ", "\n\t", "  \n  "]
            
            for empty_msg in test_cases:
                response = await client.post(
                    "/api/v1/chat/",
                    json={
                        "message": empty_msg,
                        "language": "en"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                # Should return welcome message for empty input
                assert "Government Services Assistant" in data["message"]

    @pytest.mark.asyncio
    async def test_invalid_json_handling(self):
        """Test handling of invalid JSON requests."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/api/v1/chat/",
                content="invalid json",
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 422 for invalid JSON
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_required_fields(self):
        """Test handling of requests with missing required fields."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Missing message field
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "language": "en"
                }
            )
            
            # Should return 422 for missing required field
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_very_long_message_handling(self):
        """Test handling of very long messages."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Create a very long message
            long_message = "aadhaar name change " * 1000
            
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": long_message,
                    "language": "en"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            # Should still process and return a response
            assert "message" in data