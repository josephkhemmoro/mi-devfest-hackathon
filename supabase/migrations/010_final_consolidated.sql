-- ============================================
-- FINAL CONSOLIDATED DATABASE SETUP
-- Run this in Supabase SQL Editor
-- ============================================

-- Add columns to profiles if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='profiles' AND column_name='role') THEN
        ALTER TABLE profiles ADD COLUMN role VARCHAR(50) DEFAULT 'employee';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='profiles' AND column_name='custom_permissions') THEN
        ALTER TABLE profiles ADD COLUMN custom_permissions JSONB DEFAULT '[]'::jsonb;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='profiles' AND column_name='is_active') THEN
        ALTER TABLE profiles ADD COLUMN is_active BOOLEAN DEFAULT true;
    END IF;
END $$;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);
CREATE INDEX IF NOT EXISTS idx_profiles_is_active ON profiles(is_active);

-- Make first user of each business an admin (if not already)
WITH first_users AS (
  SELECT DISTINCT ON (business_id) id, business_id
  FROM profiles
  ORDER BY business_id, created_at ASC
)
UPDATE profiles
SET role = 'admin'
WHERE id IN (SELECT id FROM first_users) AND role != 'admin';

-- Create permissions table
CREATE TABLE IF NOT EXISTS permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) UNIQUE NOT NULL,
  category VARCHAR(50) NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert permissions
INSERT INTO permissions (name, category, description) VALUES
  ('view_dashboard', 'dashboard', 'View dashboard and statistics'),
  ('edit_dashboard', 'dashboard', 'Edit dashboard settings'),
  ('view_inventory', 'inventory', 'View inventory items'),
  ('edit_inventory', 'inventory', 'Add, edit, and delete inventory items'),
  ('generate_orders', 'inventory', 'Generate AI-powered inventory orders'),
  ('view_employees', 'employees', 'View employee list'),
  ('edit_employees', 'employees', 'Add, edit, and delete employees'),
  ('manage_permissions', 'employees', 'Manage user roles and permissions'),
  ('view_schedule', 'schedule', 'View work schedules'),
  ('edit_schedule', 'schedule', 'Create and edit schedules'),
  ('generate_schedule', 'schedule', 'Generate AI-powered schedules'),
  ('set_availability', 'schedule', 'Set own availability'),
  ('view_financials', 'financials', 'View financial data'),
  ('edit_financials', 'financials', 'Edit financial transactions'),
  ('view_reminders', 'reminders', 'View reminders'),
  ('edit_reminders', 'reminders', 'Create and edit reminders'),
  ('set_reminders', 'reminders', 'Set personal reminders'),
  ('edit_business', 'business', 'Edit business settings and branding')
ON CONFLICT (name) DO NOTHING;

-- Create role_permissions table
CREATE TABLE IF NOT EXISTS role_permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  role VARCHAR(50) NOT NULL,
  permission_name VARCHAR(100) NOT NULL REFERENCES permissions(name),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(role, permission_name)
);

-- Admin gets all permissions
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

-- Create audit log
CREATE TABLE IF NOT EXISTS permission_audit_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  business_id UUID NOT NULL REFERENCES businesses(id),
  admin_id UUID NOT NULL REFERENCES profiles(id),
  target_user_id UUID NOT NULL REFERENCES profiles(id),
  action VARCHAR(50) NOT NULL,
  changes JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Drop ALL existing policies on ALL tables
DO $$ 
DECLARE r RECORD;
BEGIN
  -- Drop policies on profiles
  FOR r IN SELECT policyname FROM pg_policies WHERE tablename = 'profiles'
  LOOP
    EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(r.policyname) || ' ON profiles';
  END LOOP;
  
  -- Drop policies on permissions
  FOR r IN SELECT policyname FROM pg_policies WHERE tablename = 'permissions'
  LOOP
    EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(r.policyname) || ' ON permissions';
  END LOOP;
  
  -- Drop policies on role_permissions
  FOR r IN SELECT policyname FROM pg_policies WHERE tablename = 'role_permissions'
  LOOP
    EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(r.policyname) || ' ON role_permissions';
  END LOOP;
  
  -- Drop policies on businesses
  FOR r IN SELECT policyname FROM pg_policies WHERE tablename = 'businesses'
  LOOP
    EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(r.policyname) || ' ON businesses';
  END LOOP;
  
  -- Drop policies on permission_audit_log
  FOR r IN SELECT policyname FROM pg_policies WHERE tablename = 'permission_audit_log'
  LOOP
    EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(r.policyname) || ' ON permission_audit_log';
  END LOOP;
END $$;

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE permission_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE businesses ENABLE ROW LEVEL SECURITY;

-- Simple non-recursive policies for profiles
CREATE POLICY "insert_own_profile" ON profiles FOR INSERT TO authenticated WITH CHECK (id = auth.uid());
CREATE POLICY "select_all_profiles" ON profiles FOR SELECT TO authenticated USING (true);
CREATE POLICY "update_own_profile" ON profiles FOR UPDATE TO authenticated USING (id = auth.uid());
CREATE POLICY "service_role_all" ON profiles FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Policies for permissions tables
CREATE POLICY "Anyone can read permissions" ON permissions FOR SELECT USING (true);
CREATE POLICY "Anyone can read role_permissions" ON role_permissions FOR SELECT USING (true);

-- Policies for businesses table
CREATE POLICY "Authenticated users can create businesses" ON businesses FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "Users can view their business" ON businesses FOR SELECT TO authenticated
  USING (id IN (SELECT business_id FROM profiles WHERE id = auth.uid()));
CREATE POLICY "Users can update their business" ON businesses FOR UPDATE TO authenticated
  USING (id IN (SELECT business_id FROM profiles WHERE id = auth.uid()));
CREATE POLICY "Only admins can delete businesses" ON businesses FOR DELETE TO authenticated
  USING (id IN (SELECT p.business_id FROM profiles p WHERE p.id = auth.uid() AND p.role = 'admin'));

-- Audit log policies
CREATE POLICY "Admins can view audit logs" ON permission_audit_log FOR SELECT TO authenticated
  USING (business_id IN (SELECT business_id FROM profiles WHERE id = auth.uid()));
CREATE POLICY "Admins can insert audit logs" ON permission_audit_log FOR INSERT TO authenticated
  WITH CHECK (business_id IN (SELECT business_id FROM profiles WHERE id = auth.uid()));

-- Grant permissions
GRANT ALL ON profiles TO authenticated;
GRANT ALL ON permissions TO authenticated;
GRANT ALL ON role_permissions TO authenticated;
GRANT ALL ON businesses TO authenticated;
GRANT ALL ON permission_audit_log TO authenticated;

COMMENT ON TABLE profiles IS 'User profiles with RBAC - updated with simplified policies';
