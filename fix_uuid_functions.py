#!/usr/bin/env python3
"""
Fix UUID functions in database to use TEXT instead
This fixes the 'invalid input syntax for type uuid: "pair_86_93"' error
"""

import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

def fix_database_functions():
    """Fix database functions to use TEXT instead of UUID"""
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not service_key:
        print("❌ Missing Supabase credentials in .env file")
        return False
    
    # Parse database URL from Supabase URL
    # Supabase URL format: https://xxx.supabase.co
    # Database URL format: postgresql://postgres:[password]@db.xxx.supabase.co:5432/postgres
    
    try:
        # Extract project reference from Supabase URL
        parsed = urlparse(supabase_url)
        project_ref = parsed.hostname.split('.')[0]
        
        # Construct database URL
        # Note: You'll need to get the actual database password from Supabase dashboard
        print("⚠️  This script requires direct database access.")
        print("Please get your database password from Supabase dashboard > Settings > Database")
        print("Or use the Supabase CLI to apply the migration.")
        print("")
        print("Alternative solution: Apply the SQL manually in Supabase SQL Editor:")
        print("")
        
        # Print the SQL that needs to be executed
        sql_commands = [
            "-- Fix cleanup_old_summaries function",
            "DROP FUNCTION IF EXISTS cleanup_old_summaries(UUID);",
            "",
            "CREATE OR REPLACE FUNCTION cleanup_old_summaries(target_pair_id TEXT)",
            "RETURNS INTEGER AS $$",
            "DECLARE",
            "    deleted_count INTEGER;",
            "BEGIN",
            "    DELETE FROM conversation_summaries ",
            "    WHERE pair_id = target_pair_id ",
            "    AND id NOT IN (",
            "        SELECT id FROM conversation_summaries ",
            "        WHERE pair_id = target_pair_id ",
            "        ORDER BY created_at DESC ",
            "        LIMIT 3",
            "    );",
            "    ",
            "    GET DIAGNOSTICS deleted_count = ROW_COUNT;",
            "    RETURN deleted_count;",
            "END;",
            "$$ LANGUAGE plpgsql;",
            "",
            "-- Fix find_or_create_device_pair function",
            "DROP FUNCTION IF EXISTS find_or_create_device_pair(VARCHAR(50), VARCHAR(50));",
            "",
            "CREATE OR REPLACE FUNCTION find_or_create_device_pair(",
            "    device_a_param VARCHAR(50),",
            "    device_b_param VARCHAR(50)",
            ")",
            "RETURNS TEXT AS $$",
            "DECLARE",
            "    pair_id TEXT;",
            "    sorted_devices TEXT[];",
            "    pair_hash_value VARCHAR(64);",
            "    temp_pair_id_value VARCHAR(100);",
            "    standardized_pair_id TEXT;",
            "BEGIN",
            "    -- Sort devices to ensure AB = BA",
            "    IF device_a_param <= device_b_param THEN",
            "        sorted_devices := ARRAY[device_a_param, device_b_param];",
            "    ELSE",
            "        sorted_devices := ARRAY[device_b_param, device_a_param];",
            "    END IF;",
            "    ",
            "    -- Generate hash",
            "    pair_hash_value := md5(array_to_string(sorted_devices, '_'));",
            "    ",
            "    -- Generate standardized pair ID",
            "    standardized_pair_id := 'pair_' || ",
            "        regexp_replace(sorted_devices[1], '[^0-9]', '', 'g') || '_' ||",
            "        regexp_replace(sorted_devices[2], '[^0-9]', '', 'g');",
            "    ",
            "    -- Try to find existing pair",
            "    SELECT id INTO pair_id FROM device_pairs WHERE pair_hash = pair_hash_value;",
            "    ",
            "    -- Create new pair if not found",
            "    IF pair_id IS NULL THEN",
            "        temp_pair_id_value := 'pair_temp_' || extract(epoch from now())::bigint || '_' || substr(md5(random()::text), 1, 8);",
            "        ",
            "        INSERT INTO device_pairs (id, device_a, device_b, pair_hash, temp_pair_id)",
            "        VALUES (standardized_pair_id, sorted_devices[1], sorted_devices[2], pair_hash_value, temp_pair_id_value)",
            "        RETURNING id INTO pair_id;",
            "    END IF;",
            "    ",
            "    RETURN pair_id;",
            "END;",
            "$$ LANGUAGE plpgsql;"
        ]
        
        print("Copy and paste this SQL into Supabase SQL Editor:")
        print("=" * 60)
        for line in sql_commands:
            print(line)
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("=== Fixing Database UUID Functions ===")
    fix_database_functions()
    print("\n📝 Please execute the SQL commands above in Supabase SQL Editor to fix the UUID error.")