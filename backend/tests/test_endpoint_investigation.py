"""
Investigation test to check endpoint routing and trailing slash behavior
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_chat_endpoint_with_trailing_slash():
    """Test /api/v1/chat/ with trailing slash"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/chat/",
            json={"message": "test"}
        )
        print(f"\n=== POST /api/v1/chat/ (with trailing slash) ===")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json() if response.status_code != 404 else 'NOT FOUND'}")


@pytest.mark.asyncio
async def test_chat_endpoint_without_trailing_slash():
    """Test /api/v1/chat without trailing slash"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/chat",
            json={"message": "test"}
        )
        print(f"\n=== POST /api/v1/chat (without trailing slash) ===")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json() if response.status_code != 404 else 'NOT FOUND'}")
        if response.status_code == 307:
            print(f"Redirect location: {response.headers.get('location')}")


@pytest.mark.asyncio
async def test_chat_endpoint_with_cors_and_trailing_slash():
    """Test /api/v1/chat/ with CORS headers and trailing slash"""
    origin = "https://jansewaai-beige.vercel.app"
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver", follow_redirects=False) as client:
        # Preflight
        preflight = await client.request(
            "OPTIONS",
            "/api/v1/chat/",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST"
            }
        )
        print(f"\n=== OPTIONS /api/v1/chat/ with Origin: {origin} ===")
        print(f"Status: {preflight.status_code}")
        print(f"CORS Allow Origin: {preflight.headers.get('access-control-allow-origin', 'NOT PRESENT')}")
        
        # POST
        post = await client.post(
            "/api/v1/chat/",
            headers={"Origin": origin},
            json={"message": "test"}
        )
        print(f"\n=== POST /api/v1/chat/ with Origin: {origin} ===")
        print(f"Status: {post.status_code}")
        print(f"CORS Allow Origin: {post.headers.get('access-control-allow-origin', 'NOT PRESENT')}")


@pytest.mark.asyncio
async def test_chat_endpoint_with_cors_without_trailing_slash():
    """Test /api/v1/chat without CORS headers and without trailing slash"""
    origin = "https://jansewaai-beige.vercel.app"
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver", follow_redirects=False) as client:
        # Preflight
        preflight = await client.request(
            "OPTIONS",
            "/api/v1/chat",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST"
            }
        )
        print(f"\n=== OPTIONS /api/v1/chat (no slash) with Origin: {origin} ===")
        print(f"Status: {preflight.status_code}")
        print(f"CORS Allow Origin: {preflight.headers.get('access-control-allow-origin', 'NOT PRESENT')}")
        
        # POST
        post = await client.post(
            "/api/v1/chat",
            headers={"Origin": origin},
            json={"message": "test"}
        )
        print(f"\n=== POST /api/v1/chat (no slash) with Origin: {origin} ===")
        print(f"Status: {post.status_code}")
        print(f"CORS Allow Origin: {post.headers.get('access-control-allow-origin', 'NOT PRESENT')}")
        if post.status_code == 307:
            print(f"Redirect location: {post.headers.get('location')}")
            print(f"IMPORTANT: Redirect responses may not include CORS headers!")
