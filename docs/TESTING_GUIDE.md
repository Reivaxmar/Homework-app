# Testing Guide

This guide explains how to run tests for the Homework Management App and how the automated testing is integrated with GitHub Actions.

## Overview

The application has comprehensive test coverage across multiple layers:

- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test API endpoints and database interactions  
- **Component Tests**: Test React component behavior and rendering
- **End-to-End Tests**: Test complete user workflows
- **Authentication Tests**: Test OAuth flow and JWT handling

## Test Structure

### Backend Tests (Python/FastAPI)

Located in `backend/tests/` with the following structure:

```
backend/tests/
├── conftest.py              # Test configuration and fixtures
├── test_models/             # Database model tests
│   ├── test_user.py
│   ├── test_classes.py
│   ├── test_homework.py
│   └── test_schedule.py
├── test_routers/            # API endpoint tests
│   ├── test_auth_router.py
│   ├── test_classes_router.py
│   ├── test_homework_router.py
│   ├── test_schedules_router.py
│   ├── test_dashboard_router.py
│   └── test_calendar_router.py
├── test_services/           # Service layer tests
│   └── test_google_calendar.py
└── test_integration/        # Integration tests
    └── test_full_workflow.py
```

### Frontend Tests (React/Vitest)

Located in `frontend/src/test/` with the following structure:

```
frontend/src/test/
├── setup.js                 # Test configuration
├── __mocks__/               # Mock implementations
│   └── AuthContextMock.jsx
└── __tests__/               # Test files
    ├── components/
    │   ├── Login.test.jsx
    │   ├── Layout.test.jsx
    │   └── ProtectedRoute.test.jsx
    ├── pages/
    │   ├── Dashboard.test.jsx
    │   ├── Classes.test.jsx
    │   ├── Schedule.test.jsx
    │   └── Homework.test.jsx
    ├── contexts/
    │   └── AuthContext.test.jsx
    └── services/
        └── api.test.js
```

## Running Tests Locally

### Backend Tests

```bash
# Navigate to backend directory
cd backend

# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio pytest-cov httpx

# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_models/test_user.py

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run tests in verbose mode
python -m pytest -v

# Run tests and stop on first failure
python -m pytest -x
```

### Frontend Tests

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not already installed)
npm install

# Run all tests
npm test

# Run tests in watch mode (for development)
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run specific test file
npx vitest src/test/__tests__/components/Login.test.jsx
```

### Integration Tests

```bash
# From the root directory, start both backend and frontend
# Terminal 1:
cd backend
python run.py

# Terminal 2:
cd frontend
npm run dev

# Terminal 3: Run integration tests
cd backend
python -m pytest tests/test_integration/ -v
```

## Test Configuration

### Backend Test Configuration

Tests use an in-memory SQLite database and mock external services:

- **Database**: Temporary SQLite database created for each test
- **Authentication**: Mock JWT tokens and Supabase integration
- **Google Calendar**: Mock Google API responses
- **Environment**: Isolated test environment variables

### Frontend Test Configuration

Tests use Vitest with React Testing Library:

- **Environment**: jsdom for DOM simulation
- **Mocking**: Vi.js for mocking modules and functions
- **Components**: React Testing Library for component testing
- **Routing**: Mock React Router for navigation testing

## Automated Testing with GitHub Actions

### Workflow Overview

The repository includes a comprehensive GitHub Actions workflow (`.github/workflows/test.yml`) that runs on:

- **Push** to `main` or `develop` branches
- **Pull Requests** to `main` or `develop` branches

### Workflow Jobs

1. **Backend Tests**
   - Sets up Python 3.12
   - Installs dependencies with caching
   - Runs pytest with coverage
   - Uploads coverage to Codecov

2. **Frontend Tests**
   - Sets up Node.js 18
   - Installs npm dependencies with caching
   - Runs Vitest with coverage
   - Uploads coverage to Codecov

3. **Integration Tests**
   - Runs after backend and frontend tests pass
   - Sets up PostgreSQL service
   - Tests full application workflows
   - Uses test environment variables

4. **Lint**
   - Runs Python linting (flake8, black, isort)
   - Runs JavaScript/React linting (ESLint)

### Setting Up CI/CD

1. **Repository Secrets** (if needed):
   ```
   CODECOV_TOKEN=your-codecov-token-here
   ```

2. **Branch Protection Rules**:
   - Require status checks to pass before merging
   - Require branches to be up to date before merging
   - Require review before merging

### Coverage Reports

Coverage reports are generated for both backend and frontend:

- **Backend**: Generated with pytest-cov
- **Frontend**: Generated with Vitest coverage
- **Reports**: Uploaded to Codecov for tracking

## Writing New Tests

### Backend Test Example

```python
def test_create_homework(db, authenticated_user):
    """Test creating a new homework assignment."""
    client, token_data = authenticated_user
    
    homework_data = {
        "title": "Math Assignment",
        "description": "Complete exercises 1-10",
        "due_date": "2024-01-15",
        "class_id": 1,
        "priority": "medium"
    }
    
    response = client.post("/api/homework/", json=homework_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Math Assignment"
    assert data["priority"] == "medium"
```

### Frontend Test Example

```javascript
import { render, screen, fireEvent } from '@testing-library/react'
import { vi } from 'vitest'
import MyComponent from '../MyComponent'

// Mock dependencies
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({ user: { name: 'Test User' } })
}))

