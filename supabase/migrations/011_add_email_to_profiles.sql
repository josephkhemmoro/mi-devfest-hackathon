-- Add email column to profiles for easier access
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email VARCHAR(255);

-- Create index on email
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);

-- Create function to get user emails from auth.users
CREATE OR REPLACE FUNCTION get_user_email(user_id UUID)
RETURNS TEXT AS $$
BEGIN
  RETURN (SELECT email FROM auth.users WHERE id = user_id);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Update existing profiles with emails from auth.users
UPDATE profiles p
SET email = (SELECT email FROM auth.users WHERE id = p.id)
WHERE email IS NULL;

COMMENT ON COLUMN profiles.email IS 'User email - synced from auth.users for easier queries';
