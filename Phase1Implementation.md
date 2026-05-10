Implement Phase 1 of my Digital Calendar project.

Goal:
Build a self-hosted household dashboard for a fridge-mounted 15-inch portrait touchscreen.

Phase 1 scope only:
- Tasks: simple shared todo list.
- Grocery: simple shared shopping list.
- Meals: manual weekly meal plan text.
- Calendar: read-only Google Calendar display.
- UI: static 4-panel dashboard.
- Sync: polling only.
- No OCR.
- No Alexa.
- No advanced automation.
- No Mealie integration yet.

Architecture:
- Docker Compose based deployment.
- Backend API service.
- PostgreSQL database.
- Web frontend.
- All services hosted on an Intel NUC.
- Raspberry Pi 5 display accesses the frontend URL in browser kiosk mode.
- Access is handled by Tailscale network only. Do not implement public internet exposure.

Preferred stack:
- Backend: FastAPI with Python.
- Frontend: React.
- Database: PostgreSQL.
- Containerization: Docker Compose.

Core frontend layout:
Portrait 15-inch screen dashboard.

Panels:
1. Today / Calendar
   - Show today’s date.
   - Show upcoming Google Calendar events.
   - Read-only display.

2. Tasks
   - Show active tasks.
   - Add task.
   - Mark task complete.
   - Delete task.

3. Grocery
   - Show grocery items.
   - Add item.
   - Mark item checked.
   - Delete item.

4. Meal Plan
   - Weekly grid.
   - Days: Monday through Sunday.
   - Fields per day: breakfast, lunch, dinner.
   - Editable text fields.

Interaction rules:
- Touch-first.
- Large buttons.
- Large text.
- Common actions should take 1–2 taps.
- UI must be readable from about 8 feet away.
- Avoid clutter beyond the four panels.

Backend requirements:
Create REST API endpoints for:

Tasks:
- GET /api/tasks
- POST /api/tasks
- PATCH /api/tasks/{id}
- DELETE /api/tasks/{id}

Groceries:
- GET /api/groceries
- POST /api/groceries
- PATCH /api/groceries/{id}
- DELETE /api/groceries/{id}

Meals:
- GET /api/meals/week
- PUT /api/meals/week

Calendar:
- GET /api/calendar/events
- For now, create a placeholder calendar provider interface.
- Add clear TODO comments for Google Calendar API integration.
- Return mock events if Google credentials are not configured.

Database requirements:
Use PostgreSQL tables:

tasks:
- id
- text
- done
- created_at
- updated_at

groceries:
- id
- item
- checked
- created_at
- updated_at

meals:
- id
- week_start_date
- day_of_week
- breakfast
- lunch
- dinner
- updated_at

audit_log:
- id
- entity_type
- entity_id
- action
- payload_json
- created_at

Persistence:
- Use Docker volumes for PostgreSQL data.
- Do not store important state only in the frontend.

Polling:
- Frontend polls backend every 10 seconds.
- No WebSocket for Phase 1.

Offline/failure behavior:
- If backend is unreachable, show an “Offline: showing last loaded data” banner.
- Frontend may cache last successful data in localStorage.
- Do not allow silent data loss.

Docker Compose:
Include:
- postgres
- backend
- frontend

Developer setup:
- Provide README.md with:
  - prerequisites
  - docker compose build
  - docker compose up
  - environment variables
  - database migration/init instructions
  - kiosk-mode note for Raspberry Pi browser

Code quality:
- Keep implementation simple.
- Use clear folder structure.
- Add type hints in Python.
- Add basic validation.
- Add basic error handling.
- Do not add unnecessary frameworks.
- Do not build Phase 2 features.

Deliverables:
- Working Docker Compose project.
- Backend API.
- Frontend dashboard.
- PostgreSQL schema/init.
- README.md.