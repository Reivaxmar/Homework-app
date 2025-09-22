import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import Login from '../../../components/Login'

// Mock the AuthContext
const mockSignInWithGoogle = vi.fn()
vi.mock('../../../contexts/AuthContext', () => ({
  useAuth: () => ({
    signInWithGoogle: mockSignInWithGoogle,
  }),
}))

// Mock react-router-dom
const mockNavigate = vi.fn()
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
  BrowserRouter: ({ children }) => <div>{children}</div>,
}))

// Mock react-hot-toast
const mockToast = {
  success: vi.fn(),
  error: vi.fn(),
}
vi.mock('react-hot-toast', () => ({
  default: mockToast,
}))

describe('Login Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login form correctly', () => {
    render(<Login />)

    // Check for main heading
    expect(screen.getByText('Sign in to Homework Manager')).toBeInTheDocument()
    
    // Check for description
    expect(screen.getByText('Access your homework and sync with Google Calendar')).toBeInTheDocument()
    
    // Check for Google sign-in button
    expect(screen.getByRole('button', { name: /sign in with google/i })).toBeInTheDocument()
    
    // Check for features list
    expect(screen.getByText('Automatic Google Calendar sync')).toBeInTheDocument()
    expect(screen.getByText('Secure authentication with Supabase')).toBeInTheDocument()
    expect(screen.getByText('Access your profile and assignments')).toBeInTheDocument()
  })

  it('shows user icon', () => {
    render(<Login />)

    // The User icon should be present (we can't easily test for Lucide icons directly,
    // but we can check for the container with appropriate classes)
    const iconContainer = document.querySelector('.bg-blue-600.p-3.rounded-full')
    expect(iconContainer).toBeInTheDocument()
  })

  it('calls signInWithGoogle when button is clicked', async () => {
    mockSignInWithGoogle.mockResolvedValue()

    render(<Login />)

    const signInButton = screen.getByRole('button', { name: /sign in with google/i })
    fireEvent.click(signInButton)

    expect(mockSignInWithGoogle).toHaveBeenCalledTimes(1)
  })

  it('shows loading state when signing in', async () => {
    // Mock a delayed promise
    mockSignInWithGoogle.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

    render(<Login />)

    const signInButton = screen.getByRole('button', { name: /sign in with google/i })
    
    // Click the button
    fireEvent.click(signInButton)

    // Button should be disabled and show loading spinner
    expect(signInButton).toBeDisabled()
    
    // Check for loading spinner (animated div)
    const loadingSpinner = document.querySelector('.animate-spin')
    expect(loadingSpinner).toBeInTheDocument()

    // Wait for the promise to resolve
    await waitFor(() => {
      expect(mockSignInWithGoogle).toHaveBeenCalledTimes(1)
    })
  })

  it('handles sign-in error gracefully', async () => {
    mockSignInWithGoogle.mockRejectedValue(new Error('Sign-in failed'))

    render(<Login />)

    const signInButton = screen.getByRole('button', { name: /sign in with google/i })
    fireEvent.click(signInButton)

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to sign in with Google. Please try again.')
    })

    // Button should no longer be disabled after error
    expect(signInButton).not.toBeDisabled()
  })

  it('shows success toast on successful sign-in', async () => {
    mockSignInWithGoogle.mockResolvedValue()

    render(<Login />)

    const signInButton = screen.getByRole('button', { name: /sign in with google/i })
    fireEvent.click(signInButton)

    await waitFor(() => {
      expect(mockToast.success).toHaveBeenCalledWith('Redirecting to Google...')
    })
  })

  it('displays feature checkmarks correctly', () => {
    render(<Login />)

    // Check for checkmark icons (SVG elements with specific paths)
    const checkmarks = document.querySelectorAll('svg path[fill-rule="evenodd"]')
    expect(checkmarks).toHaveLength(3) // Three feature items
  })

  it('shows Google logo on button', () => {
    render(<Login />)

    // Google logo should be present (SVG with multiple paths)
    const googleLogo = document.querySelector('svg[viewBox="0 0 24 24"]')
    expect(googleLogo).toBeInTheDocument()
    
    // Should have multiple path elements for the Google logo
    const logoPaths = googleLogo?.querySelectorAll('path')
    expect(logoPaths?.length).toBeGreaterThan(1)
  })

  it('displays privacy notice', () => {
    render(<Login />)

    expect(screen.getByText(/By signing in, you agree to sync your Google Calendar/)).toBeInTheDocument()
  })

  it('has proper accessibility attributes', () => {
    render(<Login />)

    const signInButton = screen.getByRole('button', { name: /sign in with google/i })
    
    // Button should be keyboard accessible
    expect(signInButton).toBeInTheDocument()
    expect(signInButton.tagName).toBe('BUTTON')

    // Check for focus styles (classes that handle focus states)
    expect(signInButton).toHaveClass('focus:outline-none', 'focus:ring-2', 'focus:ring-offset-2')
  })
})