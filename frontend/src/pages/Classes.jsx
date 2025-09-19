import React, { useState } from 'react';
import { useClasses } from '../hooks/useClasses';
import ClassCard from '../components/ClassCard';

const Classes = () => {
  const { classes, loading, error, createClass, updateClass, deleteClass } = useClasses();
  const [showForm, setShowForm] = useState(false);
  const [editingClass, setEditingClass] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    teacher: '',
    year: '',
    half_group: ''
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
        half_group: formData.half_group || null
      };

      if (editingClass) {
        await updateClass(editingClass.id, submitData);
      } else {
        await createClass(submitData);
      }

      // Reset form
      setFormData({ name: '', teacher: '', year: '', half_group: '' });
      setShowForm(false);
      setEditingClass(null);
    } catch (err) {
      console.error('Error saving class:', err);
    }
  };

  const handleEdit = (classData) => {
    setEditingClass(classData);
    setFormData({
      name: classData.name,
      teacher: classData.teacher,
      year: classData.year,
      half_group: classData.half_group || ''
    });
    setShowForm(true);
  };

  const handleDelete = async (classId) => {
    if (window.confirm('Are you sure you want to delete this class?')) {
      try {
        await deleteClass(classId);
      } catch (err) {
        console.error('Error deleting class:', err);
      }
    }
  };

  const cancelForm = () => {
    setFormData({ name: '', teacher: '', year: '', half_group: '' });
    setShowForm(false);
    setEditingClass(null);
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
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">📚 My Classes</h1>
          <p className="mt-2 text-secondary-600">
            Manage your classes and teachers
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="btn btn-primary"
        >
          ➕ Add Class
        </button>
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
            {editingClass ? 'Edit Class' : 'Add New Class'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Class Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  className="input"
                  placeholder="e.g., Mathematics"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Teacher *
                </label>
                <input
                  type="text"
                  name="teacher"
                  value={formData.teacher}
                  onChange={handleInputChange}
                  required
                  className="input"
                  placeholder="e.g., Mr. Smith"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Year *
                </label>
                <input
                  type="text"
                  name="year"
                  value={formData.year}
                  onChange={handleInputChange}
                  required
                  className="input"
                  placeholder="e.g., 2024"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Half Group (Optional)
                </label>
                <select
                  name="half_group"
                  value={formData.half_group}
                  onChange={handleInputChange}
                  className="input"
                >
                  <option value="">No group</option>
                  <option value="A">Group A</option>
                  <option value="B">Group B</option>
                </select>
              </div>
            </div>
            <div className="flex space-x-3">
              <button type="submit" className="btn btn-primary">
                {editingClass ? 'Update Class' : 'Add Class'}
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

      {/* Classes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {classes.map((classData) => (
          <ClassCard
            key={classData.id}
            classData={classData}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        ))}
      </div>

      {classes.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📚</div>
          <h3 className="text-lg font-medium text-secondary-900 mb-2">No classes yet</h3>
          <p className="text-secondary-600 mb-4">Add your first class to get started</p>
          <button
            onClick={() => setShowForm(true)}
            className="btn btn-primary"
          >
            Add Your First Class
          </button>
        </div>
      )}
    </div>
  );
};

export default Classes;