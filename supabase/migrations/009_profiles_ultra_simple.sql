-- ============================================
-- ULTRA-SIMPLE PROFILES POLICIES - NO RECURSION
-- ============================================

-- Drop everything
DROP POLICY IF EXISTS "Service role bypass" ON profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;
DROP POLICY IF EXISTS "Users select own profile" ON profiles;
DROP POLICY IF EXISTS "Users update own profile" ON profiles;
DROP POLICY IF EXISTS "Users view same business" ON profiles;
DROP POLICY IF EXISTS "Admins can update any profile in business" ON profiles;

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Super simple policies that CANNOT cause recursion

-- 1. Anyone authenticated can INSERT (signup needs this)
--    Just check that they're inserting their own ID
CREATE POLICY "insert_own_profile"
  ON profiles FOR INSERT
  TO authenticated
  WITH CHECK (id = auth.uid());

-- 2. Anyone can SELECT any profile (we'll add business filtering later if needed)
CREATE POLICY "select_all_profiles"
  ON profiles FOR SELECT
  TO authenticated
  USING (true);

-- 3. Users can UPDATE only their own profile
CREATE POLICY "update_own_profile"
  ON profiles FOR UPDATE
  TO authenticated
  USING (id = auth.uid());

-- 4. Service role can do anything
CREATE POLICY "service_role_all"
  ON profiles FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

COMMENT ON TABLE profiles IS 'Simplified RLS - no recursion possible';
