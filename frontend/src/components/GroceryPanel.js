import React, { useState, useEffect } from 'react';
import { groceryApi } from '../api';
import usePolledData from '../hooks/usePolledData';

function GroceryPanel() {
  const [newItem, setNewItem] = useState('');
  const [groceries, setGroceries] = useState([]);
  const [isAdding, setIsAdding] = useState(false);

  const { data: groceriesData, isOnline, error, refetch } = usePolledData(
    () => groceryApi.getGroceries(),
    10000 // Poll every 10 seconds
  );

  useEffect(() => {
    if (groceriesData?.data) {
      setGroceries(groceriesData.data);
    }
  }, [groceriesData]);

  const handleAddItem = async (e) => {
    e.preventDefault();
    if (!newItem.trim()) return;

    setIsAdding(true);
    try {
      await groceryApi.createGrocery(newItem);
      setNewItem('');
      refetch();
    } catch (err) {
      console.error('Failed to add grocery item:', err);
    } finally {
      setIsAdding(false);
    }
  };

  const handleToggleItem = async (id, checked) => {
    try {
      await groceryApi.updateGrocery(id, { checked: !checked });
      refetch();
    } catch (err) {
      console.error('Failed to toggle grocery item:', err);
    }
  };

  const handleDeleteItem = async (id) => {
    try {
      await groceryApi.deleteGrocery(id);
      refetch();
    } catch (err) {
      console.error('Failed to delete grocery item:', err);
    }
  };

  const uncheckedItems = groceries.filter((item) => !item.checked);
  const checkedItems = groceries.filter((item) => item.checked);

  return (
    <div className="panel grocery-panel">
      <h2 className="panel-header">🛒 Grocery</h2>

      {!isOnline && (
        <div className="offline-banner">
          ⚠️ Offline: Showing cached data
        </div>
      )}

      {error && (
        <div className="error-message">
          Error loading groceries: {error}
        </div>
      )}

      <div className="panel-content">
        {groceries.length === 0 ? (
          <div className="empty-message">
            No grocery items
          </div>
        ) : (
          <>
            {uncheckedItems.map((item) => (
              <div key={item.id} className="grocery-item">
                <input
                  type="checkbox"
                  className="grocery-checkbox"
                  checked={false}
                  onChange={() => handleToggleItem(item.id, item.checked)}
                  disabled={isAdding}
                />
                <span className="grocery-text">{item.item}</span>
                <button
                  className="grocery-delete-btn"
                  onClick={() => handleDeleteItem(item.id)}
                  disabled={isAdding}
                >
                  ✕
                </button>
              </div>
            ))}

            {checkedItems.length > 0 && (
              <>
                <div style={{ marginTop: '1rem', marginBottom: '0.5rem', color: '#999', fontSize: '1rem' }}>
                  Got it
                </div>
                {checkedItems.map((item) => (
                  <div key={item.id} className="grocery-item checked">
                    <input
                      type="checkbox"
                      className="grocery-checkbox"
                      checked={true}
                      onChange={() => handleToggleItem(item.id, item.checked)}
                      disabled={isAdding}
                    />
                    <span className="grocery-text">{item.item}</span>
                    <button
                      className="grocery-delete-btn"
                      onClick={() => handleDeleteItem(item.id)}
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
      </div>

      <div className="panel-footer">
        <form onSubmit={handleAddItem} className="input-group">
          <input
            type="text"
            className="input-field"
            placeholder="Add item..."
            value={newItem}
            onChange={(e) => setNewItem(e.target.value)}
            disabled={isAdding}
          />
          <button
            type="submit"
            className="add-btn"
            disabled={isAdding || !newItem.trim()}
          >
            +
          </button>
        </form>
      </div>
    </div>
  );
}

export default GroceryPanel;
