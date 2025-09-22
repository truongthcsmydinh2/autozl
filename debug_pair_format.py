import requests
import json
from utils.pair_utils import generate_pair_id, is_valid_pair_id

def extract_numeric_id(device_str):
    """Extract numeric ID from device string"""
    import re
    
    # Try to extract from IP:port format (e.g., "192.168.4.158:8080")
    ip_port_match = re.search(r'(\d+\.\d+\.\d+\.(\d+)):(\d+)', device_str)
    if ip_port_match:
        last_octet = int(ip_port_match.group(2))
        port = int(ip_port_match.group(3))
        print(f"  IP:port format - last_octet: {last_octet}, port: {port}")
        return last_octet  # Use last octet of IP
    
    # Try to extract from IP format (e.g., "192.168.4.158")
    ip_match = re.search(r'\d+\.\d+\.\d+\.(\d+)', device_str)
    if ip_match:
        last_octet = int(ip_match.group(1))
        print(f"  IP format - last_octet: {last_octet}")
        return last_octet
    
    # Try to extract from device name with number (e.g., "Device123", "phone_456")
    device_num_match = re.search(r'(\d+)', device_str)
    if device_num_match:
        device_num = int(device_num_match.group(1))
        print(f"  Device name format - number: {device_num}")
        return device_num
    
    # Fallback: use hash of string
    fallback_id = hash(device_str) % 10000
    print(f"  Fallback hash - id: {fallback_id}")
    return fallback_id

