-- Migration: Add timezone field to users table
-- Date: 2024-03-15
-- Description: Add timezone column to support proper Google Calendar timezone handling

-- Add timezone column to users table
ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';

-- Update existing users to have UTC timezone as default
UPDATE users SET timezone = 'UTC' WHERE timezone IS NULL OR timezone = '';

-- Add comment for documentation
COMMENT ON COLUMN users.timezone IS 'IANA timezone identifier (e.g., Europe/Madrid, America/New_York)';

-- Verify the migration
SELECT COUNT(*) as users_with_timezone FROM users WHERE timezone IS NOT NULL;