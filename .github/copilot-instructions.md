# Homework Management App

A comprehensive web application for managing school schedules and homework assignments built with React (frontend) and FastAPI (Python backend).

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Prerequisites and Setup
- **Python 3.8+**: Already available, tested with Python 3.12.3
- **Node.js 16+**: Already available, tested with Node.js v20.19.5
- **npm**: Already available, tested with npm 10.8.2

### Bootstrap and Development Setup

**ALWAYS** follow these exact steps in order:

1. **Backend Setup**:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your credentials (see Authentication Setup below)
   pip install -r requirements.txt
   python run.py
   ```
   - Dependencies install takes ~30 seconds. NEVER CANCEL.
   - Server starts in ~5 seconds and runs on `http://localhost:8000`
   - Health check: `http://localhost:8000/health`
   - API docs: `http://localhost:8000/docs`

2. **Frontend Setup**:
   ```bash
   cd frontend
   cp .env.example .env
   # Edit .env with your Supabase credentials
   npm install
   npm run dev
   ```
   - Dependencies install takes ~20 seconds. NEVER CANCEL.
   - Vite dev server starts in ~3 seconds on `http://localhost:3000`

3. **Build Process**:
   ```bash
   # Frontend build - takes ~5 seconds. Set timeout to 30+ seconds.
   cd frontend && npm run build
   ```
   - **NEVER CANCEL** build commands - they complete quickly but set adequate timeout
   - Build artifacts are created in `frontend/dist/`

### Authentication Setup Requirements

**CRITICAL**: The application requires proper authentication setup to function. Without it, you'll see a blank white screen.

**For Development/Testing**:
```bash
# Backend .env (minimum working config)
DATABASE_URL=sqlite:///./homework_app.db
SUPABASE_URL=https://test-project.supabase.co
SUPABASE_ANON_KEY=test-anon-key
SUPABASE_SERVICE_ROLE_KEY=test-service-role-key
JWT_SECRET_KEY=development-secret-key-12345
GOOGLE_CLIENT_ID=test-google-client-id
GOOGLE_CLIENT_SECRET=test-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback

# Frontend .env (minimum working config)
VITE_SUPABASE_URL=https://test-project.supabase.co
VITE_SUPABASE_ANON_KEY=test-anon-key
```

**For Production**: Follow the detailed [Authentication Setup Guide](docs/AUTHENTICATION_SETUP.md) to configure real Supabase and Google OAuth credentials.

### Testing Authentication

**ALWAYS** run the authentication test after backend setup:
```bash
cd backend && python test_auth.py
```
This validates JWT token generation and authentication endpoints work correctly.

## Validation Scenarios

**MANDATORY**: After making any changes, ALWAYS run through these validation steps:

### 1. Backend Validation
```bash
cd backend
python run.py &
sleep 5
curl http://localhost:8000/health  # Should return {"status": "healthy"}
python test_auth.py               # Should show all tests passing
```

### 2. Frontend Validation  
```bash
cd frontend
npm run dev &
sleep 5
curl -I http://localhost:3000     # Should return HTTP/1.1 200 OK
```

### 3. Application Functionality Test
- Navigate to `http://localhost:3000`
- **EXPECTED**: Login page with "Welcome to Homework Management" title
- **EXPECTED**: Google Sign-in button and feature list
- **NOT EXPECTED**: Blank white page (indicates auth config issues)

### 4. Build Validation
```bash
cd frontend && npm run build      # Should complete in ~5 seconds
```

## Common Tasks and Locations

