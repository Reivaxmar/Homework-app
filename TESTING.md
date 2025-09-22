# Testing Guide for Homework Management App

This document provides comprehensive information about testing the Homework Management App, including setup, running tests, and integration with GitHub Actions.

## Table of Contents

- [Overview](#overview)
- [Backend Testing](#backend-testing)
- [Frontend Testing](#frontend-testing)
- [Running Tests Locally](#running-tests-locally)
- [Test Coverage](#test-coverage)
- [Continuous Integration](#continuous-integration)
- [Writing Tests](#writing-tests)
- [Mocking External Services](#mocking-external-services)
- [Troubleshooting](#troubleshooting)

## Overview

The Homework Management App uses a comprehensive testing strategy that includes:

- **Unit Tests**: Test individual components, functions, and classes in isolation
- **Integration Tests**: Test how different parts of the application work together
- **API Tests**: Test API endpoints and their responses
- **Component Tests**: Test React components and their behavior
- **End-to-End Tests**: Test complete user workflows

### Testing Stack

**Backend (Python/FastAPI)**:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-mock` - Mocking utilities
- `pytest-cov` - Coverage reporting
- `faker` - Test data generation
- `httpx` - HTTP client for API testing

**Frontend (React/JavaScript)**:
- `vitest` - Testing framework (Vite-native)
- `@testing-library/react` - React component testing utilities
- `@testing-library/jest-dom` - Custom Jest matchers
- `@testing-library/user-event` - User interaction simulation
- `jsdom` - DOM simulation

## Backend Testing

### Setup

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configuration**:
   - Tests use in-memory SQLite database for isolation
   - Configuration is handled by `pytest.ini`
   - Test fixtures are defined in `tests/conftest.py`

### Test Structure

```
backend/tests/
├── conftest.py              # Test configuration and fixtures
├── unit/                    # Unit tests
│   └── test_models.py       # Database model tests
├── api/                     # API endpoint tests
│   ├── test_auth.py         # Authentication endpoints
│   ├── test_classes.py      # Class management endpoints
│   ├── test_homework.py     # Homework management endpoints
│   └── test_calendar.py     # Calendar integration endpoints
└── integration/             # Integration tests
    └── test_workflows.py    # Complete user workflows
```

### Running Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test
pytest tests/unit/test_models.py::TestUserModel::test_create_user

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Backend Test Examples

**Model Testing**:
```python
def test_create_user(self, test_session):
    """Test creating a user."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-123"
    )
    test_session.add(user)
    test_session.commit()
    
    assert user.id is not None
    assert user.email == "test@example.com"
```

**API Testing**:
```python
@patch('app.auth.get_current_user')
def test_get_classes(self, mock_get_current_user, client, test_user):
    """Test getting user's classes."""
    mock_get_current_user.return_value = test_user
    
    response = client.get("/api/classes/")
    assert response.status_code == 200
```

## Frontend Testing

### Setup

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Configuration**:
   - Tests use `vitest` as the test runner
   - Configuration is in `vitest.config.js`
   - Test setup is in `src/test/setup.js`

### Test Structure

```
frontend/src/
├── test/
│   ├── setup.js             # Test configuration
│   └── utils.jsx            # Test utilities and helpers
└── __tests__/
    ├── components/          # Component tests
    ├── pages/               # Page component tests
    ├── contexts/            # Context tests
    └── services/            # Service tests
```

### Running Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run tests in watch mode
npm test -- --watch

# Run tests with UI
npm run test:ui

# Run specific test file
npm test Dashboard.test.jsx

# Run tests matching pattern
npm test -- --grep="auth"
```

### Frontend Test Examples

**Component Testing**:
```javascript
it('should render dashboard with user greeting', async () => {
  renderWithProviders(<Dashboard />, { initialUser: mockUser })
  
  expect(screen.getByText(`Welcome back, ${mockUser.full_name}!`)).toBeInTheDocument()
})
```

**Context Testing**:
```javascript
it('should handle Google sign in', async () => {
  const { result } = renderHook(() => useAuth(), { wrapper })
  
  await act(async () => {
    await result.current.signInWithGoogle()
  })
  
  expect(mockSupabaseClient.auth.signInWithOAuth).toHaveBeenCalled()
})
```

## Running Tests Locally

### Complete Test Suite

```bash
# Run all backend tests
cd backend && pytest

# Run all frontend tests
cd frontend && npm test

# Run both with coverage
cd backend && pytest --cov=app
cd frontend && npm run test:coverage
```

### Quick Test Commands

```bash
# Backend unit tests only
cd backend && pytest tests/unit/

# Frontend component tests only
cd frontend && npm test __tests__/components/

# API integration tests
cd backend && pytest tests/api/
```

## Test Coverage

### Coverage Reports

**Backend**:
- HTML report: `backend/htmlcov/index.html`
- Terminal output shows coverage percentages
- Minimum coverage threshold: 80%

**Frontend**:
- HTML report: `frontend/coverage/index.html`
- Coverage includes components, contexts, and services

### Coverage Commands

```bash
# Backend coverage
cd backend
pytest --cov=app --cov-report=html --cov-report=term

# Frontend coverage
cd frontend
npm run test:coverage
```

## Continuous Integration

### GitHub Actions Workflow

The project includes a GitHub Actions workflow (`.github/workflows/test.yml`) that:

1. **Runs on**:
   - Push to main branch
   - Pull requests
   - Manual trigger

2. **Backend Testing**:
   - Sets up Python environment
   - Installs dependencies
   - Runs pytest with coverage
   - Uploads coverage reports

3. **Frontend Testing**:
   - Sets up Node.js environment
   - Installs dependencies
   - Runs vitest with coverage
   - Uploads coverage reports

4. **External Service Mocking**:
   - All Google APIs are mocked
   - Supabase authentication is mocked
   - No real external calls are made

### Workflow Configuration

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: cd backend && pip install -r requirements.txt
      - run: cd backend && pytest --cov=app

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm test
```

## Writing Tests

### Best Practices

1. **Test Structure**:
   - Use descriptive test names
   - Follow Arrange-Act-Assert pattern
   - Keep tests focused and atomic

2. **Mocking**:
   - Mock external dependencies
   - Use fixtures for consistent test data
   - Don't mock what you're testing

3. **Assertions**:
   - Use specific assertions
   - Test both positive and negative cases
   - Verify error handling

### Test Templates

**Backend API Test**:
```python
@patch('app.auth.get_current_user')
def test_endpoint_success(self, mock_auth, client, test_user):
    """Test successful API call."""
    mock_auth.return_value = test_user
    
    response = client.get("/api/endpoint/")
    
    assert response.status_code == 200
    assert "expected_field" in response.json()
```

**Frontend Component Test**:
```javascript
it('should handle user interaction', async () => {
  renderWithProviders(<Component />, { initialUser: mockUser })
  
  const button = screen.getByRole('button', { name: /click me/i })
  await userEvent.click(button)
  
  expect(screen.getByText('Expected result')).toBeInTheDocument()
})
```

## Mocking External Services

### Google Services

**Backend** (Python):
```python
@patch('app.services.google_calendar.GoogleCalendarService')
def test_calendar_sync(self, mock_service):
    mock_service.return_value.create_event.return_value = "event_id"
    # Test logic here
```

**Frontend** (JavaScript):
```javascript
vi.mock('@supabase/supabase-js', () => ({
  createClient: vi.fn(() => mockSupabaseClient)
}))
```

### Database Mocking

- Backend tests use in-memory SQLite
- Each test gets a fresh database session
- Test data is created using factories

### API Mocking

- Frontend tests mock axios requests
- Backend tests use TestClient
- Responses are controlled and predictable

## Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   # Backend
   cd backend && python -m pytest

   # Frontend - ensure correct test setup
   cd frontend && npm test -- --no-coverage
   ```

2. **Database Issues**:
   - Tests use isolated in-memory database
   - Check fixture dependencies in `conftest.py`

3. **Async Test Issues**:
   ```python
   # Backend - use pytest-asyncio
   @pytest.mark.asyncio
   async def test_async_function():
       pass
   ```

4. **Mock Issues**:
   - Clear mocks between tests
   - Verify mock setup in `beforeEach`

### Debug Tips

1. **Verbose Output**:
   ```bash
   pytest -v -s  # Backend
   npm test -- --reporter=verbose  # Frontend
   ```

2. **Single Test**:
   ```bash
   pytest tests/unit/test_models.py::TestUserModel::test_create_user
   npm test -- Dashboard.test.jsx
   ```

3. **Coverage Details**:
   ```bash
   pytest --cov=app --cov-report=term-missing
   ```

## Environment Variables

### Test Environment

The tests use these environment variables:

```bash
# Backend (.env.test)
DATABASE_URL=sqlite:///./test.db
JWT_SECRET_KEY=test-secret-key
GOOGLE_CLIENT_ID=test-client-id
GOOGLE_CLIENT_SECRET=test-client-secret

# Frontend (test setup)
VITE_SUPABASE_URL=https://test-supabase-url.supabase.co
VITE_SUPABASE_ANON_KEY=test-anon-key
```

### CI/CD Environment

GitHub Actions automatically sets up test environments with appropriate mocking for all external services.

---

## Contributing

When adding new features:

1. Write tests for new functionality
2. Ensure all existing tests pass
3. Maintain or improve test coverage
4. Update this documentation if needed
5. Mock any new external service integrations

For questions about testing, please refer to the project's issue tracker or documentation.