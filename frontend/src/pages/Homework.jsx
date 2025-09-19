import React, { useState } from 'react';
import { useHomework } from '../hooks/useHomework';
import { useClasses } from '../hooks/useClasses';
import HomeworkCard from '../components/HomeworkCard';

const Homework = () => {
  const [filter, setFilter] = useState('all'); // all, pending, completed
  const { homework, loading, error, createHomework, updateHomework, deleteHomework, toggleComplete } = useHomework();
  const { classes } = useClasses();
  const [showForm, setShowForm] = useState(false);
  const [editingHomework, setEditingHomework] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    class_id: '',
    due_date: '',
    priority: 'medium'
  });

  const filteredHomework = homework.filter(hw => {
    if (filter === 'pending') return !hw.completed;
    if (filter === 'completed') return hw.completed;
    return true;
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        class_id: parseInt(formData.class_id),
        due_date: new Date(formData.due_date).toISOString()
      };

      if (editingHomework) {
        await updateHomework(editingHomework.id, submitData);
      } else {
        await createHomework(submitData);
      }

      // Reset form
      setFormData({
        title: '',
        description: '',
        class_id: '',
        due_date: '',
        priority: 'medium'
      });
      setShowForm(false);
      setEditingHomework(null);
    } catch (err) {
      console.error('Error saving homework:', err);
    }
  };

  const handleEdit = (homework) => {
    setEditingHomework(homework);
    const dueDate = new Date(homework.due_date).toISOString().slice(0, 16);
    setFormData({
      title: homework.title,
      description: homework.description || '',
      class_id: homework.class_id.toString(),
      due_date: dueDate,
      priority: homework.priority
    });
    setShowForm(true);
  };

  const handleDelete = async (homeworkId) => {
    if (window.confirm('Are you sure you want to delete this homework?')) {
      try {
        await deleteHomework(homeworkId);
      } catch (err) {
        console.error('Error deleting homework:', err);
      }
    }
  };

  const handleToggleComplete = async (homeworkId) => {
    try {
      await toggleComplete(homeworkId);
    } catch (err) {
      console.error('Error toggling homework completion:', err);
    }
  };

  const cancelForm = () => {
    setFormData({
      title: '',
      description: '',
      class_id: '',
      due_date: '',
      priority: 'medium'
    });
    setShowForm(false);
    setEditingHomework(null);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">📝 Homework</h1>
          <p className="mt-2 text-secondary-600">
            Track your assignments and due dates
          </p>
        </div>
        <div className="flex space-x-3">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="input min-w-0"
          >
            <option value="all">All</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>
          <button
            onClick={() => setShowForm(true)}
            className="btn btn-primary whitespace-nowrap"
          >
            ➕ Add Homework
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Add/Edit Form */}
      {showForm && (
        <div className="card p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">
            {editingHomework ? 'Edit Homework' : 'Add New Homework'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  required
                  className="input"
                  placeholder="e.g., Chapter 5 exercises"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Class *
                </label>
                <select
                  name="class_id"
                  value={formData.class_id}
                  onChange={handleInputChange}
                  required
                  className="input"
                >
                  <option value="">Select a class</option>
                  {classes.map((cls) => (
                    <option key={cls.id} value={cls.id}>
                      {cls.name} - {cls.teacher}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Due Date *
                </label>
                <input
                  type="datetime-local"
                  name="due_date"
                  value={formData.due_date}
                  onChange={handleInputChange}
                  required
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Priority
                </label>
                <select
                  name="priority"
                  value={formData.priority}
                  onChange={handleInputChange}
                  className="input"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Description
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows="3"
                  className="input"
                  placeholder="Additional details about the assignment..."
                />
              </div>
            </div>
            <div className="flex space-x-3">
              <button type="submit" className="btn btn-primary">
                {editingHomework ? 'Update Homework' : 'Add Homework'}
              </button>
              <button
                type="button"
                onClick={cancelForm}
                className="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Homework List */}
      <div className="space-y-4">
        {filteredHomework.map((hw) => (
          <HomeworkCard
            key={hw.id}
            homework={hw}
            onToggleComplete={handleToggleComplete}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        ))}
      </div>

      {filteredHomework.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📝</div>
          <h3 className="text-lg font-medium text-secondary-900 mb-2">
            {filter === 'completed' ? 'No completed homework' : 
             filter === 'pending' ? 'No pending homework' : 'No homework yet'}
          </h3>
          <p className="text-secondary-600 mb-4">
            {filter === 'all' ? 'Add your first homework assignment to get started' : 
             `You have no ${filter} homework assignments`}
          </p>
          {filter === 'all' && (
            <button
              onClick={() => setShowForm(true)}
              className="btn btn-primary"
            >
              Add Your First Homework
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default Homework;