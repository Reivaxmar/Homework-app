import React from 'react'
import { vi } from 'vitest'

// Mock AuthContext
export const mockAuthContext = {
  user: null,
  loading: false,
  signInWithGoogle: vi.fn(),
  signOut: vi.fn(),
  refreshSession: vi.fn(),
}

export const AuthProvider = ({ children }) => {
  return children
}

export const useAuth = () => mockAuthContext

// Helper to set mock auth state
export const setMockAuthUser = (user) => {
  mockAuthContext.user = user
}

export const setMockAuthLoading = (loading) => {
  mockAuthContext.loading = loading
}

export const clearMockAuth = () => {
  mockAuthContext.user = null
  mockAuthContext.loading = false
  vi.clearAllMocks()
}