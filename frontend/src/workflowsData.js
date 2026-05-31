export const WORKFLOWS_GENERATE_COMMAND = 'npm run workflows:generate';

export const DEFAULT_WORKFLOW_TASKS = [
  { id: 'generate-meal-plan', label: 'Generate meal plan', done: false },
  { id: 'review-meal-plan', label: 'Review meal plan', done: false },
  { id: 'generate-grocery-list', label: 'Generate grocery list', done: false },
  { id: 'review-grocery-list', label: 'Review grocery list', done: false },
  { id: 'shop-groceries', label: 'Shop groceries', done: false },
];

export function fetchWorkflowStatus() {
  return fetchGeneratedJson('/generated/workflow-status.json', {
    missing: true,
    ok: false,
    meal_plan_generated: false,
    grocery_list_generated: false,
    grocery_item_count: 0,
    missing_meals: [],
    warnings: [`Not generated yet. Run ${WORKFLOWS_GENERATE_COMMAND}.`],
    errors: [],
    tasks: DEFAULT_WORKFLOW_TASKS,
    artifacts: {},
  });
}

export function fetchMealPlan() {
  return fetchGeneratedJson('/generated/meal-plan.json', {
    missing: true,
    days: [],
  });
}

export function fetchGroceryList() {
  return fetchGeneratedJson('/generated/grocery-list.json', {
    missing: true,
    item_count: 0,
    categories: [],
  });
}

function fetchGeneratedJson(path, fallback) {
  return fetch(`${path}?t=${Date.now()}`)
    .then((response) => {
      if (!response.ok) {
        return { data: fallback };
      }
      return response.json().then((data) => ({ data }));
    })
    .catch(() => ({ data: fallback }));
}

export function formatQuantity(item) {
  if (item.quantity === null || item.quantity === undefined || item.quantity === '') {
    return item.item;
  }
  const quantity = Number.isInteger(item.quantity) ? item.quantity : Number(item.quantity);
  const prettyQuantity = Number.isNaN(quantity) ? item.quantity : quantity;
  return `${prettyQuantity} ${item.unit || ''} ${item.item}`.replace(/\s+/g, ' ').trim();
}
