import React, { createContext, useContext, useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import api from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [session, setSession] = useState(null)

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      if (session) {
        handleAuthSession(session)
      } else {
        setLoading(false)
      }
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      setSession(session)
      
      if (event === 'SIGNED_IN' && session) {
        await handleAuthSession(session)
      } else if (event === 'SIGNED_OUT') {
        handleSignOut()
      }
    })

    return () => subscription.unsubscribe()
  }, [])

  const handleAuthSession = async (session) => {
    try {
      // Get Google tokens if available
      const googleTokens = session.provider_token ? {
        access_token: session.provider_token,
        refresh_token: session.provider_refresh_token,
        expires_in: session.expires_in
      } : null

      // Send auth data to backend to get our backend JWT token
      const response = await api.post('/api/auth/google/callback', googleTokens || {}, {
        params: {
          supabase_user_id: session.user.id
        }
      })

      const { user: userData, access_token: backendToken } = response.data
      
      // Set the backend JWT token for all future API requests
      api.defaults.headers.common['Authorization'] = `Bearer ${backendToken}`
      
      setUser(userData)

      // Sync Google Calendar if we have Google tokens
      if (googleTokens?.access_token) {
        try {
          await syncGoogleCalendar()
        } catch (calendarError) {
          console.warn('Calendar sync failed, but user is still authenticated:', calendarError)
        }
      }
      
    } catch (error) {
      console.error('Failed to handle auth session:', error)
      // Don't throw here - allow user to be logged in even if backend fails
      // Set basic user info from Supabase session
      setUser({
        id: session.user.id,
        email: session.user.email,
        full_name: session.user.user_metadata?.full_name || session.user.user_metadata?.name || 'User',
        avatar_url: session.user.user_metadata?.avatar_url || session.user.user_metadata?.picture
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSignOut = () => {
    setUser(null)
    setSession(null)
    delete api.defaults.headers.common['Authorization']
    setLoading(false)
  }

  const signInWithGoogle = async () => {
    setLoading(true)
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          scopes: 'https://www.googleapis.com/auth/calendar',
          redirectTo: `${window.location.origin}/auth/callback`
        }
      })
      
      if (error) {
        throw error
      }
    } catch (error) {
      console.error('Google sign in failed:', error)
      setLoading(false)
      throw error
    }
  }

  const syncGoogleCalendar = async () => {
    try {
      await api.post('/api/calendar/sync')
    } catch (error) {
      console.error('Failed to sync Google Calendar:', error)
    }
  }

  const login = async (email, fullName, googleTokens = null) => {
    // Keep this for backward compatibility, but redirect to Google OAuth
    return signInWithGoogle()
  }

  const logout = async () => {
    setLoading(true)
    try {
      await supabase.auth.signOut()
    } catch (error) {
      console.error('Logout failed:', error)
    }
    // handleSignOut is called by onAuthStateChange
  }

  const updateUser = async (userData) => {
    try {
      const response = await api.put('/api/auth/me', userData)
      setUser(response.data)
      return response.data
    } catch (error) {
      console.error('Failed to update user:', error)
      throw error
    }
  }

  const value = {
    user,
    session,
    loading,
    login,
    signInWithGoogle,
    logout,
    updateUser,
    syncGoogleCalendar,
    isAuthenticated: !!session && !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}