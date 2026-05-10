import axios from 'axios';

// API base URL from environment or default
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Task API
export const taskApi = {
  getTasks: (done = null) => {
    const params = {};
    if (done !== null) params.done = done;
    return api.get('/api/tasks', { params });
  },
  createTask: (text) => api.post('/api/tasks', { text, done: false }),
  updateTask: (id, data) => api.patch(`/api/tasks/${id}`, data),
  deleteTask: (id) => api.delete(`/api/tasks/${id}`),
};

// Grocery API
export const groceryApi = {
  getGroceries: (checked = null) => {
    const params = {};
    if (checked !== null) params.checked = checked;
    return api.get('/api/groceries', { params });
  },
  createGrocery: (item) => api.post('/api/groceries', { item, checked: false }),
  updateGrocery: (id, data) => api.patch(`/api/groceries/${id}`, data),
  deleteGrocery: (id) => api.delete(`/api/groceries/${id}`),
};

// Meal API
export const mealApi = {
  getWeeklyMeals: (date = null) => {
    const params = {};
    if (date) params.date_param = date;
    return api.get('/api/meals/week', { params });
  },
  updateWeeklyMeals: (meals, date = null) => {
    const params = {};
    if (date) params.date_param = date;
    return api.put('/api/meals/week', meals, { params });
  },
};

// Calendar API
export const calendarApi = {
  getEvents: (date = null) => {
    const params = {};
    if (date) params.date_param = date;
    return api.get('/api/calendar/events', { params });
  },
};

// Health check
export const healthApi = {
  check: () => api.get('/health'),
};

export default api;
