"""
Preservation Property Tests for Chat Query Response Bug

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

CRITICAL: These tests MUST PASS on unfixed code - they verify baseline behavior to preserve.

This test suite ensures the fix doesn't break existing functionality:
- Aadhaar name change queries continue to return the service guide
- Generic greetings continue to return the welcome message
- Session IDs are generated (new UUID) or preserved (if provided)
- Language fields are preserved in responses

GOAL: Verify that for all inputs where the bug condition does NOT hold,
the behavior remains unchanged after the fix is implemented.
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase
from httpx import AsyncClient, ASGITransport
from app.main import app
import uuid


# Strategy: Generate Aadhaar name change queries
@st.composite
def aadhaar_name_query(draw):
    """Generate queries about Aadhaar name changes."""
    templates = [
        "aadhaar name change",
        "how to change name in aadhaar",
        "I need to update my name on aadhaar",
        "aadhaar name update",
        "change my aadhaar name",
        "update name in aadhaar card",
        "aadhaar card name change process",
        "help with aadhaar name modification",
    ]
    
    query = draw(st.sampled_from(templates))
    return query


# Strategy: Generate generic greetings and unclear queries
@st.composite
def generic_greeting(draw):
    """Generate generic greetings or unclear queries."""
    greetings = [
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "hi there",
        "hello there",
        "greetings",
        "help",
        "what can you do",
        "tell me about services",
        "services",
    ]
    
    query = draw(st.sampled_from(greetings))
    return query


# Strategy: Generate session IDs (valid UUIDs or None)
def session_id_strategy():
    """Generate session IDs - either None or valid UUIDs."""
    return st.one_of(
        st.none(),
        st.builds(lambda: str(uuid.uuid4()))
    )


# Strategy: Generate language codes
def language_strategy():
    """Generate language codes."""
    return st.sampled_from(["en", "hi", "ta", "te", "es", "fr"])


@pytest.mark.asyncio
@given(
    query=aadhaar_name_query(),
    language=language_strategy(),
    session_id=session_id_strategy()
)
@settings(
    max_examples=30,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
async def test_property_2a_aadhaar_name_change_preservation(query, language, session_id):
    """
    Property 2a: Preservation - Aadhaar Name Change Queries
    
    **Validates: Requirement 3.1**
    
    For any chat message containing "aadhaar" and "name" keywords,
    the system SHALL continue to return the Aadhaar name change service guide.
    
    EXPECTED OUTCOME ON UNFIXED CODE: This test PASSES
    - Response contains the Aadhaar service guide
    - service_guide field is populated with aadhaar_name_change data
    - Message indicates help with Aadhaar name change
    
    This confirms the baseline behavior that must be preserved after the fix.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {
            "message": query,
            "language": language
        }
        if session_id:
            payload["session_id"] = session_id
        
        response = await client.post(
            "/api/v1/chat/",
            json=payload
        )
        
        assert response.status_code == 200, \
            f"Chat endpoint failed with status {response.status_code} for query: {query}"
        
        data = response.json()
        
        # Verify Aadhaar service guide is returned
        assert data.get("service_guide") is not None, \
            f"Query '{query}' should return Aadhaar service guide. Got: {data}"
        
        assert data["service_guide"]["service_id"] == "aadhaar_name_change", \
            f"Query '{query}' should return aadhaar_name_change service. " \
            f"Got: {data['service_guide']['service_id']}"
        
        # Verify message mentions Aadhaar
        assert "aadhaar" in data["message"].lower(), \
            f"Response message should mention Aadhaar. Got: {data['message']}"


@pytest.mark.asyncio
@given(
    query=generic_greeting(),
    language=language_strategy(),
    session_id=session_id_strategy()
)
@settings(
    max_examples=30,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
async def test_property_2b_welcome_message_preservation(query, language, session_id):
    """
    Property 2b: Preservation - Welcome Message for Generic Greetings
    
    **Validates: Requirement 3.2**
    
    For any chat message that is a generic greeting or unclear query,
    the system SHALL continue to return the welcome message with available service options.
    
    EXPECTED OUTCOME ON UNFIXED CODE: This test PASSES
    - Response contains the welcome message
    - No service_guide field is populated
    - Message lists available services
    
    This confirms the baseline behavior that must be preserved after the fix.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {
            "message": query,
            "language": language
        }
        if session_id:
            payload["session_id"] = session_id
        
        response = await client.post(
            "/api/v1/chat/",
            json=payload
        )
        
        assert response.status_code == 200, \
            f"Chat endpoint failed with status {response.status_code} for query: {query}"
        
        data = response.json()
        
        # Verify no service guide is returned (welcome message only)
        assert data.get("service_guide") is None, \
            f"Generic query '{query}' should not return a service guide. Got: {data.get('service_guide')}"
        
        # Verify welcome message content
        message = data["message"].lower()
        assert "government services assistant" in message or "help you with" in message, \
            f"Response should contain welcome message. Got: {data['message']}"


@pytest.mark.asyncio
@given(
    query=st.text(min_size=1, max_size=100),
    language=language_strategy()
)
@settings(
    max_examples=30,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
async def test_property_2c_session_id_generation(query, language):
    """
    Property 2c: Preservation - Session ID Generation
    
    **Validates: Requirement 3.3**
    
    For any chat message without a session_id provided,
    the system SHALL continue to generate a new session_id automatically.
    
    EXPECTED OUTCOME ON UNFIXED CODE: This test PASSES
    - Response contains a session_id
    - session_id is a valid UUID format
    
    This confirms the baseline behavior that must be preserved after the fix.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/chat/",
            json={
                "message": query,
                "language": language
                # No session_id provided
            }
        )
        
        assert response.status_code == 200, \
            f"Chat endpoint failed with status {response.status_code}"
        
        data = response.json()
        
        # Verify session_id is generated
        assert "session_id" in data, \
            f"Response should contain session_id. Got: {data}"
        
        assert data["session_id"] is not None, \
            f"session_id should not be None. Got: {data}"
        
        # Verify it's a valid UUID format
        try:
            uuid.UUID(data["session_id"])
        except ValueError:
            pytest.fail(f"session_id should be a valid UUID. Got: {data['session_id']}")


