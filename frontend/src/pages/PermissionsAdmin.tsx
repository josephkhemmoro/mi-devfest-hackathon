import { useEffect, useState } from 'react'
import { Layout } from '../components/Layout'
import { useAuth } from '../contexts/AuthContext'
import api from '../lib/api'
import { Shield, Edit, Check, X, UserCog } from 'lucide-react'
import { Permissions, PERMISSION_INFO, getPermissionsByCategory } from '../lib/permissions'

interface UserPermission {
  user_id: string
  full_name: string
  email: string
  role: string
  custom_permissions: string[]
  all_permissions: string[]
  is_active: boolean
}

export default function PermissionsAdmin() {
  const { hasPermission } = useAuth()
  const [users, setUsers] = useState<UserPermission[]>([])
  const [selectedUser, setSelectedUser] = useState<UserPermission | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [editingPermissions, setEditingPermissions] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  // Redirect if not admin
  useEffect(() => {
    if (!loading && !hasPermission(Permissions.MANAGE_PERMISSIONS)) {
      window.location.href = '/dashboard'
    }
  }, [hasPermission, loading])

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await api.get('/api/admin/permissions/users')
      setUsers(response.data)
    } catch (error) {
      console.error('Failed to fetch users:', error)
    } finally {
      setLoading(false)
    }
  }

  const openEditModal = (user: UserPermission) => {
    setSelectedUser(user)
    setEditingPermissions(user.custom_permissions || [])
    setShowModal(true)
  }

  const togglePermission = (permission: string) => {
    if (editingPermissions.includes(permission)) {
      setEditingPermissions(editingPermissions.filter(p => p !== permission))
    } else {
      setEditingPermissions([...editingPermissions, permission])
    }
  }

  const savePermissions = async () => {
    if (!selectedUser) return

    try {
      await api.put(`/api/admin/permissions/users/${selectedUser.user_id}/permissions`, {
        custom_permissions: editingPermissions
      })
      
      alert('Permissions updated successfully')
      setShowModal(false)
      fetchUsers()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to update permissions')
    }
  }

  const toggleRole = async (userId: string, currentRole: string) => {
    const newRole = currentRole === 'admin' ? 'employee' : 'admin'
    
    if (!confirm(`Change user role to ${newRole}?`)) return

    try {
      await api.put(`/api/admin/permissions/users/${userId}/role`, {
        role: newRole
      })
      alert('Role updated successfully')
      fetchUsers()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to update role')
    }
  }

  const toggleUserStatus = async (userId: string, isActive: boolean) => {
    const action = isActive ? 'deactivate' : 'activate'
    
    if (!confirm(`${action.charAt(0).toUpperCase() + action.slice(1)} this user?`)) return

    try {
      await api.put(`/api/admin/permissions/users/${userId}/${action}`)
      alert(`User ${action}d successfully`)
      fetchUsers()
    } catch (error: any) {
      alert(error.response?.data?.detail || `Failed to ${action} user`)
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-600">Loading...</div>
        </div>
      </Layout>
    )
  }

  if (!hasPermission(Permissions.MANAGE_PERMISSIONS)) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center h-64">
          <Shield className="w-16 h-16 text-red-500 mb-4" />
          <h2 className="text-2xl font-bold text-gray-900">Access Denied</h2>
          <p className="text-gray-600">You don't have permission to access this page.</p>
        </div>
      </Layout>
    )
  }

  const permissionsByCategory = getPermissionsByCategory()

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <UserCog className="w-8 h-8 text-primary-600" />
          <h1 className="text-3xl font-bold text-gray-900">Manage User Access</h1>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Admin Panel:</strong> Manage roles and custom permissions for all users in your organization.
            Admins have all permissions by default. Employees have limited default access but can be granted additional permissions.
          </p>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Custom Permissions
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.user_id} className={!user.is_active ? 'bg-gray-50 opacity-60' : ''}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        user.role === 'admin'
                          ? 'bg-purple-100 text-purple-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        user.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">
                      {user.custom_permissions.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {user.custom_permissions.slice(0, 3).map((perm) => (
                            <span
                              key={perm}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                            >
                              {PERMISSION_INFO[perm]?.label || perm}
                            </span>
                          ))}
                          {user.custom_permissions.length > 3 && (
                            <span className="text-xs text-gray-500">
                              +{user.custom_permissions.length - 3} more
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-gray-400 text-xs">Default permissions only</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => openEditModal(user)}
                        className="text-primary-600 hover:text-primary-900 flex items-center gap-1"
                      >
                        <Edit className="w-4 h-4" />
                        Edit
                      </button>
                      {user.role !== 'admin' && (
                        <button
                          onClick={() => toggleUserStatus(user.user_id, user.is_active)}
                          className={`${
                            user.is_active ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'
                          } flex items-center gap-1`}
                        >
                          {user.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Edit Permissions Modal */}
      {showModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">
                Edit Permissions: {selectedUser.full_name}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                Role: <span className="font-semibold">{selectedUser.role}</span>
              </p>
              {selectedUser.role === 'admin' && (
                <p className="text-sm text-orange-600 mt-2">
                  ⚠️ Admins have all permissions by default. Custom permissions have no effect.
                </p>
              )}
              <div className="mt-3">
                <button
                  onClick={() => toggleRole(selectedUser.user_id, selectedUser.role)}
                  className="text-sm text-primary-600 hover:text-primary-800 font-medium"
                >
                  Switch to {selectedUser.role === 'admin' ? 'Employee' : 'Admin'} Role
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <div className="space-y-6">
                {Object.entries(permissionsByCategory).map(([category, perms]) => (
                  <div key={category}>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">{category}</h3>
                    <div className="space-y-2">
                      {perms.map((perm) => {
                        const isEnabled = editingPermissions.includes(perm.name)
                        const hasRolePermission = selectedUser.all_permissions.includes(perm.name) && 
                                                 !selectedUser.custom_permissions.includes(perm.name)
                        
                        return (
                          <label
                            key={perm.name}
                            className={`flex items-start p-3 rounded-lg border-2 cursor-pointer transition-colors ${
                              isEnabled
                                ? 'border-primary-500 bg-primary-50'
                                : hasRolePermission
                                ? 'border-gray-300 bg-gray-50'
                                : 'border-gray-200 bg-white hover:border-gray-300'
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={isEnabled}
                              onChange={() => togglePermission(perm.name)}
                              disabled={selectedUser.role === 'admin'}
                              className="mt-1 h-5 w-5 text-primary-600 rounded focus:ring-primary-500"
                            />
                            <div className="ml-3 flex-1">
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-medium text-gray-900">{perm.label}</span>
                                {hasRolePermission && (
                                  <span className="text-xs bg-gray-200 text-gray-700 px-2 py-0.5 rounded">
                                    From role
                                  </span>
                                )}
                              </div>
                              <p className="text-xs text-gray-500 mt-1">{perm.description}</p>
                            </div>
                          </label>
                        )
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 flex items-center gap-2"
              >
                <X className="w-4 h-4" />
                Cancel
              </button>
              <button
                onClick={savePermissions}
                disabled={selectedUser.role === 'admin'}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Check className="w-4 h-4" />
                Save Permissions
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}
