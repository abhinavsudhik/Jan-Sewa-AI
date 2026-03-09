# Railway Deployment Troubleshooting

## Current Issue: "Application failed to respond"

This means your backend is crashing on startup. Here's how to fix it:

## Step 1: Check Railway Deployment Logs

1. Go to Railway Dashboard → Your Project
2. Click on your backend service
3. Click on "Deployments" tab
4. Click on the latest deployment
5. Look at the logs - they will show the exact error

**Common errors you might see:**
- `ModuleNotFoundError` - Missing dependencies
- `Connection refused` - Database not configured
- `KeyError: 'GEMINI_API_KEY'` - Missing environment variable
- `ValidationError` - Pydantic settings validation failed

## Step 2: Required Environment Variables

Add these in Railway → Variables tab:

### Essential Variables:
```bash
# Google Gemini API (REQUIRED)
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Secret Key (REQUIRED)
SECRET_KEY=3d5703b9c7eca5a4be458d05600b81e74f13fb47623e347af29ca941c68862fc

# Environment
ENVIRONMENT=production

# CORS (REQUIRED for Vercel)
VERCEL_URL=https://jansewaai-beige.vercel.app
```

### Database (if using PostgreSQL):
```bash
# Railway will auto-provide this if you add PostgreSQL service
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### Optional:
```bash
REDIS_URL=${{Redis.REDIS_URL}}
```

## Step 3: Add PostgreSQL Database (if needed)

If your app uses a database:

1. In Railway Dashboard → Your Project
2. Click "+ New" → "Database" → "Add PostgreSQL"
3. Railway will automatically create `DATABASE_URL` variable
4. Link it to your backend service

## Step 4: Make Config More Flexible

Your current config requires certain variables. Let's make it more deployment-friendly:

### Option A: Use Default Values (Recommended)

Update your Railway environment variables to include all required fields.

### Option B: Make Variables Optional

If you want the app to start without certain features, we can modify the config to have better defaults.

## Step 5: Check Build Process

Railway uses Nixpacks. Make sure:
- `requirements.txt` is in the `backend/` directory
- `Procfile` is in the `backend/` directory
- Railway's "Root Directory" is set to `backend/`

## Step 6: Verify Start Command

In Railway → Settings → Deploy:
- Start Command should be: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Root Directory should be: `backend`

## Quick Fix Checklist

- [ ] Check Railway logs for the actual error
- [ ] Add `GEMINI_API_KEY` environment variable
- [ ] Add `SECRET_KEY` environment variable
- [ ] Add `VERCEL_URL` environment variable
- [ ] Add PostgreSQL database if needed
- [ ] Verify Root Directory is set to `backend`
- [ ] Wait for successful deployment (green checkmark)
- [ ] Test the `/health` endpoint

## After Fixing

Once deployed successfully, test these URLs:

1. Health check: `https://angelic-achievement-production-1796.up.railway.app/health`
2. CORS debug: `https://angelic-achievement-production-1796.up.railway.app/cors-debug`
3. API docs: `https://angelic-achievement-production-1796.up.railway.app/docs`

## Still Not Working?

Share the Railway deployment logs with me. The logs will show the exact error that's preventing your app from starting.
