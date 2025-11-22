-- Drop staffing_rules table
-- This table has been replaced by shift_slots which provide more granular scheduling control

DROP TABLE IF EXISTS staffing_rules CASCADE;

COMMENT ON DATABASE postgres IS 'Removed staffing_rules table - replaced by shift_slots for time-specific scheduling';
