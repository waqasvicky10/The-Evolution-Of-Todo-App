"""
Mock LLM Provider for Phase III

This provider implements keyword-based mock logic without external APIs.
Extracted from the original TodoAgent implementation.
"""

import logging
import re
from typing import List, Dict, Any, Optional

from .base import LLMProvider

logger = logging.getLogger(__name__)


def _add_task_input(user_id: int, raw: str) -> tuple:
    """Parse add-task input: extract title and priority (e.g. 'urgent task call mom' -> title='call mom', priority='urgent')."""
    raw = raw.strip()
    if not raw:
        return ("What would you like to add?", [])
    priority = None
    title = raw
    # Strip leading priority words
    for p in ("urgent", "high", "medium", "low"):
        pat = re.compile(rf"^{p}\s+(?:priority\s+)?(?:task\s+)?(?:to\s+)?", re.IGNORECASE)
        if pat.match(raw):
            priority = p
            title = pat.sub("", raw).strip()
            break
        # "urgent task call mom" -> strip "urgent task " or "urgent task to "
        pat2 = re.compile(rf"^{p}\s+task\s+(?:to\s+)?", re.IGNORECASE)
        if pat2.match(raw):
            priority = p
            title = pat2.sub("", raw).strip()
            break
    if not title or not title.replace(" ", ""):
        return ("What would you like to add? (e.g. 'call mom', 'buy groceries')", [])
    inp = {"user_id": user_id, "title": title.capitalize()}
    if priority:
        inp["priority"] = priority
    return (f"Sure! I'll add '{title.capitalize()}' to your list." + (f" (Priority: {priority})" if priority else ""), [{"name": "create_todo", "input": inp}])


