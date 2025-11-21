import { useEffect, useState } from 'react'
import { Layout } from '../components/Layout'
import api from '../lib/api'
import { UserPlus, Mail, Copy, Check } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { Permissions } from '../lib/permissions'

export default function Employees() {
  const { hasPermission } = useAuth()
  const [employees, setEmployees] = useState<any[]>([])
  const [showForm, setShowForm] = useState(false)
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [inviteResult, setInviteResult] = useState<any>(null)
  const [copiedPassword, setCopiedPassword] = useState(false)
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    role: '',
    strength: 'normal' as 'strong' | 'normal' | 'new',
    active: true,
    availability: [] as string[],
    create_user_account: false
  })
  const [inviteData, setInviteData] = useState({
    email: '',
    full_name: '',
    role: 'employee'
  })

  const days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

  useEffect(() => {
    fetchEmployees()
  }, [])

  const fetchEmployees = async () => {
    try {
      const response = await api.get('/api/employees/')
      setEmployees(response.data)
    } catch (error) {
      console.error('Failed to fetch employees:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/api/employees/', formData)
      setShowForm(false)
      setFormData({ 
        full_name: '', 
        email: '',
        role: '', 
        strength: 'normal', 
        active: true, 
        availability: [],
        create_user_account: false
      })
      fetchEmployees()
      alert('Employee created successfully!')
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create employee')
    }
  }

  const toggleDay = (day: string) => {
    setFormData(prev => ({
      ...prev,
      availability: prev.availability.includes(day) 
        ? prev.availability.filter(d => d !== day)
        : [...prev.availability, day]
    }))
  }

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await api.post('/api/admin/invite', inviteData)
      setInviteResult(response.data)
      setInviteData({ email: '', full_name: '', role: 'employee' })
      fetchEmployees()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to invite employee')
    }
  }

  const copyPassword = async () => {
    if (inviteResult?.temporary_password) {
      await navigator.clipboard.writeText(inviteResult.temporary_password)
      setCopiedPassword(true)
      setTimeout(() => setCopiedPassword(false), 2000)
    }
  }

  const closeInviteModal = () => {
    setShowInviteModal(false)
    setInviteResult(null)
    setCopiedPassword(false)
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Employee Management</h1>
          <div className="flex gap-2">
            {hasPermission(Permissions.EDIT_EMPLOYEES) && (
              <button 
                onClick={() => setShowInviteModal(true)} 
                className="px-4 py-2 bg-primary-600 text-white rounded-lg flex items-center gap-2 hover:bg-primary-700"
              >
                <Mail className="w-4 h-4" />
                Invite via Email
              </button>
            )}
            <button 
              onClick={() => setShowForm(!showForm)} 
              className="px-4 py-2 bg-gray-900 text-white rounded-lg flex items-center gap-2"
            >
              <UserPlus className="w-4 h-4" />
              Add Employee
            </button>
          </div>
        </div>

        {showForm && (
          <div className="bg-white p-6 rounded-lg shadow">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                <input 
                  placeholder="John Doe" 
                  required 
                  value={formData.full_name} 
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})} 
                  className="w-full px-4 py-2 border rounded-lg" 
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email (Optional)</label>
                <input 
                  type="email"
                  placeholder="john@example.com" 
                  value={formData.email} 
                  onChange={(e) => setFormData({...formData, email: e.target.value})} 
                  className="w-full px-4 py-2 border rounded-lg" 
                />
                <p className="text-xs text-gray-500 mt-1">Required if creating user account</p>
              </div>
              
              <div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.create_user_account}
                    onChange={(e) => setFormData({...formData, create_user_account: e.target.checked})}
                    className="w-4 h-4"
                  />
                  <span className="text-sm font-medium text-gray-700">Create login account for this employee</span>
                </label>
                <p className="text-xs text-gray-500 ml-6">Allows employee to login and access the system</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Job Role</label>
                <input 
                  placeholder="Server, Cook, Manager..." 
                  value={formData.role} 
                  onChange={(e) => setFormData({...formData, role: e.target.value})} 
                  className="w-full px-4 py-2 border rounded-lg" 
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Strength Level</label>
                <select 
                  value={formData.strength} 
                  onChange={(e) => setFormData({...formData, strength: e.target.value as any})} 
                  className="w-full px-4 py-2 border rounded-lg"
                >
                  <option value="strong">Strong (Experienced)</option>
                  <option value="normal">Normal</option>
                  <option value="new">New (Training)</option>
                </select>
              </div>
              <div>
                <p className="font-medium mb-2">Availability:</p>
                <div className="flex gap-2">
                  {days.map(day => (
                    <button
                      key={day}
                      type="button"
                      onClick={() => toggleDay(day)}
                      className={`px-3 py-2 rounded ${formData.availability.includes(day) ? 'bg-primary-600 text-white' : 'bg-gray-200'}`}
                    >
                      {day.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>
              <button type="submit" className="w-full bg-primary-600 text-white py-2 rounded">Create Employee</button>
            </form>
          </div>
        )}

        <div className="grid gap-4">
          {employees.map((emp) => (
            <div key={emp.id} className="bg-white p-6 rounded-lg shadow">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xl font-bold">{emp.full_name}</h3>
                  <p className="text-gray-600">{emp.role}</p>
                  <p className="text-sm mt-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${emp.strength === 'strong' ? 'bg-green-100 text-green-800' : emp.strength === 'new' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100'}`}>
                      {emp.strength.toUpperCase()}
                    </span>
                    <span className={`ml-2 px-2 py-1 rounded text-xs ${emp.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {emp.active ? 'Active' : 'Inactive'}
                    </span>
                  </p>
                  <p className="text-sm mt-2 text-gray-600">Available: {emp.availability.map((d: string) => d.toUpperCase()).join(', ') || 'None'}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Invite Employee Modal */}
        {showInviteModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <h2 className="text-2xl font-bold mb-4">Invite Employee via Email</h2>
              
              {!inviteResult ? (
                <form onSubmit={handleInvite} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Email Address</label>
                    <input
                      type="email"
                      required
                      value={inviteData.email}
                      onChange={(e) => setInviteData({...inviteData, email: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg"
                      placeholder="employee@example.com"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">Full Name</label>
                    <input
                      type="text"
                      required
                      value={inviteData.full_name}
                      onChange={(e) => setInviteData({...inviteData, full_name: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg"
                      placeholder="John Doe"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">Role</label>
                    <select
                      value={inviteData.role}
                      onChange={(e) => setInviteData({...inviteData, role: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg"
                    >
                      <option value="employee">Employee</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                  
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => setShowInviteModal(false)}
                      className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                    >
                      Send Invite
                    </button>
                  </div>
                </form>
              ) : (
                <div className="space-y-4">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-green-800 font-medium mb-2">✅ Invitation Sent!</p>
                    <p className="text-sm text-green-700">
                      {inviteResult.full_name} has been invited to join your team.
                    </p>
                  </div>
                  
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-yellow-900 font-medium mb-2">⚠️ Temporary Password</p>
                    <p className="text-sm text-yellow-800 mb-2">
                      Share this password with the employee. They should change it after first login.
                    </p>
                    <div className="flex items-center gap-2">
                      <code className="flex-1 bg-white px-3 py-2 rounded border border-yellow-300 font-mono text-sm">
                        {inviteResult.temporary_password}
                      </code>
                      <button
                        onClick={copyPassword}
                        className="px-3 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 flex items-center gap-2"
                      >
                        {copiedPassword ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                        {copiedPassword ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                  </div>
                  
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-blue-900 font-medium mb-1">📧 Login Credentials:</p>
                    <p className="text-sm text-blue-800">
                      <strong>Email:</strong> {inviteResult.email}<br />
                      <strong>Password:</strong> (shown above)
                    </p>
                  </div>
                  
                  <button
                    onClick={closeInviteModal}
                    className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    Done
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}
