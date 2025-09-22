#!/usr/bin/env python3
"""
Pair utilities for standardized pair ID generation
"""

import re
from typing import Union

def generate_pair_id(device1: Union[str, int], device2: Union[str, int]) -> str:
    """
    Generate standardized pair ID with devices sorted in ascending order.
    
    Args:
        device1: First device (can be IP, device name, or device ID)
        device2: Second device (can be IP, device name, or device ID)
    
    Returns:
        Standardized pair ID in format: pair_{min_id}_{max_id}
    
    Examples:
        generate_pair_id("device_33", "device_10") -> "pair_10_33"
        generate_pair_id("192.168.1.33", "192.168.1.10") -> "pair_10_33"
        generate_pair_id(33, 10) -> "pair_10_33"
        generate_pair_id("machine_7", "machine_3") -> "pair_3_7"
    """
    
    def extract_numeric_id(device: Union[str, int]) -> str:
        """Extract numeric ID from device identifier"""
        if isinstance(device, int):
            return str(device)
        
        # Convert to string and extract numeric part
        device_str = str(device)
        
        # For IP:port format (e.g., "192.168.4.160:5555"), extract IP part
        if ':' in device_str:
            ip_part = device_str.split(':')[0]
            # Extract the last octet of IP (e.g., "160" from "192.168.4.160")
            ip_numbers = re.findall(r'\d+', ip_part)
            if ip_numbers:
                return ip_numbers[-1]
        
        # For device names like "device_1758355653_1", we need to be smarter
        # If it looks like device_timestamp_id format, use the ID part
        # Otherwise, use the last numeric part
        if '_' in device_str:
            parts = device_str.split('_')
            # Check if it's device_timestamp_id format (3 parts, middle is long timestamp)
            if len(parts) == 3 and parts[0] == 'device':
                timestamp_part = parts[1]
                id_part = parts[2]
                # If middle part is a long timestamp (10+ digits) and last part is short ID
                if timestamp_part.isdigit() and len(timestamp_part) >= 10 and id_part.isdigit():
                    return id_part
            
            # For other formats, try to use the last part if it's numeric
            last_part = parts[-1]
            if last_part.isdigit():
                return last_part
        
        # Fallback: find all numbers and use the last one
        numbers = re.findall(r'\d+', device_str)
        if numbers:
            return numbers[-1]
        else:
            # Fallback: use hash of the string if no numbers found
            return str(abs(hash(device_str)) % 10000)
    
    # Extract numeric IDs
    id1 = extract_numeric_id(device1)
    id2 = extract_numeric_id(device2)
    
    # Sort to ensure consistent ordering (string comparison for complex IDs)
    ids = sorted([id1, id2])
    
    return f"pair_{ids[0]}_{ids[1]}"

def extract_device_ids_from_pair_id(pair_id: str) -> tuple[int, int]:
    """
    Extract device IDs from a standardized pair ID.
    
    Args:
        pair_id: Pair ID in format "pair_{id1}_{id2}"
    
    Returns:
        Tuple of (min_id, max_id)
    
    Example:
        extract_device_ids_from_pair_id("pair_10_33") -> (10, 33)
    """
    # Remove "pair_" prefix and split by underscore
    if pair_id.startswith("pair_"):
        ids_part = pair_id[5:]  # Remove "pair_" prefix
        parts = ids_part.split("_")
        
        if len(parts) >= 2:
            try:
                id1 = int(parts[0])
                id2 = int(parts[1])
                return (min(id1, id2), max(id1, id2))
            except ValueError:
                pass
    
    raise ValueError(f"Invalid pair ID format: {pair_id}")

def is_valid_pair_id(pair_id: str) -> bool:
    """
    Check if a pair ID follows the standardized format.
    
    Args:
        pair_id: Pair ID to validate
    
    Returns:
        True if valid, False otherwise
    
    Example:
        is_valid_pair_id("pair_10_33") -> True
        is_valid_pair_id("pair_33_10") -> False (not sorted)
        is_valid_pair_id("invalid_format") -> False
    """
    try:
        min_id, max_id = extract_device_ids_from_pair_id(pair_id)
        # Check if IDs are properly sorted
        return min_id <= max_id
    except ValueError:
        return False

# Test cases for validation
if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("device_33", "device_10", "pair_10_33"),
        ("192.168.1.33", "192.168.1.10", "pair_10_33"),
        (33, 10, "pair_10_33"),
        ("machine_7", "machine_3", "pair_3_7"),
        ("12", "15", "pair_12_15"),
        ("host_99", "host_1", "pair_1_99")
    ]
    
    print("Testing generate_pair_id function:")
    for device1, device2, expected in test_cases:
        result = generate_pair_id(device1, device2)
        status = "✅" if result == expected else "❌"
        print(f"{status} generate_pair_id({device1}, {device2}) = {result} (expected: {expected})")
    
    print("\nTesting validation functions:")
    valid_ids = ["pair_10_33", "pair_3_7", "pair_1_99"]
    invalid_ids = ["pair_33_10", "invalid_format", "pair_abc_def"]
    
    for pair_id in valid_ids:
        result = is_valid_pair_id(pair_id)
        status = "✅" if result else "❌"
        print(f"{status} is_valid_pair_id({pair_id}) = {result}")
    
    for pair_id in invalid_ids:
        result = is_valid_pair_id(pair_id)
        status = "✅" if not result else "❌"
        print(f"{status} is_valid_pair_id({pair_id}) = {result}")