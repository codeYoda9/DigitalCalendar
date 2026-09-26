import React, { useState } from 'react';
import { groceryApi } from '../api';
import usePolledData from '../hooks/usePolledData';

function GroceryPanel() {
  const [newItem, setNewItem] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [pendingItemId, setPendingItemId] = useState(null);

  const { data: groceriesData, error, refetch } = usePolledData(groceryApi.getGroceries, 60000, 'groceries');

  const handleAddItem = async (e) => {
    e.preventDefault();
    const item = newItem.trim();
    if (!item) return;

    setIsAdding(true);
    try {
      await groceryApi.createGrocery(item);
      setNewItem('');
      refetch();
    } catch (err) {
      console.error('Failed to add grocery item:', err);
    } finally {
      setIsAdding(false);
    }
  };

  const handleToggleItem = async (id, checked) => {
    setPendingItemId(id);
    try {
      await groceryApi.updateGrocery(id, { checked: !checked });
      refetch();
    } catch (err) {
      console.error('Failed to toggle grocery item:', err);
    } finally {
      setPendingItemId(null);
    }
  };

  const handleDeleteItem = async (id) => {
    setPendingItemId(id);
    try {
      await groceryApi.deleteGrocery(id);
      refetch();
    } catch (err) {
      console.error('Failed to delete grocery item:', err);
    } finally {
      setPendingItemId(null);
    }
  };

  const groceries = Array.isArray(groceriesData) ? groceriesData : [];
  const uncheckedItems = groceries.filter((item) => !item.checked);
  const checkedItems = groceries.filter((item) => item.checked);
  const renderGroceryItem = (item) => (
    <div key={item.id} className={`grocery-item ${item.checked ? 'checked' : ''}`}>
      <input
        type="checkbox"
        className="grocery-checkbox"
        checked={item.checked}
        onChange={() => handleToggleItem(item.id, item.checked)}
        disabled={pendingItemId === item.id}
        aria-label={`Mark ${item.item} ${item.checked ? 'needed' : 'bought'}`}
      />
      <span className="grocery-text">{item.item}</span>
      <button
        type="button"
        className="grocery-delete-btn"
        onClick={() => handleDeleteItem(item.id)}
        disabled={pendingItemId === item.id}
        aria-label={`Delete ${item.item}`}
      >
        ✕
      </button>
    </div>
  );

  return (
    <div className="panel grocery-panel">
      <h2 className="panel-header">🛒 Grocery</h2>

      {error && (
        <div className="error-message">
          Error loading groceries: {error}
        </div>
      )}

      <div className="panel-content">
        {groceries.length === 0 ? (
          <div className="empty-message">
            No grocery items yet
          </div>
        ) : (
          <>
            {uncheckedItems.map(renderGroceryItem)}

            {checkedItems.length > 0 && (
              <>
                <div className="grocery-section-label">Bought</div>
                {checkedItems.map(renderGroceryItem)}
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
            aria-label="Add grocery item"
          >
            +
          </button>
        </form>

      </div>
    </div>
  );
}

export default GroceryPanel;
