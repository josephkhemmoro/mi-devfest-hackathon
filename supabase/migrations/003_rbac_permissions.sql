-- ============================================
-- RBAC (Role-Based Access Control) System
-- ============================================

-- Add role and permissions columns to profiles table
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'employee';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS custom_permissions JSONB DEFAULT '[]'::jsonb;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Create index for faster role queries
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);
CREATE INDEX IF NOT EXISTS idx_profiles_is_active ON profiles(is_active);

-- Update existing admin users (first user of each business becomes admin)
WITH first_users AS (
  SELECT DISTINCT ON (business_id) id, business_id
  FROM profiles
  ORDER BY business_id, created_at ASC
)
UPDATE profiles
SET role = 'admin'
WHERE id IN (SELECT id FROM first_users);

-- Create permissions reference table (for documentation and validation)
CREATE TABLE IF NOT EXISTS permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) UNIQUE NOT NULL,
  category VARCHAR(50) NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert standard permissions
INSERT INTO permissions (name, category, description) VALUES
  -- Dashboard
  ('view_dashboard', 'dashboard', 'View dashboard and statistics'),
  ('edit_dashboard', 'dashboard', 'Edit dashboard settings'),
  
  -- Inventory
  ('view_inventory', 'inventory', 'View inventory items'),
  ('edit_inventory', 'inventory', 'Add, edit, and delete inventory items'),
  ('generate_orders', 'inventory', 'Generate AI-powered inventory orders'),
  
  -- Employees
  ('view_employees', 'employees', 'View employee list'),
  ('edit_employees', 'employees', 'Add, edit, and delete employees'),
  ('manage_permissions', 'employees', 'Manage user roles and permissions'),
  
  -- Schedule
  ('view_schedule', 'schedule', 'View work schedules'),
  ('edit_schedule', 'schedule', 'Create and edit schedules'),
  ('generate_schedule', 'schedule', 'Generate AI-powered schedules'),
  ('set_availability', 'schedule', 'Set own availability'),
  
  -- Financials
  ('view_financials', 'financials', 'View financial data'),
  ('edit_financials', 'financials', 'Edit financial transactions'),
  
  -- Reminders
  ('view_reminders', 'reminders', 'View reminders'),
  ('edit_reminders', 'reminders', 'Create and edit reminders'),
  ('set_reminders', 'reminders', 'Set personal reminders'),
  
  -- Business Settings
  ('edit_business', 'business', 'Edit business settings and branding')
ON CONFLICT (name) DO NOTHING;

-- Create role permissions mapping table
CREATE TABLE IF NOT EXISTS role_permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  role VARCHAR(50) NOT NULL,
  permission_name VARCHAR(100) NOT NULL REFERENCES permissions(name),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(role, permission_name)
);

-- Admin role gets all permissions
INSERT INTO role_permissions (role, permission_name)
SELECT 'admin', name FROM permissions
ON CONFLICT DO NOTHING;

-- Employee default permissions
INSERT INTO role_permissions (role, permission_name) VALUES
  ('employee', 'view_dashboard'),
  ('employee', 'view_inventory'),
  ('employee', 'view_schedule'),
  ('employee', 'set_availability'),
  ('employee', 'view_reminders'),
  ('employee', 'set_reminders')
ON CONFLICT DO NOTHING;

-- Create function to check if user has permission
CREATE OR REPLACE FUNCTION user_has_permission(
  user_id UUID,
  permission_name VARCHAR
) RETURNS BOOLEAN AS $$
DECLARE
  user_role VARCHAR;
  user_custom_perms JSONB;
  has_perm BOOLEAN;
BEGIN
  -- Get user role and custom permissions
  SELECT role, custom_permissions INTO user_role, user_custom_perms
  FROM profiles
  WHERE id = user_id AND is_active = true;
  
  -- If user not found or inactive, deny
  IF user_role IS NULL THEN
    RETURN FALSE;
  END IF;
  
  -- Admin role has all permissions
  IF user_role = 'admin' THEN
    RETURN TRUE;
  END IF;
  
  -- Check if permission is in custom permissions
  IF user_custom_perms ? permission_name THEN
    RETURN TRUE;
  END IF;
  
  -- Check if role has this permission
  SELECT EXISTS(
    SELECT 1 FROM role_permissions
    WHERE role = user_role AND role_permissions.permission_name = user_has_permission.permission_name
  ) INTO has_perm;
  
  RETURN has_perm;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- RLS Policies for permissions tables
ALTER TABLE permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_permissions ENABLE ROW LEVEL SECURITY;

-- Anyone can read permissions (for UI display)
CREATE POLICY "Anyone can read permissions"
  ON permissions FOR SELECT
  USING (true);

CREATE POLICY "Anyone can read role_permissions"
  ON role_permissions FOR SELECT
  USING (true);

-- Only admins can modify permissions
CREATE POLICY "Only admins can modify permissions"
  ON permissions FOR ALL
  USING (user_has_permission(auth.uid(), 'manage_permissions'));

CREATE POLICY "Only admins can modify role_permissions"
  ON role_permissions FOR ALL
  USING (user_has_permission(auth.uid(), 'manage_permissions'));

-- Add RLS policy for profiles to check permissions
CREATE POLICY "Users can view profiles in their business"
  ON profiles FOR SELECT
  USING (
    business_id IN (
      SELECT business_id FROM profiles WHERE id = auth.uid()
    )
  );

CREATE POLICY "Only admins can update other user profiles"
  ON profiles FOR UPDATE
  USING (
    id = auth.uid() OR
    user_has_permission(auth.uid(), 'manage_permissions')
  );

-- Create audit log for permission changes
CREATE TABLE IF NOT EXISTS permission_audit_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  business_id UUID NOT NULL REFERENCES businesses(id),
  admin_id UUID NOT NULL REFERENCES profiles(id),
  target_user_id UUID NOT NULL REFERENCES profiles(id),
  action VARCHAR(50) NOT NULL,
  changes JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE permission_audit_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can view audit logs in their business"
  ON permission_audit_log FOR SELECT
  USING (
    business_id IN (
      SELECT business_id FROM profiles WHERE id = auth.uid()
    ) AND
    user_has_permission(auth.uid(), 'manage_permissions')
  );

COMMENT ON TABLE profiles IS 'User profiles with role-based access control';
COMMENT ON COLUMN profiles.role IS 'User role: admin or employee';
COMMENT ON COLUMN profiles.custom_permissions IS 'Array of custom permission names granted to this user';
COMMENT ON TABLE permissions IS 'Master list of all available permissions';
COMMENT ON TABLE role_permissions IS 'Default permissions for each role';
COMMENT ON TABLE permission_audit_log IS 'Audit trail of permission changes';
