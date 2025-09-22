import React, { createContext, useContext, useState, useEffect } from 'react'

const LanguageContext = createContext()

export const useLanguage = () => {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}

const translations = {
  en: {
    // Navigation
    'nav.dashboard': 'Dashboard',
    'nav.classes': 'Classes',
    'nav.schedule': 'Schedule',
    'nav.homework': 'Homework',
    'nav.signOut': 'Sign out',
    'app.title': 'Homework App',
    
    // Dashboard
    'dashboard.title': 'Dashboard',
    'dashboard.subtitle': 'Overview of your classes and assignments',
    'dashboard.totalClasses': 'Total Classes',
    'dashboard.pendingHomework': 'Pending Homework',
    'dashboard.dueToday': 'Due Today',
    'dashboard.overdue': 'Overdue',
    'dashboard.completedWeek': 'Completed This Week',
    'dashboard.clearData': 'Clear All Data',
    'dashboard.loading': 'Loading dashboard...',
    'dashboard.dueToday.title': 'Due Today',
    'dashboard.dueToday.empty': 'No homework due today!',
    'dashboard.overdue.title': 'Overdue',
    'dashboard.overdue.empty': 'No overdue homework!',
    'dashboard.dueNextWeek.title': 'Due Next Week',
    'dashboard.dueNextWeek.empty': 'No homework due next week!',
    'dashboard.clearDataConfirm': 'Are you sure you want to remove ALL data? This will permanently delete:\n\n• All classes\n• All homework assignments\n• All schedules\n\nThis action cannot be undone!',
    
    // Classes
    'classes.title': 'Classes',
    'classes.subtitle': 'Manage your classes and subjects',
    'classes.addClass': 'Add Class',
    'classes.editClass': 'Edit Class',
    'classes.createClass': 'Create Class',
    'classes.updateClass': 'Update Class',
    'classes.cancel': 'Cancel',
    'classes.className': 'Class Name',
    'classes.classType': 'Class Type',
    'classes.color': 'Color',
    'classes.selectClassType': 'Select a class type',
    'classes.loading': 'Loading classes...',
    'classes.noClasses': 'No classes yet',
    'classes.noClassesDesc': 'Get started by adding your first class',
    'classes.students': 'students',
    'classes.edit': 'Edit',
    'classes.delete': 'Delete',
    'classes.classNameRequired': 'Class name is required',
    'classes.classTypeRequired': 'Class type is required',
    'classes.created': 'Class created successfully',
    'classes.updated': 'Class updated successfully',
    'classes.deleted': 'Class deleted successfully',
    'classes.createError': 'Failed to create class',
    'classes.updateError': 'Failed to update class',
    'classes.deleteError': 'Failed to delete class',
    
    // Class types
    'classType.maths': 'Maths',
    'classType.english': 'English',
    'classType.science': 'Science',
    'classType.history': 'History',
    'classType.geography': 'Geography',
    'classType.art': 'Art',
    'classType.music': 'Music',
    'classType.physicalEducation': 'Physical Education',
    'classType.computerScience': 'Computer Science',
    'classType.foreignLanguage': 'Foreign Language',
    'classType.literature': 'Literature',
    'classType.chemistry': 'Chemistry',
    'classType.physics': 'Physics',
    'classType.biology': 'Biology',
    'classType.other': 'Other',
    
    // Homework
    'homework.title': 'Homework',
    'homework.subtitle': 'Manage your assignments and due dates',
    'homework.addHomework': 'Add Homework',
    'homework.editHomework': 'Edit Homework',
    'homework.createHomework': 'Create Homework',
    'homework.updateHomework': 'Update Homework',
    'homework.cancel': 'Cancel',
    'homework.homeworkTitle': 'Title',
    'homework.description': 'Description (Optional)',
    'homework.class': 'Class',
    'homework.dueDate': 'Due Date',
    'homework.dueTime': 'Due Time',
    'homework.priority': 'Priority',
    'homework.status': 'Status',
    'homework.selectClass': 'Select a class',
    'homework.selectPriority': 'Select priority',
    'homework.selectStatus': 'Select status',
    'homework.loading': 'Loading homework...',
    'homework.noHomework': 'No homework yet',
    'homework.noHomeworkDesc': 'Get started by adding your first assignment',
    'homework.noPending': 'No pending homework',
    'homework.noDueToday': 'No due today homework',
    'homework.noOverdue': 'No overdue homework',
    'homework.noCompleted': 'No completed homework',
    'homework.tryFilter': 'Try changing the filter',
    'homework.titleRequired': 'Title is required',
    'homework.classRequired': 'Class is required',
    'homework.dueDateRequired': 'Due date is required',
    'homework.created': 'Homework created successfully',
    'homework.updated': 'Homework updated successfully',
    'homework.deleted': 'Homework deleted successfully',
    'homework.createError': 'Failed to create homework',
    'homework.updateError': 'Failed to update homework',
    'homework.deleteError': 'Failed to delete homework',
    'homework.descriptionPlaceholder': 'Additional details about the assignment...',
    
    // Filters
    'filter.all': 'All',
    'filter.pending': 'Pending',
    'filter.dueToday': 'Due Today',
    'filter.overdue': 'Overdue',
    'filter.completed': 'Completed',
    
    // Priorities
    'priority.low': 'Low',
    'priority.medium': 'Medium',
    'priority.high': 'High',
    
    // Status
    'status.pending': 'Pending',
    'status.inProgress': 'In Progress',
    'status.completed': 'Completed',
    
    // Login
    'login.title': 'Welcome to Homework Management',
    'login.subtitle': 'Sign in to manage your classes and assignments',
    'login.signInWithGoogle': 'Sign in with Google',
    'login.redirecting': 'Redirecting to Google...',
    'login.signInError': 'Failed to sign in with Google. Please try again.',
    'login.feature1': 'Track homework and assignments',
    'login.feature2': 'Organize classes and schedules',
    'login.feature3': 'Automatic Google Calendar sync',
    'login.feature4': 'Priority-based task management',
    'login.feature5': 'Due date reminders',
    'login.feature6': 'Progress tracking',
    
    // Common
    'common.loading': 'Loading...',
    'common.edit': 'Edit',
    'common.delete': 'Delete',
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    'common.confirm': 'Confirm',
    'common.yes': 'Yes',
    'common.no': 'No',
    'common.close': 'Close',
    'common.due': 'Due',
    'common.at': 'at',
    'common.language': 'Language',
    'common.english': 'English',
    'common.spanish': 'Spanish',
    
    // Messages
    'message.logoutSuccess': 'Logged out successfully',
    'message.dataCleared': 'All data cleared successfully',
    'message.clearDataError': 'Failed to clear data'
  },
  
  es: {
    // Navigation
    'nav.dashboard': 'Panel',
    'nav.classes': 'Clases',
    'nav.schedule': 'Horario',
    'nav.homework': 'Tareas',
    'nav.signOut': 'Cerrar sesión',
    'app.title': 'App de Tareas',
    
    // Dashboard
    'dashboard.title': 'Panel',
    'dashboard.subtitle': 'Resumen de tus clases y tareas',
    'dashboard.totalClasses': 'Total de Clases',
    'dashboard.pendingHomework': 'Tareas Pendientes',
    'dashboard.dueToday': 'Vencen Hoy',
    'dashboard.overdue': 'Atrasadas',
    'dashboard.completedWeek': 'Completadas Esta Semana',
    'dashboard.clearData': 'Borrar Todos los Datos',
    'dashboard.loading': 'Cargando panel...',
    'dashboard.dueToday.title': 'Vencen Hoy',
    'dashboard.dueToday.empty': '¡No hay tareas que venzan hoy!',
    'dashboard.overdue.title': 'Atrasadas',
    'dashboard.overdue.empty': '¡No hay tareas atrasadas!',
    'dashboard.dueNextWeek.title': 'Vencen la Próxima Semana',
    'dashboard.dueNextWeek.empty': '¡No hay tareas que venzan la próxima semana!',
    'dashboard.clearDataConfirm': '¿Estás seguro de que quieres eliminar TODOS los datos? Esto eliminará permanentemente:\n\n• Todas las clases\n• Todas las tareas\n• Todos los horarios\n\n¡Esta acción no se puede deshacer!',
    
    // Classes
    'classes.title': 'Clases',
    'classes.subtitle': 'Gestiona tus clases y materias',
    'classes.addClass': 'Agregar Clase',
    'classes.editClass': 'Editar Clase',
    'classes.createClass': 'Crear Clase',
    'classes.updateClass': 'Actualizar Clase',
    'classes.cancel': 'Cancelar',
    'classes.className': 'Nombre de la Clase',
    'classes.classType': 'Tipo de Clase',
    'classes.color': 'Color',
    'classes.selectClassType': 'Selecciona un tipo de clase',
    'classes.loading': 'Cargando clases...',
    'classes.noClasses': 'Aún no hay clases',
    'classes.noClassesDesc': 'Comienza agregando tu primera clase',
    'classes.students': 'estudiantes',
    'classes.edit': 'Editar',
    'classes.delete': 'Eliminar',
    'classes.classNameRequired': 'El nombre de la clase es obligatorio',
    'classes.classTypeRequired': 'El tipo de clase es obligatorio',
    'classes.created': 'Clase creada exitosamente',
    'classes.updated': 'Clase actualizada exitosamente',
    'classes.deleted': 'Clase eliminada exitosamente',
    'classes.createError': 'Error al crear la clase',
    'classes.updateError': 'Error al actualizar la clase',
    'classes.deleteError': 'Error al eliminar la clase',
    
    // Class types
    'classType.maths': 'Matemáticas',
    'classType.english': 'Inglés',
    'classType.science': 'Ciencias',
    'classType.history': 'Historia',
    'classType.geography': 'Geografía',
    'classType.art': 'Arte',
    'classType.music': 'Música',
    'classType.physicalEducation': 'Educación Física',
    'classType.computerScience': 'Informática',
    'classType.foreignLanguage': 'Idioma Extranjero',
    'classType.literature': 'Literatura',
    'classType.chemistry': 'Química',
    'classType.physics': 'Física',
    'classType.biology': 'Biología',
    'classType.other': 'Otro',
    
    // Homework
    'homework.title': 'Tareas',
    'homework.subtitle': 'Gestiona tus tareas y fechas de entrega',
    'homework.addHomework': 'Agregar Tarea',
    'homework.editHomework': 'Editar Tarea',
    'homework.createHomework': 'Crear Tarea',
    'homework.updateHomework': 'Actualizar Tarea',
    'homework.cancel': 'Cancelar',
    'homework.homeworkTitle': 'Título',
    'homework.description': 'Descripción (Opcional)',
    'homework.class': 'Clase',
    'homework.dueDate': 'Fecha de Entrega',
    'homework.dueTime': 'Hora de Entrega',
    'homework.priority': 'Prioridad',
    'homework.status': 'Estado',
    'homework.selectClass': 'Selecciona una clase',
    'homework.selectPriority': 'Selecciona prioridad',
    'homework.selectStatus': 'Selecciona estado',
    'homework.loading': 'Cargando tareas...',
    'homework.noHomework': 'Aún no hay tareas',
    'homework.noHomeworkDesc': 'Comienza agregando tu primera tarea',
    'homework.noPending': 'No hay tareas pendientes',
    'homework.noDueToday': 'No hay tareas que venzan hoy',
    'homework.noOverdue': 'No hay tareas atrasadas',
    'homework.noCompleted': 'No hay tareas completadas',
    'homework.tryFilter': 'Intenta cambiar el filtro',
    'homework.titleRequired': 'El título es obligatorio',
    'homework.classRequired': 'La clase es obligatoria',
    'homework.dueDateRequired': 'La fecha de entrega es obligatoria',
    'homework.created': 'Tarea creada exitosamente',
    'homework.updated': 'Tarea actualizada exitosamente',
    'homework.deleted': 'Tarea eliminada exitosamente',
    'homework.createError': 'Error al crear la tarea',
    'homework.updateError': 'Error al actualizar la tarea',
    'homework.deleteError': 'Error al eliminar la tarea',
    'homework.descriptionPlaceholder': 'Detalles adicionales sobre la tarea...',
    
    // Filters
    'filter.all': 'Todas',
    'filter.pending': 'Pendientes',
    'filter.dueToday': 'Vencen Hoy',
    'filter.overdue': 'Atrasadas',
    'filter.completed': 'Completadas',
    
    // Priorities
    'priority.low': 'Baja',
    'priority.medium': 'Media',
    'priority.high': 'Alta',
    
    // Status
    'status.pending': 'Pendiente',
    'status.inProgress': 'En Progreso',
    'status.completed': 'Completada',
    
    // Login
    'login.title': 'Bienvenido a la Gestión de Tareas',
    'login.subtitle': 'Inicia sesión para gestionar tus clases y tareas',
    'login.signInWithGoogle': 'Iniciar sesión con Google',
    'login.redirecting': 'Redirigiendo a Google...',
    'login.signInError': 'Error al iniciar sesión con Google. Por favor, inténtalo de nuevo.',
    'login.feature1': 'Seguimiento de tareas y asignaciones',
    'login.feature2': 'Organización de clases y horarios',
    'login.feature3': 'Sincronización automática con Google Calendar',
    'login.feature4': 'Gestión de tareas por prioridad',
    'login.feature5': 'Recordatorios de fechas de entrega',
    'login.feature6': 'Seguimiento del progreso',
    
    // Common
    'common.loading': 'Cargando...',
    'common.edit': 'Editar',
    'common.delete': 'Eliminar',
    'common.save': 'Guardar',
    'common.cancel': 'Cancelar',
    'common.confirm': 'Confirmar',
    'common.yes': 'Sí',
    'common.no': 'No',
    'common.close': 'Cerrar',
    'common.due': 'Vence',
    'common.at': 'a las',
    'common.language': 'Idioma',
    'common.english': 'Inglés',
    'common.spanish': 'Español',
    
    // Messages
    'message.logoutSuccess': 'Sesión cerrada exitosamente',
    'message.dataCleared': 'Todos los datos eliminados exitosamente',
    'message.clearDataError': 'Error al eliminar los datos'
  }
}

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    // Get language from localStorage or default to English
    return localStorage.getItem('language') || 'en'
  })

  useEffect(() => {
    // Save language preference to localStorage
    localStorage.setItem('language', language)
  }, [language])

  const t = (key) => {
    return translations[language][key] || key
  }

  const changeLanguage = (newLanguage) => {
    if (translations[newLanguage]) {
      setLanguage(newLanguage)
    }
  }

  const value = {
    language,
    changeLanguage,
    t,
    availableLanguages: Object.keys(translations)
  }

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  )
}