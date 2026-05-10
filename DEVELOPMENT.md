# Development Guide - Digital Calendar Phase 1

This guide covers architecture, component details, and development workflows.

## Project Structure

```
DigitalCalendar/
├── backend/                    # FastAPI application
│   ├── main.py                 # Main application with routes
│   ├── database.py             # SQLAlchemy setup
│   ├── models.py               # Database models
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── routes_tasks.py         # Task endpoints
│   ├── routes_groceries.py     # Grocery endpoints
│   ├── routes_meals.py         # Meal endpoints
│   ├── routes_calendar.py      # Calendar endpoints (mock, TODO: Google API)
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Backend container config
│   └── .dockerignore
│
├── frontend/                   # React application
│   ├── public/
│   │   └── index.html          # HTML template
│   ├── src/
│   │   ├── index.js            # React entry point
│   │   ├── index.css           # Global styles (touch-first, large text)
│   │   ├── App.js              # Main dashboard component (4-panel layout)
│   │   ├── api.js              # Backend API client
│   │   ├── hooks/
│   │   │   └── usePolledData.js # Custom hook for 10s polling
│   │   └── components/
│   │       ├── CalendarPanel.js # Today/Calendar panel
│   │       ├── TasksPanel.js    # Tasks todo list
│   │       ├── GroceryPanel.js  # Shopping list
│   │       └── MealPanel.js     # Weekly meal plan
│   ├── package.json            # Node dependencies
│   ├── Dockerfile              # Frontend container config
│   └── .dockerignore
│
├── database/
│   └── init.sql                # PostgreSQL schema initialization
│
├── docker-compose.yaml         # Docker Compose orchestration
├── README.md                   # Main documentation
├── DEVELOPMENT.md              # This file
├── .env.example                # Environment template
└── .gitignore

```

## Backend Architecture

### FastAPI Application (`backend/main.py`)
- Initializes database tables on startup
- Sets up CORS middleware for frontend access
- Registers all route modules
- Provides health check endpoint
- Lifespan events for startup/shutdown

### Database Models (`backend/models.py`)
- `Task`: id, text, done, created_at, updated_at
- `Grocery`: id, item, checked, created_at, updated_at
- `Meal`: id, week_start_date, day_of_week, breakfast, lunch, dinner, updated_at
- `AuditLog`: id, entity_type, entity_id, action, payload_json, created_at

### Request/Response Schemas (`backend/schemas.py`)
- Pydantic models for validation
- Separate Create/Update/Response schemas
- Type hints for all fields
- Config for SQLAlchemy model conversion

### Route Modules
- `routes_tasks.py`: CRUD operations for tasks
- `routes_groceries.py`: CRUD operations for grocery items
- `routes_meals.py`: Weekly meal plan retrieval and update
- `routes_calendar.py`: Calendar events (mock in Phase 1, TODO comments for Phase 2)

## Frontend Architecture

### 4-Panel Dashboard Layout
```
┌─────────────────────────────────────┐
│   📅 TODAY / CALENDAR  │  ✓ TASKS   │
│   - Date and day      │  - Active   │
│   - Events list       │  - Add task │
├────────────────────────┼────────────┤
│  🛒 GROCERY            │  🍽️ MEALS  │
│  - Items list         │  - Weekly   │
│  - Checked section    │    grid     │
│  - Add item           │  - Editable │
└─────────────────────────────────────┘
```

Responsive design:
- 2x2 grid on desktop/portrait
- Stacked on mobile
- Touch-optimized buttons and inputs
- Large text (1.3rem+) for 8-foot viewing distance

### API Communication (`frontend/src/api.js`)
- Axios instance with base URL from env
- Separate namespaced API methods
- Error handling with console logging
- Optional parameters for filtering

### Custom Hook (`frontend/src/hooks/usePolledData.js`)
- **Polling Interval**: 10 seconds (per spec)
- **Offline Fallback**: Shows cached data with banner
- **localStorage Cache**: Last successful responses cached
- **Error Handling**: Graceful degradation

### Components

#### CalendarPanel (`frontend/src/components/CalendarPanel.js`)
- Displays today's date in large format
- Shows day of week
- Lists upcoming events
- Filters events to current date onwards
- Shows offline/error banners

#### TasksPanel (`frontend/src/components/TasksPanel.js`)
- Two sections: Active & Completed
- Add task with text input
- Toggle task completion with checkbox
- Delete task button
- Real-time updates via polling

#### GroceryPanel (`frontend/src/components/GroceryPanel.js`)
- Similar layout to tasks
- Shows items and checked items
- Add item functionality
- Toggle and delete items
- Polling integration

#### MealPanel (`frontend/src/components/MealPanel.js`)
- 3-column grid for days of week
- 3 input fields per day (breakfast, lunch, dinner)
- Save entire week with single button
- Validates and updates on backend
- Offline support with caching

## API Endpoints

### Tasks
```
GET  /api/tasks          - List tasks (optional: ?done=true/false)
POST /api/tasks          - Create task (body: {text: string, done: bool})
PATCH /api/tasks/{id}    - Update task (body: {text?: string, done?: bool})
DELETE /api/tasks/{id}   - Delete task
```

### Groceries
```
GET    /api/groceries         - List items (optional: ?checked=true/false)
POST   /api/groceries         - Create item (body: {item: string, checked: bool})
PATCH  /api/groceries/{id}    - Update item (body: {item?: string, checked?: bool})
DELETE /api/groceries/{id}    - Delete item
```

### Meals
```
GET  /api/meals/week    - Get week plan (optional: ?date_param=2024-01-01)
PUT  /api/meals/week    - Update week plan (body: {Monday: {...}, ...})
```

### Calendar
```
GET  /api/calendar/events  - Get events (optional: ?date_param=2024-01-01)
     Returns: {events: [...], date: string}
```