@pytest.mark.asyncio
@given(
    query=st.text(min_size=1, max_size=100),
    language=language_strategy(),
    session_id=st.builds(lambda: str(uuid.uuid4()))
)
@settings(
    max_examples=30,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
async def test_property_2d_session_id_preservation(query, language, session_id):
    """
    Property 2d: Preservation - Session ID Preservation
    
    **Validates: Requirement 3.4**
    
    For any chat message with a valid session_id provided,
    the system SHALL continue to use that session_id in the response.
    
    EXPECTED OUTCOME ON UNFIXED CODE: This test PASSES
    - Response contains the same session_id that was provided
    
    This confirms the baseline behavior that must be preserved after the fix.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/chat/",
            json={
                "message": query,
                "language": language,
                "session_id": session_id
            }
        )
        
        assert response.status_code == 200, \
            f"Chat endpoint failed with status {response.status_code}"
        
        data = response.json()
        
        # Verify the same session_id is returned
        assert data.get("session_id") == session_id, \
            f"Response should preserve the provided session_id. " \
            f"Expected: {session_id}, Got: {data.get('session_id')}"


@pytest.mark.asyncio
@given(
    query=st.text(min_size=1, max_size=100),
    language=language_strategy()
)
@settings(
    max_examples=30,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
async def test_property_2e_language_preservation(query, language):
    """
    Property 2e: Preservation - Language Field Preservation
    
    **Validates: Requirement 3.4 (implicit language handling)**
    
    For any chat message with a language value provided,
    the system SHALL continue to preserve that language in the response.
    
    EXPECTED OUTCOME ON UNFIXED CODE: This test PASSES
    - Response contains the same language that was provided
    
    This confirms the baseline behavior that must be preserved after the fix.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/chat/",
            json={
                "message": query,
                "language": language
            }
        )
        
        assert response.status_code == 200, \
            f"Chat endpoint failed with status {response.status_code}"
        
        data = response.json()
        
        # Verify the same language is returned
        assert data.get("language") == language, \
            f"Response should preserve the provided language. " \
            f"Expected: {language}, Got: {data.get('language')}"


# Unit tests for specific preservation scenarios

@pytest.mark.asyncio
async def test_aadhaar_name_change_basic():
    """
    Unit test: Basic Aadhaar name change query
    
    Verifies that "aadhaar name change" returns the service guide.
    
    EXPECTED ON UNFIXED CODE: PASSES
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
        
        assert data.get("service_guide") is not None
        assert data["service_guide"]["service_id"] == "aadhaar_name_change"


@pytest.mark.asyncio
async def test_hello_greeting():
    """
    Unit test: Hello greeting
    
    Verifies that "hello" returns the welcome message without service guide.
    
    EXPECTED ON UNFIXED CODE: PASSES
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/chat/",
            json={
                "message": "hello",
                "language": "en"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("service_guide") is None
        assert "government services assistant" in data["message"].lower()


@pytest.mark.asyncio
async def test_session_id_auto_generation():
    """
    Unit test: Session ID auto-generation
    
    Verifies that when no session_id is provided, one is generated.
    
    EXPECTED ON UNFIXED CODE: PASSES
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/chat/",
            json={
                "message": "hello",
                "language": "en"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        # Verify it's a valid UUID
        uuid.UUID(data["session_id"])


@pytest.mark.asyncio
async def test_session_id_preservation():
    """
    Unit test: Session ID preservation
    
    Verifies that when a session_id is provided, it is preserved in the response.
    
    EXPECTED ON UNFIXED CODE: PASSES
    """
    test_session_id = str(uuid.uuid4())
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/chat/",
            json={
                "message": "hello",
                "language": "en",
                "session_id": test_session_id
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["session_id"] == test_session_id


@pytest.mark.asyncio
async def test_language_preservation():
    """
    Unit test: Language preservation
    
    Verifies that the language field is preserved in the response.
    
    EXPECTED ON UNFIXED CODE: PASSES
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/chat/",
            json={
                "message": "hello",
                "language": "hi"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["language"] == "hi"


@pytest.mark.asyncio
async def test_multiple_aadhaar_variations():
    """
    Unit test: Multiple Aadhaar name change query variations
    
    Verifies that various phrasings of Aadhaar name change queries
    all return the service guide.
    
    EXPECTED ON UNFIXED CODE: PASSES
    """
    queries = [
        "aadhaar name change",
        "how to change name in aadhaar",
        "aadhaar name update",
        "change my aadhaar name",
        "update name in aadhaar card",
    ]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        for query in queries:
            response = await client.post(
                "/api/v1/chat/",
                json={
                    "message": query,
                    "language": "en"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data.get("service_guide") is not None, \
                f"Query '{query}' should return service guide"
            assert data["service_guide"]["service_id"] == "aadhaar_name_change", \
                f"Query '{query}' should return aadhaar_name_change service"
