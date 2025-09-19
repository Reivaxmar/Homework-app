import React from 'react';
import ScheduleGrid from '../components/ScheduleGrid';

const Schedule = () => {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-secondary-900">📅 My Schedule</h1>
        <p className="mt-2 text-secondary-600">
          View your weekly class schedule with reading periods
        </p>
      </div>
      
      <ScheduleGrid />
    </div>
  );
};

export default Schedule;