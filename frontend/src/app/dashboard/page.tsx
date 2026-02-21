"use client";

/**
 * Dashboard page (/dashboard).
 *
 * Main authenticated page where users can view, create, update,
 * delete, and toggle their tasks. Protected route - requires login.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useTasks, useCreateTask, useUpdateTask, useDeleteTask, useToggleTask } from "@/hooks/useTasks";
import Navbar from "@/components/Navbar";
import TaskCard from "@/components/TaskCard";
import SmartTaskCreator from "@/components/SmartTaskCreator";
import TaskSuggestions from "@/components/TaskSuggestions";


export default function DashboardPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { tasks, isLoading: tasksLoading, error: tasksError, refetch } = useTasks();
  const { createTask, isLoading: createLoading } = useCreateTask();
  const { updateTask } = useUpdateTask();
  const { deleteTask } = useDeleteTask();
  const { toggleTask } = useToggleTask();
  const router = useRouter();

  const [newTaskDescription, setNewTaskDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState<"all" | "active" | "completed">("all");
  const [filterPriority, setFilterPriority] = useState<string>("all");
  const [sortBy, setSortBy] = useState<"newest" | "oldest" | "priority" | "dueDate">("newest");

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  // Show loading state while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  const handleCreateTask = async (description: string, metadata?: any) => {
    setError(null);

    if (!description.trim()) {
      setError("Task description cannot be empty");
      return;
    }

    // Create task data with AI metadata if provided
    const taskData = {
      description: description.trim(),
      ...metadata
    };

    const task = await createTask(taskData);
    if (task) {
      refetch();
    }
  };

  const handleToggleTask = async (taskId: number) => {
    const updatedTask = await toggleTask(taskId);
    if (updatedTask) {
      refetch();
    }
  };

  const handleUpdateTask = async (taskId: number, description: string) => {
    const updatedTask = await updateTask(taskId, { description });
    if (updatedTask) {
      refetch();
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    const success = await deleteTask(taskId);
    if (success) {
      refetch();
    }
  };

  // Phase V: search + filter + sort
  const priorityOrder: Record<string, number> = { urgent: 0, high: 1, medium: 2, low: 3 };

  const filteredTasks = tasks
    .filter((task) => {
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const matchDesc = task.description.toLowerCase().includes(q);
        const matchTags = (task.tags || []).some((t) => t.toLowerCase().includes(q));
        if (!matchDesc && !matchTags) return false;
      }
      if (filterStatus === "active" && task.is_complete) return false;
      if (filterStatus === "completed" && !task.is_complete) return false;
      if (filterPriority !== "all" && task.priority !== filterPriority) return false;
      return true;
    })
    .sort((a, b) => {
      if (sortBy === "oldest") return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      if (sortBy === "priority") return (priorityOrder[a.priority || "medium"] ?? 2) - (priorityOrder[b.priority || "medium"] ?? 2);
      if (sortBy === "dueDate") {
        if (!a.due_date && !b.due_date) return 0;
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
      }
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });

  const incompleteTasks = filteredTasks.filter(task => !task.is_complete);
  const completedTasks = filteredTasks.filter(task => task.is_complete);
  const overdueTasks = tasks.filter(task => task.due_date && !task.is_complete && new Date(task.due_date) < new Date());

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <Navbar />

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">My Tasks</h2>
          <p className="text-gray-600">
            {tasks.length} total task{tasks.length !== 1 ? "s" : ""} ({incompleteTasks.length} active, {completedTasks.length} completed)
          </p>
        </div>

        {/* Create Task Form */}
        <SmartTaskCreator 
          onCreateTask={handleCreateTask}
          isLoading={createLoading}
        />

        {/* AI Task Suggestions */}
        <TaskSuggestions
          onCreateTask={handleCreateTask}
          userContext={{
            total_tasks: tasks.length,
            completed_tasks: completedTasks.length,
            active_tasks: incompleteTasks.length,
            recent_categories: tasks.slice(0, 5).map(t => t.category).filter(Boolean)
          }}
          isVisible={true}
        />

        {/* Phase V: Search / Filter / Sort toolbar */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-3">
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm"
            />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
            </select>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Priorities</option>
              <option value="urgent">Urgent</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-indigo-500"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="priority">Priority</option>
              <option value="dueDate">Due Date</option>
            </select>
          </div>
          {overdueTasks.length > 0 && (
            <div className="mt-3 px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              ⚠️ You have {overdueTasks.length} overdue task{overdueTasks.length > 1 ? "s" : ""}
            </div>
          )}
        </div>

        {/* Tasks Error */}
        {tasksError && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {tasksError}
          </div>
        )}

        {/* Tasks Loading */}
        {tasksLoading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading tasks...</p>
          </div>
        )}

        {/* Tasks List */}
        {!tasksLoading && (
          <div className="space-y-6">
            {/* Active Tasks */}
            {incompleteTasks.length > 0 && (
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Active Tasks</h3>
                <div className="space-y-3">
                  {incompleteTasks.map((task) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      onToggle={handleToggleTask}
                      onUpdate={handleUpdateTask}
                      onDelete={handleDeleteTask}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Completed Tasks */}
            {completedTasks.length > 0 && (
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Completed Tasks</h3>
                <div className="space-y-3">
                  {completedTasks.map((task) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      onToggle={handleToggleTask}
                      onUpdate={handleUpdateTask}
                      onDelete={handleDeleteTask}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Empty State */}
            {tasks.length === 0 && (
              <div className="text-center py-12 bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="text-5xl mb-4">📝</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No tasks yet</h3>
                <p className="text-gray-600">Create your first task to get started!</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
