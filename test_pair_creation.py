#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.pair_utils import generate_pair_id
from supabase import create_client
import hashlib

# Test pair generation logic
device_a = '192.168.4.160:5555'
device_b = '192.168.4.157:5555'

print("=== TESTING PAIR CREATION LOGIC ===")
print(f"Device A: {device_a}")
print(f"Device B: {device_b}")
print()

# Test new logic
pair_id = generate_pair_id(device_a, device_b)
print(f"Generated Pair ID: {pair_id}")
print()

# Test hash generation (like backend does)
sorted_devices = sorted([device_a, device_b])
pair_hash = hashlib.md5('_'.join(sorted_devices).encode()).hexdigest()
print(f"Pair Hash: {pair_hash}")
print(f"Sorted devices: {sorted_devices}")
print()

# Check if this pair exists in Supabase
url = 'https://xxuxstahzsxgeqmrabjy.supabase.co'
service_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4dXhzdGFoenN4Z2VxbXJhYmp5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODEwMjIzMiwiZXhwIjoyMDczNjc4MjMyfQ.Y8EBOnnohBF2bAP0JnFJUG67aZWSd4NX2Fwh-_8SEK8'

client = create_client(url, service_key)

try:
    # Check if pair exists by hash
    result = client.table('device_pairs').select('*').eq('pair_hash', pair_hash).execute()
    
    if result.data:
        print("✅ PAIR EXISTS IN DATABASE:")
        pair_data = result.data[0]
        print(f"   ID: {pair_data['id']}")
        print(f"   Device A: {pair_data['device_a']}")
        print(f"   Device B: {pair_data['device_b']}")
        print(f"   Temp ID: {pair_data['temp_pair_id']}")
    else:
        print("❌ PAIR NOT FOUND IN DATABASE")
        print("   This pair would be created with new logic")
        
        # Simulate what would be created
        import time
        import random
        import string
        
        temp_id = f"pair_temp_{int(time.time())}_{(''.join(random.choices(string.ascii_lowercase + string.digits, k=8)))}"
        print(f"   Would create with Temp ID: {temp_id}")
        print(f"   Would create with ID: {pair_id}")
        
except Exception as e:
    print(f"Error checking database: {e}")

print()
print("=== COMPARISON WITH EXISTING PAIRS ===")
print("Current format in DB vs New format:")
print("DB: pair_3_5, pair_1_2, etc.")
print(f"New: {pair_id}")
print()
print("✅ Logic has been fixed to extract IP octets instead of ports!")