def debug_pair_creation():
    print("=== DEBUG PAIR CREATION ===")
    
    # 1. Get devices from API
    print("\n1. Getting devices from API...")
    try:
        response = requests.get('http://localhost:8000/api/devices')
        if response.status_code == 200:
            devices = response.json()
            print(f"Found {len(devices)} devices:")
            print(f"Devices data type: {type(devices)}")
            print(f"Devices content: {devices}")
            
            # Handle different response formats
            if isinstance(devices, dict):
                if 'devices' in devices:
                    device_list = devices['devices']
                elif 'data' in devices:
                    device_list = devices['data']
                else:
                    device_list = list(devices.values())
            else:
                device_list = devices
            
            print(f"Device list: {device_list}")
            
            # Show first 5 devices
            for i in range(min(5, len(device_list))):
                device = device_list[i]
                print(f"  {i+1}. {device}")
                print(f"     Extracted ID: {extract_numeric_id(str(device))}")
        else:
            print(f"Error getting devices: {response.status_code}")
            return
    except Exception as e:
        print(f"Error getting devices: {e}")
        return
    
    # 2. Test with real devices from API
    print("\n2. Testing with real devices...")
    if len(device_list) >= 2:
        # Use actual devices from API
        real_device_a = device_list[0]['device_id'] if isinstance(device_list[0], dict) else str(device_list[0])
        real_device_b = device_list[1]['device_id'] if isinstance(device_list[1], dict) else str(device_list[1])
        
        print(f"\nTesting real devices: {real_device_a} + {real_device_b}")
        print(f"  Device A ID: {extract_numeric_id(real_device_a)}")
        print(f"  Device B ID: {extract_numeric_id(real_device_b)}")
        
        generated_id = generate_pair_id(real_device_a, real_device_b)
        print(f"  Generated pair ID: {generated_id}")
        
        # Try to create this pair via API
        try:
            create_response = requests.post('http://localhost:8000/api/pairs/create', 
                                           json={'device_a': real_device_a, 'device_b': real_device_b})
            if create_response.status_code == 200:
                result = create_response.json()
                print(f"  API response: {result}")
                if 'pair' in result:
                    api_pair_id = result['pair'].get('id', 'N/A')
                    print(f"  API created pair ID: {api_pair_id}")
                    print(f"  Match: {'✓' if api_pair_id == generated_id else '✗'}")
            else:
                print(f"  API error: {create_response.status_code} - {create_response.text}")
        except Exception as e:
            print(f"  API error: {e}")
    
    # 3. Test specific devices that should create pair_158_81
    print("\n3. Testing specific devices for pair_158_81...")
    test_devices = [
        "192.168.4.158:5555",  # Use correct port 5555
        "192.168.4.81:5555",
        "192.168.4.158",
        "192.168.4.81"
    ]
    
    for device_a in test_devices[:2]:
        for device_b in test_devices[2:]:
            print(f"\nTesting: {device_a} + {device_b}")
            print(f"  Device A ID: {extract_numeric_id(device_a)}")
            print(f"  Device B ID: {extract_numeric_id(device_b)}")
            
            generated_id = generate_pair_id(device_a, device_b)
            print(f"  Generated pair ID: {generated_id}")
            
            # Try to create this pair via API
            try:
                create_response = requests.post('http://localhost:8000/api/pairs/create', 
                                               json={'device_a': device_a, 'device_b': device_b})
                if create_response.status_code == 200:
                    result = create_response.json()
                    print(f"  API response: {result}")
                    if 'pair' in result:
                        api_pair_id = result['pair'].get('id', 'N/A')
                        print(f"  API created pair ID: {api_pair_id}")
                    else:
                        print(f"  API created pair: {result.get('pair_id', 'N/A')}")
                else:
                    print(f"  API error: {create_response.status_code} - {create_response.text}")
            except Exception as e:
                print(f"  API error: {e}")
    
    # 4. Check existing pairs in database
    print("\n4. Checking existing pairs...")
    try:
        pairs_response = requests.get('http://localhost:8000/api/pairs')
        if pairs_response.status_code == 200:
            pairs_data = pairs_response.json()
            print(f"Pairs response type: {type(pairs_data)}")
            print(f"Pairs response content: {pairs_data}")
            
            # Handle different response formats
            if isinstance(pairs_data, dict):
                if 'pairs' in pairs_data:
                    pairs = pairs_data['pairs']
                elif 'data' in pairs_data:
                    pairs = pairs_data['data']
                else:
                    pairs = list(pairs_data.values()) if pairs_data else []
            else:
                pairs = pairs_data if isinstance(pairs_data, list) else []
            
            print(f"Found {len(pairs)} existing pairs:")
            
            # Show first 10 pairs
            for i in range(min(10, len(pairs))):
                pair = pairs[i]
                pair_id = pair.get('id', 'N/A')
                device_a = pair.get('device_a', 'N/A')
                device_b = pair.get('device_b', 'N/A')
                
                print(f"  ID: {pair_id}")
                print(f"    Devices: {device_a} + {device_b}")
                
                # Try to regenerate ID
                if device_a != 'N/A' and device_b != 'N/A':
                    regenerated = generate_pair_id(device_a, device_b)
                    match = "✓" if regenerated == pair_id else "✗"
                    print(f"    Regenerated: {regenerated} {match}")
                print()
        else:
            print(f"Error getting pairs: {pairs_response.status_code} - {pairs_response.text}")
    except Exception as e:
        print(f"Error getting pairs: {e}")
    
    # 5. Test the specific case from logs
    print("\n5. Testing specific case from logs...")
    target_pair_id = "pair_158_81"
    print(f"Looking for: {target_pair_id}")
    
    try:
        lookup_response = requests.get(f'http://localhost:8000/api/pairs/{target_pair_id}')
        if lookup_response.status_code == 200:
            print(f"✓ Found pair: {target_pair_id}")
        else:
            print(f"✗ Pair not found: {lookup_response.status_code}")
            print(f"Response text: {lookup_response.text}")
            
            # Try to find what devices would create this ID
            print("\nTrying to reverse engineer devices for this ID...")
            # pair_158_81 means device IDs 158 and 81
            possible_devices = [
                ("192.168.4.158:8080", "192.168.4.81:8080"),
                ("192.168.4.158", "192.168.4.81"),
                ("device_158", "device_81"),
                ("158", "81")
            ]
            
            for device_a, device_b in possible_devices:
                test_id = generate_pair_id(device_a, device_b)
                match = "✓" if test_id == target_pair_id else "✗"
                print(f"  {device_a} + {device_b} = {test_id} {match}")
                
    except Exception as e:
        print(f"Error looking up pair: {e}")

if __name__ == "__main__":
    debug_pair_creation()