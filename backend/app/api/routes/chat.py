"""
Chat API routes for Phase III AI Chatbot.

Provides endpoints for conversational todo management with Phase III agent integration.
"""

import sys
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
from app.api.deps import get_db, get_current_user, get_user_context
from app.models.user import User
from app.models.task import Task

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Restore Phase III Agent Integration
from app.agents import create_agent, get_agent_config, get_mcp_tool_definitions

PHASE_III_AVAILABLE = True
PERSISTENCE_AVAILABLE = False


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ChatHistoryResponse(BaseModel):
    """Chat history response model."""
    messages: List[ChatMessage]


# Fallback in-memory storage (only if persistence fails)
_conversation_history: Dict[int, List[Dict[str, str]]] = {}


def get_conversation_history(user_id: int, limit: int = 20) -> List[Dict[str, str]]:
    """Get conversation history for user (Persistent or In-Memory)."""
    if PERSISTENCE_AVAILABLE:
        try:
            messages = repo_get_messages(user_id, limit=limit)
            return [
                {"role": msg.role.value, "content": msg.content}
                for msg in messages
            ]
        except Exception as e:
            print(f"Error reading history from DB: {e}")
            
    # Fallback
    return _conversation_history.get(user_id, [])[-limit:]


def store_message(user_id: int, role: str, content: str):
    """Store a message in conversation history (Persistent or In-Memory)."""
    if PERSISTENCE_AVAILABLE:
        try:
            msg_role = MessageRole(role)
            repo_store_message(user_id, msg_role, content)
            return
        except Exception as e:
            print(f"Error storing message to DB: {e}")

    # Fallback
    if user_id not in _conversation_history:
        _conversation_history[user_id] = []
    _conversation_history[user_id].append({"role": role, "content": content})


