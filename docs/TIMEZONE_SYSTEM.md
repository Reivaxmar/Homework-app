# Timezone System Documentation

This document explains the timezone handling improvements implemented to fix Google Calendar sync issues.

## Problem Statement

The original system had a critical flaw: it assumed all times were in UTC (timezone 0), causing issues for users in other timezones. For example, a homework due at 11:59 PM in UTC+2 would appear at 1:59 AM the next day in Google Calendar.

## Solution Overview

The new system:
1. **Detects user timezone** automatically using browser APIs
2. **Stores timezone preference** in the user's profile
3. **Converts times properly** when creating calendar events
4. **Preserves local time context** throughout the application

## Technical Implementation

### Frontend Components

#### 1. Timezone Detection (`frontend/src/utils/timezone.js`)
```javascript
// Automatically detect user's timezone
const userTimezone = getUserTimezone(); // e.g., "Europe/Madrid"

// Get timezone offset
const offset = getTimezoneOffset("Europe/Madrid"); // -120 (minutes from UTC)

// Format dates in user's timezone
const formatted = formatDateInTimezone(new Date(), {}, "Europe/Madrid");
```

#### 2. Timezone Service (`frontend/src/services/timezoneService.js`)
```javascript
// Auto-detect and update user timezone on backend
await detectAndUpdateTimezone();

// Format datetime for form inputs
const { dateStr, timeStr } = formatDateTimeForInput(date, time);

// Parse form inputs considering timezone
const { date, time } = parseDateTimeFromInput("2024-03-15", "23:59");
```

### Backend Components

#### 1. User Model (`backend/app/models/user.py`)
```python
class User(Base):
    # ... existing fields ...
    timezone = Column(String(50), nullable=True, default='UTC')
    
    def get_timezone(self):
        """Get user's timezone, defaulting to UTC if not set"""
        return self.timezone or 'UTC'
```

#### 2. Google Calendar Service (`backend/app/services/google_calendar.py`)
```python
def _localize_datetime(self, dt):
    """Convert naive datetime to user's timezone"""
    user_tz = self._get_user_timezone()
    if dt.tzinfo is None:
        return user_tz.localize(dt)
    return dt.astimezone(user_tz)

def create_homework_event(self, homework: Homework):
    # Combine date and time as user's local time
    due_datetime = datetime.combine(homework.due_date, homework.due_time)
    
    # Localize to user's timezone
    due_datetime_localized = self._localize_datetime(due_datetime)
    
    # Create event with proper timezone
    event = {
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': user_timezone,  # e.g., "Europe/Madrid"
        },
        'end': {
            'dateTime': due_datetime_localized.isoformat(), 
            'timeZone': user_timezone,
        }
    }
```

#### 3. Auth Endpoints (`backend/app/routers/auth.py`)
```python
@router.put("/me/timezone")
async def update_user_timezone(timezone_update: TimezoneUpdateRequest):
    """Update user timezone with validation"""
    # Validate timezone using pytz
    pytz.timezone(timezone_update.timezone)
    current_user.timezone = timezone_update.timezone
```

## Usage Examples

### Scenario: User in Madrid (UTC+2)

**Before (Broken):**
- User sets homework due: March 15, 2024 at 11:59 PM
- System creates calendar event: March 15, 2024 at 11:59 PM UTC
- Google Calendar shows: March 16, 2024 at 1:59 AM (next day!)

**After (Fixed):**
- User sets homework due: March 15, 2024 at 11:59 PM
- System detects timezone: "Europe/Madrid"  
- System creates calendar event: March 15, 2024 at 11:59 PM Europe/Madrid
- Google Calendar shows: March 15, 2024 at 11:59 PM (correct!)

### Integration in Components

#### Homework Form
```jsx
import { detectAndUpdateTimezone, formatDateTimeForInput } from '../services/timezoneService'

function HomeworkForm() {
  useEffect(() => {
    // Auto-detect timezone on component mount
    detectAndUpdateTimezone()
  }, [])
  
  const handleSubmit = (data) => {
    // Timezone is automatically handled in backend
    // User inputs are interpreted as local time
  }
}
```

#### Calendar Integration
```python
# Backend automatically handles timezone conversion
calendar_service = GoogleCalendarService(user)
event_id = calendar_service.create_homework_event(homework)

# Event is created with user's timezone:
# - start: 2024-03-15T22:59:00+02:00 (1 hour before due)
# - end:   2024-03-15T23:59:00+02:00 (due time)
# - timeZone: "Europe/Madrid"
```

## Database Migration

To add the timezone field to existing users:

```sql
-- Add timezone column to users table
ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';

-- Update existing users to UTC (safe default)
UPDATE users SET timezone = 'UTC' WHERE timezone IS NULL;
```

## Supported Timezones

The system uses IANA timezone identifiers, supporting all standard timezones:
- `UTC` - Coordinated Universal Time
- `Europe/Madrid` - Central European Time
- `America/New_York` - Eastern Time
- `Asia/Tokyo` - Japan Standard Time
- `Australia/Sydney` - Australian Eastern Time
- And many more...

## Testing

### Manual Testing Steps

1. **Set system timezone** to UTC+2 (e.g., Madrid)
2. **Create homework** due at 11:59 PM today
3. **Check Google Calendar** - should show 11:59 PM same day
4. **Change timezone** to UTC-5 (e.g., New York)
5. **Create homework** due at 11:59 PM
6. **Verify** calendar event respects new timezone

### Automated Testing

```javascript
// Test timezone detection
test('getUserTimezone returns valid IANA identifier', () => {
  const tz = getUserTimezone()
  expect(isValidTimezone(tz)).toBe(true)
})

// Test timezone conversion
test('calendar event respects user timezone', async () => {
  const user = { timezone: 'Europe/Madrid' }
  const homework = { due_date: '2024-03-15', due_time: '23:59' }
  
  const event = await createCalendarEvent(user, homework)
  expect(event.start.timeZone).toBe('Europe/Madrid')
  expect(event.end.timeZone).toBe('Europe/Madrid')
})
```

## Troubleshooting

### Common Issues

1. **"Invalid timezone" error**
   - Ensure timezone is valid IANA identifier
   - Check browser compatibility for `Intl.DateTimeFormat`

2. **Calendar events in wrong timezone**
   - Verify user timezone is set correctly
   - Check backend logs for timezone conversion errors

3. **Timezone not detected**
   - Fallback to UTC is automatic
   - User can manually set timezone via API

### Debug Information

```javascript
// Log timezone info for debugging
console.log('Detected timezone:', getUserTimezone())
console.log('Timezone offset:', getTimezoneOffset())
console.log('User agent timezone:', Intl.DateTimeFormat().resolvedOptions().timeZone)
```

## Performance Considerations

- **Timezone detection** runs once per session
- **Translation files** are cached after first load
- **pytz library** provides fast timezone calculations
- **Calendar API calls** include timezone in request (no server-side conversion needed)

## Security Notes

- Timezone information is **not sensitive data**
- User can update timezone via authenticated API
- Invalid timezones are **validated and rejected**
- Fallback to UTC prevents application errors