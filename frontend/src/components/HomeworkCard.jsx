import React from 'react';
import { format, isPast, isToday, isTomorrow } from 'date-fns';

const HomeworkCard = ({ homework, onToggleComplete, onEdit, onDelete }) => {
  const dueDate = new Date(homework.due_date);
  const isOverdue = isPast(dueDate) && !homework.completed;
  
  const getDueDateDisplay = () => {
    if (isToday(dueDate)) return 'Due today';
    if (isTomorrow(dueDate)) return 'Due tomorrow';
    if (isPast(dueDate)) return 'Overdue';
    return `Due ${format(dueDate, 'MMM d, yyyy')}`;
  };

  const getPriorityColor = () => {
    switch (homework.priority) {
      case 'high': return 'text-red-600 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-green-600 bg-green-50';
      default: return 'text-secondary-600 bg-secondary-50';
    }
  };

  const getDueDateColor = () => {
    if (homework.completed) return 'text-green-600';
    if (isOverdue) return 'text-red-600';
    if (isToday(dueDate)) return 'text-orange-600';
    return 'text-secondary-600';
  };

  return (
    <div className={`card p-4 transition-all ${
      homework.completed ? 'opacity-75 bg-green-50' : ''
    } ${isOverdue ? 'border-red-200' : ''}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-start space-x-3">
          <button
            onClick={() => onToggleComplete(homework.id)}
            className={`mt-1 w-5 h-5 rounded border-2 flex items-center justify-center ${
              homework.completed
                ? 'bg-green-500 border-green-500 text-white'
                : 'border-secondary-300 hover:border-primary-500'
            }`}
          >
            {homework.completed && '✓'}
          </button>
          <div className="flex-1">
            <h3 className={`font-semibold ${
              homework.completed ? 'line-through text-secondary-500' : 'text-secondary-900'
            }`}>
              {homework.title}
            </h3>
            <p className="text-sm text-primary-600 font-medium">
              📚 {homework.class_ref.name}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor()}`}>
            {homework.priority}
          </span>
          <div className="flex space-x-1">
            <button
              onClick={() => onEdit(homework)}
              className="text-primary-600 hover:text-primary-800 p-1"
              title="Edit homework"
            >
              ✏️
            </button>
            <button
              onClick={() => onDelete(homework.id)}
              className="text-red-600 hover:text-red-800 p-1"
              title="Delete homework"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>

      {homework.description && (
        <p className={`text-sm mb-3 ${
          homework.completed ? 'text-secondary-400' : 'text-secondary-600'
        }`}>
          {homework.description}
        </p>
      )}

      <div className="flex items-center justify-between text-sm">
        <span className={`font-medium ${getDueDateColor()}`}>
          📅 {getDueDateDisplay()}
        </span>
        <span className="text-secondary-500">
          {format(dueDate, 'h:mm a')}
        </span>
      </div>
    </div>
  );
};

export default HomeworkCard;