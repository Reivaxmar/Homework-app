import React, { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, User, GraduationCap, BookOpen } from 'lucide-react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { classesAPI } from '../services/api'
import { useLanguage } from '../contexts/LanguageContext'

function Classes() {
  const { t } = useLanguage()
  const [classes, setClasses] = useState([])
  const [classTypes, setClassTypes] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingClass, setEditingClass] = useState(null)
  
  const { register, handleSubmit, reset, formState: { errors } } = useForm()

  // Generate a random bright color
  const generateRandomColor = () => {
    const colors = [
      '#EF4444', // Red
      '#F97316', // Orange
      '#F59E0B', // Amber
      '#EAB308', // Yellow
      '#84CC16', // Lime
      '#22C55E', // Green
      '#10B981', // Emerald
      '#14B8A6', // Teal
      '#06B6D4', // Cyan
      '#0EA5E9', // Sky
      '#3B82F6', // Blue
      '#6366F1', // Indigo
      '#8B5CF6', // Violet
      '#A855F7', // Purple
      '#D946EF', // Fuchsia
      '#EC4899', // Pink
      '#F43F5E', // Rose
    ]
    return colors[Math.floor(Math.random() * colors.length)]
  }

  useEffect(() => {
    fetchClasses()
    fetchClassTypes()
  }, [])

  const fetchClasses = async () => {
    try {
      const response = await classesAPI.getAll()
      setClasses(response.data)
    } catch (error) {
      toast.error(t('classes.loading'))
      console.error('Error fetching classes:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchClassTypes = async () => {
    try {
      const response = await classesAPI.getTypes()
      setClassTypes(response.data)
    } catch (error) {
      console.error('Error fetching class types:', error)
      // Set default types as fallback
      setClassTypes(['MATHS', 'ENGLISH', 'SCIENCE', 'HISTORY', 'GEOGRAPHY', 'ART', 'MUSIC', 'PHYSICAL_EDUCATION', 'COMPUTER_SCIENCE', 'FOREIGN_LANGUAGE', 'LITERATURE', 'CHEMISTRY', 'PHYSICS', 'BIOLOGY', 'OTHER'])
    }
  }

  // Convert class type to display name using translations
  const formatClassType = (classType) => {
    const translationKey = `classType.${classType.toLowerCase().replace(/_/g, '')}`
    const translated = t(translationKey)
    // If translation exists, use it, otherwise fall back to formatted original
    if (translated !== translationKey) {
      return translated
    }
    return classType
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ')
  }

  const onSubmit = async (data) => {
    try {
      if (editingClass) {
        await classesAPI.update(editingClass.id, data)
        toast.success(t('classes.updated'))
      } else {
        await classesAPI.create(data)
        toast.success(t('classes.created'))
      }
      
      fetchClasses()
      closeModal()
    } catch (error) {
      toast.error(editingClass ? t('classes.updateError') : t('classes.createError'))
      console.error('Error saving class:', error)
    }
  }

  const handleEdit = (classItem) => {
    setEditingClass(classItem)
    reset(classItem)
    setShowModal(true)
  }

  const handleDelete = async (classItem) => {
    if (window.confirm(`${t('classes.delete')} "${classItem.name}"?`)) {
      try {
        await classesAPI.delete(classItem.id)
        toast.success(t('classes.deleted'))
        fetchClasses()
      } catch (error) {
        toast.error(t('classes.deleteError'))
        console.error('Error deleting class:', error)
      }
    }
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingClass(null)
    reset({
      name: '',
      teacher: '',
      year: '',
      half_group: '',
      color: generateRandomColor(),
      class_type: ''
    })
  }

  const openCreateModal = () => {
    reset({
      name: '',
      teacher: '',
      year: '',
      half_group: '',
      color: generateRandomColor(),
      class_type: ''
    })
    setShowModal(true)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">{t('classes.loading')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('classes.title')}</h1>
          <p className="text-gray-600">{t('classes.subtitle')}</p>
        </div>
        <button
          onClick={openCreateModal}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          {t('classes.addClass')}
        </button>
      </div>

      {classes.length === 0 ? (
        <div className="text-center py-12">
          <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">{t('classes.noClasses')}</h3>
          <p className="text-gray-600 mb-4">{t('classes.noClassesDesc')}</p>
          <button
            onClick={openCreateModal}
            className="btn btn-primary"
          >
            {t('classes.addClass')}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {classes.map((classItem) => (
            <div key={classItem.id} className="card p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: classItem.color }}
                    />
                    <h3 className="text-lg font-semibold text-gray-900">
                      {classItem.name}
                    </h3>
                    {classItem.half_group && (
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        {classItem.half_group}
                      </span>
                    )}
                  </div>
                  
                  <div className="space-y-1 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4" />
                      <span>{classItem.teacher}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <GraduationCap className="h-4 w-4" />
                      <span>{classItem.year}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <BookOpen className="h-4 w-4" />
                      <span>{formatClassType(classItem.class_type || 'OTHER')}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(classItem)}
                    className="p-2 text-gray-400 hover:text-gray-600"
                  >
                    <Edit2 className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(classItem)}
                    className="p-2 text-gray-400 hover:text-red-600"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              {editingClass ? t('classes.editClass') : t('classes.addClass')}
            </h2>
            
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('classes.className')}
                </label>
                <input
                  type="text"
                  {...register('name', { required: t('classes.classNameRequired') })}
                  className="input"
                  placeholder="e.g., Mathematics"
                />
                {errors.name && (
                  <p className="text-red-600 text-sm mt-1">{errors.name.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Teacher
                </label>
                <input
                  type="text"
                  {...register('teacher', { required: 'Teacher name is required' })}
                  className="input"
                  placeholder="e.g., Mr. Smith"
                />
                {errors.teacher && (
                  <p className="text-red-600 text-sm mt-1">{errors.teacher.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Year
                </label>
                <input
                  type="text"
                  {...register('year', { required: 'Year is required' })}
                  className="input"
                  placeholder="e.g., 2023-2024"
                />
                {errors.year && (
                  <p className="text-red-600 text-sm mt-1">{errors.year.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Half Group (Optional)
                </label>
                <input
                  type="text"
                  {...register('half_group')}
                  className="input"
                  placeholder="e.g., A, B"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('classes.classType')}
                </label>
                <select
                  {...register('class_type', { required: t('classes.classTypeRequired') })}
                  className="input"
                >
                  <option value="">{t('classes.selectClassType')}</option>
                  {classTypes.map((type) => (
                    <option key={type} value={type}>
                      {formatClassType(type)}
                    </option>
                  ))}
                </select>
                {errors.class_type && (
                  <p className="text-red-600 text-sm mt-1">{errors.class_type.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('classes.color')}
                </label>
                <input
                  type="color"
                  {...register('color')}
                  className="w-full h-10 border border-gray-300 rounded-md"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  className="btn btn-primary flex-1"
                >
                  {editingClass ? t('classes.updateClass') : t('classes.createClass')}
                </button>
                <button
                  type="button"
                  onClick={closeModal}
                  className="btn btn-secondary flex-1"
                >
                  {t('classes.cancel')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Classes