async def execute_tool_calls_async(tool_calls: List[Dict[str, Any]], user_id: int, db: Session) -> List[Dict[str, Any]]:
    """Execute MCP tool calls asynchronously using FastAPI database."""
    from app.services.task_service import (
        create_task as service_create_task,
        get_user_tasks as service_get_user_tasks,
        search_tasks as service_search_tasks,
        get_overdue_tasks as service_get_overdue_tasks,
        get_task as service_get_task,
        update_task as service_update_task,
        delete_task as service_delete_task,
        get_task_by_id as service_get_task_by_id,
        toggle_task as service_toggle_task
    )
    from fastapi import HTTPException
    
    results = []
    
    for tool_call in tool_calls:
        tool_name = (tool_call.get("name") or "").strip()
        tool_input = tool_call.get("input", {}) or {}
        
        try:
            if tool_name == "get_user_context":
                # Handle GetUserContext Skill
                # We already have user_id and potentially user_context from dependencies
                from app.models.user import User as DBUser
                db_user = db.exec(select(DBUser).where(DBUser.id == user_id)).first()
                
                results.append({
                    "content": {
                        "success": True,
                        "user_id": user_id,
                        "email": db_user.email if db_user else f"user{user_id}@example.com",
                        "name": db_user.email.split("@")[0].capitalize() if db_user else "User",
                        "message": "User context retrieved successfully."
                    }
                })
                
            elif tool_name == "create_todo":
                # Create task using FastAPI service (supports Phase V: priority, tags, due_date)
                title = tool_input.get("title", "")
                if not title:
                    results.append({
                        "content": {
                            "success": False,
                            "error": "Title is required to create a task"
                        }
                    })
                    continue
                priority = tool_input.get("priority")
                tags = tool_input.get("tags")
                due_date = tool_input.get("due_date")
                if isinstance(due_date, str) and due_date:
                    try:
                        from datetime import datetime
                        due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                    except (ValueError, TypeError):
                        due_date = None
                task = service_create_task(db, user_id, title, priority=priority, tags=tags, due_date=due_date)
                results.append({
                    "content": {
                        "success": True,
                        "todo_id": task.id,
                        "title": task.description,
                        "completed": task.is_complete
                    }
                })
                
            elif tool_name == "add_task":
                # Handle add_task tool (AddTask Skill)
                title = tool_input.get("title", "")
                description = tool_input.get("description", "")
                
                if not title:
                    results.append({
                        "content": {
                            "success": False,
                            "error": "Title is required for add_task"
                        }
                    })
                    continue
                
                # Combine title and description for the storage
                full_desc = title.strip()
                if description and description.strip():
                    full_desc = f"{full_desc} ({description.strip()})"
                
                task = service_create_task(db, user_id, full_desc)
                
                # Special AddTask Skill Response Pattern
                results.append({
                    "content": {
                        "success": True,
                        "todo_id": task.id,
                        "title": title.strip(),
                        "full_description": full_desc,
                        "completed": task.is_complete,
                        "message": f"Task added: {title.strip()} (ID: {task.id})"
                    }
                })
                
            elif tool_name in ["list_tasks", "search_tasks", "search_todos"]:
                # Handle list_tasks and search_tasks tools (ListTasks & SearchTasks Skills)
                status = tool_input.get("status", "all")
                priority = tool_input.get("priority")
                category = tool_input.get("category")
                keyword = tool_input.get("keyword") or tool_input.get("q")
                is_complete = tool_input.get("is_complete")
                tag = tool_input.get("tag")
                sort_by = tool_input.get("sort_by", "created_at")
                sort_order = tool_input.get("sort_order", "desc")

                # Use advanced search when search_todos params (q, tag, sort_by) are present
                use_advanced = bool(keyword or tag or sort_by != "created_at" or sort_order != "desc")
                if tool_name == "search_todos" and use_advanced:
                    tasks = service_search_tasks(
                        db, user_id,
                        q=keyword, priority=priority, tag=tag,
                        is_complete=is_complete,
                        sort_by=sort_by, sort_order=sort_order
                    )
                else:
                    completed_filter = None
                    if status == "pending" or is_complete is False:
                        completed_filter = False
                    elif status == "completed" or is_complete is True:
                        completed_filter = True
                    tasks = service_get_user_tasks(
                        db, user_id,
                        completed=completed_filter,
                        priority=priority,
                        category=category
                    )
                    if keyword:
                        tasks = [t for t in tasks if keyword.lower() in t.description.lower()]
                
                # Beautiful Formatting
                filter_desc = []
                if status != "all": filter_desc.append(status)
                if priority: filter_desc.append(f"{priority} priority")
                if category: filter_desc.append(category)
                if keyword: filter_desc.append(f"containing '{keyword}'")
                
                filter_str = " ".join(filter_desc) if filter_desc else ""
                
                if not tasks:
                    message = f"You have no {filter_str} tasks."
                else:
                    message = f"Here are your {filter_str} tasks:\n"
                    for t in tasks:
                        status_emoji = "✅" if t.is_complete else "⏳"
                        priority_tag = f" [{t.priority}]" if t.priority else ""
                        message += f"{status_emoji} **ID: {t.id}** - {t.description}{priority_tag}\n"
                
                results.append({
                    "content": {
                        "success": True,
                        "status": status,
                        "priority": priority,
                        "category": category,
                        "keyword": keyword,
                        "count": len(tasks),
                        "tasks": [{"id": t.id, "title": t.description, "completed": t.is_complete} for t in tasks],
                        "message": message
                    }
                })
                
            elif tool_name == "complete_task":
                # Handle complete_task tool (CompleteTask Skill)
                todo_id = tool_input.get("todo_id")
                
                if not todo_id:
                    results.append({
                        "content": {
                            "success": False,
                            "error": "todo_id is required for complete_task"
                        }
                    })
                    continue
                
                # Use service function signature: update_task(db, task_id, user_id, description=None, is_complete=None)
                task = service_update_task(db, todo_id, user_id, is_complete=True)
                
                if not task:
                    results.append({
                        "content": {
                            "success": False,
                            "error": f"Task {todo_id} not found or unauthorized"
                        }
                    })
                else:
                    # Special CompleteTask Skill Response Pattern
                    results.append({
                        "content": {
                            "success": True,
                            "todo_id": task.id,
                            "completed": task.is_complete,
                            "message": f"Task {task.id} marked complete ✓"
                        }
                    })
                
            elif tool_name == "update_task":
                # Handle update_task tool (UpdateTask Skill)
                todo_id = tool_input.get("todo_id")
                title = tool_input.get("title", "")
                description = tool_input.get("description", "")
                
                if not todo_id:
                    results.append({
                        "content": {
                            "success": False,
                            "error": "todo_id is required for update_task"
                        }
                    })
                    continue
                
                # Combine title and description for the storage if both are provided
                # or use whichever is available.
                update_desc = None
                if title and description:
                    update_desc = f"{title.strip()} ({description.strip()})"
                elif title:
                    update_desc = title.strip()
                elif description:
                    update_desc = description.strip()
                
                # Use service function signature: update_task(db, task_id, user_id, description=None, is_complete=None)
                task = service_update_task(db, todo_id, user_id, description=update_desc)
                
                if not task:
                    results.append({
                        "content": {
                            "success": False,
                            "error": f"Task {todo_id} not found or unauthorized"
                        }
                    })
                else:
                    results.append({
                        "content": {
                            "success": True,
                            "todo_id": task.id,
                            "updated_title": task.description,
                            "message": f"Task {task.id} updated successfully: {task.description}"
                        }
                    })
                
            elif tool_name == "list_todos":
                # List tasks using FastAPI service
                tasks = service_get_user_tasks(db, user_id)
                completed_filter = tool_input.get("completed")
                
                if completed_filter is not None:
                    tasks = [t for t in tasks if t.is_complete == completed_filter]
                
                # Format tasks for process_tool_results
                todos_list = [
                    {
                        "id": t.id,
                        "title": t.description,
                        "completed": t.is_complete
                    }
                    for t in tasks
                ]
                results.append({
                    "content": {
                        "success": True,
                        "todos": todos_list
                    }
                })
                    
            elif tool_name == "update_todo":
                # Update task using FastAPI service
                todo_id = tool_input.get("todo_id")
                title = tool_input.get("title")
                completed = tool_input.get("completed")
                
                if not todo_id:
                    results.append({
                        "content": "Error: todo_id is required to update a task",
                        "success": False
                    })
                    continue
                
                try:
                    # Get existing task (will raise HTTPException if not found)
                    task = service_get_task_by_id(db, todo_id, user_id)
                    
                    # Update description if provided
                    if title:
                        updated_task = service_update_task(db, todo_id, user_id, description=title)
                    else:
                        updated_task = task
                    
                    # Update completion status if provided
                    if completed is not None:
                        if task.is_complete != completed:
                            # Toggle if needed
                            if completed:
                                updated_task = service_toggle_task(db, todo_id, user_id)
                            else:
                                # If uncompleting, toggle twice
                                if task.is_complete:
                                    updated_task = service_toggle_task(db, todo_id, user_id)
                    results.append({
                        "content": {
                            "success": True,
                            "task_id": updated_task.id,
                            "title": updated_task.description,
                            "completed": updated_task.is_complete
                        }
                    })

                except HTTPException as e:
                    results.append({
                        "content": {
                            "success": False,
                            "error": f"Task with ID {todo_id} not found"
                        }
                    })
                
            elif tool_name in ["delete_todo", "remove_task"]:
                # Handle delete_todo and remove_task (DeleteTask Skill)
                todo_id = tool_input.get("todo_id")
                
                if not todo_id:
                    results.append({
                        "content": {
                            "success": False,
                            "error": "todo_id is required for deletion"
                        }
                    })
                    continue
                
                # Check if task exists and belongs to user
                task = service_get_task(db, todo_id)
                if not task or task.user_id != user_id:
                    results.append({
                        "content": {
                            "success": False,
                            "error": f"Task {todo_id} not found or unauthorized"
                        }
                    })
                else:
                    success = service_delete_task(db, todo_id, user_id)
                    results.append({
                        "content": {
                            "success": success,
                            "todo_id": todo_id,
                            "deleted": success,
                            "message": "Task deleted permanently."
                        }
                    })
                
            elif tool_name == "get_todo":
                # Get task using FastAPI service
                todo_id = tool_input.get("todo_id")
                
                if not todo_id:
                    results.append({
                        "content": {
                            "success": False,
                            "error": "todo_id is required to get a task"
                        }
                    })
                    continue
                
                try:
                    task = service_get_task_by_id(db, todo_id, user_id)
                except HTTPException:
                    results.append({
                        "content": {
                            "success": False,
                            "error": f"Task with ID {todo_id} not found"
                        }
                    })
                    continue
                
                results.append({
                    "content": {
                        "success": True,
                        "todo_id": task.id,
                        "title": task.description,
                        "completed": task.is_complete
                    }
                })

            elif tool_name == "get_overdue_todos":
                tasks = service_get_overdue_tasks(db, user_id)
                todos_list = [{"id": t.id, "title": t.description, "completed": t.is_complete} for t in tasks]
                results.append({
                    "content": {
                        "success": True,
                        "todos": todos_list,
                        "count": len(todos_list),
                        "message": f"You have {len(todos_list)} overdue task(s)." if todos_list else "You have no overdue tasks."
                    }
                })

            else:
                results.append({
                    "content": {
                        "success": False,
                        "error": f"Unknown tool: {tool_name}"
                    }
                })
                
        except Exception as e:
            print(f"Error executing tool {tool_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "content": {
                    "success": False,
                    "error": f"Error executing {tool_name}: {str(e)}"
                }
            })
    
    return results


