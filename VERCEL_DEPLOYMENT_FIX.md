# Fix Frontend-Backend Connection on Vercel

## Problem
Your Vercel frontend can't connect to the backend due to:
1. CORS configuration blocking Vercel domain
2. Missing or incorrect environment variable
3. Backend not allowing HTTPS requests from Vercel

## Solution

### Step 1: Update Backend CORS Configuration

Update `backend/app/core/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://govt_services_user:secure_password_here@postgres:5432/govt_services"
    REDIS_URL: str = "redis://redis:6379"
    GEMINI_API_KEY: str = "your_key_here"
    SECRET_KEY: str = "dev_secret_key"
    ENVIRONMENT: str = "development"
    
    # Updated CORS to allow Vercel domains
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://*.vercel.app",  # Allow all Vercel preview deployments
        "https://your-app.vercel.app",  # Your production Vercel domain
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### Step 2: Update Backend CORS Middleware

Update `backend/app/main.py` to handle wildcard origins:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import services, chat, documents, dashboard
import re

app = FastAPI(
    title="Government Services Assistant API",
    description="AI-powered conversational agent for government services guidance",
    version="1.0.0"
)

# Enhanced CORS middleware with regex support
def is_allowed_origin(origin: str) -> bool:
    """Check if origin matches allowed patterns"""
    allowed_patterns = [
        r"^http://localhost:\d+$",  # Local development
        r"^https://.*\.vercel\.app$",  # Vercel deployments
        r"^https://your-custom-domain\.com$",  # Your custom domain
    ]
    return any(re.match(pattern, origin) for pattern in allowed_patterns)

# CORS middleware with dynamic origin checking
@app.middleware("http")
async def cors_middleware(request, call_next):
    origin = request.headers.get("origin")
    response = await call_next(request)
    
    if origin and is_allowed_origin(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response

# Fallback CORS for preflight requests
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(services.router, prefix="/api/v1/services", tags=["services"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    return {
        "message": "Government Services Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Step 3: Configure Vercel Environment Variables

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add the following variable:

```
Name: NEXT_PUBLIC_API_URL
Value: https://your-backend-url.railway.app
```

Or if using Railway:
```
Name: NEXT_PUBLIC_API_URL
Value: https://your-app.up.railway.app
```

4. Click **Save**
5. **Redeploy** your frontend (Vercel → Deployments → Redeploy)

### Step 4: Update Backend Environment Variables

If your backend is on Railway:

1. Go to Railway dashboard → Your project
2. Click on your backend service
3. Go to **Variables** tab
4. Add/Update:

```
CORS_ORIGINS=["http://localhost:3000","https://your-app.vercel.app","https://*.vercel.app"]
ENVIRONMENT=production
```

### Step 5: Test the Connection

After redeploying both frontend and backend:

1. Open browser console (F12) on your Vercel site
2. Try sending a message
3. Check for errors:

**If you see CORS error:**
```
Access to XMLHttpRequest at 'https://backend.com' from origin 'https://app.vercel.app' 
has been blocked by CORS policy
```
→ Backend CORS not configured correctly

**If you see Network error:**
```
Network Error
```
→ Check if backend URL is correct in Vercel env vars

**If you see 404:**
```
404 Not Found
```
→ API endpoint path is wrong

### Step 6: Verify Backend is Running

Test your backend directly:

```bash
# Test health endpoint
curl https://your-backend-url.railway.app/health

# Should return:
{"status":"healthy"}

# Test API endpoint
curl -X POST https://your-backend-url.railway.app/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","language":"en"}'
```

### Step 7: Debug with Browser Console

Add this to your frontend to debug:

```typescript
// In frontend/pages/index.tsx
const sendMessage = async () => {
  if (!input.trim()) return

  console.log('API_URL:', API_URL) // Check if URL is correct
  console.log('Sending to:', `${API_URL}/api/v1/chat/`)

  const userMessage: Message = { role: 'user', content: input }
  setMessages(prev => [...prev, userMessage])
  setInput('')
  setLoading(true)

  try {
    const response = await axios.post(`${API_URL}/api/v1/chat/`, {
      message: input,
      language: 'en'
    })
    console.log('Response:', response.data) // Check response
    // ... rest of code
  } catch (error) {
    console.error('Full error:', error) // See full error
    console.error('Error response:', error.response?.data) // See backend error
    // ... rest of code
  }
}
```

## Quick Fix Checklist

- [ ] Updated backend CORS configuration
- [ ] Redeployed backend (Railway/other)
- [ ] Added `NEXT_PUBLIC_API_URL` to Vercel environment variables
- [ ] Redeployed frontend on Vercel
- [ ] Tested backend health endpoint directly
- [ ] Checked browser console for errors
- [ ] Verified API URL in frontend console logs

## Common Issues & Solutions

### Issue 1: "CORS policy" error
**Solution:** Update backend CORS to include your Vercel domain

### Issue 2: "Network Error"
**Solution:** Check if `NEXT_PUBLIC_API_URL` is set correctly in Vercel

### Issue 3: Backend returns 404
**Solution:** Verify API endpoint path matches backend routes

### Issue 4: Backend not responding
**Solution:** Check if backend service is running (Railway dashboard)

### Issue 5: Environment variable not updating
**Solution:** Redeploy after changing environment variables

## Alternative: Use Vercel Serverless Functions

If backend connection is still problematic, you can proxy requests through Vercel:

Create `frontend/pages/api/chat.ts`:

```typescript
import type { NextApiRequest, NextApiResponse } from 'next'
import axios from 'axios'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const response = await axios.post(
      `${BACKEND_URL}/api/v1/chat/`,
      req.body
    )
    res.status(200).json(response.data)
  } catch (error) {
    console.error('Proxy error:', error)
    res.status(500).json({ error: 'Backend request failed' })
  }
}
```

Then update frontend to use `/api/chat` instead of direct backend URL.

## Need More Help?

Share these details:
1. Your Vercel frontend URL
2. Your backend URL (Railway/other)
3. Error message from browser console
4. Response from `curl https://your-backend/health`

I'll help you debug further!
