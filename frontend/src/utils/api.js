import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Classes API
export const classesAPI = {
  getAll: () => api.get('/api/classes'),
  getById: (id) => api.get(`/api/classes/${id}`),
  create: (data) => api.post('/api/classes', data),
  update: (id, data) => api.put(`/api/classes/${id}`, data),
  delete: (id) => api.delete(`/api/classes/${id}`),
};

// Schedule API
export const scheduleAPI = {
  getWeekly: () => api.get('/api/schedule'),
  getSlots: () => api.get('/api/schedule/slots'),
  createSlot: (data) => api.post('/api/schedule/slots', data),
  updateSlot: (id, data) => api.put(`/api/schedule/slots/${id}`, data),
  deleteSlot: (id) => api.delete(`/api/schedule/slots/${id}`),
};

// Homework API
export const homeworkAPI = {
  getAll: (params = {}) => api.get('/api/homework', { params }),
  getById: (id) => api.get(`/api/homework/${id}`),
  create: (data) => api.post('/api/homework', data),
  update: (id, data) => api.put(`/api/homework/${id}`, data),
  delete: (id) => api.delete(`/api/homework/${id}`),
  toggleComplete: (id) => api.put(`/api/homework/${id}/complete`),
};

export default api;