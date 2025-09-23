/**
 * Timezone utility functions for handling user timezone detection and conversion
 */

/**
 * Get the user's detected timezone
 * @returns {string} IANA timezone identifier (e.g., "Europe/Madrid", "America/New_York")
 */
export function getUserTimezone() {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
  } catch (error) {
    console.warn('Failed to detect user timezone, falling back to UTC:', error);
    return 'UTC';
  }
}

/**
 * Get timezone offset in minutes from UTC
 * @param {string} timezone - IANA timezone identifier
 * @param {Date} date - Date to get offset for
 * @returns {number} Offset in minutes (negative for timezones ahead of UTC)
 */
export function getTimezoneOffset(timezone = getUserTimezone(), date = new Date()) {
  try {
    // Create dates in the specified timezone and UTC
    const utcDate = new Date(date.toISOString());
    const tzDate = new Date(date.toLocaleString('en-US', { timeZone: timezone }));
    
    // Calculate the difference in minutes
    return (utcDate - tzDate) / (1000 * 60);
  } catch (error) {
    console.warn('Failed to calculate timezone offset:', error);
    return 0;
  }
}

/**
 * Convert a local date/time to ISO string with timezone info
 * @param {Date} date - Local date
 * @param {Date} time - Local time
 * @param {string} timezone - Target timezone
 * @returns {string} ISO string with timezone
 */
export function createTimezoneAwareISOString(date, time, timezone = getUserTimezone()) {
  try {
    // Combine date and time
    const combined = new Date(date);
    combined.setHours(time.getHours(), time.getMinutes(), time.getSeconds());
    
    // Format as ISO string but preserve the intended timezone
    return combined.toISOString().replace('Z', getTimezoneOffsetString(timezone, combined));
  } catch (error) {
    console.warn('Failed to create timezone-aware ISO string:', error);
    return new Date(date).toISOString();
  }
}

/**
 * Get timezone offset as a string (+HH:MM or -HH:MM)
 * @param {string} timezone - IANA timezone identifier
 * @param {Date} date - Date to get offset for
 * @returns {string} Offset string like "+02:00" or "-05:00"
 */
export function getTimezoneOffsetString(timezone = getUserTimezone(), date = new Date()) {
  try {
    const offset = getTimezoneOffset(timezone, date);
    const hours = Math.floor(Math.abs(offset) / 60);
    const minutes = Math.abs(offset) % 60;
    const sign = offset <= 0 ? '+' : '-';
    
    return `${sign}${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  } catch (error) {
    console.warn('Failed to get timezone offset string:', error);
    return '+00:00';
  }
}

/**
 * Format a date in the user's timezone
 * @param {Date} date - Date to format
 * @param {Object} options - Intl.DateTimeFormat options
 * @param {string} timezone - Target timezone
 * @returns {string} Formatted date string
 */
export function formatDateInTimezone(date, options = {}, timezone = getUserTimezone()) {
  try {
    return date.toLocaleString('en-US', {
      timeZone: timezone,
      ...options
    });
  } catch (error) {
    console.warn('Failed to format date in timezone:', error);
    return date.toLocaleString();
  }
}

/**
 * Check if a timezone is valid
 * @param {string} timezone - IANA timezone identifier to validate
 * @returns {boolean} True if timezone is valid
 */
export function isValidTimezone(timezone) {
  try {
    Intl.DateTimeFormat(undefined, { timeZone: timezone });
    return true;
  } catch (error) {
    return false;
  }
}