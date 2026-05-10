# Digital Calendar - Phase 1

A self-hosted household dashboard for a 15-inch portrait touchscreen. Perfect for mounting on a fridge and accessible via Tailscale network.

## Features (Phase 1)

- **📅 Calendar**: Read-only Google Calendar display (mock events in Phase 1)
- **✓ Tasks**: Shared todo list with add/mark complete/delete
- **🛒 Grocery**: Shared shopping list with checked items
- **🍽️ Meals**: Weekly meal planning with breakfast/lunch/dinner per day
- **📱 Touch-first UI**: Large buttons and text, readable from ~8 feet away
- **📡 Polling**: Frontend polls backend every 10 seconds
- **🔒 Tailscale**: Access via Tailscale network only (no public internet exposure)

## Architecture

```
Raspberry Pi 5 (Display)
  └─ Browser (Kiosk Mode)
      └─ Frontend (React) - 3000
          └─ Backend API (FastAPI) - 8000
              └─ PostgreSQL - 5432
```

All services run on an Intel NUC via Docker Compose, accessed securely through Tailscale.

## Prerequisites

- Docker and Docker Compose (20.10+)
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- Internet connection for initial docker image pulls
- Tailscale account and installed on both NUC and Raspberry Pi

## Quick Start

### 1. Clone and Navigate

```bash
cd /home/shreyasshivalkar/Projects/DigitalCalendar
```

### 2. Build and Start Services

```bash
docker compose build
docker compose up -d
```

### 3. Verify Services

Check that all services are running:

```bash
docker compose ps
```

Expected output:
```
CONTAINER ID   IMAGE                          PORTS
abc123...      digital-calendar-db            5432
def456...      digital-calendar-backend       8000
ghi789...      digital-calendar-frontend      3000
```

### 4. Access Dashboard

- **Local Desktop**: http://localhost:3000
- **From Raspberry Pi**: Use the Tailscale IP of the NUC, e.g., http://100.x.x.x:3000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

### 5. Check Backend Health

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": "healthy"
}
```

## Configuration

### Environment Variables

Create a `.env` file in the project root if you need to override defaults:

```bash
# Database
DATABASE_URL=postgresql://digitalcalendar:digitalcalendar@db:5432/digitalcalendar

# Backend
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://100.104.202.19:3000
PORT=8000
ENV=production

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

## API Endpoints

### Tasks
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create task
- `PATCH /api/tasks/{id}` - Update task (mark done, edit text)
- `DELETE /api/tasks/{id}` - Delete task

### Groceries
- `GET /api/groceries` - List all items
- `POST /api/groceries` - Create item
- `PATCH /api/groceries/{id}` - Update item (mark checked, edit)
- `DELETE /api/groceries/{id}` - Delete item

### Meals
- `GET /api/meals/week?date_param=2024-01-01` - Get weekly meal plan
- `PUT /api/meals/week` - Update entire week

### Calendar
- `GET /api/calendar/events?date_param=2024-01-01` - Get events for date onwards

### Health & Info
- `GET /health` - Health check
- `GET /` - API info

See full API docs at: http://localhost:8000/docs

## Database Schema

### Tasks Table
```sql
id          SERIAL PRIMARY KEY
text        VARCHAR(255) NOT NULL
done        BOOLEAN DEFAULT FALSE
created_at  TIMESTAMP
updated_at  TIMESTAMP
```

### Groceries Table
```sql
id          SERIAL PRIMARY KEY
item        VARCHAR(255) NOT NULL
checked     BOOLEAN DEFAULT FALSE
created_at  TIMESTAMP
updated_at  TIMESTAMP
```

### Meals Table
```sql
id              SERIAL PRIMARY KEY
week_start_date DATE NOT NULL
day_of_week     VARCHAR(10) NOT NULL
breakfast       VARCHAR(255)
lunch           VARCHAR(255)
dinner          VARCHAR(255)
updated_at      TIMESTAMP
```

### Audit Log Table
```sql
id          SERIAL PRIMARY KEY
entity_type VARCHAR(50) NOT NULL
entity_id   INTEGER
action      VARCHAR(50) NOT NULL
payload_json JSONB
created_at  TIMESTAMP
```

## Development