class MockProvider(LLMProvider):
    """
    Mock LLM provider using keyword-based intent recognition.
    
    This is the fallback provider when no API key is available.
    It now supports:
    1. Keyword-based intent recognition
    2. Context awareness (referencing previous tasks)
    3. Confirmation flows (for delete)
    4. Urdu language support
    """
    
    def __init__(self):
        """Initialize the Mock Provider."""
        logger.info("MockProvider initialized (No External APIs)")
    
    def is_urdu(self, text: str) -> bool:
        """Simple check if the text contains Urdu/Arabic characters."""
        return any('\u0600' <= char <= '\u06FF' for char in text)
    
    def normalize_urdu(self, text: str) -> str:
        """Normalize Urdu text: trim and remove punctuation."""
        normalized = re.sub(r'[۔؟!،]', ' ', text)
        return normalized.strip()

    def _get_context_from_history(self, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Extract context from conversation history.
        Finds the last mentioned Task ID or details.
        """
        context = {"last_id": None, "pending_action": None, "pending_id": None}
        
        if not history:
            return context
            
        # Scan backwards
        for i in range(len(history) - 1, -1, -1):
            msg = history[i]
            content = msg.get("content", "").lower()
            role = msg.get("role")
            
            # Check for pending confirmations
            if role == "assistant":
                # Check for delete confirmation question
                confirmation_match = re.search(r"(?:sure|confirm).*delete.*task\s+(\d+)", content)
                if confirmation_match:
                    context["pending_action"] = "delete"
                    context["pending_id"] = int(confirmation_match.group(1))
                    if not context["last_id"]:
                        context["last_id"] = context["pending_id"]
                    break # Found the most recent pending action
            
            # Extract ID if mentioning a known task pattern
            id_match = re.search(r"(?:task|id|item)(?:\s*[:#])?\s+(\d+)", content)
            if id_match and not context["last_id"]:
                context["last_id"] = int(id_match.group(1))
                
        return context
    
    def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        user_id: int,
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a user message using keyword matching with context."""
        is_urdu_msg = self.is_urdu(user_message)
        msg = self.normalize_urdu(user_message.lower()) if is_urdu_msg else user_message.lower().strip()
        logger.info(f"Mock processing message: {msg} (Urdu: {is_urdu_msg})")
        
        # Get context
        context = self._get_context_from_history(conversation_history or [])
        last_id = context.get("last_id")
        
        tool_calls = []
        response_text = ""
        matched = False
        
        # Ordinal Mapping for Urdu
        urdu_ordinals = {
            "پہلا": 1, "پہلے": 1,
            "دوسرا": 2, "دوسرے": 2,
            "تیسرا": 3, "تیسرے": 3,
            "چوتھا": 4, "چوتھے": 4,
            "پانچواں": 5, "پانچویں": 5
        }
        
        # 1. Handle Confirmation Flows (Priority)
        if context.get("pending_action") == "delete" and context.get("pending_id"):
            pending_id = context["pending_id"]
            
            # Check for Yes/No with word boundaries to avoid false positives
            yes_pattern = r"\b(?:yes|sure|confirm|ok|yeah|do it|y)\b|(?:\bجی\b|\bہاں\b|\bبلکل\b)"
            no_pattern = r"\b(?:no|cancel|stop|don't|wait)\b|(?:\bنہیں\b|\bمت\b|\bرک\b)"
            
            if re.search(yes_pattern, msg):
                resp_text = f"میں ٹاسک {pending_id} کو حذف کر رہا ہوں۔" if is_urdu_msg else f"I'm deleting task {pending_id} for you."
                return {
                    "response_text": resp_text,
                    "tool_calls": [{
                        "name": "delete_todo", 
                        "input": {"user_id": user_id, "todo_id": pending_id},
                        "tool_use_id": f"mock_delete_confirm_{user_id}_{pending_id}"
                    }],
                    "requires_tool_execution": True,
                    "stop_reason": "end_turn",
                    "language": "ur" if is_urdu_msg else "en"
                }
            elif re.search(no_pattern, msg):
                resp_text = "حذف کرنے کا عمل منسوخ کر دیا گیا ہے۔" if is_urdu_msg else "Deletion cancelled."
                return {
                    "response_text": resp_text,
                    "tool_calls": [],
                    "requires_tool_execution": False,
                    "stop_reason": "end_turn",
                    "language": "ur" if is_urdu_msg else "en"
                }
        
        # 1b. Phase V intents (search, overdue, priority, tags)
        phase_v = self._process_phase_v_intents(msg, user_id, is_urdu_msg)
        if phase_v:
            return phase_v

        # 2. Define Rules
        if is_urdu_msg:
            rules = [
                ("list", r"(فہرست|لسٹ|دکھا|دیکھ|بتا|کیا ہے|کیا ہیں|میرے کام|ٹاسک|لسٹ)", 
                 lambda m, ctx: ("آپ کی ٹو ڈو فہرست حاصل کی جا رہی ہے...", [])),
                ("add", r"(?:^|\s)(.+)\s+(?:شامل کریں|شامل کرو|لکھیں|ایڈ کریں|ڈالیں|ڈالو|اضافہ کریں|اضافہ کرو|کریں|بنائیں)(?:\s+(.+))?", 
                 lambda m, ctx: (f"جی بالکل! میں '{m.group(1).strip() + (' ' + m.group(2).strip() if m.group(2) else '')}' کو آپ کی فہرست میں شامل کر رہا ہوں۔", 
                            [{"name": "create_todo", "input": {"user_id": user_id, "title": m.group(1).strip() + (" " + m.group(2).strip() if m.group(2) else "")}}])),
                            
                # Context-aware updates/deletes in Urdu 
                # (Simplified for Hackathon - assumes explicit IDs mostly, but could support 'it' if Urdu grammar supported here)
                
                ("complete", r"(ٹاسک|کام|نمبر)?\s*(\d+|پہلا|دوسرا|تیسرا|چوتھا|پانچواں)\s*(ٹاسک|کام|نمبر)?\s*(مکمل|ختم|ہو گیا|ڈن|کریں|کردیں|کرو)", 
                 lambda m, ctx: (f"ٹاسک {m.group(2)} کو مکمل نشان زد کیا جا رہا ہے۔", 
                            [{"name": "update_todo", "input": {"user_id": user_id, "todo_id": urdu_ordinals.get(m.group(2), int(m.group(2)) if m.group(2).isdigit() else 1), "completed": True}}])),
                            
                ("delete_request", r"(ٹاسک|کام|نمبر)?\s*(\d+|پہلا|دوسرا|تیسرا|چوتھا|پانچواں)\s*(ٹاسک|کام|نمبر)?\s*(حذف|نکال|مٹائیں|ختم کریں|کرو|کریں|ڈیلیٹ)", 
                 lambda m, ctx: (f"کیا آپ واقعی ٹاسک {m.group(2)} کو حذف کرنا چاہتے ہیں؟ (Are you sure you want to delete task {m.group(2)}?)", [])), 
                 # Note: Returns text asking for confirmation, NOT tool call.
                 
                ("update", r"(ٹاسک|کام|نمبر)?\s*(\d+|پہلا|دوسرا|تیسرا|چوتھا|پانچواں)\s*(ٹاسک|کام|نمبر)?\s*(کا نام بدل کر|کو بدل کر|کو|بدلو|اپڈیٹ کرو|اپڈیٹ)\s*['\"]?(.*?)['\"]?\s*(کر دیں|تبدیل کریں|بنا دیں|کرو|کریں)", 
                 lambda m, ctx: (f"ٹاسک {m.group(2)} کو '{m.group(5).strip()}' میں تبدیل کیا جا رہا ہے۔", 
                            [{"name": "update_todo", "input": {"user_id": user_id, "todo_id": urdu_ordinals.get(m.group(2), int(m.group(2)) if m.group(2).isdigit() else 1), "title": m.group(5).strip()}}])),
            ]
        else:
            # English Rules
            rules = [
                # Status-specific lists (must come before general list pattern)
                ("list_pending", r"(?:what's|what is|show|list|get).*(pending|incomplete|unfinished|not done|to.?do|left)", 
                 lambda m, ctx: ("Fetching your pending tasks...", [])),
                 
                ("list_completed", r"(?:what|show|list|get).*(completed|finished|done|complete)", 
                 lambda m, ctx: ("Fetching your completed tasks...", [])),
                
                # General list (catch-all) — "show my tasks", "show tasks", "my tasks", "list tasks"
                ("list", r"(show|list|get|fetch|what are|display|my)\s*(my\s+)?(tasks?|todos?|list|items)", 
                 lambda m, ctx: ("Fetching your todo list...", [])),
                 
                ("add", r"(?:add|create|new task|remember to|remind me to)\s+(?:a task to|a task|to|task|that)?\s*(.+)", 
                 lambda m, ctx: _add_task_input(user_id, m.group(1).strip())),

                # Implicit "Task [description]" for voice/shorthand (e.g. "a task by groceries")
                ("add_implicit", r"(?:^|\s)(?:a\s+)?task\s+(?!id\b|number\b|\d)(?:to\s+|about\s+|by\s+|for\s+)?(.+)", 
                 lambda m, ctx: (f"Sure! I'll add '{m.group(1).strip().capitalize()}' to your list.", 
                            [{"name": "create_todo", "input": {"user_id": user_id, "title": m.group(1).strip().capitalize()}}])),
                
                # Context-aware reference ("it", "that", "this")
                ("complete_context", r"(?:complete|finish|mark|check off)\s+(?:it|that|this|the task)$",
                 lambda m, ctx: (f"Marking task {ctx} as complete.", 
                            [{"name": "update_todo", "input": {"user_id": user_id, "todo_id": ctx, "completed": True}}]) if ctx else ("Which task would you like to complete?", [])),
                            
                ("delete_context", r"(?:delete|remove|erase)\s+(?:it|that|this|the task)$",
                 lambda m, ctx: (f"Are you sure you want to delete task {ctx}? This cannot be undone.", []) if ctx else ("Which task would you like to delete?", [])),

                # Explicit ID commands (merged and simplified regexes)
                ("complete", r"(?:complete|mark|finish)\s+(?:task|id)?\s*(\d+)", 
                 lambda m, ctx: (f"Marking task {m.group(1)} as complete.", 
                            [{"name": "update_todo", "input": {"user_id": user_id, "todo_id": int(m.group(1)), "completed": True}}])),
                            
                ("delete_request", r"(?:delete|remove)\s+(?:task|id)?\s*(\d+)", 
                 lambda m, ctx: (f"Are you sure you want to delete task {m.group(1)}? This cannot be undone.", [])),
                 
                ("update", r"(?:update|change|rename)\s+(?:task|id)?\s*(\d+)\s+(?:to|with)\s+['\"]?(.*?)['\"]?$", 
                 lambda m, ctx: (f"Updating task {m.group(1)} to '{m.group(2).strip()}'." , 
                            [{"name": "update_todo", "input": {"user_id": user_id, "todo_id": int(m.group(1)), "title": m.group(2).strip()}}])),
            ]
        
        # Apply Rules
        for intent, pattern, generator in rules:
            match = re.search(pattern, msg, re.IGNORECASE) if not is_urdu_msg else re.search(pattern, user_message)
            if match:
                # Pass context (last_id) to the generator if needed
                res_text, calls = generator(match, last_id)
                
                response_text = res_text
                tool_calls = calls
                
                if intent == "list":
                    tool_calls = [{
                        "tool_use_id": "mock_list_" + str(user_id),
                        "name": "list_todos",
                        "input": {"user_id": user_id}
                    }]
                elif intent == "list_pending":
                    tool_calls = [{
                        "tool_use_id": "mock_list_pending_" + str(user_id),
                        "name": "list_todos",
                        "input": {"user_id": user_id, "completed": False}
                    }]
                elif intent == "list_completed":
                    tool_calls = [{
                        "tool_use_id": "mock_list_completed_" + str(user_id),
                        "name": "list_todos",
                        "input": {"user_id": user_id, "completed": True}
                    }]
                elif tool_calls:
                    for i, call in enumerate(tool_calls):
                        call["tool_use_id"] = f"mock_{intent}_{i}_{user_id}"
                matched = True
                break
        
        if not matched:
            if is_urdu_msg:
                response_text = "معذرت، میں سمجھ نہیں سکا۔ میں کام شامل کرنے، فہرست دیکھنے، اپ ڈیٹ کرنے یا حذف کرنے میں آپ کی مدد کر سکتا ہوں۔"
            else:
                response_text = "I'm sorry, I didn't quite catch that. I can help you add, list, update, or delete tasks."
        
        return {
            "response_text": response_text,
            "tool_calls": tool_calls,
            "requires_tool_execution": len(tool_calls) > 0,
            "stop_reason": "end_turn",
            "language": "ur" if is_urdu_msg else "en"
        }
    
    def _process_phase_v_intents(self, msg: str, user_id: int, is_urdu: bool) -> Optional[Dict[str, Any]]:
        """Phase V intent patterns: search, overdue, priority, tags, due date, recurring."""
        lang = "ur" if is_urdu else "en"

        # Overdue
        if re.search(r"overdue|late|missed|past due|مدت ختم|دیر", msg, re.IGNORECASE):
            return {
                "response_text": "آپ کی مدت ختم شدہ ٹاسکس حاصل کی جا رہی ہیں..." if is_urdu else "Fetching your overdue tasks...",
                "tool_calls": [{"tool_use_id": f"mock_overdue_{user_id}", "name": "get_overdue_todos", "input": {"user_id": user_id}}],
                "requires_tool_execution": True, "stop_reason": "end_turn", "language": lang,
            }

        # Priority set — "set task 5 priority to high"
        prio_match = re.search(r"(?:set|change|make)\s+(?:task|id)?\s*(\d+)\s+(?:priority|prio)\s+(?:to\s+)?(urgent|high|medium|low)", msg, re.IGNORECASE)
        if prio_match:
            tid, prio = int(prio_match.group(1)), prio_match.group(2).lower()
            return {
                "response_text": f"Setting task {tid} priority to {prio}.",
                "tool_calls": [{"tool_use_id": f"mock_prio_{user_id}", "name": "update_todo", "input": {"user_id": user_id, "todo_id": tid, "priority": prio}}],
                "requires_tool_execution": True, "stop_reason": "end_turn", "language": lang,
            }

        # Recurring set — "make task 3 repeat weekly" / "set task 2 recurring daily"
        recur_match = re.search(r"(?:make|set)\s+(?:task|id)?\s*(\d+)\s+(?:repeat|recurring|recur)\s+(?:to\s+)?(daily|weekly|monthly)", msg, re.IGNORECASE)
        if recur_match:
            tid, pattern = int(recur_match.group(1)), recur_match.group(2).lower()
            return {
                "response_text": f"Setting task {tid} to repeat {pattern}.",
                "tool_calls": [{"tool_use_id": f"mock_recur_{user_id}", "name": "update_todo", "input": {"user_id": user_id, "todo_id": tid, "recurring_pattern": pattern}}],
                "requires_tool_execution": True, "stop_reason": "end_turn", "language": lang,
            }

        # Tag add — "tag task 5 with work meeting" / "add tags #work #meeting to task 5"
        tag_match = re.search(r"(?:tag|add tags?)\s+(?:task|id)?\s*(\d+)\s+(?:with|as|:)?\s*(.+)", msg, re.IGNORECASE)
        if tag_match:
            tid = int(tag_match.group(1))
            raw_tags = re.findall(r"#?(\w+)", tag_match.group(2))
            if raw_tags:
                return {
                    "response_text": f"Adding tags {raw_tags} to task {tid}.",
                    "tool_calls": [{"tool_use_id": f"mock_tag_{user_id}", "name": "update_todo", "input": {"user_id": user_id, "todo_id": tid, "tags": raw_tags}}],
                    "requires_tool_execution": True, "stop_reason": "end_turn", "language": lang,
                }

        # Skip search if user is ADDING a task (add/create/remind at start)
        if re.search(r"^(add|create|new task|remember to|remind me to)\s+", msg, re.IGNORECASE):
            return None

        # Due today / due this week — shortcut searches
        if re.search(r"\bdue\s+today\b", msg, re.IGNORECASE):
            return {
                "response_text": "Fetching tasks due today...",
                "tool_calls": [{"tool_use_id": f"mock_due_today_{user_id}", "name": "search_todos", "input": {"user_id": user_id, "sort_by": "due_date", "sort_order": "asc"}}],
                "requires_tool_execution": True, "stop_reason": "end_turn", "language": lang,
            }

        # Search / Find tasks — "Search tasks" (no keyword) or "Find tasks tagged #" (no tag) -> list all
        if re.search(r"^search\s*tasks?\s*$", msg, re.IGNORECASE) or re.search(r"^find\s+tasks?\s+tagged\s*#?\s*$", msg, re.IGNORECASE) or re.search(r"^search\s*$", msg, re.IGNORECASE):
            return {
                "response_text": "Fetching your todo list...",
                "tool_calls": [{"tool_use_id": f"mock_list_{user_id}", "name": "list_todos", "input": {"user_id": user_id}}],
                "requires_tool_execution": True, "stop_reason": "end_turn", "language": lang,
            }

        # Advanced search — only when user explicitly searches (not when adding)
        has_search_keyword = re.search(r"\b(search|find|filter)\b", msg, re.IGNORECASE)
        has_qualifier = re.search(r"\b(tagged|tag|#\w+|urgent|high|low|medium|priority|sort|due|before|after|about|containing)\b", msg, re.IGNORECASE)

        if has_search_keyword or has_qualifier:
            from ..task_parser import parse_search_query
            filters = parse_search_query(msg)
            has_real_filter = any(filters.get(k) for k in ("keyword", "priority", "tag", "sort_by"))
            if has_real_filter:
                tool_input: Dict[str, Any] = {"user_id": user_id}
                if filters.get("keyword"):
                    tool_input["q"] = filters["keyword"]
                if filters.get("priority"):
                    tool_input["priority"] = filters["priority"]
                if filters.get("tag"):
                    tool_input["tag"] = filters["tag"]
                if filters.get("sort_by"):
                    tool_input["sort_by"] = filters["sort_by"]

                return {
                    "response_text": "تلاش کی جا رہی ہے..." if is_urdu else "Searching your tasks...",
                    "tool_calls": [{"tool_use_id": f"mock_search_{user_id}", "name": "search_todos", "input": tool_input}],
                    "requires_tool_execution": True, "stop_reason": "end_turn", "language": lang,
                }

        return None

    def get_model_info(self) -> Dict[str, Any]:
        """Get mock provider info."""
        return {
            "model": "local-mock-v2-phase-v",
            "provider": "local",
            "capabilities": ["english", "urdu", "voice-ready", "context-aware",
                             "search", "priority", "tags", "due-dates", "recurring", "overdue"]
        }
