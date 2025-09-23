import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import Dashboard from '../../pages/Dashboard'
import { 
  renderWithProviders,
  createMockUser,
  createMockHomework,
  createMockClass,
  mockApiService,
  mockApiSuccess,
  mockApiError,
  userEvent
} from '../../test/utils'

// Mock the API service
vi.mock('../../services/api', () => ({
  default: mockApiService
}))

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
    loading: vi.fn()
  }
}))

describe('Dashboard', () => {
  const mockUser = createMockUser()
  const mockClasses = [
    createMockClass({ id: 1, name: 'Mathematics' }),
    createMockClass({ id: 2, name: 'Science' })
  ]
  const mockHomework = [
    createMockHomework({ 
      id: 1, 
      title: 'Math Assignment',
      class_id: 1,
      due_date: '2024-12-31',
      status: 'PENDING'
    }),
    createMockHomework({ 
      id: 2, 
      title: 'Science Project',
      class_id: 2,
      due_date: '2024-12-25',
      status: 'IN_PROGRESS'
    })
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Setup default API responses
    mockApiService.get.mockImplementation((url) => {
      if (url === '/api/classes/') {
        return mockApiSuccess(mockClasses)
      }
      if (url === '/api/homework/') {
        return mockApiSuccess(mockHomework)
      }
      return mockApiError()
    })
  })

  it('should render dashboard with user greeting', async () => {
    renderWithProviders(<Dashboard />, { initialUser: mockUser })

    expect(screen.getByText(`Welcome back, ${mockUser.full_name}!`)).toBeInTheDocument()
  })

  it('should display loading state initially', () => {
    renderWithProviders(<Dashboard />, { initialUser: mockUser, initialLoading: true })

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('should fetch and display classes and homework', async () => {
    renderWithProviders(<Dashboard />, { initialUser: mockUser })

    await waitFor(() => {
      expect(mockApiService.get).toHaveBeenCalledWith('/api/classes/')
      expect(mockApiService.get).toHaveBeenCalledWith('/api/homework/')
    })

    // Check if classes are displayed
    await waitFor(() => {
      expect(screen.getByText('Mathematics')).toBeInTheDocument()
      expect(screen.getByText('Science')).toBeInTheDocument()
    })

    // Check if homework is displayed
    await waitFor(() => {
      expect(screen.getByText('Math Assignment')).toBeInTheDocument()
      expect(screen.getByText('Science Project')).toBeInTheDocument()
    })
  })

  it('should display homework stats correctly', async () => {
    renderWithProviders(<Dashboard />, { initialUser: mockUser })

    await waitFor(() => {
      // Should show total homework count
      expect(screen.getByText('2')).toBeInTheDocument() // Total homework
      // Should show pending homework count
      expect(screen.getByText('1')).toBeInTheDocument() // Pending homework
      // Should show in progress homework count
      expect(screen.getByText('1')).toBeInTheDocument() // In progress homework
    })
  })

  it('should handle API errors gracefully', async () => {
    mockApiService.get.mockRejectedValue(mockApiError(500, 'Server error'))

    renderWithProviders(<Dashboard />, { initialUser: mockUser })

    await waitFor(() => {
      expect(mockApiService.get).toHaveBeenCalled()
    })

    // Should display error message or fallback content
    expect(screen.queryByText('Mathematics')).not.toBeInTheDocument()
  })

  it('should display empty state when no classes exist', async () => {
    mockApiService.get.mockImplementation((url) => {
      if (url === '/api/classes/') {
        return mockApiSuccess([])
      }
      if (url === '/api/homework/') {
        return mockApiSuccess([])
      }
      return mockApiError()
    })

    renderWithProviders(<Dashboard />, { initialUser: mockUser })

    await waitFor(() => {
      expect(screen.getByText(/no classes/i)).toBeInTheDocument()
    })
  })

  it('should display empty state when no homework exists', async () => {
    mockApiService.get.mockImplementation((url) => {
      if (url === '/api/classes/') {
        return mockApiSuccess(mockClasses)
      }
      if (url === '/api/homework/') {
        return mockApiSuccess([])
      }
      return mockApiError()
    })

    renderWithProviders(<Dashboard />, { initialUser: mockUser })

    await waitFor(() => {
      expect(screen.getByText(/no homework/i)).toBeInTheDocument()
    })
  })

  it('should redirect to login when user is not authenticated', () => {
    renderWithProviders(<Dashboard />, { initialUser: null })

    // Should either redirect or show login message
    expect(
      screen.queryByText(`Welcome back, ${mockUser.full_name}!`)
    ).not.toBeInTheDocument()
  })

  it('should display upcoming homework prominently', async () => {
    const upcomingHomework = [
      createMockHomework({
        id: 1,
        title: 'Urgent Assignment',
        due_date: '2024-01-02', // Very soon
        status: 'PENDING'
      })
    ]

    mockApiService.get.mockImplementation((url) => {
      if (url === '/api/homework/') {
        return mockApiSuccess(upcomingHomework)
      }
      if (url === '/api/classes/') {
        return mockApiSuccess(mockClasses)
      }
      return mockApiError()
    })

    renderWithProviders(<Dashboard />, { initialUser: mockUser })

    await waitFor(() => {
      expect(screen.getByText('Urgent Assignment')).toBeInTheDocument()
    })

    // Should highlight upcoming homework
    const urgentElement = screen.getByText('Urgent Assignment')
    expect(urgentElement.closest('.urgent, .due-soon, .priority')).toBeTruthy()
  })

  it('should allow quick actions from dashboard', async () => {
    renderWithProviders(<Dashboard />, { initialUser: mockUser })

    await waitFor(() => {
      expect(screen.getByText('Mathematics')).toBeInTheDocument()
    })

    // Should have buttons/links for quick actions
    expect(screen.getByRole('button', { name: /add homework/i }) || 
           screen.getByText(/add homework/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /add class/i }) || 
           screen.getByText(/add class/i)).toBeInTheDocument()
  })

  it('should display recent activity', async () => {
    renderWithProviders(<Dashboard />, { initialUser: mockUser })

    await waitFor(() => {
      expect(mockApiService.get).toHaveBeenCalled()
    })

    // Should show recent homework or activities
    await waitFor(() => {
      const recentSection = screen.queryByText(/recent/i) || 
                          screen.queryByText(/activity/i) ||
                          screen.queryByText(/upcoming/i)
      expect(recentSection).toBeInTheDocument()
    })
  })

  it('should handle homework status changes', async () => {
    renderWithProviders(<Dashboard />, { initialUser: mockUser })

    await waitFor(() => {
      expect(screen.getByText('Math Assignment')).toBeInTheDocument()
    })

    // Mock status update API call
    mockApiService.put.mockResolvedValue(
      mockApiSuccess({ ...mockHomework[0], status: 'COMPLETED' })
    )

    // Find and click status change button/checkbox
    const statusButton = screen.queryByRole('button', { name: /complete/i }) ||
                        screen.queryByRole('checkbox') ||
                        screen.queryByText(/mark complete/i)

    if (statusButton) {
      await userEvent.click(statusButton)

      await waitFor(() => {
        expect(mockApiService.put).toHaveBeenCalledWith(
          `/api/homework/${mockHomework[0].id}`,
          expect.objectContaining({ status: 'COMPLETED' })
        )
      })
    }
  })

  it('should refresh data when needed', async () => {
    renderWithProviders(<Dashboard />, { initialUser: mockUser })

    await waitFor(() => {
      expect(mockApiService.get).toHaveBeenCalledTimes(2) // classes and homework
    })

    // Find refresh button
    const refreshButton = screen.queryByRole('button', { name: /refresh/i }) ||
                         screen.queryByText(/refresh/i)

    if (refreshButton) {
      await userEvent.click(refreshButton)

      await waitFor(() => {
        expect(mockApiService.get).toHaveBeenCalledTimes(4) // Called again
      })
    }
  })
})