test('renders component correctly', () => {
  render(<MyComponent />)
  
  expect(screen.getByText('Test User')).toBeInTheDocument()
  
  const button = screen.getByRole('button', { name: /click me/i })
  fireEvent.click(button)
  
  expect(screen.getByText('Button clicked!')).toBeInTheDocument()
})
```

## Test Data and Fixtures

### Backend Fixtures

The `conftest.py` file provides reusable fixtures:

- `db`: Fresh database session for each test
- `client`: FastAPI test client with database override
- `authenticated_user`: Client with valid JWT token
- `test_user_data`: Sample user data
- `test_class_data`: Sample class data
- `test_homework_data`: Sample homework data

### Frontend Mocks

The `__mocks__` directory contains mock implementations:

- `AuthContextMock.jsx`: Mock authentication context
- API service mocks for testing without backend

## Best Practices

### General Testing Principles

1. **Test Behavior, Not Implementation**: Focus on what the code does, not how
2. **Arrange, Act, Assert**: Structure tests clearly
3. **One Assertion Per Test**: Keep tests focused and specific
4. **Descriptive Test Names**: Make test purpose clear from the name
5. **Independent Tests**: Tests should not depend on each other

### Backend Testing

1. **Use Fixtures**: Leverage pytest fixtures for test data
2. **Mock External Services**: Don't make real API calls in tests
3. **Test Edge Cases**: Include error conditions and boundary cases
4. **Database Isolation**: Each test gets a fresh database

### Frontend Testing

1. **User-Centric Tests**: Test from the user's perspective
2. **Mock Dependencies**: Mock complex dependencies and external services
3. **Accessibility Testing**: Include accessibility assertions
4. **Component Isolation**: Test components in isolation when possible

## Troubleshooting Tests

### Common Backend Issues

1. **Database Connection**: Ensure test database is properly configured
2. **Mock Issues**: Verify mocks are properly set up and cleared
3. **Async Tests**: Use `pytest-asyncio` for async test functions
4. **Import Errors**: Check Python path and module imports

### Common Frontend Issues

1. **Mock Problems**: Ensure mocks are hoisted properly with `vi.mock()`
2. **DOM Testing**: Use appropriate queries from Testing Library
3. **Async Components**: Use `waitFor` for async operations
4. **Router Issues**: Mock React Router hooks when needed

### Debugging Tips

1. **Verbose Output**: Use `-v` flag for detailed test output
2. **Stop on Failure**: Use `-x` flag to stop on first failure
3. **Print Debugging**: Add `console.log` or `print` statements temporarily
4. **Test Isolation**: Run single tests to isolate issues

## Performance Considerations

### Backend Performance

- Use database transactions for faster test execution
- Cache pip dependencies in CI/CD
- Run tests in parallel where possible
- Mock expensive operations

### Frontend Performance

- Use shallow rendering when deep rendering isn't needed
- Mock heavy dependencies
- Cache npm dependencies in CI/CD
- Use `vi.fn()` instead of real implementations

## Continuous Improvement

### Monitoring Test Health

1. **Coverage Tracking**: Maintain high code coverage (>80%)
2. **Test Performance**: Monitor test execution time
3. **Flaky Tests**: Identify and fix unreliable tests
4. **Maintenance**: Regularly update test dependencies

### Adding New Test Types

Consider adding these test types as the application grows:

1. **Performance Tests**: Test API response times
2. **Security Tests**: Test authentication and authorization
3. **Accessibility Tests**: Automated accessibility testing
4. **Visual Regression Tests**: Test UI changes
5. **Load Tests**: Test application under load

This testing infrastructure provides a solid foundation for maintaining code quality and preventing regressions as the application evolves.