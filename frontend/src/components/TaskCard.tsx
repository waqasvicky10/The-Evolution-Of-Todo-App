"use client";

/**
 * TaskCard component.
 *
 * Displays a single task with toggle, edit, and delete functionality.
 * Supports inline editing mode and displays AI-enhanced metadata.
 */

import { useState } from "react";
import { Task } from "@/types/api";


interface TaskCardProps {
  task: Task;
  onToggle: (taskId: number) => void;
  onUpdate: (taskId: number, description: string) => void;
  onDelete: (taskId: number) => void;
  isLoading?: boolean;
}


export default function TaskCard({
  task,
  onToggle,
  onUpdate,
  onDelete,
  isLoading = false,
}: TaskCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editingDescription, setEditingDescription] = useState(task.description);
  const [error, setError] = useState<string | null>(null);

  const handleStartEdit = () => {
    setIsEditing(true);
    setEditingDescription(task.description);
    setError(null);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditingDescription(task.description);
    setError(null);
  };

  const handleSaveEdit = () => {
    setError(null);

    if (!editingDescription.trim()) {
      setError("Task description cannot be empty");
      return;
    }

    onUpdate(task.id, editingDescription.trim());
    setIsEditing(false);
  };

  const handleDelete = () => {
    if (confirm("Are you sure you want to delete this task?")) {
      onDelete(task.id);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-purple-700 bg-purple-50 border-purple-200';
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'work': return '💼';
      case 'personal': return '👤';
      case 'health': return '🏥';
      case 'learning': return '📚';
      case 'shopping': return '🛒';
      default: return '📝';
    }
  };

  const getRecurringLabel = (pattern: string) => {
    switch (pattern) {
      case 'daily': return 'Daily';
      case 'weekly': return 'Weekly';
      case 'monthly': return 'Monthly';
      default: return pattern;
    }
  };

  const isOverdue = task.due_date && !task.is_complete && new Date(task.due_date) < new Date();
  const tags = task.tags || [];
  const aiTags = task.ai_tags ? (() => { try { return JSON.parse(task.ai_tags!); } catch { return []; } })() : [];
  const aiSuggestions = task.ai_suggestions ? (() => { try { return JSON.parse(task.ai_suggestions!); } catch { return []; } })() : [];

  const cardClassName = task.is_complete
    ? "bg-gray-50 rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition"
    : "bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition";

  return (
    <div className={cardClassName}>
      {isEditing ? (
        // Edit mode
        <div>
          <div className="flex gap-3 mb-2">
            <input
              type="text"
              value={editingDescription}
              onChange={(e) => setEditingDescription(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              disabled={isLoading}
              autoFocus
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleSaveEdit();
                } else if (e.key === "Escape") {
                  handleCancelEdit();
                }
              }}
            />
            <button
              onClick={handleSaveEdit}
              disabled={isLoading}
              className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              Save
            </button>
            <button
              onClick={handleCancelEdit}
              disabled={isLoading}
              className="px-4 py-2 bg-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              Cancel
            </button>
          </div>
          {error && (
            <div className="text-sm text-red-600 mt-1">{error}</div>
          )}
        </div>
      ) : (
        // View mode
        <div>
          <div className="flex items-center gap-3 mb-3">
            {/* Checkbox */}
            <input
              type="checkbox"
              checked={task.is_complete}
              onChange={() => onToggle(task.id)}
              disabled={isLoading}
              className="h-5 w-5 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500 cursor-pointer disabled:cursor-not-allowed"
              title={task.is_complete ? "Mark as incomplete" : "Mark as complete"}
            />

            {/* Task description */}
            <span
              className={`flex-1 ${
                task.is_complete ? "text-gray-500 line-through" : "text-gray-900"
              }`}
            >
              {task.description}
            </span>

            {/* Action buttons */}
            <div className="flex gap-2">
              {!task.is_complete && (
                <button
                  onClick={handleStartEdit}
                  disabled={isLoading}
                  className="px-3 py-1 text-sm text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded-md transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Edit
                </button>
              )}
              <button
                onClick={handleDelete}
                disabled={isLoading}
                className="px-3 py-1 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Delete
              </button>
            </div>
          </div>

          {/* Phase V metadata row */}
          <div className="flex flex-wrap items-center gap-2 mb-2">
            {/* Priority */}
            {task.priority && (
              <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full capitalize border ${getPriorityColor(task.priority)}`}>
                {task.priority}
              </span>
            )}

            {/* Category */}
            {task.category && (
              <div className="flex items-center text-sm text-gray-600">
                <span className="mr-1">{getCategoryIcon(task.category)}</span>
                <span className="capitalize">{task.category}</span>
              </div>
            )}

            {/* Due date */}
            {task.due_date && (
              <span className={`inline-flex items-center px-2 py-1 text-xs rounded-full ${isOverdue ? 'bg-red-100 text-red-700 font-semibold' : 'bg-gray-100 text-gray-600'}`}>
                {isOverdue ? '⚠️' : '📅'} {new Date(task.due_date).toLocaleDateString()}
              </span>
            )}

            {/* Reminder */}
            {task.reminder_at && !task.is_complete && (
              <span className="inline-flex items-center px-2 py-1 text-xs bg-amber-100 text-amber-700 rounded-full">
                🔔 {new Date(task.reminder_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </span>
            )}

            {/* Recurring */}
            {task.recurring_pattern && (
              <span className="inline-flex items-center px-2 py-1 text-xs bg-indigo-100 text-indigo-700 rounded-full">
                🔁 {getRecurringLabel(task.recurring_pattern)}
              </span>
            )}

            {/* Duration */}
            {task.estimated_duration && (
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                ⏱️ {task.estimated_duration}
              </span>
            )}

            {/* User tags (Phase V) */}
            {tags.map((tag: string, index: number) => (
              <span key={`tag-${index}`} className="inline-flex px-2 py-1 text-xs bg-teal-100 text-teal-700 rounded-full">
                #{tag}
              </span>
            ))}

            {/* AI Tags */}
            {aiTags.map((tag: string, index: number) => (
              <span key={`ai-${index}`} className="inline-flex px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">
                #{tag}
              </span>
            ))}
          </div>

          {/* AI Suggestions (collapsed by default) */}
          {aiSuggestions.length > 0 && !task.is_complete && (
            <details className="mt-2">
              <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                💡 AI Suggestions ({aiSuggestions.length})
              </summary>
              <div className="mt-2 pl-4 border-l-2 border-blue-200">
                {aiSuggestions.map((suggestion: string, index: number) => (
                  <p key={index} className="text-xs text-gray-600 mb-1">
                    • {suggestion}
                  </p>
                ))}
              </div>
            </details>
          )}

          {/* Task metadata (timestamps) */}
          <div className="mt-2 text-xs text-gray-400 flex gap-4">
            <span>Created: {new Date(task.created_at).toLocaleDateString()}</span>
            {task.updated_at !== task.created_at && (
              <span>Updated: {new Date(task.updated_at).toLocaleDateString()}</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
