import { useEffect, useState } from 'react'
import { Layout } from '../components/Layout'
import api from '../lib/api'
import { format, startOfWeek, addWeeks } from 'date-fns'

export default function Schedule() {
  const [shifts, setShifts] = useState<any[]>([])
  const [weekStart, setWeekStart] = useState(format(startOfWeek(new Date(), { weekStartsOn: 1 }), 'yyyy-MM-dd'))
  const [showRulesModal, setShowRulesModal] = useState(false)

  const days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
  const [ruleCounts, setRuleCounts] = useState<any>({
    mon: 3, tue: 3, wed: 3, thu: 3, fri: 5, sat: 4, sun: 2
  })

  useEffect(() => {
    fetchShifts()
    fetchStaffingRules()
  }, [weekStart])

  const fetchShifts = async () => {
    try {
      const response = await api.get(`/api/schedule/shifts/${weekStart}`)
      setShifts(response.data)
    } catch (error) {
      console.error('Failed to fetch shifts:', error)
    }
  }

  const fetchStaffingRules = async () => {
    try {
      const response = await api.get('/api/schedule/staffing-rules')
      
      // Update counts from existing rules
      const counts: any = { mon: 3, tue: 3, wed: 3, thu: 3, fri: 5, sat: 4, sun: 2 }
      response.data.forEach((rule: any) => {
        counts[rule.day_of_week] = rule.required_count
      })
      setRuleCounts(counts)
    } catch (error) {
      console.error('Failed to fetch staffing rules:', error)
    }
  }

  const saveStaffingRules = async () => {
    try {
      for (const day of days) {
        try {
          await api.post('/api/schedule/staffing-rules', {
            day_of_week: day,
            required_count: ruleCounts[day]
          })
        } catch (error: any) {
          // If already exists, update it
          if (error.response?.status === 400) {
            await api.put(`/api/schedule/staffing-rules/${day}`, {
              required_count: ruleCounts[day]
            })
          }
        }
      }
      alert('Staffing rules saved!')
      setShowRulesModal(false)
      fetchStaffingRules()
    } catch (error) {
      alert('Failed to save staffing rules')
    }
  }

  const generateSchedule = async () => {
    if (!confirm('Generate AI-powered schedule for this week?')) return
    try {
      await api.post('/api/schedule/generate', { week_start: weekStart })
      alert('Schedule generated!')
      fetchShifts()
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to generate schedule'
      alert(message)
    }
  }

  const nextWeek = () => {
    const next = format(addWeeks(new Date(weekStart), 1), 'yyyy-MM-dd')
    setWeekStart(next)
  }

  const prevWeek = () => {
    const prev = format(addWeeks(new Date(weekStart), -1), 'yyyy-MM-dd')
    setWeekStart(prev)
  }

  const groupByDay = () => {
    const days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    const grouped: any = {}
    days.forEach(day => { grouped[day] = [] })
    shifts.forEach(shift => {
      if (grouped[shift.day_of_week]) {
        grouped[shift.day_of_week].push(shift)
      }
    })
    return grouped
  }

  const grouped = groupByDay()

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Schedule</h1>
          <div className="flex gap-3">
            <button 
              onClick={() => setShowRulesModal(true)} 
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Set Staffing Rules
            </button>
            <button 
              onClick={generateSchedule} 
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Generate AI Schedule
            </button>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button onClick={prevWeek} className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">← Prev Week</button>
          <span className="font-medium">Week of {weekStart}</span>
          <button onClick={nextWeek} className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">Next Week →</button>
        </div>

        <div className="grid grid-cols-7 gap-4">
          {Object.entries(grouped).map(([day, dayShifts]: [string, any]) => (
            <div key={day} className="bg-white p-4 rounded-lg shadow">
              <h3 className="font-bold text-center mb-2">{day.toUpperCase()}</h3>
              <div className="space-y-2">
                {dayShifts.length > 0 ? dayShifts.map((shift: any) => (
                  <div key={shift.id} className="text-sm p-2 bg-primary-50 rounded">
                    <p className="font-medium">{shift.employee_name}</p>
                    <p className="text-xs text-gray-600">{shift.start_time} - {shift.end_time}</p>
                  </div>
                )) : (
                  <p className="text-sm text-gray-400 text-center">No shifts</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Staffing Rules Modal */}
      {showRulesModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full">
            <h2 className="text-2xl font-bold mb-4">Set Staffing Requirements</h2>
            <p className="text-gray-600 mb-6">How many employees do you need each day?</p>
            
            <div className="space-y-4">
              {days.map(day => (
                <div key={day} className="flex items-center justify-between">
                  <label className="font-medium capitalize">{day}:</label>
                  <input
                    type="number"
                    min="0"
                    max="20"
                    value={ruleCounts[day]}
                    onChange={(e) => setRuleCounts({...ruleCounts, [day]: parseInt(e.target.value) || 0})}
                    className="w-20 px-3 py-2 border rounded-lg"
                  />
                </div>
              ))}
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowRulesModal(false)}
                className="flex-1 px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                onClick={saveStaffingRules}
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Save Rules
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}
