import React from 'react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '../../contexts/AuthContext'
import { createMockUser, mockSupabaseClient, mockApiService } from '../../test/utils'

// Mock the Supabase client
vi.mock('@supabase/supabase-js', () => ({
  createClient: vi.fn(() => mockSupabaseClient)
}))

// Mock the API service
vi.mock('../../services/api', () => ({
  default: mockApiService
}))

const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should provide initial auth state', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.user).toBeNull()
    expect(result.current.session).toBeNull()
    expect(result.current.loading).toBe(true)
    expect(result.current.isAuthenticated).toBe(false)
    expect(typeof result.current.login).toBe('function')
    expect(typeof result.current.signInWithGoogle).toBe('function')
    expect(typeof result.current.logout).toBe('function')
    expect(typeof result.current.updateUser).toBe('function')
    expect(typeof result.current.syncGoogleCalendar).toBe('function')
  })

  it('should handle Google sign in', async () => {
    const mockSession = {
      access_token: 'mock-token',
      refresh_token: 'mock-refresh-token'
    }

    mockSupabaseClient.auth.signInWithOAuth.mockResolvedValue({
      error: null
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await result.current.signInWithGoogle()
    })

    expect(mockSupabaseClient.auth.signInWithOAuth).toHaveBeenCalledWith({
      provider: 'google',
      options: {
        scopes: 'https://www.googleapis.com/auth/calendar',
        redirectTo: `${window.location.origin}/auth/callback`
      }
    })
  })

  it('should handle Google sign in error', async () => {
    const mockError = new Error('OAuth failed')
    mockSupabaseClient.auth.signInWithOAuth.mockResolvedValue({
      error: mockError
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    await expect(
      act(async () => {
        await result.current.signInWithGoogle()
      })
    ).rejects.toThrow('OAuth failed')
  })

  it('should handle logout', async () => {
    mockSupabaseClient.auth.signOut.mockResolvedValue({ error: null })

    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await result.current.logout()
    })

    expect(mockSupabaseClient.auth.signOut).toHaveBeenCalled()
  })

  it('should handle logout error', async () => {
    const mockError = new Error('Logout failed')
    mockSupabaseClient.auth.signOut.mockResolvedValue({ error: mockError })

    const { result } = renderHook(() => useAuth(), { wrapper })

    // Should not throw even if logout fails
    await act(async () => {
      await result.current.logout()
    })

    expect(mockSupabaseClient.auth.signOut).toHaveBeenCalled()
  })

  it('should update user profile', async () => {
    const mockUser = createMockUser()
    const updatedUser = { ...mockUser, full_name: 'Updated Name' }

    mockApiService.put.mockResolvedValue({ data: updatedUser })

    const { result } = renderHook(() => useAuth(), { wrapper })

    let updateResult
    await act(async () => {
      updateResult = await result.current.updateUser({ full_name: 'Updated Name' })
    })

    expect(mockApiService.put).toHaveBeenCalledWith('/api/auth/me', { full_name: 'Updated Name' })
    expect(updateResult).toEqual(updatedUser)
  })

  it('should handle update user error', async () => {
    const mockError = { response: { status: 400, data: { detail: 'Update failed' } } }
    mockApiService.put.mockRejectedValue(mockError)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await expect(
      act(async () => {
        await result.current.updateUser({ full_name: 'Updated Name' })
      })
    ).rejects.toEqual(mockError)
  })

  it('should sync Google Calendar', async () => {
    mockApiService.post.mockResolvedValue({ data: { message: 'Synced successfully' } })

    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await result.current.syncGoogleCalendar()
    })

    expect(mockApiService.post).toHaveBeenCalledWith('/api/calendar/sync')
  })

  it('should handle Google Calendar sync error', async () => {
    const mockError = new Error('Sync failed')
    mockApiService.post.mockRejectedValue(mockError)

    const { result } = renderHook(() => useAuth(), { wrapper })

    // Should not throw even if sync fails
    await act(async () => {
      await result.current.syncGoogleCalendar()
    })

    expect(mockApiService.post).toHaveBeenCalledWith('/api/calendar/sync')
  })

  it('should handle auth state change', async () => {
    const mockUser = createMockUser()
    const mockSession = {
      access_token: 'mock-token',
      user: {
        id: 'supabase-user-id',
        email: mockUser.email,
        user_metadata: {
          full_name: mockUser.full_name,
          avatar_url: mockUser.avatar_url
        }
      }
    }

    // Mock successful API response for auth callback
    mockApiService.post.mockResolvedValue({
      data: {
        access_token: 'jwt-token',
        user: mockUser
      }
    })

    // Mock the auth state change callback
    let authStateChangeCallback
    mockSupabaseClient.auth.onAuthStateChange.mockImplementation((callback) => {
      authStateChangeCallback = callback
      return {
        data: { subscription: { unsubscribe: vi.fn() } }
      }
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    // Simulate auth state change
    await act(async () => {
      authStateChangeCallback('SIGNED_IN', mockSession)
    })

    // Wait for state updates
    await waitFor(() => {
      expect(result.current.user).toEqual(mockUser)
      expect(result.current.session).toEqual(mockSession)
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.loading).toBe(false)
    })
  })

  it('should handle auth state change to signed out', async () => {
    // Mock the auth state change callback
    let authStateChangeCallback
    mockSupabaseClient.auth.onAuthStateChange.mockImplementation((callback) => {
      authStateChangeCallback = callback
      return {
        data: { subscription: { unsubscribe: vi.fn() } }
      }
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    // Simulate sign out
    await act(async () => {
      authStateChangeCallback('SIGNED_OUT', null)
    })

    await waitFor(() => {
      expect(result.current.user).toBeNull()
      expect(result.current.session).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.loading).toBe(false)
    })
  })

  it('should handle backend authentication failure gracefully', async () => {
    const mockSession = {
      access_token: 'mock-token',
      user: {
        id: 'supabase-user-id',
        email: 'test@example.com',
        user_metadata: {
          full_name: 'Test User',
          avatar_url: 'https://example.com/avatar.jpg'
        }
      }
    }

    // Mock failed API response
    mockApiService.post.mockRejectedValue(new Error('Backend error'))

    // Mock the auth state change callback
    let authStateChangeCallback
    mockSupabaseClient.auth.onAuthStateChange.mockImplementation((callback) => {
      authStateChangeCallback = callback
      return {
        data: { subscription: { unsubscribe: vi.fn() } }
      }
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    // Simulate auth state change with backend failure
    await act(async () => {
      authStateChangeCallback('SIGNED_IN', mockSession)
    })

    // Should still set basic user info from Supabase session
    await waitFor(() => {
      expect(result.current.user).toEqual({
        id: 'supabase-user-id',
        email: 'test@example.com',
        full_name: 'Test User',
        avatar_url: 'https://example.com/avatar.jpg'
      })
      expect(result.current.session).toEqual(mockSession)
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.loading).toBe(false)
    })
  })
})