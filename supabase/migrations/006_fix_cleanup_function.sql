-- Fix cleanup_old_summaries function to use TEXT instead of UUID
-- This fixes the UUID syntax error when saving summaries

-- Drop the old function
DROP FUNCTION IF EXISTS cleanup_old_summaries(UUID);

-- Recreate with TEXT parameter
CREATE OR REPLACE FUNCTION cleanup_old_summaries(target_pair_id TEXT)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM conversation_summaries 
    WHERE pair_id = target_pair_id 
    AND id NOT IN (
        SELECT id FROM conversation_summaries 
        WHERE pair_id = target_pair_id 
        ORDER BY created_at DESC 
        LIMIT 3
    );
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Also fix find_or_create_device_pair function to return TEXT
DROP FUNCTION IF EXISTS find_or_create_device_pair(VARCHAR(50), VARCHAR(50));

CREATE OR REPLACE FUNCTION find_or_create_device_pair(
    device_a_param VARCHAR(50),
    device_b_param VARCHAR(50)
)
RETURNS TEXT AS $$
DECLARE
    pair_id TEXT;
    sorted_devices TEXT[];
    pair_hash_value VARCHAR(64);
    temp_pair_id_value VARCHAR(100);
    standardized_pair_id TEXT;
BEGIN
    -- Sort devices to ensure AB = BA
    IF device_a_param <= device_b_param THEN
        sorted_devices := ARRAY[device_a_param, device_b_param];
    ELSE
        sorted_devices := ARRAY[device_b_param, device_a_param];
    END IF;
    
    -- Generate hash
    pair_hash_value := md5(array_to_string(sorted_devices, '_'));
    
    -- Generate standardized pair ID
    standardized_pair_id := 'pair_' || 
        regexp_replace(sorted_devices[1], '[^0-9]', '', 'g') || '_' ||
        regexp_replace(sorted_devices[2], '[^0-9]', '', 'g');
    
    -- Try to find existing pair
    SELECT id INTO pair_id FROM device_pairs WHERE pair_hash = pair_hash_value;
    
    -- Create new pair if not found
    IF pair_id IS NULL THEN
        temp_pair_id_value := 'pair_temp_' || extract(epoch from now())::bigint || '_' || substr(md5(random()::text), 1, 8);
        
        INSERT INTO device_pairs (id, device_a, device_b, pair_hash, temp_pair_id)
        VALUES (standardized_pair_id, sorted_devices[1], sorted_devices[2], pair_hash_value, temp_pair_id_value)
        RETURNING id INTO pair_id;
    END IF;
    
    RETURN pair_id;
END;
$$ LANGUAGE plpgsql;