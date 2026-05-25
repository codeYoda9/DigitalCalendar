import React from 'react';
import usePolledData from '../hooks/usePolledData';
import { WORKFLOWS_GENERATE_COMMAND, fetchWorkflowStatus } from '../workflowsData';

function WorkflowsPanel() {
  const { data: status, error } = usePolledData(fetchWorkflowStatus, 30000);
  const today = new Date();
  const isSaturday = today.getDay() === 6;
  const tasks = status?.tasks || [];
  const completedTasks = tasks.filter((task) => task.done).length;
  const missingMeals = status?.missing_meals || [];
  const warnings = [...(status?.errors || []), ...(status?.warnings || [])];
  const shopTask = tasks.find((task) => task.id === 'shop-groceries');
  const groceryHref = status?.grocery_list_generated ? status?.artifacts?.grocery_list_html : null;
  const mealPlanHref = status?.meal_plan_generated ? status?.artifacts?.meal_plan_html : null;

  return (
    <div className="panel workflows-panel">
      <h2 className="panel-header">Workflows</h2>

      {error && (
        <div className="error-message">
          Workflow status is not available yet.
        </div>
      )}

      {isSaturday ? (
        <div className="shopping-reminder prominent">
          <strong>Review grocery list and shop groceries.</strong>
          <span> Shop task: {shopTask?.done ? 'complete' : 'pending'}.</span>
          {' '}
          {groceryHref ? (
            <a href={groceryHref} target="_blank" rel="noreferrer">Open list</a>
          ) : (
            <span>Run {WORKFLOWS_GENERATE_COMMAND} first.</span>
          )}
        </div>
      ) : (
        <div className="shopping-reminder">
          <strong>Shopping:</strong> next Saturday. Shop task is {shopTask?.done ? 'complete' : 'pending'}.
          {' '}
          {groceryHref && <a href={groceryHref} target="_blank" rel="noreferrer">Open list</a>}
        </div>
      )}

      <div className="workflows-summary-grid">
        <div className="workflows-summary-item">
          <span className="summary-label">Meal plan</span>
          <strong>{status?.meal_plan_generated ? 'Ready' : 'Not generated'}</strong>
        </div>
        <div className="workflows-summary-item">
          <span className="summary-label">Groceries</span>
          <strong>{status?.grocery_item_count || 0} items</strong>
        </div>
        <div className="workflows-summary-item">
          <span className="summary-label">Tasks</span>
          <strong>{completedTasks}/{tasks.length || 5} done</strong>
        </div>
        <div className="workflows-summary-item">
          <span className="summary-label">Generated</span>
          <strong>{formatGeneratedAt(status?.last_generated_at)}</strong>
        </div>
        <div className="workflows-summary-item">
          <span className="summary-label">Warnings</span>
          <strong>{status?.warning_count || warnings.length || missingMeals.length}</strong>
        </div>
      </div>

      <div className="workflows-links">
        {mealPlanHref ? (
          <a href={mealPlanHref} target="_blank" rel="noreferrer">Meal plan</a>
        ) : (
          <span>Meal plan: run {WORKFLOWS_GENERATE_COMMAND}</span>
        )}
        {groceryHref ? (
          <a href={groceryHref} target="_blank" rel="noreferrer">Grocery list</a>
        ) : (
          <span>Grocery list: not generated yet</span>
        )}
      </div>

      <div className="workflows-checklist">
        {tasks.length === 0 ? (
          <div className="empty-message">No weekly checklist yet</div>
        ) : (
          tasks.map((task) => (
            <div key={task.id} className={`workflows-task ${task.done ? 'done' : ''}`}>
              <span className="workflows-task-box">{task.done ? '✓' : ''}</span>
              <span>{task.label}</span>
            </div>
          ))
        )}
      </div>

      {(missingMeals.length > 0 || warnings.length > 0) && (
        <div className="workflows-warnings">
          {missingMeals.length > 0 && (
            <div><strong>Missing meals:</strong> {missingMeals.join(', ')}</div>
          )}
          {warnings.slice(0, 4).map((warning) => (
            <div key={warning}>{warning}</div>
          ))}
        </div>
      )}
    </div>
  );
}

function formatGeneratedAt(value) {
  if (!value) return 'Never';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Unknown';
  return date.toLocaleString([], { weekday: 'short', hour: 'numeric', minute: '2-digit' });
}

export default WorkflowsPanel;
