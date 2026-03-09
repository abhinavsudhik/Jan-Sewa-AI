# Fix CORS Error on Railway

## Problem
Your Vercel frontend (`https://jansewaai-beige.vercel.app`) cannot access your Railway backend because the backend doesn't allow requests from that origin.

## Solution

### Step 1: Set Environment Variable on Railway

1. Go to your Railway dashboard: https://railway.app/dashboard
2. Select your project: `angelic-achievement-production-1796`
3. Click on your backend service
4. Go to the "Variables" tab
5. Add this environment variable:
   ```
   VERCEL_URL=https://jansewaai-beige.vercel.app
   ```
6. Click "Add" or "Save"
7. Railway will automatically redeploy your backend

### Step 2: Verify the Fix

After Railway redeploys (usually takes 1-2 minutes):

1. Open your Vercel app: https://jansewaai-beige.vercel.app
2. Try sending a chat message
3. The CORS error should be gone

### Optional: Add Multiple Origins

If you have multiple frontend URLs (staging, production, etc.), you can add them using:

```
ADDITIONAL_CORS_ORIGINS=https://staging.example.com,https://another-domain.com
```

## How It Works

The backend code in `backend/app/core/config.py` reads the `VERCEL_URL` environment variable and adds it to the list of allowed CORS origins. When Railway restarts with this variable set, your Vercel frontend will be able to make requests.

## Current Allowed Origins

After setting `VERCEL_URL`, your backend will allow requests from:
- `http://localhost:3000` (local development)
- `http://localhost:3001` (local development)
- `https://jansewaai-beige.vercel.app` (your Vercel deployment)

## Troubleshooting

If it still doesn't work after setting the variable:

1. Check Railway logs to confirm the variable is set
2. Verify the Vercel URL is exactly correct (no trailing slash)
3. Clear your browser cache and try again
4. Check Railway deployment logs for any errors
