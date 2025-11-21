-- ============================================
-- SIMPLIFY: Single Employee System
-- Remove complex RBAC, just use is_admin boolean
-- ============================================

-- Add is_admin column if not exists
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT false;

-- Update existing admins
UPDATE profiles SET is_admin = true WHERE role = 'admin';
UPDATE profiles SET is_admin = false WHERE role != 'admin';

-- Create simple index
CREATE INDEX IF NOT EXISTS idx_profiles_is_admin ON profiles(is_admin);

-- Drop complex RBAC tables (optional - comment out if you want to keep)
-- DROP TABLE IF EXISTS permission_audit_log CASCADE;
-- DROP TABLE IF EXISTS role_permissions CASCADE;
-- DROP TABLE IF EXISTS permissions CASCADE;

COMMENT ON COLUMN profiles.is_admin IS 'Simple admin flag: true = admin (full access), false = employee (limited access)';
