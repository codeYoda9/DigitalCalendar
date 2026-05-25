import React from 'react';
import CalendarPanel from './components/CalendarPanel';
import TasksPanel from './components/TasksPanel';
import GroceryPanel from './components/GroceryPanel';
import MealPanel from './components/MealPanel';
import WorkflowsPanel from './components/WorkflowsPanel';
import './index.css';

const AVAILABLE_VIEWS = new Set(['dashboard', 'calendar', 'workflows']);

function getRequestedView() {
  const defaultView = process.env.REACT_APP_DEFAULT_VIEW || 'dashboard';

  if (typeof window === 'undefined') {
    return AVAILABLE_VIEWS.has(defaultView) ? defaultView : 'dashboard';
  }

  const searchParams = new URLSearchParams(window.location.search);
  const queryView = searchParams.get('view');
  if (AVAILABLE_VIEWS.has(queryView)) {
    return queryView;
  }

  const pathView = window.location.pathname.split('/').filter(Boolean)[0];
  if (AVAILABLE_VIEWS.has(pathView)) {
    return pathView;
  }

  return AVAILABLE_VIEWS.has(defaultView) ? defaultView : 'dashboard';
}

function App() {
  const view = getRequestedView();

  if (view === 'calendar') {
    return (
      <div className="page-shell single-panel-page">
        <CalendarPanel />
      </div>
    );
  }

  if (view === 'workflows') {
    return (
      <div className="page-shell single-panel-page">
        <WorkflowsPanel />
      </div>
    );
  }

  return (
    <div className="dashboard">
      <MealPanel />
      <GroceryPanel />
      <TasksPanel />
    </div>
  );
}

export default App;
