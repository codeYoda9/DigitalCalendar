# Quick Reference - Digital Calendar Phase 1

## 🚀 Quick Start

```bash
# Navigate to project
cd /home/shreyasshivalkar/Projects/DigitalCalendar

# Build and start
docker compose build
docker compose up -d

# Verify all running
docker compose ps

# Access dashboard
# Main dashboard: http://localhost:3000
# Workflows page: http://localhost:3002
# Raspberry Pi: http://[NUC_TAILSCALE_IP]:3000 or :3002
# API Docs: http://localhost:8000/docs
```

## 📋 Key Commands

| Command | Purpose |
|---------|---------|
| `docker compose build` | Build all images |
| `docker compose up -d` | Start all services |
| `docker compose down` | Stop all services |
| `docker compose logs -f backend` | View backend logs |
| `docker compose ps` | Check status |
| `docker exec -it digital-calendar-db psql -U digitalcalendar -d digitalcalendar` | Database CLI |

## 🔧 Development

### Backend
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## 📊 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/tasks` | GET | List tasks |
| `/api/tasks` | POST | Create task |
| `/api/groceries` | GET | List groceries |
| `/api/meals/week` | GET | Get meal plan |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |

## 🗂️ Project Structure

```
backend/          → FastAPI application (Python)
frontend/         → React dashboard (JavaScript)
database/         → SQL schema
docker-compose.yaml → Orchestration
```

## 🔐 Default Credentials

| Service | User | Password | Database |
|---------|------|----------|----------|
| PostgreSQL | digitalcalendar | digitalcalendar | digitalcalendar |

## 🎯 Features

- ✅ 4-panel touch-first dashboard
- ✅ Shared tasks todo list
- ✅ Shared grocery shopping list
- ✅ Weekly meal planning
- ✅ 10-second polling
- ✅ Offline support with caching
- ✅ Tailscale network access
- ✅ Docker Compose deployment

## 📱 Responsive Design

- **Desktop (>1024px)**: 2×2 grid
- **Mobile (<1024px)**: Single column
- **15-inch Portrait**: Optimized layout
- **Touch-optimized**: Large buttons and text

## 🔗 URLs

| Service | URL |
|---------|-----|
| Main Dashboard | http://localhost:3000 |
| Workflows Page | http://localhost:3002 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Database | localhost:5432 |

## 🚨 Troubleshooting

### Backend won't start
```bash
docker logs digital-calendar-backend
```

### Database won't connect
```bash
docker exec digital-calendar-db pg_isready -U digitalcalendar
```

### Frontend shows offline
Check CORS in backend environment variables

### Port already in use
Change port in `docker-compose.yaml`

## 📚 Documentation

- `README.md` - Main documentation
- `DEVELOPMENT.md` - Developer guide
- `Phase1Implementation.md` - Original specification
- `QUICK_REFERENCE.md` - This file

## 🎮 Next Steps

1. Build and start: `docker compose build && docker compose up -d`
2. Verify services: `docker compose ps`
3. Access dashboard: http://localhost:3000
4. Access Workflows page: http://localhost:3002
5. Check API docs: http://localhost:8000/docs
6. For Raspberry Pi: Configure Kiosk mode (see README.md)

---

**Phase**: 1 (Core MVP)
**Backend**: FastAPI + PostgreSQL
**Frontend**: React with polling
**Deployment**: Docker Compose
**Network**: Tailscale
