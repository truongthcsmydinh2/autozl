#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def check_uuid_functions():
    """Check for functions that still use UUID parameters"""
    try:
        # Get Supabase credentials
        supabase_url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not service_key:
            print("❌ Missing Supabase credentials")
            return
        
        # Create Supabase client
        supabase: Client = create_client(supabase_url, service_key)
        
        # Query to find functions with UUID parameters
        query = """
        SELECT 
            r.routine_name,
            p.parameter_name,
            p.data_type,
            p.ordinal_position
        FROM information_schema.routines r
        JOIN information_schema.parameters p ON r.specific_name = p.specific_name
        WHERE r.routine_schema = 'public' 
        AND p.data_type = 'uuid'
        ORDER BY r.routine_name, p.ordinal_position;
        """
        
        result = supabase.rpc('exec_sql', {'sql': query})
        
        if result.data:
            print("🔍 Functions with UUID parameters found:")
            for row in result.data:
                print(f"  Function: {row['routine_name']} - Parameter: {row['parameter_name']} ({row['data_type']})")
        else:
            print("✅ No functions with UUID parameters found")
            
    except Exception as e:
        print(f"❌ Error checking functions: {e}")
        
        # Alternative: Check using direct SQL query
        print("\n🔄 Trying alternative method...")
        try:
            # Simple query to check if there are any functions that might cause issues
            result = supabase.rpc('exec_sql', {'sql': "SELECT proname FROM pg_proc WHERE proname LIKE '%cleanup%' OR proname LIKE '%find_or_create%';"})
            if result.data:
                print("📋 Found related functions:")
                for row in result.data:
                    print(f"  - {row['proname']}")
        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")

if __name__ == '__main__':
    check_uuid_functions()