from utils.data_manager import data_manager

# Check devices from data_manager
devices = data_manager.device_repo.get_all_devices()
print('Devices from data_manager:')
if hasattr(devices, 'data'):
    device_list = devices.data or []
else:
    device_list = devices or []

for device in device_list[:5]:
    print(f'{device["device_id"]}: phone={device.get("phone_number", "NULL")}')

print(f'\nTotal devices: {len(device_list)}')

# Also check phone mapping
print('\nPhone mapping:')
for device_id, phone in list(data_manager.phone_mapping.items())[:5]:
    print(f'{device_id}: {phone}')