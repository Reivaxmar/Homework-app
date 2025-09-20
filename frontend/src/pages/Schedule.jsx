import React, { useState, useEffect } from 'react'
import { Plus, Edit2, Save, X } from 'lucide-react'
import toast from 'react-hot-toast'
import { schedulesAPI, classesAPI } from '../services/api'
import { format } from 'date-fns'

const DAYS = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
const DAY_NAMES = {
  MONDAY: 'Monday',
  TUESDAY: 'Tuesday',
  WEDNESDAY: 'Wednesday',
  THURSDAY: 'Thursday',
  FRIDAY: 'Friday'
}

const DEFAULT_TIMES = [
  { start: '08:00', end: '08:50' },
  { start: '09:00', end: '09:50' },
  { start: '10:10', end: '11:00' },
  { start: '11:10', end: '12:00' },
  { start: '12:30', end: '13:20' },
  { start: '13:30', end: '14:20' }
]

function Schedule() {
  const [schedule, setSchedule] = useState(null)
  const [classes, setClasses] = useState([])
  const [slots, setSlots] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingSlot, setEditingSlot] = useState(null)
  const [isCreating, setIsCreating] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [classesRes] = await Promise.all([
        classesAPI.getAll()
      ])
      
      setClasses(classesRes.data)
      
      // Try to get active schedule for current year
      const currentYear = new Date().getFullYear()
      try {
        const scheduleRes = await schedulesAPI.getActive(`${currentYear}-${currentYear + 1}`)
        setSchedule(scheduleRes.data)
        
        const slotsRes = await schedulesAPI.getSlots(scheduleRes.data.id)
        setSlots(slotsRes.data)
      } catch (scheduleError) {
        // No active schedule exists, create one
        await createDefaultSchedule()
      }
    } catch (error) {
      toast.error('Failed to fetch data')
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const createDefaultSchedule = async () => {
    try {
      const currentYear = new Date().getFullYear()
      const scheduleData = {
        name: 'Default Schedule',
        year: `${currentYear}-${currentYear + 1}`
      }
      
      const scheduleRes = await schedulesAPI.create(scheduleData)
      setSchedule(scheduleRes.data)
      
      // Create default empty slots
      const defaultSlots = []
      DAYS.forEach(day => {
        DEFAULT_TIMES.forEach((time, index) => {
          defaultSlots.push({
            day,
            slot_number: index + 1,
            start_time: time.start,
            end_time: time.end,
            slot_type: index === 5 ? 'READING' : 'CLASS', // Last slot is reading time
            schedule_id: scheduleRes.data.id
          })
        })
      })
      
      // Create all slots
      const createdSlots = []
      for (const slotData of defaultSlots) {
        const slotRes = await schedulesAPI.createSlot(scheduleRes.data.id, slotData)
        createdSlots.push(slotRes.data)
      }
      
      setSlots(createdSlots)
      toast.success('Default schedule created')
    } catch (error) {
      toast.error('Failed to create schedule')
      console.error('Error creating schedule:', error)
    }
  }

  const getSlotForDayAndPeriod = (day, period) => {
    return slots.find(slot => slot.day === day && slot.slot_number === period)
  }

  const getClassById = (classId) => {
    return classes.find(c => c.id === classId)
  }

  const handleSlotEdit = (slot) => {
    setEditingSlot(slot)
  }

  const handleSlotSave = async (slot, classId) => {
    try {
      const updateData = { class_id: classId || null }
      await schedulesAPI.updateSlot(schedule.id, slot.id, updateData)
      
      // Update local state
      setSlots(slots.map(s => 
        s.id === slot.id 
          ? { ...s, class_id: classId, class_: classId ? getClassById(classId) : null }
          : s
      ))
      
      setEditingSlot(null)
      toast.success('Slot updated successfully')
    } catch (error) {
      toast.error('Failed to update slot')
      console.error('Error updating slot:', error)
    }
  }

  const SlotCell = ({ day, period }) => {
    const slot = getSlotForDayAndPeriod(day, period)
    const isEditing = editingSlot?.id === slot?.id
    
    if (!slot) return <div className="p-2 border border-gray-200 bg-gray-50"></div>

    if (isEditing) {
      return (
        <div className="p-2 border border-gray-200 bg-white">
          <select
            className="w-full text-xs p-1 border rounded"
            defaultValue={slot.class_id || ''}
            onChange={(e) => handleSlotSave(slot, e.target.value ? parseInt(e.target.value) : null)}
            onBlur={() => setEditingSlot(null)}
            autoFocus
          >
            <option value="">-- Select Class --</option>
            {slot.slot_type === 'READING' && <option value="">Reading Time</option>}
            {slot.slot_type === 'FREE' && <option value="">Free Time</option>}
            {classes.map(cls => (
              <option key={cls.id} value={cls.id}>{cls.name}</option>
            ))}
          </select>
        </div>
      )
    }

    const classInfo = slot.class_id ? getClassById(slot.class_id) : null
    const isEmpty = !classInfo && slot.slot_type === 'CLASS'
    
    return (
      <div
        className={`p-2 border border-gray-200 cursor-pointer hover:bg-gray-50 min-h-[60px] ${
          isEmpty ? 'bg-gray-50' : ''
        }`}
        onClick={() => handleSlotEdit(slot)}
        style={classInfo ? { backgroundColor: classInfo.color + '20' } : {}}
      >
        {classInfo ? (
          <div className="text-xs">
            <div className="font-medium text-gray-900">{classInfo.name}</div>
            <div className="text-gray-600">{classInfo.teacher}</div>
            {classInfo.half_group && (
              <div className="text-gray-500">Group {classInfo.half_group}</div>
            )}
          </div>
        ) : slot.slot_type === 'READING' ? (
          <div className="text-xs text-gray-600 font-medium">📚 Reading Time</div>
        ) : slot.slot_type === 'FREE' ? (
          <div className="text-xs text-gray-600 font-medium">🕐 Free Time</div>
        ) : (
          <div className="text-xs text-gray-400">Click to assign</div>
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading schedule...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Schedule</h1>
          <p className="text-gray-600">
            {schedule ? `${schedule.name} - ${schedule.year}` : 'Manage your weekly schedule'}
          </p>
        </div>
      </div>

      {schedule ? (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[100px]">
                    Time
                  </th>
                  {DAYS.map(day => (
                    <th key={day} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[160px]">
                      {DAY_NAMES[day]}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {DEFAULT_TIMES.map((time, period) => (
                  <tr key={period}>
                    <td className="px-4 py-2 bg-gray-50 border-r border-gray-200">
                      <div className="text-sm font-medium text-gray-900">
                        Period {period + 1}
                      </div>
                      <div className="text-xs text-gray-600">
                        {time.start} - {time.end}
                      </div>
                    </td>
                    {DAYS.map(day => (
                      <td key={day} className="p-0">
                        <SlotCell day={day} period={period + 1} />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No schedule found</h3>
            <p className="text-gray-600 mb-4">Create a schedule to get started</p>
            <button
              onClick={createDefaultSchedule}
              className="btn btn-primary"
            >
              Create Schedule
            </button>
          </div>
        </div>
      )}

      <div className="card p-4">
        <h3 className="text-sm font-medium text-gray-900 mb-2">Instructions:</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Click on any slot to assign a class</li>
          <li>• Last period (6th) is reserved for reading time by default</li>
          <li>• Each slot is 50 minutes with 10-minute breaks</li>
          <li>• Lunch break is from 12:00-12:30</li>
        </ul>
      </div>
    </div>
  )
}

export default Schedule