import React from 'react';

const ClassCard = ({ classData, onEdit, onDelete }) => {
  return (
    <div className="card p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-secondary-900">{classData.name}</h3>
          <p className="text-secondary-600">👨‍🏫 {classData.teacher}</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => onEdit(classData)}
            className="text-primary-600 hover:text-primary-800 p-1"
            title="Edit class"
          >
            ✏️
          </button>
          <button
            onClick={() => onDelete(classData.id)}
            className="text-red-600 hover:text-red-800 p-1"
            title="Delete class"
          >
            🗑️
          </button>
        </div>
      </div>
      
      <div className="space-y-2">
        <div className="flex items-center text-sm text-secondary-600">
          <span className="w-16">📅 Year:</span>
          <span>{classData.year}</span>
        </div>
        
        {classData.half_group && (
          <div className="flex items-center text-sm text-secondary-600">
            <span className="w-16">👥 Group:</span>
            <span>{classData.half_group}</span>
          </div>
        )}
        
        <div className="flex items-center text-sm text-secondary-600">
          <span className="w-16">📝 Created:</span>
          <span>{new Date(classData.created_at).toLocaleDateString()}</span>
        </div>
      </div>
    </div>
  );
};

export default ClassCard;