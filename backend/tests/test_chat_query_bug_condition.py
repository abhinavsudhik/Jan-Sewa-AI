"""
Bug Condition Exploration Test for Chat Query Response Bug

**Validates: Requirements 1.1, 1.2, 1.3, 2.1, 2.2, 2.3**

CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

This test encodes the expected behavior - it will validate the fix when it passes after implementation.
GOAL: Surface counterexamples that demonstrate the bug exists.

The bug condition is:
- Queries about services other than "aadhaar name change" (e.g., "data access", "status tracking")
  return only a generic welcome message instead of service-specific responses
- The system advertises services in the welcome message but has no logic to handle queries about them
- Users cannot get help with advertised services like "data access requests" or "service status tracking"
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase
from httpx import AsyncClient, ASGITransport
from app.main import app


# Strategy: Generate service query messages
@st.composite
def service_query(draw):
    """Generate queries about advertised services (data access, status tracking)."""
    service_keywords = [
        (["data", "access"], "data access"),
        (["status", "tracking"], "status tracking"),
        (["data", "access", "request"], "data access request"),
        (["service", "status"], "service status"),
    ]
    
    keywords, service_name = draw(st.sampled_from(service_keywords))
    
    # Generate different query patterns
    templates = [
        "How do I request {service}?",
        "I need help with {service}",
        "Tell me about {service}",
        "What is {service}?",
        "Help me with {service}",
        "{service}",
        "I want to know about {service}",
        "Can you help with {service}?",
    ]
    
    template = draw(st.sampled_from(templates))
    query = template.format(service=service_name)
    
    return query, keywords


@pytest.mark.asyncio
@given(query_data=service_query())
@settings(
    max_examples=50,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
async def test_property_1_service_query_recognition(query_data):
    """
    Property 1: Bug Condition - Service Query Recognition
    
    **Validates: Requirements 2.1, 2.2, 2.3**
    
    For any chat message where the user queries about advertised services
    (containing keywords like "data access", "status tracking", or other service-related terms),
    the fixed process_chat function SHALL either return the corresponding service guide
    from MOCK_SERVICES if available, or return a helpful "coming soon" message indicating
    the service is being developed.
    
    EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
    - Response contains only the generic welcome message
    - No service_guide field is populated
    - No "coming soon" message is provided
    - The system advertises services it cannot help with
    
    This failure confirms the bug exists due to hardcoded single-service logic.
    """
    query, keywords = query_data
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/chat/",
            json={
                "message": query,
                "language": "en"
            }
        )
        
        assert response.status_code == 200, \
            f"Chat endpoint failed with status {response.status_code} for query: {query}"
        
        data = response.json()
        
        # The fixed system should either:
        # 1. Return a service_guide (if the service exists in MOCK_SERVICES), OR
        # 2. Return a message containing "coming soon" (if the service doesn't exist yet)
        
        has_service_guide = data.get("service_guide") is not None
        has_coming_soon = "coming soon" in data.get("message", "").lower()
        
        assert has_service_guide or has_coming_soon, \
            f"Query '{query}' with keywords {keywords} should return either a service guide or 'coming soon' message. " \
            f"Got response: {data.get('message')[:200]}... " \
            f"service_guide present: {has_service_guide}"


@pytest.mark.asyncio
async def test_data_access_query():
    """
    Unit test: Data access query
    
    Tests that a query about "data access" returns either a service guide
    or a "coming soon" message.
    
    EXPECTED ON UNFIXED CODE: FAILS - returns only welcome message
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/chat/",
            json={
                "message": "How do I request data access?",
                "language": "en"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        has_service_guide = data.get("service_guide") is not None
        has_coming_soon = "coming soon" in data.get("message", "").lower()
        
        assert has_service_guide or has_coming_soon, \
            f"Data access query should return service guide or 'coming soon' message. " \
            f"Got: {data.get('message')}"


@pytest.mark.asyncio
async def test_status_tracking_query():
    """
    Unit test: Status tracking query
    
    Tests that a query about "status tracking" returns either a service guide
    or a "coming soon" message.
    
    EXPECTED ON UNFIXED CODE: FAILS - returns only welcome message
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/chat/",
            json={
                "message": "I need help with service status tracking",
                "language": "en"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        has_service_guide = data.get("service_guide") is not None
        has_coming_soon = "coming soon" in data.get("message", "").lower()
        
        assert has_service_guide or has_coming_soon, \
            f"Status tracking query should return service guide or 'coming soon' message. " \
            f"Got: {data.get('message')}"


@pytest.mark.asyncio
async def test_data_access_request_simple():
    """
    Unit test: Simple "data access request" query
    
    Tests that a simple query "data access request" returns either a service guide
    or a "coming soon" message.
    
    EXPECTED ON UNFIXED CODE: FAILS - returns only welcome message
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/chat/",
            json={
                "message": "data access request",
                "language": "en"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        has_service_guide = data.get("service_guide") is not None
        has_coming_soon = "coming soon" in data.get("message", "").lower()
        
        assert has_service_guide or has_coming_soon, \
            f"'data access request' query should return service guide or 'coming soon' message. " \
            f"Got: {data.get('message')}"


@pytest.mark.asyncio
async def test_multiple_service_queries():
    """
    Unit test: Multiple different service queries
    
    Tests that various service query patterns all receive proper responses
    (either service guide or "coming soon" message).
    
    EXPECTED ON UNFIXED CODE: FAILS - all return only welcome message
    """
    service_queries = [
        "data access",
        "status tracking",
        "help with data access requests",
        "I need service status tracking",
        "tell me about data access",
        "what is status tracking",
    ]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
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
            
            has_service_guide = data.get("service_guide") is not None
            has_coming_soon = "coming soon" in data.get("message", "").lower()
            
            assert has_service_guide or has_coming_soon, \
                f"Query '{query}' should return service guide or 'coming soon' message. " \
                f"Got: {data.get('message')}"
