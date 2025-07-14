# Deployment Guide

## Current Issue
The frontend on Vercel shows "Backend: failed" because it can't reach the local backend server.

## Quick Solutions

### Option 1: Deploy Backend to Railway (Recommended)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy Backend:**
   ```bash
   cd backend
   railway login
   railway init
   railway up
   ```

3. **Update Vercel Environment Variables:**
   - Go to your Vercel dashboard
   - Navigate to your project settings
   - Add environment variable:
     ```
     VITE_API_URL=https://your-backend-app.railway.app
     ```

4. **Redeploy Frontend:**
   - Push changes to trigger Vercel rebuild
   - Or manually redeploy in Vercel dashboard

### Option 2: Use ngrok for Testing

1. **Install ngrok:** https://ngrok.com/download
2. **Expose local backend:**
   ```bash
   ngrok http 8000
   ```
3. **Update Vercel environment variable:**
   ```
   VITE_API_URL=https://your-ngrok-url.ngrok.io
   ```

### Option 3: Deploy Backend to Render

1. **Create account:** https://render.com
2. **Connect GitHub repository**
3. **Deploy as Web Service:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
4. **Update Vercel environment variable with Render URL**

## Environment Variables

### Local Development
- Uses `.env.local` with `VITE_API_URL=http://127.0.0.1:8000`

### Production (Vercel)
- Set `VITE_API_URL` to your deployed backend URL
- Example: `https://your-backend-app.railway.app`

## Backend Requirements for Deployment

The backend needs these configurations for production:

1. **CORS Settings:** Already configured for frontend domains
2. **Environment Variables:** Database URL, etc.
3. **Dependencies:** All in `requirements.txt`
4. **Health Check:** Available at `/health` endpoint

## Testing the Fix

1. Deploy backend to chosen platform
2. Update `VITE_API_URL` in Vercel
3. Redeploy frontend
4. Check that "Backend: connected" appears on the frontend

## Current Backend Status
✅ Backend is running locally and healthy
✅ All API endpoints are working
✅ Frontend code updated to use environment variables
❌ Backend not deployed to public server (causing Vercel issue)
