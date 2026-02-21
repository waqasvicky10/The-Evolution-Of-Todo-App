# Login Error Fix - "Connect to Server" / ERR_CONNECTION_REFUSED

## Problem
Login fails with:
- `401 Unauthorized` or `net::ERR_CONNECTION_REFUSED` on `api/auth/login`
- "Connect to Server" error

## Cause
The frontend on Vercel needs to talk to your **backend API**. Right now `API_URL` is not set, so it tries to connect to `localhost:8000` (which does not exist on Vercel).

---

## Fix (2 Steps)

### Step 1: Deploy Backend (if not done)

Deploy the backend to **Render** or **Railway**:

1. Go to https://render.com (or railway.app)
2. Create a new **Web Service**
3. Connect your GitHub repo: `The-Evolution-Of-Todo-App-phase-V`
4. Set **Root Directory**: `backend`
5. Add environment variables:
   - `DATABASE_URL` (from Neon or use SQLite)
   - `SECRET_KEY` (any long random string)
   - `CORS_ORIGINS` = `https://phase5-todo-app.vercel.app`
6. Deploy and copy your backend URL (e.g. `https://todo-api-xyz.onrender.com`)

---

### Step 2: Add API_URL in Vercel

1. Go to https://vercel.com/dashboard
2. Open project **phase5-todo-app**
3. **Settings** → **Environment Variables**
4. Click **Add**
5. **Name:** `API_URL`
6. **Value:** Your backend URL (e.g. `https://todo-api-xyz.onrender.com`)
7. **Environment:** Production (and Preview if you want)
8. **Save**
9. **Deployments** → Latest → **Redeploy**

---

## Quick Checklist

- [ ] Backend deployed (Render/Railway)
- [ ] Backend URL copied
- [ ] `API_URL` added in Vercel (with backend URL)
- [ ] `CORS_ORIGINS` on backend includes `https://phase5-todo-app.vercel.app`
- [ ] Redeployed on Vercel after adding env var

---

## Test

1. Visit https://phase5-todo-app.vercel.app
2. Click Register → create account
3. Login → should work