### Health
```
GET  /health    - Health check (returns: {status: string, database: string})
```

## Development Workflow

### Local Backend Development
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

### Local Frontend Development
```bash
cd frontend
npm install
npm start
```

Automatically opens at: http://localhost:3000

### Local Database
```bash
# Connect with psql
docker exec -it digital-calendar-db psql -U digitalcalendar -d digitalcalendar

# Common queries
SELECT * FROM tasks;
SELECT * FROM groceries;
SELECT * FROM meals WHERE week_start_date = '2024-01-01';
```

### Docker Compose Workflow
```bash
# Build all services
docker compose build

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f [service_name]

# Stop all services
docker compose down

# Remove volumes (caution: deletes data)
docker compose down -v
```

## Styling System

### CSS Principles
- Mobile-first responsive design
- Large buttons and text (minimum 1.2rem for body text)
- High contrast colors (#667eea purple, white backgrounds)
- Rounded corners (8-12px)
- Touch-friendly spacing (1rem+ padding)

### Color Palette
- Primary: `#667eea` (Purple)
- Secondary: `#764ba2` (Dark purple)
- Background: White
- Text: `#333` (Dark gray)
- Muted: `#999` (Light gray)
- Success: `#e8f5e9` (Light green)
- Error: `#ffebee` (Light red)

### Responsive Breakpoints
- Desktop (>1024px): 2x2 grid layout
- Tablet/Mobile (<1024px): Single column stacked layout

## Error Handling

### Frontend Error States
- Backend unreachable → Shows offline banner with cached data
- API error response → Shows error message in panel
- Network timeout → Falls back to cache
- Invalid input → Disables button and doesn't submit

### Backend Error States
- Database connection failed → Returns 503 Service Unavailable
- Invalid request body → Returns 422 Unprocessable Entity
- Resource not found → Returns 404 Not Found
- Database operation failed → Returns 500 Internal Server Error

## Caching Strategy

### Frontend localStorage
```javascript
// Cached keys
'cached_getTasks'
'cached_getGroceries'
'cached_getWeeklyMeals'
'cached_getEvents'
```

### Cache Behavior
- Stored on successful API response
- Restored on network error
- User notified of offline state
- Cache persists across refreshes
- No automatic cache expiration (Phase 1)

## Performance Considerations

### Polling Optimization
- **Interval**: 10 seconds (balance between freshness and server load)
- **Request timeout**: 10 seconds
- **Concurrent requests**: One poll cycle at a time
- **No request deduplication** in Phase 1

### Database Query Optimization
- Indexes on: done, checked, week_start_date, entity tracking
- Pagination support: limit/skip parameters
- No N+1 queries (simple one-to-one relationships)

### Frontend Optimization
- React.StrictMode in development
- No unnecessary re-renders (hooks handle state)
- CSS optimized for Chromium (Raspberry Pi browser)
- Minimal dependencies (react, react-dom, axios, date-fns)

## TODO: Phase 2 Features

### Calendar Integration
In `backend/routes_calendar.py`:
```python
# TODO: Integrate Google Calendar API
# - Add GOOGLE_CALENDAR_CREDENTIALS environment variable
# - Use google-auth and google-auth-oauthlib libraries
# - Implement OAuth flow for initial setup
# - Cache tokens in secure storage
# - Fetch real events from Google Calendar API
# - Handle timezone conversion
# - Fall back to mock events if credentials not configured
```

### WebSocket Support
- Replace polling with bidirectional updates
- Reduce server load
- Real-time collaboration improvements

### User Authentication
- Multi-user accounts
- Household member roles
- Shared vs personal items

### Advanced Features
- Mealie recipe integration
- Alexa voice commands
- Mobile native app
- OCR for recipes

## Testing

### Manual Testing Checklist
- [ ] Add task → appears in list
- [ ] Mark task complete → moves to completed section
- [ ] Delete task → removed from list
- [ ] Add grocery → appears in list
- [ ] Mark grocery checked → moved to checked section
- [ ] Delete grocery → removed from list
- [ ] Edit meal plan → saved and persisted
- [ ] Navigate between dates (calendar)
- [ ] Offline mode shows banner
- [ ] Data cached in localStorage

### Backend Testing
```bash
# Run tests (when added)
pytest backend/tests/

# Manual API testing
curl http://localhost:8000/health
curl http://localhost:8000/api/tasks
curl -X POST http://localhost:8000/api/tasks -d '{"text":"Test task"}' -H "Content-Type: application/json"
```

## Debugging

### Frontend Debug Steps
1. Open Chrome DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for API calls
4. Check Storage → localStorage for cached data
5. Check Elements tab for CSS issues

### Backend Debug Steps
1. Check logs: `docker logs digital-calendar-backend`
2. Connect to database: `docker exec -it digital-calendar-db psql ...`
3. Use Swagger UI at `/docs`
4. Use ReDoc at `/redoc`
5. Add print statements or logging

### Database Debug
```bash
# Connect to database
docker exec -it digital-calendar-db psql -U digitalcalendar -d digitalcalendar

# View schema
\dt
\d tasks

# Check data
SELECT * FROM tasks;
SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 10;
```

## Deployment Checklist

- [ ] Set strong database password
- [ ] Configure CORS_ORIGINS for production domain
- [ ] Update REACT_APP_API_URL for production
- [ ] Enable HTTPS via Caddy
- [ ] Set up database backups
- [ ] Monitor logs and errors
- [ ] Test Tailscale connectivity from Raspberry Pi
- [ ] Test all features on actual 15" screen
- [ ] Configure Kiosk mode on Raspberry Pi
- [ ] Test offline/cache behavior

---

**Last Updated**: 2024
**Phase**: 1 (Core functionality with polling)
