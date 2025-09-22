#!/usr/bin/env python3

from supabase import create_client

# Supabase config
url = 'https://xxuxstahzsxgeqmrabjy.supabase.co'
service_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4dXhzdGFoenN4Z2VxbXJhYmp5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODEwMjIzMiwiZXhwIjoyMDczNjc4MjMyfQ.Y8EBOnnohBF2bAP0JnFJUG67aZWSd4NX2Fwh-_8SEK8'

client = create_client(url, service_key)

try:
    result = client.table('device_pairs').select('id, device_a, device_b, temp_pair_id').limit(10).execute()
    
    print('Current pairs in Supabase:')
    print('=' * 50)
    
    for row in result.data:
        print(f'ID: {row["id"]}')
        print(f'Device A: {row["device_a"]}')
        print(f'Device B: {row["device_b"]}')
        print(f'Temp ID: {row["temp_pair_id"]}')
        print('-' * 30)
        
    print(f'\nTotal pairs found: {len(result.data)}')
    
except Exception as e:
    print(f'Error: {e}')