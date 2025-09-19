import React, { useState, useEffect } from 'react';
import { scheduleAPI } from '../utils/api';

const ScheduleGrid = () => {
  const [schedule, setSchedule] = useState({
    monday: [],
    tuesday: [],
    wednesday: [],
    thursday: [],
    friday: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
  const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const periods = [1, 2, 3, 4, 5, 6, 7]; // 7 is reading/free time

  useEffect(() => {
    fetchSchedule();
  }, []);

  const fetchSchedule = async () => {
    try {
      setLoading(true);
      const response = await scheduleAPI.getWeekly();
      setSchedule(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load schedule');
      console.error('Error fetching schedule:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSlotForPeriod = (daySchedule, period) => {
    return daySchedule.find(slot => slot.period === period);
  };

  const formatTime = (timeString) => {
    if (!timeString) return '';
    const time = new Date(`2000-01-01T${timeString}`);
    return time.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-600">{error}</p>
        <button 
          onClick={fetchSchedule}
          className="mt-2 btn btn-secondary text-sm"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <h2 className="text-2xl font-bold text-secondary-900 mb-6">Weekly Schedule</h2>
      
      <div className="overflow-x-auto">
        <div className="grid grid-cols-6 gap-2 min-w-full">
          {/* Header row */}
          <div className="p-3 bg-secondary-100 rounded-lg font-semibold text-secondary-700 text-center">
            Period
          </div>
          {dayNames.map((day) => (
            <div key={day} className="p-3 bg-secondary-100 rounded-lg font-semibold text-secondary-700 text-center">
              {day}
            </div>
          ))}

          {/* Schedule rows */}
          {periods.map((period) => (
            <React.Fragment key={period}>
              <div className="p-3 bg-secondary-50 rounded-lg text-center font-medium text-secondary-600">
                {period === 7 ? 'Reading' : `Period ${period}`}
              </div>
              {days.map((day) => {
                const slot = getSlotForPeriod(schedule[day], period);
                return (
                  <div
                    key={`${day}-${period}`}
                    className={`p-3 rounded-lg border-2 border-dashed border-secondary-200 min-h-[80px] ${
                      slot ? 'bg-primary-50 border-primary-200' : 'bg-white hover:bg-secondary-50'
                    }`}
                  >
                    {slot ? (
                      <div className="text-center">
                        {slot.is_reading_time ? (
                          <div>
                            <p className="font-medium text-primary-700">📖 Reading Time</p>
                            <p className="text-xs text-secondary-600 mt-1">
                              {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                            </p>
                          </div>
                        ) : slot.class_ref ? (
                          <div>
                            <p className="font-medium text-primary-700">{slot.class_ref.name}</p>
                            <p className="text-xs text-secondary-600">{slot.class_ref.teacher}</p>
                            <p className="text-xs text-secondary-600 mt-1">
                              {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                            </p>
                          </div>
                        ) : (
                          <div>
                            <p className="text-secondary-500 text-sm">Free Period</p>
                            <p className="text-xs text-secondary-600 mt-1">
                              {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                            </p>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-center text-secondary-400 text-sm">
                        Empty
                      </div>
                    )}
                  </div>
                );
              })}
            </React.Fragment>
          ))}
        </div>
      </div>

      <div className="mt-6 flex justify-center">
        <button className="btn btn-primary">
          ✏️ Edit Schedule
        </button>
      </div>
    </div>
  );
};

export default ScheduleGrid;