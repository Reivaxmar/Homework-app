import { useState, useEffect } from 'react';
import { homeworkAPI } from '../utils/api';

export const useHomework = (filters = {}) => {
  const [homework, setHomework] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHomework = async () => {
    try {
      setLoading(true);
      const response = await homeworkAPI.getAll(filters);
      setHomework(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch homework');
      console.error('Error fetching homework:', err);
    } finally {
      setLoading(false);
    }
  };

  const createHomework = async (homeworkData) => {
    try {
      const response = await homeworkAPI.create(homeworkData);
      setHomework(prev => [...prev, response.data]);
      return response.data;
    } catch (err) {
      setError('Failed to create homework');
      throw err;
    }
  };

  const updateHomework = async (id, homeworkData) => {
    try {
      const response = await homeworkAPI.update(id, homeworkData);
      setHomework(prev => prev.map(h => h.id === id ? response.data : h));
      return response.data;
    } catch (err) {
      setError('Failed to update homework');
      throw err;
    }
  };

  const deleteHomework = async (id) => {
    try {
      await homeworkAPI.delete(id);
      setHomework(prev => prev.filter(h => h.id !== id));
    } catch (err) {
      setError('Failed to delete homework');
      throw err;
    }
  };

  const toggleComplete = async (id) => {
    try {
      const response = await homeworkAPI.toggleComplete(id);
      setHomework(prev => prev.map(h => h.id === id ? response.data : h));
      return response.data;
    } catch (err) {
      setError('Failed to toggle homework completion');
      throw err;
    }
  };

  useEffect(() => {
    fetchHomework();
  }, [JSON.stringify(filters)]);

  return {
    homework,
    loading,
    error,
    fetchHomework,
    createHomework,
    updateHomework,
    deleteHomework,
    toggleComplete,
  };
};