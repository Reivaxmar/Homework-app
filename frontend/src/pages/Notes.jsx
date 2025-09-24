import React, { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, Eye, EyeOff, Search, Filter, BookOpen, School, GraduationCap, Globe, Link, FileText, ExternalLink } from 'lucide-react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { notesAPI, classesAPI } from '../services/api'
import { useLanguage } from '../contexts/LanguageContext'

function Notes() {
  const { t, language } = useLanguage()
  const [activeTab, setActiveTab] = useState('my-notes')
  const [notes, setNotes] = useState([])
  const [publicNotes, setPublicNotes] = useState([])
  const [classTypes, setClassTypes] = useState([])
  const [educationLevels, setEducationLevels] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingNote, setEditingNote] = useState(null)
  const [filters, setFilters] = useState({
    class_type: '',
    education_level: '',
    year: '',
    school: ''
  })
  
  // Google Drive state
  const [driveUrl, setDriveUrl] = useState('')
  const [attachingDriveFile, setAttachingDriveFile] = useState(false)
  
  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm()

  useEffect(() => {
    fetchInitialData()
  }, [language])  // Re-fetch when language changes

  useEffect(() => {
    if (activeTab === 'my-notes') {
      fetchNotes()
    } else {
      fetchPublicNotes()
    }
  }, [activeTab, filters])

  const fetchInitialData = async () => {
    try {
      const [classTypesRes, educationLevelsRes] = await Promise.all([
        classesAPI.getTypes(),
        notesAPI.getEducationLevels(language)
      ])
      setClassTypes(classTypesRes.data)
      setEducationLevels(educationLevelsRes.data)
    } catch (error) {
      console.error('Error fetching initial data:', error)
    }
  }

  const fetchNotes = async () => {
    try {
      setLoading(true)
      const params = activeTab === 'my-notes' ? {} : filters
      const response = await notesAPI.getAll(params)
      setNotes(response.data)
    } catch (error) {
      toast.error('Error loading notes')
      console.error('Error fetching notes:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchPublicNotes = async () => {
    try {
      setLoading(true)
      const cleanFilters = Object.fromEntries(
        Object.entries(filters).filter(([_, value]) => value !== '')
      )
      const response = await notesAPI.getPublic(cleanFilters)
      setPublicNotes(response.data)
    } catch (error) {
      toast.error('Error loading public notes')
      console.error('Error fetching public notes:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatClassType = (classType) => {
    return classType
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ')
  }

  const formatEducationLevel = (levelValue) => {
    // Find the level object from the current education levels
    const levelObj = educationLevels.find(level => level.value === levelValue)
    if (levelObj) {
      return levelObj.display
    }
    
    // Fallback for backward compatibility
    if (levelValue && levelValue.startsWith('GRADE_')) {
      return `Grade ${levelValue.split('_')[1]}`
    }
    return levelValue || ''
  }

  const onSubmit = async (data) => {
    try {
      if (editingNote) {
        await notesAPI.update(editingNote.id, data)
        toast.success('Note updated successfully')
      } else {
        await notesAPI.create(data)
        toast.success('Note created successfully')
      }
      setShowModal(false)
      setEditingNote(null)
      reset()
      fetchNotes()
    } catch (error) {
      const errorMessage = error.response?.data?.detail || (editingNote ? 'Error updating note' : 'Error creating note')
      toast.error(errorMessage)
      console.error('Error saving note:', error)
    }
  }

  const handleEdit = (note) => {
    setEditingNote(note)
    reset(note)
    setShowModal(true)
  }

  const handleDelete = async (note) => {
    if (window.confirm('Are you sure you want to delete this note?')) {
      try {
        await notesAPI.delete(note.id)
        toast.success('Note deleted successfully')
        fetchNotes()
      } catch (error) {
        toast.error('Error deleting note')
        console.error('Error deleting note:', error)
      }
    }
  }

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const clearFilters = () => {
    setFilters({
      class_type: '',
      education_level: '',
      year: '',
      school: ''
    })
  }

  // Google Drive functions
  const handleAttachDriveFile = async (noteId) => {
    if (!driveUrl.trim()) {
      toast.error('Please enter a Google Drive URL')
      return
    }

    try {
      setAttachingDriveFile(true)
      await notesAPI.attachDriveFile(noteId, driveUrl)
      toast.success('Google Drive file attached successfully')
      setDriveUrl('')
      fetchNotes()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error attaching Google Drive file')
      console.error('Error attaching drive file:', error)
    } finally {
      setAttachingDriveFile(false)
    }
  }

  const handleDetachDriveFile = async (noteId) => {
    if (window.confirm('Are you sure you want to remove the Google Drive file from this note?')) {
      try {
        await notesAPI.detachDriveFile(noteId)
        toast.success('Google Drive file detached successfully')
        fetchNotes()
      } catch (error) {
        toast.error('Error detaching Google Drive file')
        console.error('Error detaching drive file:', error)
      }
    }
  }

  const renderDriveFileInfo = (note) => {
    if (!note.google_drive_file_id) return null

    return (
      <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-blue-600" />
            <div>
              <p className="text-sm font-medium text-blue-900">
                {note.google_drive_file_name || 'Google Drive File'}
              </p>
              {note.google_drive_mime_type && (
                <p className="text-xs text-blue-600">
                  {note.google_drive_mime_type.split('/')[1]?.toUpperCase() || 'Document'}
                </p>
              )}
            </div>
          </div>
          <div className="flex gap-1">
            {note.google_drive_file_url && (
              <a
                href={note.google_drive_file_url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-1 text-blue-600 hover:text-blue-800"
                title="Open in Google Drive"
              >
                <ExternalLink className="h-4 w-4" />
              </a>
            )}
            {activeTab === 'my-notes' && (
              <button
                onClick={() => handleDetachDriveFile(note.id)}
                className="p-1 text-red-400 hover:text-red-600"
                title="Remove Google Drive file"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    )
  }

  const renderDriveAttachment = (note) => {
    if (activeTab !== 'my-notes') return null

    return (
      <div className="mt-3 p-3 bg-gray-50 border rounded-lg">
        <div className="flex items-center gap-2 mb-2">
          <Link className="h-4 w-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">Attach Google Drive File</span>
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Paste Google Drive URL or file ID here"
            value={driveUrl}
            onChange={(e) => setDriveUrl(e.target.value)}
            className="flex-1 px-3 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={() => handleAttachDriveFile(note.id)}
            disabled={attachingDriveFile || !driveUrl.trim()}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300"
          >
            {attachingDriveFile ? 'Attaching...' : 'Attach'}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          You can paste any Google Drive shareable link or file ID
        </p>
      </div>
    )
  }

  const currentNotes = activeTab === 'my-notes' ? notes : publicNotes

  if (loading && currentNotes.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notes</h1>
          <p className="text-gray-600">Manage your study notes and explore shared knowledge</p>
        </div>
        {activeTab === 'my-notes' && (
          <button
            onClick={() => {
              setEditingNote(null)
              reset()
              setShowModal(true)
            }}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Note
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('my-notes')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'my-notes'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              My Notes
            </div>
          </button>
          <button
            onClick={() => setActiveTab('explorer')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'explorer'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <Globe className="h-4 w-4" />
              Explore Public Notes
            </div>
          </button>
        </nav>
      </div>

      {/* Filters for Explorer */}
      {activeTab === 'explorer' && (
        <div className="card p-4">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="h-4 w-4" />
            <span className="font-medium">Filters</span>
            <button
              onClick={clearFilters}
              className="text-sm text-blue-600 hover:text-blue-800 ml-auto"
            >
              Clear All
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subject
              </label>
              <select
                value={filters.class_type}
                onChange={(e) => handleFilterChange('class_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="">All Subjects</option>
                {classTypes.map(type => (
                  <option key={type} value={type}>
                    {formatClassType(type)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Education Level
              </label>
              <select
                value={filters.education_level}
                onChange={(e) => handleFilterChange('education_level', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="">All Levels</option>
                {educationLevels.map(level => (
                  <option key={level.value} value={level.value}>
                    {level.display}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Year
              </label>
              <input
                type="text"
                placeholder="e.g., 2023-2024"
                value={filters.year}
                onChange={(e) => handleFilterChange('year', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                School
              </label>
              <input
                type="text"
                placeholder="School name"
                value={filters.school}
                onChange={(e) => handleFilterChange('school', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>
        </div>
      )}

      {/* Notes List */}
      {currentNotes.length === 0 ? (
        <div className="text-center py-12">
          <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {activeTab === 'my-notes' ? 'No notes yet' : 'No public notes found'}
          </h3>
          <p className="text-gray-600">
            {activeTab === 'my-notes' 
              ? 'Create your first note to get started'
              : 'Try adjusting your filters or check back later'
            }
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {currentNotes.map((note) => (
            <div key={note.id} className="card p-6">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {note.title}
                  </h3>
                  <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                    <BookOpen className="h-4 w-4" />
                    <span>{formatClassType(note.class_type)}</span>
                  </div>
                  {note.education_level && (
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                      <GraduationCap className="h-4 w-4" />
                      <span>{formatEducationLevel(note.education_level)}</span>
                    </div>
                  )}
                  {note.school && (
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                      <School className="h-4 w-4" />
                      <span>{note.school}</span>
                    </div>
                  )}
                </div>
                {activeTab === 'my-notes' && (
                  <div className="flex gap-2">
                    {note.is_public ? (
                      <Eye className="h-4 w-4 text-green-600" title="Public" />
                    ) : (
                      <EyeOff className="h-4 w-4 text-gray-400" title="Private" />
                    )}
                    <button
                      onClick={() => handleEdit(note)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(note)}
                      className="p-1 text-gray-400 hover:text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </div>
              
              <div className="text-gray-700 text-sm mb-3 line-clamp-3">
                {note.content}
              </div>
              
              {/* Google Drive File Display */}
              {renderDriveFileInfo(note)}
              
              <div className="flex justify-between items-center text-xs text-gray-500">
                <span>Year: {note.year}</span>
                <span>{new Date(note.updated_at).toLocaleDateString()}</span>
              </div>
              
              {/* Google Drive Attachment Section for My Notes */}
              {activeTab === 'my-notes' && !note.google_drive_file_id && renderDriveAttachment(note)}
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">
                  {editingNote ? 'Edit Note' : 'Create New Note'}
                </h2>
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false)
                    setEditingNote(null)
                    reset()
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  {...register('title', { required: 'Title is required' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
                {errors.title && (
                  <p className="text-red-500 text-sm mt-1">{errors.title.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Content / Description *
                </label>
                <textarea
                  rows={6}
                  {...register('content', { required: 'Content is required' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="Enter note content or a description of your shared Google Drive document"
                />
                {errors.content && (
                  <p className="text-red-500 text-sm mt-1">{errors.content.message}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  When sharing a Google Drive file, this can serve as a description of the document
                </p>
              </div>

              {/* Google Drive Integration */}
              <div className="border-t pt-4">
                <div className="flex items-center gap-2 mb-3">
                  <FileText className="h-4 w-4 text-blue-600" />
                  <span className="text-sm font-medium text-gray-700">Google Drive File (Optional)</span>
                </div>
                
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Google Drive URL or File ID
                    </label>
                    <input
                      type="text"
                      {...register('google_drive_file_url')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      placeholder="https://drive.google.com/file/d/... or paste file ID"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Paste any Google Drive shareable link. The file will be linked to this note.
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      File Name (Optional)
                    </label>
                    <input
                      type="text"
                      {...register('google_drive_file_name')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      placeholder="Custom display name for the file"
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Subject *
                  </label>
                  <select
                    {...register('class_type', { required: 'Subject is required' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="">Select Subject</option>
                    {classTypes.map(type => (
                      <option key={type} value={type}>
                        {formatClassType(type)}
                      </option>
                    ))}
                  </select>
                  {errors.class_type && (
                    <p className="text-red-500 text-sm mt-1">{errors.class_type.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Education Level
                  </label>
                  <select
                    {...register('education_level')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="">Select Level</option>
                    {educationLevels.map(level => (
                      <option key={level.value} value={level.value}>
                        {level.display}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  School
                </label>
                <input
                  type="text"
                  {...register('school')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="Enter school name"
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_public"
                  {...register('is_public')}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                />
                <label htmlFor="is_public" className="ml-2 text-sm text-gray-700">
                  Make this note public (others can view it)
                </label>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false)
                    setEditingNote(null)
                    reset()
                  }}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                >
                  {editingNote ? 'Update Note' : 'Create Note'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Notes