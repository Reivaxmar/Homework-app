import React, { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, CheckSquare, Clock, AlertTriangle, Filter } from 'lucide-react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { homeworkAPI, classesAPI } from '../services/api'
import { format, isToday, isPast, parseISO } from 'date-fns'

const PRIORITY_COLORS = {
  LOW: 'bg-green-100 text-green-800',
  MEDIUM: 'bg-yellow-100 text-yellow-800',
  HIGH: 'bg-red-100 text-red-800'
}

const STATUS_COLORS = {
  PENDING: 'bg-gray-100 text-gray-800',
  IN_PROGRESS: 'bg-blue-100 text-blue-800',
  COMPLETED: 'bg-green-100 text-green-800'
}

function Homework() {
  const [homework, setHomework] = useState([])
  const [classes, setClasses] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingHomework, setEditingHomework] = useState(null)
  const [filter, setFilter] = useState('all')
  
  const { register, handleSubmit, reset, formState: { errors } } = useForm()

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [homeworkRes, classesRes] = await Promise.all([
        homeworkAPI.getAll(),
        classesAPI.getAll()
      ])
      
      setHomework(homeworkRes.data)
      setClasses(classesRes.data)
    } catch (error) {
      toast.error('Failed to fetch data')
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async (data) => {
    try {
      // Convert class_id to integer
      data.class_id = parseInt(data.class_id)
      
      if (editingHomework) {
        await homeworkAPI.update(editingHomework.id, data)
        toast.success('Homework updated successfully')
      } else {
        await homeworkAPI.create(data)
        toast.success('Homework created successfully')
      }
      
      fetchData()
      closeModal()
    } catch (error) {
      toast.error('Failed to save homework')
      console.error('Error saving homework:', error)
    }
  }

  const handleEdit = (homeworkItem) => {
    setEditingHomework(homeworkItem)
    reset({
      ...homeworkItem,
      due_date: format(parseISO(homeworkItem.due_date), 'yyyy-MM-dd')
    })
    setShowModal(true)
  }

  const handleDelete = async (homeworkItem) => {
    if (window.confirm(`Are you sure you want to delete "${homeworkItem.title}"?`)) {
      try {
        await homeworkAPI.delete(homeworkItem.id)
        toast.success('Homework deleted successfully')
        fetchData()
      } catch (error) {
        toast.error('Failed to delete homework')
        console.error('Error deleting homework:', error)
      }
    }
  }

  const handleToggleComplete = async (homeworkItem) => {
    try {
      if (homeworkItem.status === 'COMPLETED') {
        await homeworkAPI.reopen(homeworkItem.id)
        toast.success('Homework reopened')
      } else {
        await homeworkAPI.complete(homeworkItem.id)
        toast.success('Homework marked as completed')
      }
      fetchData()
    } catch (error) {
      toast.error('Failed to update homework status')
      console.error('Error updating homework status:', error)
    }
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingHomework(null)
    reset({
      title: '',
      description: '',
      class_id: '',
      due_date: '',
      priority: 'MEDIUM'
    })
  }

  const openCreateModal = () => {
    reset({
      title: '',
      description: '',
      class_id: '',
      due_date: format(new Date(), 'yyyy-MM-dd'),
      priority: 'MEDIUM'
    })
    setShowModal(true)
  }

  const getClassById = (classId) => {
    return classes.find(c => c.id === classId)
  }

  const filteredHomework = homework.filter(item => {
    if (filter === 'all') return true
    if (filter === 'pending') return item.status !== 'COMPLETED'
    if (filter === 'completed') return item.status === 'COMPLETED'
    if (filter === 'due_today') return isToday(parseISO(item.due_date))
    if (filter === 'overdue') return isPast(parseISO(item.due_date)) && item.status !== 'COMPLETED'
    return true
  })

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'HIGH': return <AlertTriangle className="h-4 w-4" />
      case 'MEDIUM': return <Clock className="h-4 w-4" />
      case 'LOW': return <CheckSquare className="h-4 w-4" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  const getStatusBadge = (homework) => {
    const dueDate = parseISO(homework.due_date)
    const isOverdue = isPast(dueDate) && homework.status !== 'COMPLETED'
    const isDueToday = isToday(dueDate)
    
    if (homework.status === 'COMPLETED') {
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Completed</span>
    }
    
    if (isOverdue) {
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">Overdue</span>
    }
    
    if (isDueToday) {
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Due Today</span>
    }
    
    return <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[homework.status]}`}>
      {homework.status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
    </span>
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading homework...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Homework</h1>
          <p className="text-gray-600">Manage your assignments and due dates</p>
        </div>
        <button
          onClick={openCreateModal}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Add Homework
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {[
          { key: 'all', label: 'All' },
          { key: 'pending', label: 'Pending' },
          { key: 'due_today', label: 'Due Today' },
          { key: 'overdue', label: 'Overdue' },
          { key: 'completed', label: 'Completed' }
        ].map(filterOption => (
          <button
            key={filterOption.key}
            onClick={() => setFilter(filterOption.key)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              filter === filterOption.key
                ? 'bg-primary-100 text-primary-800'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {filterOption.label}
          </button>
        ))}
      </div>

      {filteredHomework.length === 0 ? (
        <div className="text-center py-12">
          <CheckSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {filter === 'all' ? 'No homework yet' : `No ${filter.replace('_', ' ')} homework`}
          </h3>
          <p className="text-gray-600 mb-4">
            {filter === 'all' ? 'Get started by adding your first assignment' : 'Try changing the filter'}
          </p>
          {filter === 'all' && (
            <button
              onClick={openCreateModal}
              className="btn btn-primary"
            >
              Add Homework
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredHomework.map((homeworkItem) => {
            const classInfo = getClassById(homeworkItem.class_id)
            const dueDate = parseISO(homeworkItem.due_date)
            
            return (
              <div key={homeworkItem.id} className="card p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-start gap-3">
                      <button
                        onClick={() => handleToggleComplete(homeworkItem)}
                        className={`mt-1 p-1 rounded ${
                          homeworkItem.status === 'COMPLETED'
                            ? 'text-green-600 hover:text-green-700'
                            : 'text-gray-400 hover:text-gray-600'
                        }`}
                      >
                        <CheckSquare className={`h-5 w-5 ${
                          homeworkItem.status === 'COMPLETED' ? 'fill-current' : ''
                        }`} />
                      </button>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className={`text-lg font-semibold ${
                            homeworkItem.status === 'COMPLETED' 
                              ? 'text-gray-500 line-through' 
                              : 'text-gray-900'
                          }`}>
                            {homeworkItem.title}
                          </h3>
                          <div className={`px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1 ${PRIORITY_COLORS[homeworkItem.priority]}`}>
                            {getPriorityIcon(homeworkItem.priority)}
                            {homeworkItem.priority}
                          </div>
                        </div>
                        
                        {homeworkItem.description && (
                          <p className="text-gray-600 mb-2">{homeworkItem.description}</p>
                        )}
                        
                        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                          {classInfo && (
                            <div className="flex items-center gap-1">
                              <div
                                className="w-3 h-3 rounded-full"
                                style={{ backgroundColor: classInfo.color }}
                              />
                              <span>{classInfo.name}</span>
                            </div>
                          )}
                          <div>Due: {format(dueDate, 'MMM d, yyyy')}</div>
                          {getStatusBadge(homeworkItem)}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => handleEdit(homeworkItem)}
                      className="p-2 text-gray-400 hover:text-gray-600"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(homeworkItem)}
                      className="p-2 text-gray-400 hover:text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 max-h-screen overflow-y-auto">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              {editingHomework ? 'Edit Homework' : 'Add New Homework'}
            </h2>
            
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  {...register('title', { required: 'Title is required' })}
                  className="input"
                  placeholder="e.g., Math homework chapter 5"
                />
                {errors.title && (
                  <p className="text-red-600 text-sm mt-1">{errors.title.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (Optional)
                </label>
                <textarea
                  {...register('description')}
                  className="input"
                  rows={3}
                  placeholder="Additional details about the assignment..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Class
                </label>
                <select
                  {...register('class_id', { required: 'Class is required' })}
                  className="input"
                >
                  <option value="">Select a class</option>
                  {classes.map(cls => (
                    <option key={cls.id} value={cls.id}>{cls.name}</option>
                  ))}
                </select>
                {errors.class_id && (
                  <p className="text-red-600 text-sm mt-1">{errors.class_id.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Due Date
                </label>
                <input
                  type="date"
                  {...register('due_date', { required: 'Due date is required' })}
                  className="input"
                />
                {errors.due_date && (
                  <p className="text-red-600 text-sm mt-1">{errors.due_date.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Priority
                </label>
                <select
                  {...register('priority')}
                  className="input"
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                </select>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  className="btn btn-primary flex-1"
                >
                  {editingHomework ? 'Update Homework' : 'Create Homework'}
                </button>
                <button
                  type="button"
                  onClick={closeModal}
                  className="btn btn-secondary flex-1"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Homework