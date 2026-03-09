"""
Preservation Property Tests for CORS Configuration

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

Property 2: Preservation - Non-Vercel CORS Behavior Unchanged

These tests verify that the fix does not break existing functionality.
They capture the baseline behavior observed on UNFIXED code and ensure
it remains unchanged after the fix is applied.

EXPECTED OUTCOME ON UNFIXED CODE: Tests PASS (confirms baseline behavior)
EXPECTED OUTCOME ON FIXED CODE: Tests PASS (confirms no regressions)
"""

import pytest
from hypothesis import given, strategies as st, settings, Phase
from httpx import AsyncClient, ASGITransport
from app.main import app


# Strategy: Generate localhost origins with configured ports only
@st.composite
def localhost_origin(draw):
    """Generate localhost origins with ports that are configured in CORS middleware."""
    # Only test ports that are actually allowed in the current configuration
    port = draw(st.sampled_from([3000, 3001]))
    return f"http://localhost:{port}"


# Strategy: Generate common API endpoints
@st.composite
def api_endpoint(draw):
    """Generate various API endpoints to test CORS across routes."""
    endpoints = [
        "/api/v1/chat",
        "/api/v1/services",
        "/api/v1/documents",
        "/api/v1/dashboard"
    ]
    return draw(st.sampled_from(endpoints))


