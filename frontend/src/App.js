import React from 'react';
import CalendarPanel from './components/CalendarPanel';
import TasksPanel from './components/TasksPanel';
import GroceryPanel from './components/GroceryPanel';
import MealPanel from './components/MealPanel';
import './index.css';

function App() {
  return (
    <div className="dashboard">
      <CalendarPanel />
      <TasksPanel />
      <GroceryPanel />
      <MealPanel />
    </div>
  );
}

export default App;
