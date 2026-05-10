import React, { useState, useEffect } from 'react';
import { format, startOfWeek } from 'date-fns';
import { mealApi } from '../api';
import usePolledData from '../hooks/usePolledData';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const MEALS = ['breakfast', 'lunch', 'dinner'];

function MealPanel() {
  const today = new Date();
  const weekStart = startOfWeek(today, { weekStartsOn: 1 }); // Monday = 1

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

  const { data: mealsData, isOnline, error, refetch } = usePolledData(
    () => mealApi.getWeeklyMeals(format(weekStart, 'yyyy-MM-dd')),
    10000 // Poll every 10 seconds
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
      await mealApi.updateWeeklyMeals(mealData, format(weekStart, 'yyyy-MM-dd'));
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

      {!isOnline && (
        <div className="offline-banner">
          ⚠️ Offline: Showing cached data
        </div>
      )}

      {error && (
        <div className="error-message">
          Error loading meals: {error}
        </div>
      )}

      <div className="panel-content">
        <div className="meal-plan-grid">
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
      </div>

      <div className="panel-footer">
        <button
          className="meal-save-btn"
          onClick={handleSaveMeals}
          disabled={isSaving}
        >
          {isSaving ? 'Saving...' : 'Save Week'}
        </button>
      </div>
    </div>
  );
}

export default MealPanel;
