import { useState, useEffect } from 'react';
import { classesAPI } from '../utils/api';

export const useClasses = () => {
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchClasses = async () => {
    try {
      setLoading(true);
      const response = await classesAPI.getAll();
      setClasses(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch classes');
      console.error('Error fetching classes:', err);
    } finally {
      setLoading(false);
    }
  };

  const createClass = async (classData) => {
    try {
      const response = await classesAPI.create(classData);
      setClasses(prev => [...prev, response.data]);
      return response.data;
    } catch (err) {
      setError('Failed to create class');
      throw err;
    }
  };

  const updateClass = async (id, classData) => {
    try {
      const response = await classesAPI.update(id, classData);
      setClasses(prev => prev.map(c => c.id === id ? response.data : c));
      return response.data;
    } catch (err) {
      setError('Failed to update class');
      throw err;
    }
  };

  const deleteClass = async (id) => {
    try {
      await classesAPI.delete(id);
      setClasses(prev => prev.filter(c => c.id !== id));
    } catch (err) {
      setError('Failed to delete class');
      throw err;
    }
  };

  useEffect(() => {
    fetchClasses();
  }, []);

  return {
    classes,
    loading,
    error,
    fetchClasses,
    createClass,
    updateClass,
    deleteClass,
  };
};