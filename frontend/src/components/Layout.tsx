/**
 * Layout Component with white-labeled header
 * Displays business logo and navigation
 */
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useBusiness } from '../contexts/BusinessContext'
import { LogOut, LayoutDashboard, Package, Users, Calendar, DollarSign, Bell, Shield } from 'lucide-react'
import { Permissions } from '../lib/permissions'

interface LayoutProps {
  children: React.ReactNode
}

export const Layout = ({ children }: LayoutProps) => {
  const { logout, hasPermission, role } = useAuth()
  const { businessName, logoUrl } = useBusiness()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // Navigation items with permission requirements
  const allNavItems = [
    { 
      path: '/dashboard', 
      icon: LayoutDashboard, 
      label: 'Dashboard',
      permission: Permissions.VIEW_DASHBOARD
    },
    { 
      path: '/inventory', 
      icon: Package, 
      label: 'Inventory',
      permission: Permissions.VIEW_INVENTORY
    },
    { 
      path: '/employees', 
      icon: Users, 
      label: 'Employees',
      permission: Permissions.VIEW_EMPLOYEES
    },
    { 
      path: '/schedule', 
      icon: Calendar, 
      label: 'Schedule',
      permission: Permissions.VIEW_SCHEDULE
    },
    { 
      path: '/money', 
      icon: DollarSign, 
      label: 'Financials',
      permission: Permissions.VIEW_FINANCIALS
    },
    { 
      path: '/reminders', 
      icon: Bell, 
      label: 'Reminders',
      permission: Permissions.VIEW_REMINDERS
    },
    { 
      path: '/admin/permissions', 
      icon: Shield, 
      label: 'Manage Access',
      permission: Permissions.MANAGE_PERMISSIONS,
      adminOnly: true
    },
  ]

  // Filter nav items based on permissions
  const navItems = allNavItems.filter(item => hasPermission(item.permission))

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Business Logo */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Business Name */}
            <div className="flex items-center space-x-3">
              {logoUrl ? (
                <img src={logoUrl} alt={businessName || 'Business'} className="h-10 w-10 object-contain" />
              ) : (
                <div className="h-10 w-10 bg-primary-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-xl">
                    {businessName?.charAt(0) || 'A'}
                  </span>
                </div>
              )}
              <div>
                <h1 className="text-xl font-bold text-gray-900">{businessName || 'Astra ERP'}</h1>
                <p className="text-xs text-gray-500">
                  Business Operating System {role && <span className="text-primary-600">• {role.charAt(0).toUpperCase() + role.slice(1)}</span>}
                </p>
              </div>
            </div>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition"
            >
              <LogOut size={18} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1 overflow-x-auto">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium transition whitespace-nowrap ${
                    isActive
                      ? 'text-primary-600 border-b-2 border-primary-600'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  } ${(item as any).adminOnly ? 'bg-purple-50' : ''}`}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                  {(item as any).adminOnly && (
                    <Shield size={14} className="text-purple-600" />
                  )}
                </Link>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}
