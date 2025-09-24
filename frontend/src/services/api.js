import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Auth API
export const authAPI = {
  login: (data) => api.post('/api/auth/login', data),
  googleCallback: (data, supabaseUserId) => api.post(`/api/auth/google/callback?supabase_user_id=${supabaseUserId}`, data),
  getCurrentUser: () => api.get('/api/auth/me'),
  updateProfile: (data) => api.put('/api/auth/me', data),
}

// Classes API
export const classesAPI = {
  getAll: () => api.get('/api/classes/'),
  getById: (id) => api.get(`/api/classes/${id}`),
  getTypes: () => api.get('/api/classes/types'),
  create: (data) => api.post('/api/classes/', data),
  update: (id, data) => api.put(`/api/classes/${id}`, data),
  delete: (id) => api.delete(`/api/classes/${id}`),
  getHomework: (id) => api.get(`/api/classes/${id}/homework`),
}

// Schedules API
export const schedulesAPI = {
  getAll: () => api.get('/api/schedules/'),
  getById: (id) => api.get(`/api/schedules/${id}`),
  getActive: (year) => api.get(`/api/schedules/active/${year}`),
  create: (data) => api.post('/api/schedules/', data),
  activate: (id) => api.put(`/api/schedules/${id}/activate`),
  delete: (id) => api.delete(`/api/schedules/${id}`),
  
  // Schedule slots
  getSlots: (scheduleId) => api.get(`/api/schedules/${scheduleId}/slots`),
  createSlot: (scheduleId, data) => api.post(`/api/schedules/${scheduleId}/slots`, data),
  updateSlot: (scheduleId, slotId, data) => api.put(`/api/schedules/${scheduleId}/slots/${slotId}`, data),
  deleteSlot: (scheduleId, slotId) => api.delete(`/api/schedules/${scheduleId}/slots/${slotId}`),
}

// Homework API
export const homeworkAPI = {
  getAll: (params = {}) => api.get('/api/homework/', { params }),
  getById: (id) => api.get(`/api/homework/${id}`),
  getDueToday: () => api.get('/api/homework/due-today'),
  getOverdue: () => api.get('/api/homework/overdue'),
  getUpcoming: (days = 7) => api.get(`/api/homework/upcoming?days=${days}`),
  getDueNextWeek: () => api.get('/api/homework/upcoming?days=7'),
  create: (data) => api.post('/api/homework/', data),
  update: (id, data) => api.put(`/api/homework/${id}`, data),
  complete: (id) => api.put(`/api/homework/${id}/complete`),
  reopen: (id) => api.put(`/api/homework/${id}/reopen`),
  delete: (id) => api.delete(`/api/homework/${id}`),
}

// Dashboard API
export const dashboardAPI = {
  getSummary: () => api.get('/api/dashboard/summary'),
  clearAllData: () => api.delete('/api/dashboard/clear-all-data'),
}

// Notes API
export const notesAPI = {
  // User notes
  getAll: (params = {}) => api.get('/api/notes/', { params }),
  getById: (id) => api.get(`/api/notes/${id}`),
  create: (data) => api.post('/api/notes/', data),
  update: (id, data) => api.put(`/api/notes/${id}`, data),
  delete: (id) => api.delete(`/api/notes/${id}`),
  
  // Public notes exploration
  getPublic: (params = {}) => api.get('/api/notes/public', { params }),
  getEducationLevels: () => api.get('/api/notes/education-levels'),
}

export default api