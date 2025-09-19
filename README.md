# Homework App

A responsive web application for managing school schedules, classes, and homework assignments.

## Features

- **Editable 5-day schedule**: 6 classes per day with 30-minute reading/free periods
- **Class management**: Add/edit classes with name, teacher, year, and optional half-group
- **Homework tracking**: Input homework per class and date, auto-linked to schedule
- **Google Calendar integration**: Sync with Google Calendar
- **Responsive design**: Works on both mobile and desktop

## Tech Stack

- **Frontend**: React with TailwindCSS
- **Backend**: Python FastAPI
- **Database**: SQLite
- **Calendar Integration**: Google Calendar API

## Project Structure

```
homework-app/
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── models/    # Database models
│   │   ├── routes/    # API endpoints
│   │   └── main.py    # FastAPI app
│   ├── requirements.txt
│   └── database.db
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.js
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Setup and Installation

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## API Endpoints

- `GET /api/classes` - Get all classes
- `POST /api/classes` - Create a new class
- `PUT /api/classes/{id}` - Update a class
- `DELETE /api/classes/{id}` - Delete a class
- `GET /api/schedule` - Get weekly schedule
- `POST /api/schedule` - Update schedule
- `GET /api/homework` - Get homework assignments
- `POST /api/homework` - Create homework assignment
- `PUT /api/homework/{id}` - Update homework assignment
- `DELETE /api/homework/{id}` - Delete homework assignment

## License

MIT License - see LICENSE file for details.