### Backend Development

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start FastAPI server (with auto-reload):
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. The API will be available at http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Frontend Development

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm start
   ```

4. The dashboard will open at http://localhost:3000 with hot reload

5. Build for production:
   ```bash
   npm run build
   ```

### Database Development

1. Access PostgreSQL directly:
   ```bash
   docker exec -it digital-calendar-db psql -U digitalcalendar -d digitalcalendar
   ```

2. Common commands:
   ```sql
   \dt                    -- List tables
   SELECT * FROM tasks;   -- View tasks
   SELECT * FROM groceries; -- View groceries
   ```

## Raspberry Pi Kiosk Mode Setup

### Prerequisites
- Raspberry Pi 5 with Tailscale installed and connected
- Display connected via HDMI

### Steps

1. **Update and Install Browser**
   ```bash
   sudo apt update
   sudo apt install -y chromium-browser
   ```

2. **Install Kiosk Mode Manager**
   ```bash
   sudo apt install -y unclutter x11-xserver-utils
   ```

3. **Create Startup Script** (`~/start-kiosk.sh`):
   ```bash
   #!/bin/bash
   export DISPLAY=:0
   xset s off -dpms
   unclutter -idle 0 &
   chromium-browser \
     --kiosk \
     --no-first-run \
     --no-default-browser-check \
     --disable-popup-blocking \
     --disable-prompt-on-repost \
     --disable-session-crashed-bubble \
     http://[NUC_TAILSCALE_IP]:3000
   ```

4. **Make Executable**
   ```bash
   chmod +x ~/start-kiosk.sh
   ```

5. **Add to Autostart** (crontab):
   ```bash
   crontab -e
   # Add: @reboot /home/pi/start-kiosk.sh
   ```

6. **Configure Screen Rotation** (if portrait):
   Edit `/boot/config.txt`:
   ```
   display_rotate=2  # 90 degree rotation
   ```

## Troubleshooting

### Database Connection Failed
```
Error: could not connect to server: Connection refused
```

Check if database is running:
```bash
docker exec digital-calendar-db pg_isready -U digitalcalendar
```

If not running, check logs:
```bash
docker logs digital-calendar-db
```

### Backend Not Starting
```
docker logs digital-calendar-backend
```

Common issues:
- Database not ready: Backend tries to connect before DB is healthy
- Port 8000 already in use: Change PORT in .env or docker-compose.yaml

### Frontend Shows "Offline" Banner
1. Check backend is running: `curl http://localhost:8000/health`
2. Check CORS configuration in backend environment
3. Check browser console for network errors (F12)

### No Events in Calendar
Phase 1 shows mock events. To integrate Google Calendar API:
- See TODO comments in `backend/routes_calendar.py`
- Requires Google Calendar credentials
- Will be implemented in Phase 2

## Polling Behavior

The frontend polls the backend every **10 seconds**:
- Task list
- Grocery list
- Meal plan
- Calendar events

If the backend becomes unreachable:
- Shows "Offline: showing cached data" banner
- Continues showing last successfully loaded data from localStorage
- Automatically reconnects when backend is available again

## Offline Support

Data is cached in browser localStorage:
- Last successful API responses are cached
- If backend is unreachable, cached data is displayed
- No silent data loss—user is informed of offline status

## Phase 2 Roadmap

- Google Calendar API integration
- WebSocket support (replace polling)
- User authentication/multiuser accounts
- Mealie recipe integration
- Alexa voice integration
- Advanced automation and scheduling
- OCR for recipe photos
- Mobile app native version

## Deployment to Production

### 1. Security Configuration
- Set strong PostgreSQL password
- Configure CORS_ORIGINS for production domain
- Use environment-specific .env files
- Ensure Tailscale is properly configured

### 2. Data Backup
```bash
# Backup database
docker exec digital-calendar-db pg_dump -U digitalcalendar digitalcalendar > backup.sql

# Restore from backup
docker exec -i digital-calendar-db psql -U digitalcalendar digitalcalendar < backup.sql
```

### 3. Monitoring Logs
```bash
# View all service logs
docker compose logs -f

# View specific service
docker compose logs -f backend
```

### 4. Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend
```

## Contributing

Contributions are welcome! Please:
1. Create a feature branch
2. Keep changes focused and simple
3. Test locally with `docker compose`
4. Ensure backward compatibility

## License

This project is provided as-is for personal household use.

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review API documentation at `/docs`
3. Check container logs: `docker compose logs [service_name]`
4. Verify all services are healthy: `docker compose ps`

---

**Note**: This is Phase 1 implementation focusing on core features with polling and basic mock data. More advanced features (Google Calendar, WebSockets, user auth) are planned for later phases.
