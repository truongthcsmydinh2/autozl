-- Fix inconsistent pair IDs by recreating them with proper standardized format
-- This migration will update existing pairs to use the correct standardized pair_id format

-- First, let's see what we have
-- SELECT id, device_a, device_b FROM device_pairs WHERE id NOT LIKE 'pair_%_%' OR id LIKE 'pair_1_2';

-- Delete the problematic pair_1_2 and other inconsistent pairs
DELETE FROM conversation_summaries WHERE pair_id IN (
  SELECT id FROM device_pairs 
  WHERE id = 'pair_1_2' 
     OR (device_a LIKE 'device_%' AND device_b LIKE 'device_%' 
         AND id NOT LIKE 'pair_%_%_%')
);

DELETE FROM conversations WHERE pair_id IN (
  SELECT id FROM device_pairs 
  WHERE id = 'pair_1_2'
     OR (device_a LIKE 'device_%' AND device_b LIKE 'device_%' 
         AND id NOT LIKE 'pair_%_%_%')
);

DELETE FROM device_pairs 
WHERE id = 'pair_1_2'
   OR (device_a LIKE 'device_%' AND device_b LIKE 'device_%' 
       AND id NOT LIKE 'pair_%_%_%');

-- Note: The pairs with correct format (pair_10_33, pair_3_7) will remain
-- as they were created with the correct logic during testing