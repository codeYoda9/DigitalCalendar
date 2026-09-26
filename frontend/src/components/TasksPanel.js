import React, { useState } from 'react';
import { taskApi } from '../api';
import usePolledData from '../hooks/usePolledData';

function TasksPanel() {
  const [newTask, setNewTask] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [pendingTaskId, setPendingTaskId] = useState(null);

  const { data: tasksData, error, refetch } = usePolledData(taskApi.getTasks, 60000, 'tasks');

  const handleAddTask = async (e) => {
    e.preventDefault();
    const text = newTask.trim();
    if (!text) return;

    setIsAdding(true);
    try {
      await taskApi.createTask(text);
      setNewTask('');
      refetch();
    } catch (err) {
      console.error('Failed to add task:', err);
    } finally {
      setIsAdding(false);
    }
  };

  const handleToggleTask = async (id, done) => {
    setPendingTaskId(id);
    try {
      await taskApi.updateTask(id, { done: !done });
      refetch();
    } catch (err) {
      console.error('Failed to toggle task:', err);
    } finally {
      setPendingTaskId(null);
    }
  };

  const handleDeleteTask = async (id) => {
    setPendingTaskId(id);
    try {
      await taskApi.deleteTask(id);
      refetch();
    } catch (err) {
      console.error('Failed to delete task:', err);
    } finally {
      setPendingTaskId(null);
    }
  };

  const tasks = Array.isArray(tasksData) ? tasksData : [];
  const activeTasks = tasks.filter((t) => !t.done);
  const completedTasks = tasks.filter((t) => t.done);
  const renderTask = (task) => (
    <div key={task.id} className={`task-item ${task.done ? 'completed' : ''}`}>
      <input
        type="checkbox"
        className="task-checkbox"
        checked={task.done}
        onChange={() => handleToggleTask(task.id, task.done)}
        disabled={pendingTaskId === task.id}
        aria-label={`Mark ${task.text} ${task.done ? 'active' : 'done'}`}
      />
      <span className="task-text">{task.text}</span>
      <button
        type="button"
        className="task-delete-btn"
        onClick={() => handleDeleteTask(task.id)}
        disabled={pendingTaskId === task.id}
        aria-label={`Delete ${task.text}`}
      >
        ✕
      </button>
    </div>
  );

  return (
    <div className="panel tasks-panel">
      <h2 className="panel-header">✓ Tasks</h2>

      {error && (
        <div className="error-message">
          Error loading tasks: {error}
        </div>
      )}

      <div className="panel-content">
        {tasks.length === 0 ? (
          <div className="empty-message">
            No tasks yet
          </div>
        ) : (
          <>
            {activeTasks.map(renderTask)}

            {completedTasks.length > 0 && (
              <>
                <div className="task-section-label">Completed</div>
                {completedTasks.map(renderTask)}
              </>
            )}
          </>
        )}
      </div>

      <div className="panel-footer">
        <form onSubmit={handleAddTask} className="input-group">
          <input
            type="text"
            className="input-field"
            placeholder="Add task..."
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
            disabled={isAdding}
          />
          <button
            type="submit"
            className="add-btn"
            disabled={isAdding || !newTask.trim()}
            aria-label="Add task"
          >
            +
          </button>
        </form>

      </div>
    </div>
  );
}

export default TasksPanel;
