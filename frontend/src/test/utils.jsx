import React from 'react'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '../contexts/AuthContext'

// Mock Supabase client for testing
const mockSupabaseClient = {
  auth: {
    signInWithOAuth: vi.fn(),
    signOut: vi.fn(),
    getSession: vi.fn(),
    getUser: vi.fn(),
    onAuthStateChange: vi.fn(() => ({
      data: { subscription: { unsubscribe: vi.fn() } }
    }))
  }
}

// Mock API service
const mockApiService = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  defaults: {
    headers: {
      common: {}
    }
  }
}

// Test wrapper with all necessary providers
function TestWrapper({ children, initialUser = null, initialLoading = false }) {
  // Mock AuthContext value
  const mockAuthValue = {
    user: initialUser,
    session: initialUser ? { access_token: 'mock-token' } : null,
    loading: initialLoading,
    login: vi.fn(),
    signInWithGoogle: vi.fn(),
    logout: vi.fn(),
    updateUser: vi.fn(),
    syncGoogleCalendar: vi.fn(),
    isAuthenticated: !!initialUser
  }

  return (
    <BrowserRouter>
      <AuthProvider value={mockAuthValue}>
        {children}
      </AuthProvider>
    </BrowserRouter>
  )
}

// Custom render function with providers
export function renderWithProviders(ui, options = {}) {
  const {
    initialUser = null,
    initialLoading = false,
    ...renderOptions
  } = options

  const Wrapper = ({ children }) => (
    <TestWrapper initialUser={initialUser} initialLoading={initialLoading}>
      {children}
    </TestWrapper>
  )

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    mockSupabaseClient,
    mockApiService
  }
}

// Mock user data factory
export const createMockUser = (overrides = {}) => ({
  id: 1,
  email: 'test@example.com',
  full_name: 'Test User',
  avatar_url: 'https://example.com/avatar.jpg',
  supabase_user_id: 'test-user-123',
  ...overrides
})

// Mock class data factory
export const createMockClass = (overrides = {}) => ({
  id: 1,
  name: 'Test Class',
  teacher: 'Test Teacher',
  year: '2024',
  color: '#FF5733',
  class_type: 'OTHER',
  half_group: null,
  user_id: 1,
  ...overrides
})

// Mock homework data factory
export const createMockHomework = (overrides = {}) => ({
  id: 1,
  title: 'Test Homework',
  description: 'Test homework description',
  due_date: '2024-12-31',
  due_time: '23:59:00',
  status: 'PENDING',
  priority: 'MEDIUM',
  class_id: 1,
  user_id: 1,
  google_calendar_event_id: null,
  assigned_date: '2024-01-01',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  completed_at: null,
  ...overrides
})

// Mock schedule data factory
export const createMockSchedule = (overrides = {}) => ({
  id: 1,
  name: 'Test Schedule',
  year: '2024',
  is_active: true,
  user_id: 1,
  slots: [],
  ...overrides
})

// Mock API responses
export const mockApiResponses = {
  user: createMockUser(),
  classes: [createMockClass()],
  homework: [createMockHomework()],
  schedule: createMockSchedule(),
  auth: {
    access_token: 'mock-jwt-token',
    user: createMockUser()
  }
}

// Helper to mock successful API calls
export const mockApiSuccess = (data) => Promise.resolve({ data })

// Helper to mock API errors
export const mockApiError = (status = 400, message = 'API Error') => 
  Promise.reject({
    response: {
      status,
      data: { detail: message }
    }
  })

// Mock toast notifications
export const mockToast = {
  success: vi.fn(),
  error: vi.fn(),
  loading: vi.fn(),
  dismiss: vi.fn()
}

// Setup mocks for external libraries
export const setupMocks = () => {
  // Mock react-hot-toast
  vi.mock('react-hot-toast', () => ({
    default: mockToast,
    toast: mockToast
  }))

  // Mock axios
  vi.mock('axios', () => ({
    default: mockApiService,
    create: vi.fn(() => mockApiService)
  }))

  // Mock Supabase
  vi.mock('@supabase/supabase-js', () => ({
    createClient: vi.fn(() => mockSupabaseClient)
  }))
}

// Test utilities for user interactions
export const userEvent = {
  click: async (element) => {
    const { userEvent } = await import('@testing-library/user-event')
    const user = userEvent.setup()
    return user.click(element)
  },
  type: async (element, text) => {
    const { userEvent } = await import('@testing-library/user-event')
    const user = userEvent.setup()
    return user.type(element, text)
  },
  selectOptions: async (element, values) => {
    const { userEvent } = await import('@testing-library/user-event')
    const user = userEvent.setup()
    return user.selectOptions(element, values)
  },
  upload: async (element, file) => {
    const { userEvent } = await import('@testing-library/user-event')
    const user = userEvent.setup()
    return user.upload(element, file)
  }
}

// Make renderWithProviders available globally
global.renderWithProviders = renderWithProviders

export * from '@testing-library/react'
export { vi } from 'vitest'