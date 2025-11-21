import { useEffect, useState } from 'react'
import { Layout } from '../components/Layout'
import api from '../lib/api'
import { DollarSign, TrendingUp, TrendingDown, PieChart } from 'lucide-react'

export default function Money() {
  const [financials, setFinancials] = useState<any[]>([])
  const [summary, setSummary] = useState<any>(null)
  const [showForm, setShowForm] = useState(false)
  const [selectedWeek, setSelectedWeek] = useState<any>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    week_start: '',
    gross_sales: 0,
    payroll: 0,
    cogs: 0,
    rent: 0,
    utilities: 0,
    supplies: 0,
    marketing: 0,
    maintenance: 0,
    insurance: 0,
    processing_fees: 0,
    other_expenses: 0
  })

  useEffect(() => {
    fetchFinancials()
    fetchSummary()
  }, [])

  const fetchFinancials = async () => {
    try {
      const response = await api.get('/api/financials/')
      setFinancials(response.data)
    } catch (error) {
      console.error('Failed to fetch financials:', error)
    }
  }

  const fetchSummary = async () => {
    try {
      const response = await api.get('/api/financials/summary')
      setSummary(response.data)
    } catch (error) {
      console.error('Failed to fetch summary:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (isEditing && selectedWeek) {
        // Update existing record
        await api.put(`/api/financials/${selectedWeek.week_start}`, formData)
        setIsEditing(false)
        setSelectedWeek(null)
      } else {
        // Create new record
        await api.post('/api/financials/', formData)
      }
      setShowForm(false)
      setFormData({
        week_start: '',
        gross_sales: 0,
        payroll: 0,
        cogs: 0,
        rent: 0,
        utilities: 0,
        supplies: 0,
        marketing: 0,
        maintenance: 0,
        insurance: 0,
        processing_fees: 0,
        other_expenses: 0
      })
      fetchFinancials()
      fetchSummary()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to save record')
    }
  }

  const handleViewWeek = (record: any) => {
    setSelectedWeek(record)
  }

  const handleEditWeek = (record: any) => {
    setFormData({
      week_start: record.week_start,
      gross_sales: record.gross_sales,
      payroll: record.payroll,
      cogs: record.cogs,
      rent: record.rent,
      utilities: record.utilities,
      supplies: record.supplies,
      marketing: record.marketing,
      maintenance: record.maintenance,
      insurance: record.insurance,
      processing_fees: record.processing_fees,
      other_expenses: record.other_expenses
    })
    setSelectedWeek(record)
    setIsEditing(true)
    setShowForm(true)
  }

  const handleCloseDetail = () => {
    setSelectedWeek(null)
    setIsEditing(false)
  }

  const getStatusColor = (status: string) => {
    if (status === 'green') return 'bg-green-100 text-green-800'
    if (status === 'yellow') return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Financial Dashboard</h1>
            <p className="text-gray-600">Track revenue, expenses, and profitability</p>
          </div>
          <button 
            onClick={() => setShowForm(!showForm)} 
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center gap-2"
          >
            <DollarSign size={20} />
            {showForm ? 'Cancel' : 'Add Financial Record'}
          </button>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Revenue</p>
                  <p className="text-2xl font-bold text-gray-900">${summary.total_revenue.toLocaleString()}</p>
                </div>
                <div className="p-3 bg-green-100 rounded-lg">
                  <TrendingUp className="text-green-600" size={24} />
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Expenses</p>
                  <p className="text-2xl font-bold text-gray-900">${summary.total_expenses.toLocaleString()}</p>
                </div>
                <div className="p-3 bg-red-100 rounded-lg">
                  <TrendingDown className="text-red-600" size={24} />
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Net Profit</p>
                  <p className={`text-2xl font-bold ${summary.total_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ${summary.total_profit.toLocaleString()}
                  </p>
                </div>
                <div className={`p-3 rounded-lg ${summary.total_profit >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
                  <DollarSign className={summary.total_profit >= 0 ? 'text-green-600' : 'text-red-600'} size={24} />
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Avg Profit Margin</p>
                  <p className={`text-2xl font-bold ${summary.avg_profit_margin >= 20 ? 'text-green-600' : summary.avg_profit_margin >= 10 ? 'text-yellow-600' : 'text-red-600'}`}>
                    {summary.avg_profit_margin}%
                  </p>
                </div>
                <div className="p-3 bg-blue-100 rounded-lg">
                  <PieChart className="text-blue-600" size={24} />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Add/Edit Record Form */}
        {showForm && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4 text-gray-900">
              {isEditing ? 'Edit Financial Record' : 'Add Financial Record'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-900">Week Start Date</label>
                  <input 
                    type="date" 
                    required 
                    value={formData.week_start} 
                    onChange={(e) => setFormData({...formData, week_start: e.target.value})} 
                    className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-900">Gross Sales / Revenue</label>
                  <input 
                    type="number" 
                    required 
                    step="0.01" 
                    value={formData.gross_sales || ''} 
                    onChange={(e) => setFormData({...formData, gross_sales: parseFloat(e.target.value) || 0})} 
                    className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50"
                    placeholder="0.00"
                  />
                </div>
              </div>

              <div className="border-t pt-4">
                <h3 className="font-semibold mb-3 text-gray-900">Expenses</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700">💰 Cost of Goods Sold</label>
                    <input type="number" step="0.01" value={formData.cogs || ''} onChange={(e) => setFormData({...formData, cogs: parseFloat(e.target.value) || 0})} className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50" placeholder="0.00" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700">👥 Payroll</label>
                    <input type="number" step="0.01" value={formData.payroll || ''} onChange={(e) => setFormData({...formData, payroll: parseFloat(e.target.value) || 0})} className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50" placeholder="0.00" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700">🏢 Rent/Lease</label>
                    <input type="number" step="0.01" value={formData.rent || ''} onChange={(e) => setFormData({...formData, rent: parseFloat(e.target.value) || 0})} className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50" placeholder="0.00" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700">⚡ Utilities</label>
                    <input type="number" step="0.01" value={formData.utilities || ''} onChange={(e) => setFormData({...formData, utilities: parseFloat(e.target.value) || 0})} className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50" placeholder="0.00" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700">📦 Supplies</label>
                    <input type="number" step="0.01" value={formData.supplies || ''} onChange={(e) => setFormData({...formData, supplies: parseFloat(e.target.value) || 0})} className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50" placeholder="0.00" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700">📱 Marketing</label>
                    <input type="number" step="0.01" value={formData.marketing || ''} onChange={(e) => setFormData({...formData, marketing: parseFloat(e.target.value) || 0})} className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50" placeholder="0.00" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700">🔧 Maintenance</label>
                    <input type="number" step="0.01" value={formData.maintenance || ''} onChange={(e) => setFormData({...formData, maintenance: parseFloat(e.target.value) || 0})} className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50" placeholder="0.00" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700">📋 Insurance</label>
                    <input type="number" step="0.01" value={formData.insurance || ''} onChange={(e) => setFormData({...formData, insurance: parseFloat(e.target.value) || 0})} className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50" placeholder="0.00" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700">💳 Processing Fees</label>
                    <input type="number" step="0.01" value={formData.processing_fees || ''} onChange={(e) => setFormData({...formData, processing_fees: parseFloat(e.target.value) || 0})} className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50" placeholder="0.00" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700">📊 Other Expenses</label>
                    <input type="number" step="0.01" value={formData.other_expenses || ''} onChange={(e) => setFormData({...formData, other_expenses: parseFloat(e.target.value) || 0})} className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50" placeholder="0.00" />
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                <button 
                  type="button"
                  onClick={() => {
                    setShowForm(false)
                    setIsEditing(false)
                    setFormData({
                      week_start: '',
                      gross_sales: 0,
                      payroll: 0,
                      cogs: 0,
                      rent: 0,
                      utilities: 0,
                      supplies: 0,
                      marketing: 0,
                      maintenance: 0,
                      insurance: 0,
                      processing_fees: 0,
                      other_expenses: 0
                    })
                  }}
                  className="flex-1 bg-gray-200 text-gray-800 py-2 rounded-lg hover:bg-gray-300"
                >
                  Cancel
                </button>
                <button type="submit" className="flex-1 bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700">
                  {isEditing ? 'Update Record' : 'Add Record'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Financial Records Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b">
            <h2 className="text-xl font-bold text-gray-900">Weekly Performance</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Week</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Revenue</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Expenses</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Net Profit</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Profit %</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payroll %</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Health</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {financials.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                      No financial records yet. Add your first one above!
                    </td>
                  </tr>
                ) : (
                  financials.map((record) => (
                    <tr key={record.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => handleViewWeek(record)}>
                      <td className="px-6 py-4 text-sm text-gray-900">{record.week_start}</td>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">${record.gross_sales.toLocaleString()}</td>
                      <td className="px-6 py-4 text-sm text-gray-900">${record.total_expenses.toLocaleString()}</td>
                      <td className={`px-6 py-4 text-sm font-bold ${record.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        ${record.net_profit.toLocaleString()}
                      </td>
                      <td className={`px-6 py-4 text-sm font-bold ${record.profit_margin >= 20 ? 'text-green-600' : record.profit_margin >= 10 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {record.profit_margin}%
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">{record.payroll_pct}%</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(record.status)}`}>
                          {record.status === 'green' ? '✅ Healthy' : record.status === 'yellow' ? '⚠️ Warning' : '❌ Critical'}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Week Detail Modal */}
        {selectedWeek && !isEditing && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999] p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-gray-900">Week of {selectedWeek.week_start}</h2>
                <button onClick={handleCloseDetail} className="text-gray-500 hover:text-gray-700">
                  ✕
                </button>
              </div>

              {/* Summary Section */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Revenue</p>
                  <p className="text-xl font-bold text-gray-900">${selectedWeek.gross_sales.toLocaleString()}</p>
                </div>
                <div className="bg-red-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Total Expenses</p>
                  <p className="text-xl font-bold text-gray-900">${selectedWeek.total_expenses.toLocaleString()}</p>
                </div>
                <div className={`p-4 rounded-lg ${selectedWeek.net_profit >= 0 ? 'bg-blue-50' : 'bg-red-50'}`}>
                  <p className="text-sm text-gray-600">Net Profit</p>
                  <p className={`text-xl font-bold ${selectedWeek.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ${selectedWeek.net_profit.toLocaleString()}
                  </p>
                </div>
              </div>

              {/* Expense Breakdown */}
              <div className="border-t pt-4">
                <h3 className="font-semibold mb-3 text-gray-900">Expense Breakdown</h3>
                <div className="space-y-2">
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-700">💰 Cost of Goods Sold</span>
                    <span className="font-medium text-gray-900">${selectedWeek.cogs.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-700">👥 Payroll ({selectedWeek.payroll_pct}%)</span>
                    <span className="font-medium text-gray-900">${selectedWeek.payroll.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-700">🏢 Rent/Lease</span>
                    <span className="font-medium text-gray-900">${selectedWeek.rent.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-700">⚡ Utilities</span>
                    <span className="font-medium text-gray-900">${selectedWeek.utilities.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-700">📦 Supplies</span>
                    <span className="font-medium text-gray-900">${selectedWeek.supplies.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-700">📱 Marketing</span>
                    <span className="font-medium text-gray-900">${selectedWeek.marketing.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-700">🔧 Maintenance</span>
                    <span className="font-medium text-gray-900">${selectedWeek.maintenance.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-700">📋 Insurance</span>
                    <span className="font-medium text-gray-900">${selectedWeek.insurance.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-700">💳 Processing Fees</span>
                    <span className="font-medium text-gray-900">${selectedWeek.processing_fees.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-700">📊 Other Expenses</span>
                    <span className="font-medium text-gray-900">${selectedWeek.other_expenses.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Metrics */}
              <div className="border-t pt-4 mt-4">
                <h3 className="font-semibold mb-3 text-gray-900">Key Metrics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Profit Margin</p>
                    <p className={`text-lg font-bold ${selectedWeek.profit_margin >= 20 ? 'text-green-600' : selectedWeek.profit_margin >= 10 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {selectedWeek.profit_margin}%
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Health Status</p>
                    <span className={`inline-block px-3 py-1 text-sm font-medium rounded ${getStatusColor(selectedWeek.status)}`}>
                      {selectedWeek.status === 'green' ? '✅ Healthy' : selectedWeek.status === 'yellow' ? '⚠️ Warning' : '❌ Critical'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2 mt-6">
                <button 
                  onClick={handleCloseDetail}
                  className="flex-1 bg-gray-200 text-gray-800 py-2 rounded-lg hover:bg-gray-300"
                >
                  Close
                </button>
                <button 
                  onClick={() => handleEditWeek(selectedWeek)}
                  className="flex-1 bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700"
                >
                  Edit Record
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}
