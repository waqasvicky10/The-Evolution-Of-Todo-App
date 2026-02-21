# Vercel Deployment - Phase 5

**Target URL:** https://phase5-todo-app.vercel.app

---

## Quick Deploy

### 1. Import Project (New)

1. Go to [vercel.com](https://vercel.com) → **Add New** → **Project**
2. Import from GitHub: `The-Evolution-Of-Todo-App-phase-V`
3. **Project Name:** `phase5-todo-app` ← This will be your URL
4. **Root Directory:** `frontend` (Click Edit and select it)
5. **Environment Variables** — add:
   - `API_URL` = Your backend URL (e.g. `https://todo-api.onrender.com`)
6. Click **Deploy**

### 2. Update Existing Project

If you already have a Vercel project:

1. Open [Vercel Dashboard](https://vercel.com/dashboard)
2. Project → **Settings** → **General**
3. Change **Project Name** to: `phase5-todo-app`
4. Save → URL will become: **https://phase5-todo-app.vercel.app**

### 3. Redeploy (After Code Update)

```bash
# Option A: GitHub push — auto deploy
git push origin main

# Option B: Via Vercel CLI
cd frontend
npx vercel --prod
```

---

## Root Directory Setting (404 Fix)

**Path:** Settings → **General** (or **Build and Deployment**) → scroll down → **Root Directory** → Edit → type `frontend` → Save

Detailed guide: [VERCEL_ROOT_DIRECTORY_GUIDE.md](VERCEL_ROOT_DIRECTORY_GUIDE.md)

---

## Config Summary

| Setting | Value |
|---------|-------|
| Project Name | phase5-todo-app |
| Root Directory | frontend |
| Framework | Next.js |
| Build Command | npm run build |
| Live URL | https://phase5-todo-app.vercel.app |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_URL` | **Yes** (production) | Backend API URL — **required for login/tasks** |
| `NEXT_PUBLIC_BASE_URL` | Yes | `https://phase5-todo-app.vercel.app` |
| `NEXT_PUBLIC_API_BASE_URL` | No | Leave empty for proxy mode |

**Without `API_URL`:** Login will fail with "Connect to Server" / ERR_CONNECTION_REFUSED. See [LOGIN_ERROR_FIX.md](LOGIN_ERROR_FIX.md).

---

## Backend CORS

Allow CORS in your backend:

```
https://phase5-todo-app.vercel.app
```

Add this URL to `CORS_ORIGINS` (or equivalent) in your Render/Railway dashboard.
