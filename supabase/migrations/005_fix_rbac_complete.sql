-- ============================================
-- COMPLETE FIX: Drop all dependent policies first, then rebuild
-- ============================================

-- Step 1: Drop ALL policies that depend on user_has_permission
DROP POLICY IF EXISTS "Only admins can modify permissions" ON permissions;
DROP POLICY IF EXISTS "Only admins can modify role_permissions" ON role_permissions;
DROP POLICY IF EXISTS "Admins can view audit logs in their business" ON permission_audit_log;
DROP POLICY IF EXISTS "Users can view profiles in their business" ON profiles;
DROP POLICY IF EXISTS "Only admins can update other user profiles" ON profiles;

-- Step 2: Now we can drop the function
DROP FUNCTION IF EXISTS user_has_permission(UUID, VARCHAR) CASCADE;

-- Step 3: Recreate the function with proper security settings
CREATE OR REPLACE FUNCTION user_has_permission(
  check_user_id UUID,
  permission_name VARCHAR
) RETURNS BOOLEAN AS $$
DECLARE
  user_role VARCHAR;
  user_custom_perms JSONB;
  has_perm BOOLEAN;
BEGIN
  -- Bypass RLS by using explicit schema and security definer context
  SELECT role, custom_permissions INTO user_role, user_custom_perms
  FROM public.profiles
  WHERE id = check_user_id AND is_active = true;
  
  IF user_role IS NULL THEN
    RETURN FALSE;
  END IF;
  
  IF user_role = 'admin' THEN
    RETURN TRUE;
  END IF;
  
  IF user_custom_perms ? permission_name THEN
    RETURN TRUE;
  END IF;
  
  SELECT EXISTS(
    SELECT 1 FROM public.role_permissions rp
    WHERE rp.role = user_role 
    AND rp.permission_name = user_has_permission.permission_name
  ) INTO has_perm;
  
  RETURN has_perm;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- Grant execute to authenticated users
GRANT EXECUTE ON FUNCTION user_has_permission(UUID, VARCHAR) TO authenticated;

-- Step 4: Recreate NON-RECURSIVE policies for profiles table
-- These use direct role checks instead of calling user_has_permission to avoid recursion

-- Users can view their own profile
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  USING (id = auth.uid());

-- Users can view profiles in their business (non-recursive)
CREATE POLICY "Users can view business profiles"
  ON profiles FOR SELECT
  USING (
    business_id IN (
      SELECT business_id FROM profiles WHERE id = auth.uid()
    )
  );

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (id = auth.uid());

-- Admins can update profiles (direct role check, no function call)
CREATE POLICY "Admins can update business profiles"
  ON profiles FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM profiles p
      WHERE p.id = auth.uid()
      AND p.role = 'admin'
      AND p.business_id = profiles.business_id
    )
  );

-- Admins can insert profiles
CREATE POLICY "Admins can insert profiles"
  ON profiles FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM profiles p
      WHERE p.id = auth.uid()
      AND p.role = 'admin'
    )
  );

-- Step 5: Recreate policies for permission tables (these CAN use the function safely)

-- Permissions table
CREATE POLICY "Only admins can modify permissions"
  ON permissions FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Role permissions table
CREATE POLICY "Only admins can modify role_permissions"
  ON role_permissions FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Audit log - admins only
CREATE POLICY "Admins can view audit logs in their business"
  ON permission_audit_log FOR SELECT
  USING (
    business_id IN (
      SELECT business_id FROM profiles WHERE id = auth.uid()
    ) AND
    EXISTS (
      SELECT 1 FROM profiles
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Step 6: Add policy for audit log inserts
CREATE POLICY "Admins can insert audit logs"
  ON permission_audit_log FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

COMMENT ON FUNCTION user_has_permission IS 'Check user permissions without RLS recursion - uses SECURITY DEFINER';
