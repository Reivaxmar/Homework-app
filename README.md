# Homework Management App

A comprehensive web application for managing school schedules and homework assignments. Built with React, TailwindCSS, and FastAPI.

## Features

### 🔐 Authentication & Security
- **Supabase Authentication** - Secure user management with Supabase
- **Google OAuth Integration** - Sign in with your Google account
- **Google Calendar Sync** - Automatically sync homework with Google Calendar
- **JWT Token Management** - Secure API access with JSON Web Tokens
- **Profile Management** - Update user profile and preferences

### 📚 Class Management
- Create and manage school classes with teacher information
- Color-coded classes for easy identification
- Optional half-group support (A, B groups)
- Year-based organization

### 📅 Schedule Management
- Interactive 5-day weekly schedule grid
- 6 periods per day with customizable time slots
- Editable schedule slots - click to assign classes
- Built-in reading/free time periods
- Real-time schedule updates

### 📝 Homework Tracking
- Create and manage homework assignments
- Link homework to specific classes
- Priority levels (Low, Medium, High)
- Due date tracking with overdue detection
- Status management (Pending, In Progress, Completed)
- Filter homework by status and due dates

### 📊 Dashboard
- Overview statistics for classes and homework
- Quick access to pending, due today, and overdue assignments
- Weekly completion tracking
- Visual indicators for urgent tasks

### 📱 responsive Design
- Mobile-first responsive design
- Works seamlessly on desktop, tablet, and mobile devices
- Collapsible navigation for mobile

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Lightweight database
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Supabase** - Authentication backend
- **Google APIs** - Calendar and OAuth integration

### Frontend
- **React 18** - UI framework
- **TailwindCSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **React Hook Form** - Form handling
- **React Hot Toast** - Notifications
- **Lucide React** - Icon library
- **Vite** - Build tool
- **Supabase JS** - Authentication and real-time features

## Project Structure

```
homework-app/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Database models
│   │   │   ├── classes.py
│   │   │   ├── schedule.py
│   │   │   └── homework.py
│   │   ├── routers/        # API endpoints
│   │   │   ├── classes.py
│   │   │   ├── schedules.py
│   │   │   ├── homework.py
│   │   │   └── dashboard.py
│   │   ├── schemas.py      # Pydantic models
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   └── run.py
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   └── Layout.jsx
│   │   ├── pages/         # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Classes.jsx
│   │   │   ├── Schedule.jsx
│   │   │   └── Homework.jsx
│   │   ├── services/      # API services
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn
- Supabase account (https://supabase.com)
- Google Cloud Console project (for OAuth and Calendar API)

### Authentication Setup

⚠️ **Important**: Before running the application, you need to set up authentication. See the detailed [Authentication Setup Guide](docs/AUTHENTICATION_SETUP.md) for complete instructions.

Quick setup:
1. Create a Supabase project
2. Set up Google OAuth in Google Cloud Console
3. Configure environment variables (see `.env.example` files)
4. Enable Google provider in Supabase

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Supabase and Google OAuth credentials
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Start the development server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Create and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

3. Install dependencies:
```bash
npm install
```

4. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/login` - Simple login (legacy)
- `POST /api/auth/google/callback` - Handle Google OAuth callback
- `GET /api/auth/me` - Get current user information
- `PUT /api/auth/me` - Update current user information

### Calendar Integration
- `POST /api/calendar/sync` - Sync all homework with Google Calendar
- `POST /api/calendar/sync/{homework_id}` - Sync specific homework to calendar

### Classes
- `GET /api/classes/` - List all classes
- `POST /api/classes/` - Create a new class
- `GET /api/classes/{id}` - Get class by ID
- `PUT /api/classes/{id}` - Update class
- `DELETE /api/classes/{id}` - Delete class

