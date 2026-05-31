import React, { useState, useEffect, useCallback } from 'react';
import { format, startOfWeek } from 'date-fns';
import { mealApi } from '../api';
import usePolledData from '../hooks/usePolledData';
import { WORKFLOWS_GENERATE_COMMAND, fetchMealPlan, fetchWorkflowStatus } from '../workflowsData';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const MEALS = ['breakfast', 'lunch', 'dinner'];

function MealPanel() {
  const today = new Date();
  const weekStart = startOfWeek(today, { weekStartsOn: 1 }); // Monday = 1
  const weekStartParam = format(weekStart, 'yyyy-MM-dd');
  const fetchWeeklyMeals = useCallback(
    () => mealApi.getWeeklyMeals(weekStartParam),
    [weekStartParam]
  );

  const [mealData, setMealData] = useState({
    Monday: { breakfast: '', lunch: '', dinner: '' },
    Tuesday: { breakfast: '', lunch: '', dinner: '' },
    Wednesday: { breakfast: '', lunch: '', dinner: '' },
    Thursday: { breakfast: '', lunch: '', dinner: '' },
    Friday: { breakfast: '', lunch: '', dinner: '' },
    Saturday: { breakfast: '', lunch: '', dinner: '' },
    Sunday: { breakfast: '', lunch: '', dinner: '' },
  });
  const [isSaving, setIsSaving] = useState(false);

  const { data: generatedPlan } = usePolledData(fetchMealPlan, 30000);
  const { data: workflowStatus } = usePolledData(fetchWorkflowStatus, 30000);
  const { data: mealsData, error, refetch } = usePolledData(
    fetchWeeklyMeals,
    60000,
    `weekly-meals-${weekStartParam}`
  );

  useEffect(() => {
    if (mealsData) {
      setMealData(mealsData);
    }
  }, [mealsData]);

  const handleMealChange = (day, mealType, value) => {
    setMealData((prev) => ({
      ...prev,
      [day]: {
        ...prev[day],
        [mealType]: value,
      },
    }));
  };

  const handleSaveMeals = async () => {
    setIsSaving(true);
    try {
      await mealApi.updateWeeklyMeals(mealData, weekStartParam);
      refetch();
    } catch (err) {
      console.error('Failed to save meals:', err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="panel meal-panel">
      <h2 className="panel-header">🍽️ Meals</h2>

      {error && (
        <div className="error-message">
          Error loading meals: {error}
        </div>
      )}

      <div className="panel-content">
        {generatedPlan?.missing ? (
          <div className="workflows-empty">
            <strong>Generated meal plan not available.</strong>
            <span>Run {WORKFLOWS_GENERATE_COMMAND}.</span>
          </div>
        ) : (
          <div className="generated-meal-list">
            {(generatedPlan?.days || []).map((day) => (
              <div key={day.day} className="generated-meal-day">
                <div className="meal-day-label">{day.day}</div>
                {(day.meals || []).map((meal) => (
                  <div key={`${day.day}-${meal.slot}`} className={meal.recipe ? 'generated-meal' : 'generated-meal missing'}>
                    <span className="meal-type">{meal.slot}</span>
                    <strong>{meal.recipe || 'Missing meal'}</strong>
                    {meal.warning && <span className="meal-warning">{meal.warning}</span>}
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}

        {(workflowStatus?.missing_meals || []).length > 0 && (
          <div className="workflows-warnings compact">
            <strong>Missing meals</strong>
            {(workflowStatus.missing_meals || []).map((meal) => (
              <div key={meal}>{meal}</div>
            ))}
          </div>
        )}
      </div>

      <div className="panel-footer">
        <details className="manual-overrides">
          <summary>Manual meal overrides</summary>
          <div className="meal-plan-grid manual-grid">
            {DAYS.map((day) => (
              <div key={day} className="meal-day">
                <div className="meal-day-label">{day.slice(0, 3)}</div>
                {MEALS.map((mealType) => (
                  <div key={`${day}-${mealType}`}>
                    <div className="meal-type">{mealType}</div>
                    <input
                      type="text"
                      className="meal-input"
                      value={mealData[day]?.[mealType] || ''}
                      onChange={(e) => handleMealChange(day, mealType, e.target.value)}
                      placeholder={`${mealType}...`}
                      disabled={isSaving}
                    />
                  </div>
                ))}
              </div>
            ))}
          </div>
          <button
            className="meal-save-btn"
            onClick={handleSaveMeals}
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save Week'}
          </button>
        </details>
      </div>
    </div>
  );
}

export default MealPanel;
