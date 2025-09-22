-- Clean existing data to test fresh standardized pair IDs
-- This migration removes old data that might interfere with testing

-- Delete all existing data from related tables first (due to foreign key constraints)
DELETE FROM conversation_summaries;
DELETE FROM conversations;
DELETE FROM device_pairs;

-- Reset any sequences if they exist
-- Note: Since we changed to text IDs, there shouldn't be sequences, but this is for safety

-- Verify tables are empty
-- SELECT COUNT(*) FROM device_pairs; -- Should return 0
-- SELECT COUNT(*) FROM conversations; -- Should return 0  
-- SELECT COUNT(*) FROM conversation_summaries; -- Should return 0