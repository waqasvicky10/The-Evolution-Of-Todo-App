# Backend Deploy — No Credit Card Required

Render card maang raha hai. Yeh platforms **card ke bina** free deploy dete hain:

---

## Option 1: Koyeb (Recommended)

**https://www.koyeb.com** — FastAPI support, no card

### Steps:

1. **Sign up:** https://app.koyeb.com/auth/signup  
   - GitHub se sign up karein (card nahi maangega)

2. **Create App:**
   - Dashboard → **Create App**
   - **GitHub** select karein
   - Repo: **The-Evolution-Of-Todo-App** select karein

3. **Settings:**
   - **Name:** `phase5-todo-api`
   - **Root directory:** `backend`
   - **Build command:** `pip install -r requirements.txt`
   - **Run command:** `uvicorn app.main:app --host 0.0.0.0`  
  (Koyeb auto-sets PORT; agar port chahiye to `--port $PORT` add karein)

4. **Environment Variables** (Add):
   | Key | Value |
   |-----|-------|
   | `SECRET_KEY` | `phase5-secret-key-32chars` |
   | `CORS_ORIGINS` | `https://phase5-todo-app.vercel.app` |
   | `DATABASE_URL` | `sqlite:///./todo.db` |

5. **Deploy** par click karein

6. Deploy hone ke baad **URL copy** karein (e.g. `https://phase5-todo-api-xxx.koyeb.app`)

---

## Option 2: Cyclic.sh

**https://www.cyclic.sh** — Python beta, no card

### Steps:

1. **Sign up:** https://www.cyclic.sh/sign-up (GitHub se)

2. **New App** → GitHub repo connect: **The-Evolution-Of-Todo-App**

3. **Root directory:** `backend`

4. **Environment Variables** add karein (same as above)

5. Deploy karein

---

## After Deploy (Dono platforms ke liye)

1. **Vercel** → phase5-todo-app → **Settings** → **Environment Variables**
2. Add: **API_URL** = apna backend URL (Koyeb/Cyclic se)
3. **Redeploy** karein
4. Test: https://phase5-todo-app.vercel.app — Login try karein