# Strategy: Generate HTTP methods
def http_method():
    """Generate various HTTP methods."""
    return st.sampled_from(["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])


@pytest.mark.asyncio
@given(origin=localhost_origin())
@settings(
    max_examples=30,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
async def test_property_2_localhost_cors_preserved(origin):
    """
    Property 2a: Localhost CORS Behavior Preserved
    
    **Validates: Requirements 3.1, 3.2**
    
    For any HTTP request from localhost origins (http://localhost:3000, http://localhost:3001),
    the CORSMiddleware SHALL continue to return proper CORS headers exactly as it did
    before the fix, preserving development workflow.
    
    Observed baseline behavior:
    - Preflight OPTIONS requests return 200 with proper CORS headers
    - Access-Control-Allow-Origin matches the request origin
    - Access-Control-Allow-Credentials is 'true'
    - Access-Control-Allow-Methods includes all methods
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Test preflight OPTIONS request
        preflight_response = await client.request(
            "OPTIONS",
            "/api/v1/chat",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        
        # Assert preflight behavior is preserved
        assert preflight_response.status_code == 200, \
            f"Preflight request failed for {origin} with status {preflight_response.status_code}"
        
        assert "access-control-allow-origin" in preflight_response.headers, \
            f"Missing 'Access-Control-Allow-Origin' header for localhost origin: {origin}"
        
        assert preflight_response.headers["access-control-allow-origin"] == origin, \
            f"Expected 'Access-Control-Allow-Origin: {origin}', got '{preflight_response.headers.get('access-control-allow-origin')}'"
        
        assert preflight_response.headers.get("access-control-allow-credentials") == "true", \
            f"Expected 'Access-Control-Allow-Credentials: true', got '{preflight_response.headers.get('access-control-allow-credentials')}'"
        
        # Verify methods are allowed
        allow_methods = preflight_response.headers.get("access-control-allow-methods", "")
        assert "POST" in allow_methods, \
            f"POST method not in allowed methods: {allow_methods}"


@pytest.mark.asyncio
async def test_property_2_health_endpoint_preserved():
    """
    Property 2b: Health Endpoint Behavior Preserved
    
    **Validates: Requirement 3.3**
    
    The /health endpoint SHALL continue to respond correctly with status 200
    and the expected JSON response, exactly as it did before the fix.
    
    Observed baseline behavior:
    - Returns 200 status code
    - Returns {"status": "healthy"} JSON response
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200, \
            f"Health endpoint returned status {response.status_code}, expected 200"
        
        assert response.json() == {"status": "healthy"}, \
            f"Health endpoint returned unexpected response: {response.json()}"


@pytest.mark.asyncio
async def test_property_2_root_endpoint_preserved():
    """
    Property 2c: Root Endpoint Behavior Preserved
    
    **Validates: Requirement 3.3**
    
    The / endpoint SHALL continue to respond correctly with status 200
    and the expected JSON response, exactly as it did before the fix.
    
    Observed baseline behavior:
    - Returns 200 status code
    - Returns API information JSON with message, version, and docs fields
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/")
        
        assert response.status_code == 200, \
            f"Root endpoint returned status {response.status_code}, expected 200"
        
        response_data = response.json()
        assert "message" in response_data, "Root endpoint missing 'message' field"
        assert "version" in response_data, "Root endpoint missing 'version' field"
        assert "docs" in response_data, "Root endpoint missing 'docs' field"
        assert response_data["version"] == "1.0.0", \
            f"Unexpected version: {response_data['version']}"


@pytest.mark.asyncio
@given(method=http_method())
@settings(
    max_examples=20,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
async def test_property_2_cors_credentials_preserved(method):
    """
    Property 2d: CORS Credentials Setting Preserved
    
    **Validates: Requirement 3.4**
    
    For any HTTP method in cross-origin requests from localhost,
    the CORSMiddleware SHALL continue to allow credentials
    (Access-Control-Allow-Credentials: true), exactly as before the fix.
    
    Observed baseline behavior:
    - Access-Control-Allow-Credentials is always 'true' for localhost origins
    """
    origin = "http://localhost:3000"
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.request(
            "OPTIONS",
            "/api/v1/chat",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": method
            }
        )
        
        assert response.headers.get("access-control-allow-credentials") == "true", \
            f"Expected credentials allowed for method {method}, got '{response.headers.get('access-control-allow-credentials')}'"


@pytest.mark.asyncio
async def test_property_2_cors_methods_preserved():
    """
    Property 2e: CORS Methods Setting Preserved
    
    **Validates: Requirement 3.5**
    
    The CORSMiddleware SHALL continue to allow all HTTP methods
    (allow_methods=["*"]), exactly as before the fix.
    
    Observed baseline behavior:
    - Access-Control-Allow-Methods includes: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
    """
    origin = "http://localhost:3000"
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.request(
            "OPTIONS",
            "/api/v1/chat",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST"
            }
        )
        
        allow_methods = response.headers.get("access-control-allow-methods", "")
        
        # Verify all common methods are allowed
        expected_methods = ["DELETE", "GET", "POST", "PUT", "PATCH", "OPTIONS"]
        for method in expected_methods:
            assert method in allow_methods, \
                f"Method {method} not in allowed methods: {allow_methods}"


@pytest.mark.asyncio
@given(headers=st.lists(
    st.sampled_from([
        "content-type",
        "authorization",
        "x-custom-header",
        "x-api-key",
        "accept"
    ]),
    min_size=1,
    max_size=3,
    unique=True
))
@settings(
    max_examples=20,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
async def test_property_2_cors_headers_preserved(headers):
    """
    Property 2f: CORS Headers Setting Preserved
    
    **Validates: Requirement 3.6**
    
    For any headers included in cross-origin requests from localhost,
    the CORSMiddleware SHALL continue to allow all headers
    (allow_headers=["*"]), exactly as before the fix.
    
    Observed baseline behavior:
    - Access-Control-Allow-Headers echoes back the requested headers
    - All requested headers are allowed
    """
    origin = "http://localhost:3000"
    headers_str = ", ".join(headers)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.request(
            "OPTIONS",
            "/api/v1/chat",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": headers_str
            }
        )
        
        allow_headers = response.headers.get("access-control-allow-headers", "")
        
        # Verify all requested headers are allowed
        for header in headers:
            assert header in allow_headers.lower(), \
                f"Header '{header}' not in allowed headers: {allow_headers}"


@pytest.mark.asyncio
async def test_property_2_specific_localhost_3000():
    """
    Unit test: Specific localhost:3000 preservation
    
    **Validates: Requirement 3.1**
    
    Verifies that requests from http://localhost:3000 continue to work
    exactly as they did before the fix.
    """
    origin = "http://localhost:3000"
    
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
        
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin
        assert response.headers["access-control-allow-credentials"] == "true"


@pytest.mark.asyncio
async def test_property_2_specific_localhost_3001():
    """
    Unit test: Specific localhost:3001 preservation
    
    **Validates: Requirement 3.2**
    
    Verifies that requests from http://localhost:3001 continue to work
    exactly as they did before the fix.
    """
    origin = "http://localhost:3001"
    
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
        
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin
        assert response.headers["access-control-allow-credentials"] == "true"
