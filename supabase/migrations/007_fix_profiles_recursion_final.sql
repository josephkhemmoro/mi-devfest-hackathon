-- ============================================
-- FINAL FIX: Remove ALL recursive policies on profiles
-- ============================================

-- Drop ALL policies on profiles table
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can view business profiles" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Admins can update business profiles" ON profiles;
DROP POLICY IF EXISTS "Admins can insert profiles" ON profiles;

-- Temporarily disable RLS to allow signup to work
-- We'll use service role key in backend for profile operations
ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;

-- Re-enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create SIMPLE policies that don't cause recursion
-- Key: Don't query profiles table in the USING clause for profiles policies!

-- Allow service role to do anything (backend uses service role key)
CREATE POLICY "Service role full access"
  ON profiles FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Allow users to SELECT their own profile only
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  TO authenticated
  USING (id = auth.uid());

-- Allow users to UPDATE their own profile only  
CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  TO authenticated
  USING (id = auth.uid())
  WITH CHECK (id = auth.uid());

-- For INSERT: Only allow during signup (backend will use service role)
-- For admin operations: Backend will use service role key
-- This avoids recursion entirely

COMMENT ON TABLE profiles IS 'User profiles - backend uses service role for complex operations to avoid RLS recursion';
