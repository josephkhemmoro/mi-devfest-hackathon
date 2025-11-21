-- ============================================
-- SIMPLE NON-RECURSIVE POLICIES FOR PROFILES
-- ============================================

-- Drop all existing policies
DROP POLICY IF EXISTS "Service role full access" ON profiles;
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can view business profiles" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Admins can update business profiles" ON profiles;
DROP POLICY IF EXISTS "Admins can insert profiles" ON profiles;

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- CRITICAL: These policies MUST NOT query the profiles table to avoid recursion

-- 1. Allow users to INSERT their own profile during signup
-- Check: The new row's ID must match the authenticated user's ID
CREATE POLICY "Users can insert own profile"
  ON profiles FOR INSERT
  TO authenticated
  WITH CHECK (id = auth.uid());

-- 2. Allow users to SELECT their own profile
CREATE POLICY "Users select own profile"
  ON profiles FOR SELECT
  TO authenticated
  USING (id = auth.uid());

-- 3. Allow users to UPDATE their own profile
CREATE POLICY "Users update own profile"
  ON profiles FOR UPDATE
  TO authenticated
  USING (id = auth.uid())
  WITH CHECK (id = auth.uid());

-- 4. Use a stored user's business_id in their JWT metadata to allow viewing business peers
-- This requires that we store business_id in the user's auth metadata (which we do!)
CREATE POLICY "Users view same business"
  ON profiles FOR SELECT
  TO authenticated
  USING (
    business_id = (auth.jwt() -> 'user_metadata' ->> 'business_id')::uuid
  );

-- 5. For admin operations (updating other users), we check the JWT metadata role
-- Backend sets role in JWT during login
CREATE POLICY "Admins can update any profile in business"
  ON profiles FOR UPDATE
  TO authenticated
  USING (
    (auth.jwt() -> 'user_metadata' ->> 'business_id')::uuid = business_id
    AND role = 'admin'
  )
  WITH CHECK (
    (auth.jwt() -> 'user_metadata' ->> 'business_id')::uuid = business_id
  );

-- 6. Service role has full access (for backend service operations)
CREATE POLICY "Service role bypass"
  ON profiles FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

COMMENT ON POLICY "Users view same business" ON profiles IS 'Uses JWT metadata to avoid recursion';
