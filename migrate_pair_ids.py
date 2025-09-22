#!/usr/bin/env python3
"""
Migration script to fix inconsistent pair IDs in database
"""

import os
from supabase import create_client
from dotenv import load_dotenv
from utils.pair_utils import generate_pair_id

load_dotenv()

def migrate_pair_ids():
    """Migrate old format pair IDs to new standardized format"""
    
    # Initialize Supabase client
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    supabase = create_client(url, key)
    
    print("Starting pair ID migration...")
    print("=" * 50)
    
    try:
        # Get all device pairs
        result = supabase.table('device_pairs').select('*').execute()
        
        if not result.data:
            print("No pairs found in database.")
            return
        
        pairs_to_update = []
        
        print(f"Found {len(result.data)} pairs. Checking for inconsistencies...\n")
        
        for pair in result.data:
            current_id = pair['id']
            device_a = pair['device_a']
            device_b = pair['device_b']
            
            # Generate what the ID should be with current logic
            correct_id = generate_pair_id(device_a, device_b)
            
            if current_id != correct_id:
                pairs_to_update.append({
                    'current_id': current_id,
                    'correct_id': correct_id,
                    'device_a': device_a,
                    'device_b': device_b,
                    'pair_hash': pair['pair_hash'],
                    'temp_pair_id': pair['temp_pair_id'],
                    'created_at': pair['created_at']
                })
                
                print(f"❌ Inconsistent: {current_id}")
                print(f"   Devices: {device_a} + {device_b}")
                print(f"   Should be: {correct_id}")
                print()
            else:
                print(f"✅ Consistent: {current_id}")
        
        if not pairs_to_update:
            print("\n🎉 All pair IDs are already consistent!")
            return
        
        print(f"\n📝 Found {len(pairs_to_update)} pairs that need updating.")
        
        # Ask for confirmation
        response = input("\nDo you want to proceed with the migration? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return
        
        print("\nStarting migration...")
        
        updated_count = 0
        error_count = 0
        
        for pair_update in pairs_to_update:
            try:
                current_id = pair_update['current_id']
                correct_id = pair_update['correct_id']
                
                # Check if the correct ID already exists
                existing_check = supabase.table('device_pairs').select('id').eq('id', correct_id).execute()
                
                if existing_check.data:
                    print(f"⚠️  Skipping {current_id} -> {correct_id} (target ID already exists)")
                    continue
                
                # Update the pair ID
                update_result = supabase.table('device_pairs').update({
                    'id': correct_id
                }).eq('id', current_id).execute()
                
                if update_result.data:
                    print(f"✅ Updated: {current_id} -> {correct_id}")
                    updated_count += 1
                else:
                    print(f"❌ Failed to update: {current_id}")
                    error_count += 1
                    
            except Exception as e:
                print(f"❌ Error updating {current_id}: {str(e)}")
                error_count += 1
        
        print(f"\n📊 Migration Summary:")
        print(f"   ✅ Successfully updated: {updated_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"   📝 Total processed: {len(pairs_to_update)}")
        
        if updated_count > 0:
            print("\n🎉 Migration completed! Pair IDs are now consistent.")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")

if __name__ == "__main__":
    migrate_pair_ids()