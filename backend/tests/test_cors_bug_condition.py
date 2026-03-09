"""
Bug Condition Exploration Test for CORS Misconfiguration

**Validates: Requirements 2.1, 2.2, 2.3**

CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

This test encodes the expected behavior - it will validate the fix when it passes after implementation.
GOAL: Surface counterexamples that demonstrate the bug exists.

The bug condition is:
- Requests from Vercel domains (https://*.vercel.app) fail to receive proper CORS headers
- CORSMiddleware has conflicting configuration (both allow_origin_regex and allow_origins set)
- Response lacks 'Access-Control-Allow-Origin' header for Vercel origins
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase
from httpx import AsyncClient, ASGITransport
from app.main import app


# Strategy: Generate Vercel subdomain origins
@st.composite
def vercel_origin(draw):
    """Generate valid Vercel deployment origins."""
    # Generate subdomain: alphanumeric with hyphens, 1-63 chars
    subdomain_parts = draw(st.lists(
        st.text(
            alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), whitelist_characters='-'),
            min_size=1,
            max_size=20
        ).filter(lambda x: x and not x.startswith('-') and not x.endswith('-')),
        min_size=1,
        max_size=3
    ))
    subdomain = '-'.join(subdomain_parts)
    return f"https://{subdomain}.vercel.app"


@pytest.mark.asyncio
@given(origin=vercel_origin())
@settings(
    max_examples=50,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
async def test_property_1_cors_requests_from_vercel_succeed(origin):
    """
    Property 1: Bug Condition - CORS Requests from Vercel Succeed
    
    **Validates: Requirements 2.1, 2.2, 2.3**
    
    For any HTTP request where the origin matches a Vercel domain pattern (https://*.vercel.app),
    the CORSMiddleware SHALL return the appropriate 'Access-Control-Allow-Origin' header
    in the response, allowing the browser to complete the request successfully.
    
    EXPECTED OUTCOME ON UNFIXED CODE: This test FAILS
    - Missing 'Access-Control-Allow-Origin' header in response
    - Or header value doesn't match the request origin
    - Or 'Access-Control-Allow-Credentials' is not 'true'
    
    This failure confirms the bug exists due to conflicting CORS configuration.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Test 1: Preflight OPTIONS request
        preflight_response = await client.request(
            "OPTIONS",
            "/api/v1/chat",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        
        # Assert preflight returns proper CORS headers
        assert "access-control-allow-origin" in preflight_response.headers, \
            f"Preflight response missing 'Access-Control-Allow-Origin' header for origin: {origin}"
        
        assert preflight_response.headers["access-control-allow-origin"] == origin, \
            f"Expected 'Access-Control-Allow-Origin: {origin}', got '{preflight_response.headers.get('access-control-allow-origin')}'"
        
        assert preflight_response.headers.get("access-control-allow-credentials") == "true", \
            f"Expected 'Access-Control-Allow-Credentials: true', got '{preflight_response.headers.get('access-control-allow-credentials')}'"
        
        # Test 2: Actual POST request to /api/v1/chat
        post_response = await client.post(
            "/api/v1/chat",
            headers={
                "Origin": origin,
                "Content-Type": "application/json"
            },
            json={"message": "test query"}
        )
        
        # Assert POST response includes proper CORS headers
        assert "access-control-allow-origin" in post_response.headers, \
            f"POST response missing 'Access-Control-Allow-Origin' header for origin: {origin}"
        
        assert post_response.headers["access-control-allow-origin"] == origin, \
            f"Expected 'Access-Control-Allow-Origin: {origin}', got '{post_response.headers.get('access-control-allow-origin')}'"
        
        assert post_response.headers.get("access-control-allow-credentials") == "true", \
            f"Expected 'Access-Control-Allow-Credentials: true', got '{post_response.headers.get('access-control-allow-credentials')}'"


@pytest.mark.asyncio
async def test_specific_vercel_origin_preflight():
    """
    Unit test: Specific Vercel origin preflight request
    
    Tests that a preflight OPTIONS request from a specific Vercel domain
    receives the correct CORS headers.
    
    EXPECTED ON UNFIXED CODE: FAILS - missing CORS headers
    """
    origin = "https://jansewaai-beige.vercel.app"
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.request(
            "OPTIONS",
            "/api/v1/chat",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        
        assert response.status_code == 200, f"Preflight request failed with status {response.status_code}"
        assert "access-control-allow-origin" in response.headers, \
            "Preflight response missing 'Access-Control-Allow-Origin' header"
        assert response.headers["access-control-allow-origin"] == origin, \
            f"Expected origin '{origin}', got '{response.headers.get('access-control-allow-origin')}'"
        assert response.headers.get("access-control-allow-credentials") == "true", \
            "Missing or incorrect 'Access-Control-Allow-Credentials' header"


@pytest.mark.asyncio
async def test_specific_vercel_origin_post():
    """
    Unit test: Specific Vercel origin POST request
    
    Tests that a POST request from a specific Vercel domain receives
    the correct CORS headers in the response.
    
    EXPECTED ON UNFIXED CODE: FAILS - missing CORS headers
    """
    origin = "https://jansewaai-beige.vercel.app"
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/chat",
            headers={
                "Origin": origin,
                "Content-Type": "application/json"
            },
            json={"message": "how to change aadhaar name"}
        )
        
        # Note: The endpoint might return 422 or other errors due to missing fields,
        # but CORS headers should still be present
        assert "access-control-allow-origin" in response.headers, \
            "POST response missing 'Access-Control-Allow-Origin' header"
        assert response.headers["access-control-allow-origin"] == origin, \
            f"Expected origin '{origin}', got '{response.headers.get('access-control-allow-origin')}'"
        assert response.headers.get("access-control-allow-credentials") == "true", \
            "Missing or incorrect 'Access-Control-Allow-Credentials' header"


@pytest.mark.asyncio
async def test_multiple_vercel_subdomains():
    """
    Unit test: Multiple different Vercel subdomains
    
    Tests that various Vercel subdomain patterns all receive proper CORS headers.
    
    EXPECTED ON UNFIXED CODE: FAILS - missing CORS headers for all Vercel origins
    """
    vercel_origins = [
        "https://my-app.vercel.app",
        "https://test-deployment.vercel.app",
        "https://staging-env.vercel.app",
        "https://prod-123.vercel.app"
    ]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        for origin in vercel_origins:
            response = await client.request(
                "OPTIONS",
                "/api/v1/chat",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "POST"
                }
            )
            
            assert "access-control-allow-origin" in response.headers, \
                f"Missing CORS header for origin: {origin}"
            assert response.headers["access-control-allow-origin"] == origin, \
                f"Incorrect CORS header for origin: {origin}"