@router.get("/history", response_model=ChatHistoryResponse)
def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat conversation history for the authenticated user.
    """
    history = get_conversation_history(current_user.id, limit=50)
    
    # Convert to ChatMessage format
    messages = [
        ChatMessage(
            role=msg["role"],
            content=msg["content"],
            timestamp=None
        )
        for msg in history
    ]
    
    return ChatHistoryResponse(messages=messages)


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    user_context: dict = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Send a chat message and get AI response using Phase III agent.
    
    Uses GetUserContext skill to extract user information from JWT token
    for personalized chatbot responses.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    user_id = current_user.id
    message = request.message.strip()
    
    # GetUserContext Skill: Log user context for debugging and personalization
    print(f"[Chat API] GetUserContext: user_id={user_context.get('user_id')}, "
          f"email={user_context.get('email')}, name={user_context.get('name')}")
    
    # Store user message
    store_message(user_id, "user", message)
    
    # Use Phase III Agent if available
    if PHASE_III_AVAILABLE:
        try:
            # Get conversation history
            history = get_conversation_history(user_id, limit=20)
            history_messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in history
            ]
            
            # Create agent and get tools
            agent = create_agent(api_key="mock", config=get_agent_config())
            tools = get_mcp_tool_definitions()
            
            # Process message with agent
            print(f"[Chat API] Processing message: {message[:50]}...")
            print(f"[Chat API] History length: {len(history_messages)}")
            print(f"[Chat API] Tools available: {len(tools)}")
            
            # Subagent Routing Logic
            system_prompt = None
            identity_keywords = ["who am i", "my profile", "my account", "my email", "who is logged in"]
            context_keywords = [" it ", " that ", " this ", " last ", " previous ", " more ", " those "]
            task_keywords = ["task", "todo", "add", "list", "show", "search", "update", "delete", "complete", "remove"]
            
            msg_lower = f" {message.lower()} " # Pad with spaces for word boundary match
            
            if any(kw in msg_lower for kw in identity_keywords):
                from app.agents.agent_prompts import USER_INFO_SUBAGENT_PROMPT
                system_prompt = USER_INFO_SUBAGENT_PROMPT
                print(f"[Chat API] Routing to UserInfoSubagent")
            elif any(kw in msg_lower for kw in context_keywords):
                from app.agents.agent_prompts import CONVERSATION_MANAGER_SUBAGENT_PROMPT
                system_prompt = CONVERSATION_MANAGER_SUBAGENT_PROMPT
                print(f"[Chat API] Routing to ConversationManagerSubagent")
            elif any(kw in msg_lower for kw in task_keywords):
                from app.agents.agent_prompts import TASK_CRUD_SUBAGENT_PROMPT
                system_prompt = TASK_CRUD_SUBAGENT_PROMPT
                print(f"[Chat API] Routing to TaskCRUDSubagent")
            
            agent_response = agent.process_message(
                user_message=message,
                conversation_history=history_messages,
                user_id=user_id,
                tools=tools,
                system_prompt=system_prompt
            )
            
            print(f"[Chat API] Agent response keys: {agent_response.keys() if isinstance(agent_response, dict) else 'Not a dict'}")
            print(f"[Chat API] Requires tool execution: {agent_response.get('requires_tool_execution', False)}")
            
            # Execute tool calls if needed
            final_response = agent_response.get("response_text", "")
            tool_calls_executed = []
            
            print(f"[Chat API] Initial response: {final_response[:100] if final_response else 'Empty'}")
            
            if agent_response.get("requires_tool_execution") and agent_response.get("tool_calls"):
                try:
                    # Normalize tool calls format (mock provider uses different structure)
                    tool_calls_to_execute = []
                    for tc in agent_response["tool_calls"]:
                        # Handle both formats: {"name": "...", "input": {...}} and {"name": "...", ...}
                        if isinstance(tc, dict):
                            tool_name = tc.get("name", "")
                            tool_input = tc.get("input", {})
                            # If no "input" key, use the whole dict except "name" and "tool_use_id"
                            if not tool_input:
                                tool_input = {k: v for k, v in tc.items() if k not in ["name", "tool_use_id"]}
                            tool_calls_to_execute.append({
                                "name": tool_name,
                                "input": tool_input
                            })
                    
                    print(f"[Chat API] Executing {len(tool_calls_to_execute)} tool calls")
                    
                    # Execute tools asynchronously
                    tool_results = await execute_tool_calls_async(
                        tool_calls_to_execute,
                        user_id,
                        db
                    )
                    
                    print(f"[Chat API] Tool execution completed: {len(tool_results)} results")
                    
                    # Get final response from tool results
                    try:
                        final_agent_response = agent.process_tool_results(
                            tool_results=tool_results,
                            user_id=user_id
                        )
                        final_response = final_agent_response.get("response_text", final_response)
                    except Exception as e:
                        print(f"[Chat API] Error in process_tool_results: {e}")
                        import traceback
                        print(f"[Chat API] process_tool_results traceback:\n{traceback.format_exc()}")
                        # Generate response from tool results manually
                        if tool_results:
                            result_messages = []
                            for r in tool_results:
                                content = r.get("content", {})
                                if isinstance(content, dict):
                                    if content.get("success", False):
                                        if "todos" in content:
                                            todos = content["todos"]
                                            if todos:
                                                task_list = "\n".join([
                                                    f"{t.get('id')}. {t.get('title')} {'✅' if t.get('completed') else '⏳'}"
                                                    for t in todos
                                                ])
                                                result_messages.append(f"Your tasks:\n{task_list}")
                                            else:
                                                result_messages.append("You have no tasks.")
                                        elif "todo_id" in content:
                                            todo_id = content["todo_id"]
                                            if "deleted" in content:
                                                result_messages.append(f"Successfully deleted task {todo_id}.")
                                            elif "title" in content:
                                                title = content["title"]
                                                result_messages.append(f"Task '{title}' processed successfully (ID: {todo_id}).")
                                elif isinstance(content, str):
                                    result_messages.append(content)
                            
                            if result_messages:
                                final_response = " ".join(result_messages)
                            else:
                                final_response = "I've processed your request successfully."
                    
                    tool_calls_executed = tool_calls_to_execute
                except Exception as e:
                    print(f"Error executing tools: {e}")
                    import traceback
                    traceback.print_exc()
                    final_response = final_response or "I processed your request, but encountered an error with tool execution."
            
            # Ensure we have a response
            if not final_response or not final_response.strip():
                # If no response from agent, try to generate one from tool results
                if tool_calls_executed:
                    # Extract results from tool execution
                    tool_summaries = []
                    for tool_call in tool_calls_executed:
                        tool_name = tool_call.get("name", "unknown")
                        tool_summaries.append(f"Executed {tool_name}")
                    final_response = f"I've processed your request. {', '.join(tool_summaries)}."
                else:
                    final_response = "I've processed your request."
            
            print(f"[Chat API] Final response: {final_response[:100]}")
            
            # Store assistant response
            store_message(user_id, "assistant", final_response)
            
            return ChatResponse(
                response=final_response,
                tool_calls=tool_calls_executed if tool_calls_executed else None
            )
            
        except Exception as e:
            error_msg = str(e)
            print(f"[Chat API] ❌ Error in Phase III agent: {error_msg}")
            import traceback
            full_traceback = traceback.format_exc()
            print(f"[Chat API] Full traceback:\n{full_traceback}")
            
            # Return detailed error for debugging (can be made user-friendly later)
            return ChatResponse(
                response=f"I encountered an error: {error_msg}. Please check the backend logs for details. Error type: {type(e).__name__}"
            )
    
    # Agent processed or error handled above
