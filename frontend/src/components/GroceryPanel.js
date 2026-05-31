import React, { useState } from 'react';
import { groceryApi } from '../api';
import usePolledData from '../hooks/usePolledData';
import {
  WORKFLOWS_GENERATE_COMMAND,
  fetchGroceryList,
  fetchWorkflowStatus,
  formatQuantity,
} from '../workflowsData';

function GroceryPanel() {
  const [newItem, setNewItem] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  const { data: generatedGroceries } = usePolledData(fetchGroceryList, 30000);
  const { data: workflowStatus } = usePolledData(fetchWorkflowStatus, 30000);
  const { data: groceriesData, error, refetch } = usePolledData(groceryApi.getGroceries, 60000, 'groceries');

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

  const groceries = Array.isArray(groceriesData) ? groceriesData : [];
  const uncheckedItems = groceries.filter((item) => !item.checked);
  const checkedItems = groceries.filter((item) => item.checked);
  const groceryHref = workflowStatus?.grocery_list_generated ? workflowStatus?.artifacts?.grocery_list_html : null;

  return (
    <div className="panel grocery-panel">
      <h2 className="panel-header">🛒 Grocery</h2>

      {error && (
        <div className="error-message">
          Error loading groceries: {error}
        </div>
      )}

      <div className="panel-content">
        {generatedGroceries?.missing ? (
          <div className="workflows-empty">
            <strong>Generated grocery list not available.</strong>
            <span>Run {WORKFLOWS_GENERATE_COMMAND}.</span>
          </div>
        ) : (
          <div className="generated-grocery-list">
            <div className="generated-grocery-summary">
              <strong>{generatedGroceries?.item_count || 0} generated items</strong>
              {groceryHref && <a href={groceryHref} target="_blank" rel="noreferrer">Open full list</a>}
            </div>
            {(generatedGroceries?.categories || []).map((category) => (
              <div key={category.category} className="grocery-category">
                <div className="grocery-category-title">{category.category}</div>
                {(category.items || []).slice(0, 5).map((item) => (
                  <div key={`${category.category}-${item.item}-${item.unit}`} className="generated-grocery-item">
                    {formatQuantity(item)}
                  </div>
                ))}
                {(category.items || []).length > 5 && (
                  <div className="generated-more">+{category.items.length - 5} more</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="panel-footer">
        <details className="manual-overrides">
          <summary>Manual grocery overrides</summary>
          {groceries.length === 0 ? (
            <div className="empty-message small">
              No manual grocery items
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
        </details>
      </div>
    </div>
  );
}

export default GroceryPanel;
