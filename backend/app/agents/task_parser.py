"""
Task parsing utilities for natural language processing.

This module provides simple parsing logic to extract task title and description
from natural language requests like "Add a task to buy groceries tomorrow".
"""

import re
from typing import Dict, Tuple, Optional, Any

def parse_task_input(text: str) -> Dict[str, Optional[str]]:
    """
    Parse natural language text to extract task title and description.
    
    Args:
        text: The user's natural language request
        
    Returns:
        Dictionary with 'title' and 'description'
        
    Example:
        >>> parse_task_input("Add a task to buy groceries tomorrow")
        {'title': 'buy groceries', 'description': 'tomorrow'}
    """
    # Common prefixes to remove
    prefixes = [
        r"^add a task to\s+",
        r"^add task to\s+",
        r"^add a todo to\s+",
        r"^add todo to\s+",
        r"^add\s+",
        r"^remind me to\s+",
        r"^create a task to\s+",
        r"^create task for\s+",
    ]
    
    clean_text = text.lower().strip()
    for prefix in prefixes:
        clean_text = re.sub(prefix, "", clean_text, flags=re.IGNORECASE)
    
    # Split into title and description based on common separators
    # "buy groceries tomorrow" -> title: buy groceries, desc: tomorrow
    # "call mom at 5pm" -> title: call mom, desc: at 5pm
    
    separators = [
        r"\s+tomorrow",
        r"\s+today",
        r"\s+at\s+\d+",
        r"\s+on\s+",
        r"\s+next\s+",
        r"\s+by\s+",
        r"\s+in\s+",
    ]
    
    title = clean_text
    description = ""
    
    for sep in separators:
        match = re.search(sep, clean_text, flags=re.IGNORECASE)
        if match:
            split_idx = match.start()
            title = clean_text[:split_idx].strip()
            description = clean_text[split_idx:].strip()
            break
            
    # Fallback: if no title found (all text was prefix), use the whole text
    if not title and text:
        title = text.strip()
        
    return {
        "title": title,
        "description": description if description else None
    }

def parse_list_status(text: str) -> str:
    """
    Parse natural language text to extract list status filter.
    
    Args:
        text: The user's natural language request
        
    Returns:
        Status string: "all", "pending", or "completed"
        
    Example:
        >>> parse_list_status("show my pending tasks")
        'pending'
    """
    clean_text = text.lower().strip()
    
    if "completed" in clean_text or "done" in clean_text or "finished" in clean_text:
        return "completed"
    elif "pending" in clean_text or "incomplete" in clean_text:
        return "pending"
    else:
        return "all"

