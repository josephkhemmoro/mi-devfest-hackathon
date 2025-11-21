-- ============================================
-- FIX: Allow authenticated users to create businesses during signup
-- ============================================

-- Drop existing restrictive policy if any
DROP POLICY IF EXISTS "Users can only access their own business" ON businesses;

-- Allow authenticated users to INSERT businesses (for signup)
CREATE POLICY "Authenticated users can create businesses"
  ON businesses FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Allow users to view their own business
CREATE POLICY "Users can view their business"
  ON businesses FOR SELECT
  TO authenticated
  USING (
    id IN (
      SELECT business_id FROM profiles WHERE id = auth.uid()
    )
  );

-- Allow users to update their own business
CREATE POLICY "Users can update their business"
  ON businesses FOR UPDATE
  TO authenticated
  USING (
    id IN (
      SELECT business_id FROM profiles WHERE id = auth.uid()
    )
  );

-- Only admins can delete businesses (extra safety)
CREATE POLICY "Only admins can delete businesses"
  ON businesses FOR DELETE
  TO authenticated
  USING (
    id IN (
      SELECT p.business_id 
      FROM profiles p
      WHERE p.id = auth.uid() AND p.role = 'admin'
    )
  );

COMMENT ON POLICY "Authenticated users can create businesses" ON businesses IS 'Allows new users to create a business during signup';
