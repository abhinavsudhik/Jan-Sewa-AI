"""
Investigation test to see what CORS headers are actually being returned
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_investigate_cors_headers():
    """
    Investigate what CORS headers are actually being returned for Vercel origins
    """
    origin = "https://jansewaai-beige.vercel.app"
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Test preflight
        response = await client.request(
            "OPTIONS",
            "/api/v1/chat",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        
        print(f"\n=== Preflight Response for {origin} ===")
        print(f"Status: {response.status_code}")
        print(f"All headers: {dict(response.headers)}")
        print(f"CORS Allow Origin: {response.headers.get('access-control-allow-origin', 'NOT PRESENT')}")
        print(f"CORS Allow Credentials: {response.headers.get('access-control-allow-credentials', 'NOT PRESENT')}")
        
        # Test POST
        post_response = await client.post(
            "/api/v1/chat",
            headers={
                "Origin": origin,
                "Content-Type": "application/json"
            },
            json={"message": "test"}
        )
        
        print(f"\n=== POST Response for {origin} ===")
        print(f"Status: {post_response.status_code}")
        print(f"All headers: {dict(post_response.headers)}")
        print(f"CORS Allow Origin: {post_response.headers.get('access-control-allow-origin', 'NOT PRESENT')}")
        print(f"CORS Allow Credentials: {post_response.headers.get('access-control-allow-credentials', 'NOT PRESENT')}")


@pytest.mark.asyncio
async def test_investigate_localhost_cors():
    """
    Investigate CORS headers for localhost (should work)
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
        
        print(f"\n=== Preflight Response for {origin} ===")
        print(f"Status: {response.status_code}")
        print(f"CORS Allow Origin: {response.headers.get('access-control-allow-origin', 'NOT PRESENT')}")
        print(f"CORS Allow Credentials: {response.headers.get('access-control-allow-credentials', 'NOT PRESENT')}")
