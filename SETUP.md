# Heckathon-3 — Setup Guide

## One-Time Setup

### 1. Backend `.env` (required)

Create `backend/.env` or root `.env`:

```
DATABASE_URL=sqlite:///./todo.db
SECRET_KEY=your-secret-key-at-least-32-characters-long
MOCK_MODE=true
```

### 2. Frontend `.env.local` (already created)

`frontend/.env.local` should have:

```
NEXT_PUBLIC_API_BASE_URL=
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

**Important:** `NEXT_PUBLIC_API_BASE_URL` must be **empty**. This makes the frontend use the Next.js proxy, so:
- No CORS errors
- Works on any port (3000, 3001)
- Backend and frontend connect reliably

---

## Run Locally

### Terminal 1 — Backend

```powershell
cd F:\heckathon-3\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 — Frontend

```powershell
cd F:\heckathon-3\frontend
npm run dev
```

### Open

http://localhost:3000 (or 3001 if Next.js uses that port)

---

## Run with Docker

```powershell
cd F:\heckathon-3
docker-compose up -d --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Redpanda Console: http://localhost:8080

---

## How It Works

| Mode | API calls | CORS? |
|------|-----------|-------|
| Proxy (NEXT_PUBLIC_API_BASE_URL empty) | Browser → localhost:3000/api/* → Next.js → backend:8000 | No |
| Direct (NEXT_PUBLIC_API_BASE_URL=http://localhost:8000) | Browser → localhost:8000/api/* | Yes (must be configured) |

**Recommended:** Use proxy mode (empty `NEXT_PUBLIC_API_BASE_URL`).
