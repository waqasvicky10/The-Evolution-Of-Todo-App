# Chat Testing Guide — Project Submission

Use this guide to verify all chat buttons and voice commands work before submitting your project.

---

## Prerequisites

1. **Log in first** — Chat requires authentication. If you get 401 errors, log in again.
2. **Start the app:**
   ```powershell
   # Terminal 1 — Backend
   cd F:\heckathon-3\backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Terminal 2 — Frontend
   cd F:\heckathon-3\frontend
   npm run dev
   ```
3. Open **http://localhost:3000** in Chrome.
4. Register or log in, then go to **AI Chat** (or **/chat**).

---

## Button Commands (Click to Test)

| Button       | What it does                    | Expected result                          |
|-------------|----------------------------------|------------------------------------------|
| **My Tasks**| Lists all your tasks             | Shows task list or "You have no tasks"   |
| **Add Urgent** | Adds an urgent task           | Puts "Add urgent task " in box — type description (e.g. "call mom") and press Enter |
| **Overdue** | Shows overdue tasks              | Shows overdue tasks or "You have no overdue tasks" |
| **Search**  | Lists all tasks (search mode)    | Same as My Tasks                         |
| **Due Today** | Shows tasks due today         | Shows tasks sorted by due date           |
| **#tagged** | Search by tag                    | Puts "Find tasks tagged #" in box — type tag (e.g. "work") and press Enter |

---

## How to Use Each Button

### 1. My Tasks
- **Click** the button → message is sent immediately.
- **Expected:** List of your tasks or "You have no tasks."

### 2. Add Urgent
- **Click** the button → "Add urgent task " appears in the input.
- **Type** a description (e.g. `call mom`) and press **Enter**.
- **Expected:** "Task added: call mom (ID: X)" with priority urgent.

### 3. Overdue
- **Click** the button → message is sent immediately.
- **Expected:** List of overdue tasks or "You have no overdue tasks."

### 4. Search
- **Option A:** Click and send immediately → lists all tasks.
- **Option B:** Type a keyword after (e.g. `Search tasks work`) → filters by keyword.

### 5. Due Today
- **Click** the button → message is sent immediately.
- **Expected:** Tasks sorted by due date (or empty if none).

### 6. #tagged
- **Click** the button → "Find tasks tagged #" appears in the input.
- **Type** a tag (e.g. `work`) and press **Enter**.
- **Expected:** Tasks with that tag, or "You have no tasks."

---

## Voice Commands (How to Speak)

Use the **microphone** button, then say one of these phrases clearly:

| Say this                    | Action                          |
|----------------------------|----------------------------------|
| "Show my tasks"            | Lists all tasks                 |
| "Add urgent task call mom" | Adds urgent task "call mom"     |
| "Add task buy groceries"   | Adds task "buy groceries"       |
| "Show overdue tasks"       | Lists overdue tasks             |
| "Search tasks"             | Lists all tasks                 |
| "Show tasks due today"     | Lists tasks due today           |
| "Find tasks tagged work"   | Searches tasks with tag "work"  |
| "Complete task 1"          | Marks task 1 as done            |
| "Delete task 2"            | Asks for confirmation, then deletes |

**Voice tips:**
- Use **Chrome** (best support).
- Speak clearly and at a moderate pace.
- Reduce background noise.
- Use **HTTPS** or **localhost** (required for microphone).

---

## Typed Commands (Type in Chat)

You can also type these in the chat box:

| Type this                  | Action                          |
|---------------------------|----------------------------------|
| Show my tasks             | Lists all tasks                 |
| Add task buy milk         | Adds task "buy milk"            |
| Add urgent task deploy    | Adds urgent task "deploy"        |
| Show overdue tasks        | Lists overdue tasks             |
| Search tasks              | Lists all tasks                 |
| Show tasks due today      | Lists tasks due today           |
| Find tasks tagged #work    | Searches by tag "work"          |
| Complete task 1            | Marks task 1 complete           |
| Delete task 1              | Deletes task 1 (with confirm)   |

---

## Quick Verification Checklist

Before submitting, run through this list:

- [ ] Logged in successfully
- [ ] **My Tasks** — shows list
- [ ] **Add Urgent** — add "test task", then check list
- [ ] **Overdue** — shows overdue or empty
- [ ] **Search** — shows list
- [ ] **Due Today** — shows list (or empty)
- [ ] **#tagged** — add tag, search works
- [ ] **Voice** — at least one command works (e.g. "Show my tasks")
- [ ] No 401 errors (if yes, log in again)

---

## If You Get Errors

| Error                    | Fix                                      |
|--------------------------|------------------------------------------|
| 401 Unauthorized         | Log in again; session may have expired  |
| "Unknown tool"           | Restart backend; ensure latest code     |
| Voice not working        | Use Chrome, allow microphone, use HTTPS |
| Empty response           | Check backend is running on port 8000    |

---

## Run Commands Summary

```powershell
# Backend
cd F:\heckathon-3\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (new terminal)
cd F:\heckathon-3\frontend
npm run dev
```

Then open **http://localhost:3000**, log in, and go to **AI Chat**.
