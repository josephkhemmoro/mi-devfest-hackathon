import { useEffect, useState } from 'react'
import { Layout } from '../components/Layout'
import api from '../lib/api'
import { UserPlus, Copy, Check } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export default function Employees() {
  const { role } = useAuth()
  const isAdmin = role === 'admin'
  const [employees, setEmployees] = useState<any[]>([])
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [inviteResult, setInviteResult] = useState<any>(null)
  const [copiedPassword, setCopiedPassword] = useState(false)
  const [inviteData, setInviteData] = useState({
    email: '',
    full_name: '',
    role: 'employee'
  })

  useEffect(() => {
    fetchEmployees()
  }, [])

  const fetchEmployees = async () => {
    try {
      // Fetch from profiles table to get user accounts
      const response = await api.get('/api/employees/profiles')
      setEmployees(response.data)
    } catch (error) {
      console.error('Failed to fetch employees:', error)
    }
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

  const handleAdminToggle = async (userId: string, isAdminStatus: boolean) => {
    try {
      console.log('[ADMIN_TOGGLE] Updating user:', userId, 'to is_admin:', isAdminStatus)
      const response = await api.put(`/api/employees/profiles/${userId}/admin`, { is_admin: isAdminStatus })
      console.log('[ADMIN_TOGGLE] Response:', response.data)
      
      await fetchEmployees()
      console.log('[ADMIN_TOGGLE] Employees refreshed')
      
      alert(`✅ User is now ${isAdminStatus ? 'an Admin' : 'an Employee'}`)
    } catch (error: any) {
      console.error('[ADMIN_TOGGLE] Error:', error)
      alert(error.response?.data?.detail || 'Failed to update admin status')
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
          <h1 className="text-3xl font-bold text-gray-900">Employees</h1>
          {isAdmin && (
            <button 
              onClick={() => setShowInviteModal(true)} 
              className="px-4 py-2 bg-primary-600 text-white rounded-lg flex items-center gap-2 hover:bg-primary-700"
            >
              <UserPlus className="w-4 h-4" />
              Invite Employee
            </button>
          )}
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Note:</strong> All employees must be invited via email to get login access. 
            Use the "Invite Employee" button above to add new team members.
          </p>
        </div>


        <div className="grid gap-4">
          {employees.map((emp) => (
            <div key={emp.user_id} className="bg-white p-6 rounded-lg shadow">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-xl font-bold">{emp.full_name}</h3>
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      emp.is_admin ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {emp.is_admin ? 'Admin' : 'Employee'}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      emp.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {emp.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm mt-1">{emp.email}</p>
                </div>
                
                {/* Simple Admin Toggle */}
                {isAdmin && (
                  <div className="ml-4">
                    <label className="block text-xs font-medium text-gray-700 mb-1">Access Level</label>
                    <select
                      value={emp.is_admin ? 'admin' : 'employee'}
                      onChange={(e) => handleAdminToggle(emp.user_id, e.target.value === 'admin')}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="employee">Employee</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Invite Employee Modal */}
        {showInviteModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999] p-4">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <h2 className="text-2xl font-bold mb-4 text-gray-900">Invite Employee via Email</h2>
              
              {!inviteResult ? (
                <form onSubmit={handleInvite} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-900">Email Address</label>
                    <input
                      type="email"
                      required
                      value={inviteData.email}
                      onChange={(e) => setInviteData({...inviteData, email: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50"
                      placeholder="employee@example.com"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-900">Full Name</label>
                    <input
                      type="text"
                      required
                      value={inviteData.full_name}
                      onChange={(e) => setInviteData({...inviteData, full_name: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50"
                      placeholder="John Doe"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-900">Role</label>
                    <select
                      value={inviteData.role}
                      onChange={(e) => setInviteData({...inviteData, role: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg text-gray-900 bg-gray-50"
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
                      <code className="flex-1 bg-white px-3 py-2 rounded border border-yellow-300 font-mono text-sm text-gray-900">
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
