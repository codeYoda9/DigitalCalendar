import React, { useState, useEffect } from 'react';
import { taskApi } from '../api';
import usePolledData from '../hooks/usePolledData';
import { WORKFLOWS_GENERATE_COMMAND, fetchWorkflowStatus } from '../workflowsData';

function TasksPanel() {
  const [newTask, setNewTask] = useState('');
  const [tasks, setTasks] = useState([]);
  const [isAdding, setIsAdding] = useState(false);

  const { data: workflowStatus } = usePolledData(fetchWorkflowStatus, 30000);
  const { data: tasksData, error, refetch } = usePolledData(
    () => taskApi.getTasks(),
    60000
  );

  useEffect(() => {
    if (tasksData?.data) {
      setTasks(tasksData.data);
    }
  }, [tasksData]);

  const handleAddTask = async (e) => {
    e.preventDefault();
    if (!newTask.trim()) return;

    setIsAdding(true);
    try {
      await taskApi.createTask(newTask);
      setNewTask('');
      refetch();
    } catch (err) {
      console.error('Failed to add task:', err);
    } finally {
      setIsAdding(false);
    }
  };

  const handleToggleTask = async (id, done) => {
    try {
      await taskApi.updateTask(id, { done: !done });
      refetch();
    } catch (err) {
      console.error('Failed to toggle task:', err);
    }
  };

  const handleDeleteTask = async (id) => {
    try {
      await taskApi.deleteTask(id);
      refetch();
    } catch (err) {
      console.error('Failed to delete task:', err);
    }
  };

  const activeTasks = tasks.filter((t) => !t.done);
  const completedTasks = tasks.filter((t) => t.done);
  const workflowTasks = workflowStatus?.tasks || [];

  return (
    <div className="panel tasks-panel">
      <h2 className="panel-header">✓ Tasks</h2>

      {error && (
        <div className="error-message">
          Error loading tasks: {error}
        </div>
      )}

      <div className="panel-content">
        {workflowStatus?.missing ? (
          <div className="workflows-empty">
            <strong>Workflow tasks not loaded.</strong>
            <span>Run {WORKFLOWS_GENERATE_COMMAND}.</span>
          </div>
        ) : (
          <div className="workflows-task-list">
            {workflowTasks.map((task) => (
              <div key={task.id} className={`task-item workflows-task-row ${task.done ? 'completed' : ''}`}>
                <span className="workflows-task-box">{task.done ? '✓' : ''}</span>
                <span className="task-text">{task.label}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="panel-footer">
        <details className="manual-overrides">
          <summary>Manual task overrides</summary>
          {tasks.length === 0 ? (
            <div className="empty-message small">
              No manual tasks
            </div>
          ) : (
            <>
              {activeTasks.map((task) => (
                <div key={task.id} className="task-item">
                  <input
                    type="checkbox"
                    className="task-checkbox"
                    checked={false}
                    onChange={() => handleToggleTask(task.id, task.done)}
                    disabled={isAdding}
                  />
                  <span className="task-text">{task.text}</span>
                  <button
                    className="task-delete-btn"
                    onClick={() => handleDeleteTask(task.id)}
                    disabled={isAdding}
                  >
                    ✕
                  </button>
                </div>
              ))}

              {completedTasks.length > 0 && (
                <>
                  <div style={{ marginTop: '1rem', marginBottom: '0.5rem', color: '#999', fontSize: '1rem' }}>
                    Completed
                  </div>
                  {completedTasks.map((task) => (
                    <div key={task.id} className="task-item completed">
                      <input
                        type="checkbox"
                        className="task-checkbox"
                        checked={true}
                        onChange={() => handleToggleTask(task.id, task.done)}
                        disabled={isAdding}
                      />
                      <span className="task-text">{task.text}</span>
                      <button
                        className="task-delete-btn"
                        onClick={() => handleDeleteTask(task.id)}
                        disabled={isAdding}
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </>
              )}
            </>
          )}
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
            >
              +
            </button>
          </form>
        </details>
      </div>
    </div>
  );
}

export default TasksPanel;
