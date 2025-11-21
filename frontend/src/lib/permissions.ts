/**
 * Permission constants and utilities
 * Matches backend permissions.py
 */

export const Permissions = {
  // Dashboard
  VIEW_DASHBOARD: 'view_dashboard',
  EDIT_DASHBOARD: 'edit_dashboard',
  
  // Inventory
  VIEW_INVENTORY: 'view_inventory',
  EDIT_INVENTORY: 'edit_inventory',
  GENERATE_ORDERS: 'generate_orders',
  
  // Employees
  VIEW_EMPLOYEES: 'view_employees',
  EDIT_EMPLOYEES: 'edit_employees',
  MANAGE_PERMISSIONS: 'manage_permissions',
  
  // Schedule
  VIEW_SCHEDULE: 'view_schedule',
  EDIT_SCHEDULE: 'edit_schedule',
  GENERATE_SCHEDULE: 'generate_schedule',
  SET_AVAILABILITY: 'set_availability',
  
  // Financials
  VIEW_FINANCIALS: 'view_financials',
  EDIT_FINANCIALS: 'edit_financials',
  
  // Reminders
  VIEW_REMINDERS: 'view_reminders',
  EDIT_REMINDERS: 'edit_reminders',
  SET_REMINDERS: 'set_reminders',
  
  // Business
  EDIT_BUSINESS: 'edit_business',
} as const

export type PermissionType = typeof Permissions[keyof typeof Permissions]

export interface PermissionInfo {
  name: string
  category: string
  description: string
  label: string
}

// Permission metadata for UI display
export const PERMISSION_INFO: Record<string, PermissionInfo> = {
  [Permissions.VIEW_DASHBOARD]: {
    name: Permissions.VIEW_DASHBOARD,
    category: 'Dashboard',
    description: 'View dashboard and statistics',
    label: 'View Dashboard'
  },
  [Permissions.EDIT_DASHBOARD]: {
    name: Permissions.EDIT_DASHBOARD,
    category: 'Dashboard',
    description: 'Edit dashboard settings',
    label: 'Edit Dashboard'
  },
  [Permissions.VIEW_INVENTORY]: {
    name: Permissions.VIEW_INVENTORY,
    category: 'Inventory',
    description: 'View inventory items',
    label: 'View Inventory'
  },
  [Permissions.EDIT_INVENTORY]: {
    name: Permissions.EDIT_INVENTORY,
    category: 'Inventory',
    description: 'Add, edit, and delete inventory items',
    label: 'Edit Inventory'
  },
  [Permissions.GENERATE_ORDERS]: {
    name: Permissions.GENERATE_ORDERS,
    category: 'Inventory',
    description: 'Generate AI-powered inventory orders',
    label: 'Generate Orders'
  },
  [Permissions.VIEW_EMPLOYEES]: {
    name: Permissions.VIEW_EMPLOYEES,
    category: 'Employees',
    description: 'View employee list',
    label: 'View Employees'
  },
  [Permissions.EDIT_EMPLOYEES]: {
    name: Permissions.EDIT_EMPLOYEES,
    category: 'Employees',
    description: 'Add, edit, and delete employees',
    label: 'Edit Employees'
  },
  [Permissions.MANAGE_PERMISSIONS]: {
    name: Permissions.MANAGE_PERMISSIONS,
    category: 'Employees',
    description: 'Manage user roles and permissions',
    label: 'Manage User Permissions'
  },
  [Permissions.VIEW_SCHEDULE]: {
    name: Permissions.VIEW_SCHEDULE,
    category: 'Schedule',
    description: 'View work schedules',
    label: 'View Schedule'
  },
  [Permissions.EDIT_SCHEDULE]: {
    name: Permissions.EDIT_SCHEDULE,
    category: 'Schedule',
    description: 'Create and edit schedules',
    label: 'Edit Schedule'
  },
  [Permissions.GENERATE_SCHEDULE]: {
    name: Permissions.GENERATE_SCHEDULE,
    category: 'Schedule',
    description: 'Generate AI-powered schedules',
    label: 'Generate AI Schedule'
  },
  [Permissions.SET_AVAILABILITY]: {
    name: Permissions.SET_AVAILABILITY,
    category: 'Schedule',
    description: 'Set own availability',
    label: 'Set Own Availability'
  },
  [Permissions.VIEW_FINANCIALS]: {
    name: Permissions.VIEW_FINANCIALS,
    category: 'Financials',
    description: 'View financial data',
    label: 'View Financials'
  },
  [Permissions.EDIT_FINANCIALS]: {
    name: Permissions.EDIT_FINANCIALS,
    category: 'Financials',
    description: 'Edit financial transactions',
    label: 'Edit Financials'
  },
  [Permissions.VIEW_REMINDERS]: {
    name: Permissions.VIEW_REMINDERS,
    category: 'Reminders',
    description: 'View reminders',
    label: 'View Reminders'
  },
  [Permissions.EDIT_REMINDERS]: {
    name: Permissions.EDIT_REMINDERS,
    category: 'Reminders',
    description: 'Create and edit reminders',
    label: 'Edit Reminders'
  },
  [Permissions.SET_REMINDERS]: {
    name: Permissions.SET_REMINDERS,
    category: 'Reminders',
    description: 'Set personal reminders',
    label: 'Set Personal Reminders'
  },
  [Permissions.EDIT_BUSINESS]: {
    name: Permissions.EDIT_BUSINESS,
    category: 'Business',
    description: 'Edit business settings and branding',
    label: 'Edit Business Settings'
  },
}

// Group permissions by category for UI display
export const getPermissionsByCategory = (): Record<string, PermissionInfo[]> => {
  const grouped: Record<string, PermissionInfo[]> = {}
  
  Object.values(PERMISSION_INFO).forEach(perm => {
    if (!grouped[perm.category]) {
      grouped[perm.category] = []
    }
    grouped[perm.category].push(perm)
  })
  
  return grouped
}
