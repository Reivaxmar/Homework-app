import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'

const AuthCallback = () => {
  const navigate = useNavigate()
  const { loading, isAuthenticated } = useAuth()

  useEffect(() => {
    if (!loading) {
      if (isAuthenticated) {
        toast.success('Authentication successful!')
        navigate('/dashboard')
      } else {
        toast.error('Authentication failed')
        navigate('/login')
      }
    }
  }, [loading, isAuthenticated, navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
        <h2 className="mt-4 text-xl font-semibold text-gray-900">
          Completing authentication...
        </h2>
        <p className="mt-2 text-gray-600">
          Please wait while we set up your account and sync your Google Calendar.
        </p>
      </div>
    </div>
  )
}

export default AuthCallback