import React, { createContext, useContext, useState, useEffect } from 'react'
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
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      // Set the token in API headers
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      
      // Try to get current user info
      getCurrentUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const getCurrentUser = async () => {
    try {
      const response = await api.get('/api/auth/me')
      setUser(response.data)
    } catch (error) {
      console.error('Failed to get current user:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, fullName, googleTokens = null) => {
    try {
      const response = await api.post('/api/auth/login', {
        email,
        full_name: fullName,
        google_access_token: googleTokens?.access_token,
        google_refresh_token: googleTokens?.refresh_token
      })

      const { user: userData, access_token } = response.data
      
      setUser(userData)
      setToken(access_token)
      localStorage.setItem('token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      return userData
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
    delete api.defaults.headers.common['Authorization']
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
    token,
    loading,
    login,
    logout,
    updateUser,
    isAuthenticated: !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}