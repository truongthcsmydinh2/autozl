#!/usr/bin/env python3
from utils.pair_utils import generate_pair_id

print('Test pair generation for devices 81 and 85:')
device1 = '192.168.5.81:5555'
device2 = '192.168.5.85:5555'
result = generate_pair_id(device1, device2)
print(f'{device1} + {device2} = {result}')

# Test reverse order
result_reverse = generate_pair_id(device2, device1)
print(f'{device2} + {device1} = {result_reverse}')

print(f'\nBoth should be the same: {result == result_reverse}')