def extract_task_id(text: str) -> Optional[int]:
    """
    Extract a numeric task ID from natural language text.
    
    Args:
        text: The user's request (e.g., "mark task 5 as done")
        
    Returns:
        The extracted ID as an integer, or None if not found
        
    Example:
        >>> extract_task_id("complete task 123")
        123
    """
    # Look for patterns like "task 5", "item 10", "#15", or just a standalone number
    patterns = [
        r"(?:task|item|id|#)\s*(\d+)",
        r"(?:^|\s)(\d+)(?:\s|$)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
            
    return None

def extract_search_term(text: str) -> Optional[str]:
    """
    Extract a task name or search term from natural language text.
    
    Args:
        text: The user's request (e.g., "delete the meeting task")
        
    Returns:
        The extracted search term, or None if not found
        
    Example:
        >>> extract_search_term("remove the groceries todo")
        'groceries'
    """
    # Common deletion prefixes and suffixes to remove
    # Order patterns from most specific to least specific
    removal_patterns = [
        r"^delete the\s+",
        r"^remove the\s+",
        r"^delete my\s+",
        r"^remove my\s+",
        r"^cancel the\s+",
        r"^delete\s+",
        r"^remove\s+",
        r"^cancel\s+",
        r"\s+task$",
        r"\s+todo$",
        r"\s+item$"
    ]
    
    clean_text = text.lower().strip()
    
    # Don't extract if it contains what looks like an ID (handled by extract_task_id)
    if re.search(r"(?:task|item|id|#)\s*\d+|\b\d+\b", clean_text, re.IGNORECASE):
        return None
        
    for pattern in removal_patterns:
        clean_text = re.sub(pattern, "", clean_text, flags=re.IGNORECASE)
    
    return clean_text.strip() if clean_text.strip() else None

def parse_update_input(text: str) -> Dict[str, Any]:
    """
    Parse natural language text to extract task ID and new content for updates.
    
    Args:
        text: The user's request (e.g., "Change task 2 to Buy milk and eggs")
        
    Returns:
        Dictionary with 'task_id' and 'new_content'
        
    Example:
        >>> parse_update_input("Change task 2 to Buy milk")
        {'task_id': 2, 'new_content': 'Buy milk'}
    """
    # Pattern to match "Change task <ID> to <Content>" or "Update item <ID>: <Content>"
    patterns = [
        r"(?:change|update|edit)\s+(?:task|item|id|#)?\s*(\d+)\s*(?:to|with|:)\s*(.+)",
        r"(?:change|update|edit)\s+(?:task|item|id|#)?\s*(\d+)\s+(.+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {
                "task_id": int(match.group(1)),
                "new_content": match.group(2).strip()
            }
            
    # Fallback to just ID extraction if possible
    task_id = extract_task_id(text)
    return {
        "task_id": task_id,
        "new_content": None
    }

def parse_search_query(text: str) -> Dict[str, Any]:
    """
    Parse natural language text to extract search filters — Phase V.

    Supports: keyword, priority (low/medium/high/urgent), category,
    tag, due-date hints, and sort preference.
    """
    clean_text = text.lower().strip()

    # Priority
    priority = None
    if "urgent" in clean_text:
        priority = "urgent"
    elif "high priority" in clean_text or "high" in clean_text:
        priority = "high"
    elif "low priority" in clean_text or "low" in clean_text:
        priority = "low"
    elif "medium priority" in clean_text:
        priority = "medium"

    # Category
    categories = ["work", "personal", "shopping", "health", "finance", "study", "learning"]
    category = None
    for cat in categories:
        if cat in clean_text:
            category = cat
            break

    # Tag extraction — "tagged X" or "tag X" or "#X"
    tag = None
    tag_match = re.search(r"(?:tagged?|#)\s*(\w+)", clean_text)
    if tag_match:
        tag = tag_match.group(1)

    # Sort preference
    sort_by = None
    if "by due" in clean_text or "by deadline" in clean_text:
        sort_by = "due_date"
    elif "by priority" in clean_text:
        sort_by = "priority"
    elif "newest" in clean_text or "recent" in clean_text:
        sort_by = "created_at"

    # Keyword — strip common prefixes
    search_prefixes = [
        r"^show me tasks containing\s+",
        r"^search for tasks with\s+",
        r"^search for\s+",
        r"^find tasks? (?:about|with|for)\s+",
        r"^list my tasks about\s+",
        r"^show me my\s+",
        r"^show my\s+",
        r"^list my\s+",
        r"^show\s+",
        r"^list\s+",
        r"^find\s+",
    ]
    keyword = clean_text
    for prefix in search_prefixes:
        keyword = re.sub(prefix, "", keyword, flags=re.IGNORECASE)

    noise = ["tasks", "task", "items", "item", "todo", "todos",
             "high", "low", "medium", "urgent", "priority",
             "tagged", "tag", "#", "by due", "by deadline", "by priority",
             "newest", "recent"]
    for n in noise:
        keyword = keyword.replace(n, "")
    keyword = keyword.strip()

    if keyword == priority or keyword == category or keyword == tag:
        keyword = None

    return {
        "priority": priority,
        "category": category,
        "tag": tag,
        "sort_by": sort_by,
        "keyword": keyword if keyword else None,
    }


# ---------------------------------------------------------------------------
# Phase V — Advanced field extraction
# ---------------------------------------------------------------------------

_PRIORITY_MAP = {
    "urgent": "urgent", "asap": "urgent", "critical": "urgent", "فوری": "urgent",
    "high": "high", "important": "high", "اعلی": "high", "اہم": "high",
    "medium": "medium", "normal": "medium", "درمیانی": "medium",
    "low": "low", "trivial": "low", "کم": "low",
}

_RECURRING_MAP = {
    "daily": "daily", "every day": "daily", "روزانہ": "daily",
    "weekly": "weekly", "every week": "weekly", "ہفتہ وار": "weekly",
    "monthly": "monthly", "every month": "monthly", "ماہانہ": "monthly",
}


def extract_priority(text: str) -> Optional[str]:
    """Extract priority from natural language text."""
    lower = text.lower()
    for kw, val in _PRIORITY_MAP.items():
        if kw in lower:
            return val
    return None


def extract_tags(text: str) -> list:
    """Extract hashtag-style tags from text (e.g. '#work #urgent')."""
    return re.findall(r"#(\w+)", text)


def extract_due_date_hint(text: str) -> Optional[str]:
    """
    Extract a due-date hint from text.
    Returns a human-readable string like 'tomorrow', 'next monday', or an ISO date.
    """
    lower = text.lower()
    patterns = [
        (r"(?:due|by|before|deadline)\s+(tomorrow)", "tomorrow"),
        (r"(?:due|by|before|deadline)\s+(today)", "today"),
        (r"(?:due|by|before|deadline)\s+(next\s+\w+)", None),
        (r"(\d{4}-\d{2}-\d{2})", None),
    ]
    for pat, default_val in patterns:
        m = re.search(pat, lower)
        if m:
            return default_val or m.group(1)
    return None


def extract_recurring(text: str) -> Optional[str]:
    """Extract recurring pattern from text."""
    lower = text.lower()
    for kw, val in _RECURRING_MAP.items():
        if kw in lower:
            return val
    return None


def parse_advanced_task_input(text: str) -> Dict[str, Any]:
    """
    Phase V: Parse natural language into a full task creation payload.
    Extracts title, priority, tags, due_date hint, and recurring pattern.
    """
    base = parse_task_input(text)
    return {
        **base,
        "priority": extract_priority(text),
        "tags": extract_tags(text),
        "due_date_hint": extract_due_date_hint(text),
        "recurring": extract_recurring(text),
    }