### Key Directories
```
homework-app/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy database models
│   │   │   ├── classes.py  # Class/subject models
│   │   │   ├── homework.py # Homework assignment models
│   │   │   ├── schedule.py # Schedule and time slot models
│   │   │   └── user.py     # User authentication models
│   │   ├── routers/        # FastAPI route handlers
│   │   │   ├── auth.py     # Authentication endpoints
│   │   │   ├── classes.py  # Class management APIs
│   │   │   ├── homework.py # Homework CRUD APIs  
│   │   │   ├── calendar.py # Google Calendar integration
│   │   │   └── dashboard.py# Dashboard statistics
│   │   ├── services/       # Business logic services
│   │   ├── config.py       # Configuration management
│   │   └── main.py         # FastAPI application entry
│   ├── requirements.txt    # Python dependencies
│   ├── run.py             # Development server startup
│   └── test_auth.py       # Authentication test script
├── frontend/              # React Vite frontend
│   ├── src/
│   │   ├── components/    # Reusable React components
│   │   ├── pages/        # Main application pages
│   │   │   ├── Dashboard.jsx  # Main dashboard view
│   │   │   ├── Classes.jsx    # Class management page
│   │   │   ├── Schedule.jsx   # Weekly schedule grid
│   │   │   └── Homework.jsx   # Homework tracking page
│   │   ├── services/     # API client services
│   │   └── App.jsx       # Main React application
│   ├── package.json      # Node.js dependencies and scripts
│   └── vite.config.js    # Vite build configuration
└── docs/                 # Documentation
    └── AUTHENTICATION_SETUP.md  # Detailed auth setup guide
```

### Critical Files to Monitor
- **After changing authentication**: Always check `backend/app/auth.py` and run `backend/test_auth.py`
- **After changing API contracts**: Check corresponding files in `backend/app/routers/` and `frontend/src/services/`  
- **After changing database models**: Check `backend/app/models/` and restart backend server
- **After changing UI components**: Check `frontend/src/components/` and pages in `frontend/src/pages/`

## Troubleshooting

### Build/Startup Issues
- **Backend fails to start**: Check Python dependencies with `pip install -r requirements.txt`
- **Frontend fails to start**: Check Node dependencies with `npm install`
- **Blank white page**: Environment variables not configured - see Authentication Setup above
- **Database errors**: Delete `homework_app.db` file and restart backend to recreate schema

### Linting Issues  
- **ESLint configuration missing**: `npm run lint` fails because no ESLint config exists
- **This is normal** - the project doesn't have ESLint configured yet
- **DO NOT** fix this unless specifically asked - it's not a critical error

### Authentication Issues
- **JWT warnings**: The default JWT secret triggers a security warning - this is expected in development
- **API authentication failures**: Run `python test_auth.py` to verify JWT setup
- **Google OAuth errors**: Need real Supabase/Google credentials for full authentication flow

## Technology Stack Details

### Backend (FastAPI)
- **Framework**: FastAPI with Uvicorn ASGI server
- **Database**: SQLite with SQLAlchemy ORM  
- **Authentication**: JWT tokens + Supabase + Google OAuth
- **APIs**: Google Calendar integration for homework sync
- **Validation**: Pydantic models for request/response schemas

### Frontend (React + Vite)
- **Framework**: React 18 with Vite build tool
- **Styling**: TailwindCSS utility framework
- **Routing**: React Router for client-side navigation
- **HTTP**: Axios for API communication
- **Forms**: React Hook Form for form handling
- **UI**: Lucide React icons, React Hot Toast notifications

### Development Workflow
- **Backend changes**: Server auto-reloads with file changes
- **Frontend changes**: Vite provides instant HMR (Hot Module Reload)
- **Database changes**: Restart backend to apply SQLAlchemy schema changes
- **API changes**: Check both backend routes and frontend service calls

## Performance Expectations

- **Backend dependencies install**: ~30 seconds
- **Frontend dependencies install**: ~20 seconds  
- **Backend server startup**: ~5 seconds
- **Frontend dev server startup**: ~3 seconds
- **Frontend build**: ~5 seconds
- **Authentication test**: ~2 seconds

**NEVER CANCEL** any of these operations. Use timeouts of 60+ seconds for safety.

## API Endpoints Reference

### Quick API Test Commands
```bash
# Health check
curl http://localhost:8000/health

# API documentation  
curl http://localhost:8000/docs

# Authentication test
curl http://localhost:8000/api/auth/me  # Should return 401 without token
```

### Main Endpoints
- `GET /health` - Health check
- `GET /docs` - OpenAPI documentation
- `POST /api/auth/google/callback` - Google OAuth callback
- `GET /api/auth/me` - Current user profile  
- `GET /api/classes/` - List classes
- `GET /api/homework/` - List homework assignments
- `GET /api/schedules/active/{year}` - Get active schedule
- `GET /api/dashboard/summary` - Dashboard statistics

ALWAYS verify API changes with both backend tests and frontend integration.