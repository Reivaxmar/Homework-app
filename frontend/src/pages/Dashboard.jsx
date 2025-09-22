import React, { useState, useEffect } from 'react'
import { BookOpen, CheckSquare, Clock, AlertTriangle, Calendar, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { dashboardAPI, homeworkAPI } from '../services/api'
import { useLanguage } from '../contexts/LanguageContext'
import { format } from 'date-fns'

function Dashboard() {
  const { t } = useLanguage()
  const [summary, setSummary] = useState({
    total_classes: 0,
    pending_homework: 0,
    due_today: 0,
    overdue: 0,
    completed_this_week: 0
  })
  const [dueToday, setDueToday] = useState([])
  const [overdue, setOverdue] = useState([])
  const [dueNextWeek, setDueNextWeek] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [summaryRes, dueTodayRes, overdueRes, dueNextWeekRes] = await Promise.all([
        dashboardAPI.getSummary(),
        homeworkAPI.getDueToday(),
        homeworkAPI.getOverdue(),
        homeworkAPI.getDueNextWeek()
      ])
      
      setSummary(summaryRes.data)
      setDueToday(dueTodayRes.data)
      setOverdue(overdueRes.data)
      setDueNextWeek(dueNextWeekRes.data)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleClearAllData = async () => {
    const confirmed = window.confirm(t('dashboard.clearDataConfirm'))
    
    if (confirmed) {
      try {
        await dashboardAPI.clearAllData()
        toast.success(t('message.dataCleared'))
        // Refresh the dashboard data
        fetchDashboardData()
      } catch (error) {
        toast.error(t('message.clearDataError'))
        console.error('Error clearing data:', error)
      }
    }
  }

  const StatCard = ({ title, value, icon: Icon, color = 'blue' }) => {
    const colorClasses = {
      blue: 'bg-blue-50 text-blue-700',
      green: 'bg-green-50 text-green-700',
      yellow: 'bg-yellow-50 text-yellow-700',
      red: 'bg-red-50 text-red-700',
      purple: 'bg-purple-50 text-purple-700'
    }

    return (
      <div className="card p-6">
        <div className="flex items-center">
          <div className={`rounded-lg p-3 ${colorClasses[color]}`}>
            <Icon className="h-6 w-6" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
          </div>
        </div>
      </div>
    )
  }

  const HomeworkList = ({ title, homework, emptyMessage, color = 'gray' }) => (
    <div className="card">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">{title}</h3>
      </div>
      <div className="p-6">
        {homework.length === 0 ? (
          <p className="text-gray-500 text-center py-4">{emptyMessage}</p>
        ) : (
          <div className="space-y-3">
            {homework.map((item) => (
              <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{item.title}</h4>
                  <p className="text-sm text-gray-600">
                    {t('common.due')}: {format(new Date(item.due_date), 'MMM d, yyyy')} {t('common.at')} {item.due_time || '23:59'}
                  </p>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  color === 'red' 
                    ? 'bg-red-100 text-red-800' 
                    : color === 'blue'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {item.priority}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">{t('dashboard.loading')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('dashboard.title')}</h1>
          <p className="text-gray-600">{t('dashboard.subtitle')}</p>
        </div>
        <button
          onClick={handleClearAllData}
          className="inline-flex items-center px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-red-50 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
        >
          <Trash2 className="h-4 w-4 mr-2" />
          {t('dashboard.clearData')}
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <StatCard
          title={t('dashboard.totalClasses')}
          value={summary.total_classes}
          icon={BookOpen}
          color="blue"
        />
        <StatCard
          title={t('dashboard.pendingHomework')}
          value={summary.pending_homework}
          icon={CheckSquare}
          color="purple"
        />
        <StatCard
          title={t('dashboard.dueToday')}
          value={summary.due_today}
          icon={Clock}
          color="yellow"
        />
        <StatCard
          title={t('dashboard.overdue')}
          value={summary.overdue}
          icon={AlertTriangle}
          color="red"
        />
        <StatCard
          title={t('dashboard.completedWeek')}
          value={summary.completed_this_week}
          icon={Calendar}
          color="green"
        />
      </div>

      {/* Homework Lists */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <HomeworkList
          title={t('dashboard.dueToday.title')}
          homework={dueToday}
          emptyMessage={t('dashboard.dueToday.empty')}
          color="yellow"
        />
        <HomeworkList
          title={t('dashboard.dueNextWeek.title')}
          homework={dueNextWeek}
          emptyMessage={t('dashboard.dueNextWeek.empty')}
          color="blue"
        />
        <HomeworkList
          title={t('dashboard.overdue.title')}
          homework={overdue}
          emptyMessage={t('dashboard.overdue.empty')}
          color="red"
        />
      </div>
    </div>
  )
}

export default Dashboard