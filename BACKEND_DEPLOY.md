# Backend Deploy - One Click (Render)

## Deploy to Render (2 minutes)

### Option A: Deploy Button (Easiest)

**Click this button:**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/waqasvicky10/The-Evolution-Of-Todo-App)

1. Click the button above
2. Sign in to Render (or create account with GitHub)
3. Click **Deploy Blueprint**
4. Wait 3–5 minutes for build
5. Copy your backend URL (e.g. `https://phase5-todo-api.onrender.com`)

---

### Option B: Manual Blueprint

1. Go to https://dashboard.render.com
2. **New +** → **Blueprint**
3. Connect repo: `The-Evolution-Of-Todo-App`
4. Click **Deploy Blueprint**
5. Copy backend URL when done

---

## After Deploy: Add API_URL to Vercel

1. Vercel → **phase5-todo-app** → **Settings** → **Environment Variables**
2. Add: **Name** `API_URL`, **Value** = your Render backend URL
3. **Redeploy** the frontend

---

## Test

- Backend health: `https://YOUR-BACKEND-URL.onrender.com/health`
- Frontend login: https://phase5-todo-app.vercel.app
