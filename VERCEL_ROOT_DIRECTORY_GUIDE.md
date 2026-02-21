# Vercel Root Directory - Where to Find It

## Exact Path (Step by Step)

1. Open **https://vercel.com/dashboard**
2. Click your project: **phase5-todo-app**
3. Click **Settings** (top menu)
4. In the left sidebar, look for one of these:
   - **General** → scroll down to **Build and Development Settings**
   - **Build and Deployment** (direct link)
5. Find **Root Directory** — it has an **Edit** button next to it
6. Click **Edit** → type `frontend` → **Save**

---

## If You Don't See "Build and Deployment"

Try this path:

- **Settings** → **General** → scroll down
- Look for: **Root Directory** or **Build and Development Settings**
- Sometimes it appears under **Framework Preset** section

---

## Alternative: Set Root Directory During Import

If the project has no deployments yet, you can **re-import**:

1. **Add New** → **Project**
2. Import **The-Evolution-Of-Todo-App-phase-V** from GitHub
3. **Before** clicking Deploy, click **Edit** next to **Root Directory**
4. Select or type: `frontend`
5. Then Deploy

---

## Alternative: Deploy via CLI (No Root Directory Needed)

When you deploy from the `frontend` folder via CLI, Root Directory is not used:

```powershell
cd f:\heckathon-3\frontend
npx vercel --prod
```

This deploys the frontend directly. Root Directory only matters for **GitHub-connected** deployments.
