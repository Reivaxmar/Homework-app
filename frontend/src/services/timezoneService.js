/**
 * Timezone service for handling user timezone detection and backend updates
 */

import { getUserTimezone } from '../utils/timezone'
import { authAPI } from './api'

/**
 * Detect and update user timezone on the backend
 * @returns {Promise<boolean>} Success status
 */
export async function detectAndUpdateTimezone() {
  try {
    const detectedTimezone = getUserTimezone()
    
    // For now, just log the detected timezone since we need to add the endpoint to authAPI
    console.log(`Detected timezone: ${detectedTimezone}`)
    
    // TODO: Add timezone update endpoint to authAPI when implemented
    // const response = await authAPI.updateTimezone({ timezone: detectedTimezone })
    
    return true
  } catch (error) {
    console.warn('Failed to update timezone on backend:', error)
    return false
  }
}

/**
 * Format datetime for homework form inputs considering user timezone
 * @param {Date} date - Date to format
 * @param {Date} time - Time to format  
 * @returns {Object} Formatted date and time strings
 */
export function formatDateTimeForInput(date, time) {
  const userTimezone = getUserTimezone()
  
  try {
    // Format date as YYYY-MM-DD
    const dateStr = date.toLocaleDateString('en-CA') // ISO format
    
    // Format time as HH:MM
    const timeStr = time.toLocaleTimeString('en-GB', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit'
    })
    
    return { dateStr, timeStr, timezone: userTimezone }
  } catch (error) {
    console.warn('Failed to format datetime for input:', error)
    return { 
      dateStr: date.toISOString().split('T')[0], 
      timeStr: '23:59', 
      timezone: 'UTC' 
    }
  }
}

/**
 * Parse form input values considering user timezone
 * @param {string} dateStr - Date string from input (YYYY-MM-DD)
 * @param {string} timeStr - Time string from input (HH:MM)
 * @returns {Object} Parsed Date objects
 */
export function parseDateTimeFromInput(dateStr, timeStr) {
  try {
    const [year, month, day] = dateStr.split('-').map(Number)
    const [hours, minutes] = timeStr.split(':').map(Number)
    
    const date = new Date(year, month - 1, day) // month is 0-indexed
    const time = new Date()
    time.setHours(hours, minutes, 0, 0)
    
    return { date, time }
  } catch (error) {
    console.warn('Failed to parse datetime from input:', error)
    const now = new Date()
    return { 
      date: now, 
      time: new Date(now.getTime() + 24 * 60 * 60 * 1000) // tomorrow
    }
  }
}