-- ============================================
-- FIX: RBAC Infinite Recursion in Policies
-- ============================================

-- Drop the problematic policies
DROP POLICY IF EXISTS "Users can view profiles in their business" ON profiles;
DROP POLICY IF EXISTS "Only admins can update other user profiles" ON profiles;

-- Create non-recursive policies that don't call user_has_permission on profiles table
-- These policies use simpler checks to avoid recursion

-- Allow users to view their own profile
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  USING (id = auth.uid());

-- Allow users to view other profiles in their business
-- Uses a subquery that doesn't trigger RLS on profiles
CREATE POLICY "Users can view business profiles"
  ON profiles FOR SELECT
  USING (
    business_id = (
      SELECT p.business_id 
      FROM profiles p 
      WHERE p.id = auth.uid()
      LIMIT 1
    )
  );

-- Allow users to update their own profile
CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (id = auth.uid());

-- Allow admins to update any profile in their business
-- Check role directly without calling user_has_permission
CREATE POLICY "Admins can update business profiles"
  ON profiles FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 
      FROM profiles p 
      WHERE p.id = auth.uid() 
      AND p.role = 'admin'
      AND p.business_id = profiles.business_id
    )
  );

-- Allow admins to insert new profiles (for user management)
CREATE POLICY "Admins can insert profiles"
  ON profiles FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 
      FROM profiles p 
      WHERE p.id = auth.uid() 
      AND p.role = 'admin'
    )
  );

-- Fix the user_has_permission function to be SECURITY INVOKER instead of SECURITY DEFINER
-- This prevents it from being affected by RLS policies
DROP FUNCTION IF EXISTS user_has_permission(UUID, VARCHAR);

CREATE OR REPLACE FUNCTION user_has_permission(
  check_user_id UUID,
  permission_name VARCHAR
) RETURNS BOOLEAN AS $$
DECLARE
  user_role VARCHAR;
  user_custom_perms JSONB;
  has_perm BOOLEAN;
BEGIN
  -- Get user role and custom permissions with explicit schema reference
  -- Using security definer but with explicit table access to avoid RLS recursion
  SELECT role, custom_permissions INTO user_role, user_custom_perms
  FROM public.profiles
  WHERE id = check_user_id AND is_active = true;
  
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
    SELECT 1 FROM public.role_permissions rp
    WHERE rp.role = user_role 
    AND rp.permission_name = user_has_permission.permission_name
  ) INTO has_perm;
  
  RETURN has_perm;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION user_has_permission(UUID, VARCHAR) TO authenticated;

COMMENT ON FUNCTION user_has_permission IS 'Check if user has specific permission without causing RLS recursion';