### Schedules
- `GET /api/schedules/` - List all schedules
- `POST /api/schedules/` - Create a new schedule
- `GET /api/schedules/active/{year}` - Get active schedule for year
- `GET /api/schedules/{id}/slots` - Get schedule slots
- `POST /api/schedules/{id}/slots` - Create schedule slot
- `PUT /api/schedules/{id}/slots/{slot_id}` - Update schedule slot

### Homework
- `GET /api/homework/` - List homework (with filters)
- `POST /api/homework/` - Create homework
- `GET /api/homework/due-today` - Get homework due today
- `GET /api/homework/overdue` - Get overdue homework
- `PUT /api/homework/{id}/complete` - Mark as completed
- `PUT /api/homework/{id}/reopen` - Reopen homework

### Dashboard
- `GET /api/dashboard/summary` - Get dashboard statistics

## Features in Detail

### Schedule Management
- **5-Day Schedule**: Monday through Friday
- **6 Periods per Day**: Customizable time slots
- **Interactive Grid**: Click any slot to assign a class
- **Default Times**: 
  - Period 1: 08:00 - 08:50
  - Period 2: 09:00 - 09:50
  - Period 3: 10:10 - 11:00 (10-min break)
  - Period 4: 11:10 - 12:00
  - Period 5: 12:30 - 13:20 (30-min lunch break)
  - Period 6: 13:30 - 14:20 (Reading time by default)

### Homework Management
- **Priority System**: Visual priority indicators (Low/Medium/High)
- **Status Tracking**: Pending → In Progress → Completed
- **Smart Filtering**: Filter by status, due date, and class
- **Due Date Alerts**: Visual indicators for overdue and due today
- **Class Integration**: Automatically linked to class colors and info

### Dashboard Analytics
- **Real-time Stats**: Live updates of homework and class counts
- **Quick Overview**: Pending, due today, overdue, and completed counts
- **Visual Indicators**: Color-coded stats for quick assessment

## Future Enhancements

- 📧 **Email Notifications**: Automated reminders for due assignments
- 👥 **Multi-user Support**: Student and teacher accounts
- 📱 **PWA Support**: Offline functionality and app installation
- 🔔 **Push Notifications**: Browser notifications for deadlines
- 📈 **Analytics Dashboard**: Progress tracking and performance metrics
- 🎨 **Themes**: Dark mode and custom color themes
- 📤 **Export Features**: PDF reports and calendar exports
- 🔄 **Real-time Sync**: Live updates across devices
- 📊 **Advanced Calendar Views**: Month/week views and recurring events

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing

This application includes comprehensive testing coverage:

### Test Suites

- **Backend Tests**: 89 tests with 75% coverage
  - Model tests (User, Class, Homework, Schedule)
  - API route tests (Authentication, Classes, Homework)
  - Service tests (Google Calendar integration)
  - Integration tests (Full workflows)

- **Frontend Tests**: Component and page tests
  - React component testing with React Testing Library
  - Mock implementations for external dependencies
  - User interaction and accessibility testing

### Running Tests

**Backend:**
```bash
cd backend
python -m pytest --cov=app --cov-report=html
```

**Frontend:**
```bash
cd frontend
npm test
```

**With Coverage:**
```bash
cd backend && python -m pytest --cov=app --cov-report=term-missing
cd frontend && npm run test:coverage
```

### Continuous Integration

GitHub Actions automatically run all tests on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

The CI pipeline includes:
- Backend tests with PostgreSQL integration
- Frontend tests with Node.js
- Code linting (Python: flake8, black, isort | JavaScript: ESLint)
- Coverage reporting

### Testing Documentation

See [Testing Guide](docs/TESTING_GUIDE.md) for:
- Detailed testing instructions
- Writing new tests
- CI/CD integration
- Best practices and troubleshooting

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Screenshots

### Dashboard
Overview of classes and homework with real-time statistics.

### Class Management
Manage your school classes with teacher information and color coding.

### Schedule View
Interactive weekly schedule grid for easy class assignment.

### Homework Tracking
Comprehensive homework management with filtering and status tracking.

### Mobile Responsive
Fully responsive design that works seamlessly on all devices.