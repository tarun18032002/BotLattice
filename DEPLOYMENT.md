# Deployment Guide

This document covers deploying BotLattice to production using Vercel (frontend) and a backend hosting service.

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account (sign up at https://vercel.com)
- GitHub repo connected to Vercel

### Steps

1. **Connect Repository**
   - Go to https://vercel.com/new
   - Select your GitHub repo (tarun18032002/BotLattice)
   - Select `frontend` as root directory

2. **Configure Build Settings**
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install` (default)
   - Framework: `Vite`

3. **Set Environment Variables** in Vercel Project Settings:
   ```
   VITE_WS_URL=https://your-backend-domain.com/ws/chat
   VITE_GOOGLE_CLIENT_ID=your-google-client-id (optional)
   ```

4. **Deploy**
   - Click Deploy
   - Vercel will build and deploy automatically
   - Your frontend will be available at `https://your-project.vercel.app`

## Backend Deployment Options

Since Vercel is primarily for serverless/static, you need a separate backend host. Options:

### Option A: Railway (Recommended for this stack)

1. **Sign up** at https://railway.app
2. **Create PostgreSQL database**
3. **Deploy FastAPI backend**
   - Connect GitHub repo
   - Select `backend` directory
   - Set environment variables:
     ```
     POSTGRES_USER=<from Railway DB>
     POSTGRES_PASSWORD=<from Railway DB>
     POSTGRES_DB=<from Railway DB>
     POSTGRES_HOST=<from Railway DB>
     POSTGRES_PORT=5432
     GOOGLE_CLIENT_ID=your-google-client-id
     ```
   - Railway auto-detects Python and uses `uvicorn`
4. Backend will be at `https://your-backend-xyz.railway.app`

### Option B: Render

1. **Sign up** at https://render.com
2. **Deploy PostgreSQL** (Render Postgres service)
3. **Deploy FastAPI backend** (New → Web Service)
   - Connect GitHub repo, select `backend` directory
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt` (or use uv)
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port 8080`
   - Set same env vars as Railway
4. Backend will be at `https://your-backend.onrender.com`

### Option C: AWS / Heroku / DigitalOcean

All support FastAPI + PostgreSQL. Similar setup, each has own guides.

## After Deployment

1. **Update frontend env** in Vercel:
   ```
   VITE_WS_URL=https://your-backend-domain.com/ws/chat
   ```

2. **Update backend CORS** (optional):
   - Modify `main.py` to allow your Vercel frontend domain:
     ```python
     allow_origins=["https://your-project.vercel.app", ...]
     ```

3. **Test end-to-end**:
   - Navigate to frontend URL
   - Sign in / register
   - Try ingestion, settings, chat

## Database Backup & Monitoring

- Most hosting services provide automatic backups
- Monitor logs from Vercel and your backend host
- Set up alerts for errors/downtime

## Cost Notes

- **Vercel**: Free tier sufficient for development
- **Railway**: ~$5/month for database + minimal backend
- **Render**: Free tier available but with limitations
- **Production**: Budget $20-100/month depending on traffic

## Troubleshooting

- **CORS errors**: Update `main.py` allow_origins to include your frontend domain
- **WebSocket connection fails**: Check `VITE_WS_URL` is correct and uses `wss://` (secure)
- **Auth not working**: Verify `GOOGLE_CLIENT_ID` matches frontend and backend
- **Database connection fails**: Check host/port/credentials in backend env
