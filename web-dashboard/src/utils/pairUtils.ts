/**
 * Pair utilities for standardized pair ID generation
 * This should match the Python implementation in utils/pair_utils.py
 */

/**
 * Generate standardized pair ID with devices sorted in ascending order.
 * 
 * @param device1 First device (can be IP, device name, or device ID)
 * @param device2 Second device (can be IP, device name, or device ID)
 * @returns Standardized pair ID in format: pair_{min_id}_{max_id}
 * 
 * @example
 * generatePairId("device_33", "device_10") // "pair_10_33"
 * generatePairId("192.168.1.33", "192.168.1.10") // "pair_10_33"
 * generatePairId(33, 10) // "pair_10_33"
 * generatePairId("machine_7", "machine_3") // "pair_3_7"
 */
export function generatePairId(device1: string | number, device2: string | number): string {
  /**
   * Extract numeric ID from device identifier
   */
  function extractNumericId(device: string | number): number {
    if (typeof device === 'number') {
      return device;
    }
    
    // Convert to string and extract numeric part
    const deviceStr = String(device);
    
    // For IP:port format (e.g., "192.168.4.160:5555"), extract IP part
    if (deviceStr.includes(':')) {
      const ipPart = deviceStr.split(':')[0];
      // Extract the last octet of IP (e.g., "160" from "192.168.4.160")
      const ipNumbers = ipPart.match(/\d+/g);
      if (ipNumbers && ipNumbers.length > 0) {
        return parseInt(ipNumbers[ipNumbers.length - 1], 10);
      }
    }
    
    // For device names like "device_1758355653_1", extract the part after last underscore
    // If it's a number, use it. Otherwise, extract all numbers
    if (deviceStr.includes('_')) {
      const parts = deviceStr.split('_');
      // Try to use the last part if it's numeric
      const lastPart = parts[parts.length - 1];
      if (/^\d+$/.test(lastPart)) {
        return parseInt(lastPart, 10);
      }
    }
    
    // Fallback: find all numbers and use the last one
    const numbers = deviceStr.match(/\d+/g);
    if (numbers && numbers.length > 0) {
      return parseInt(numbers[numbers.length - 1], 10);
    } else {
      // Fallback: use hash of the string if no numbers found
      let hash = 0;
      for (let i = 0; i < deviceStr.length; i++) {
        const char = deviceStr.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
      }
      return Math.abs(hash) % 10000;
    }
  }
  
  // Extract numeric IDs
  const id1 = extractNumericId(device1);
  const id2 = extractNumericId(device2);
  
  // Sort to ensure consistent ordering (string comparison for complex IDs)
  const ids = [String(id1), String(id2)].sort();
  
  return `pair_${ids[0]}_${ids[1]}`;
}

/**
 * Extract device IDs from a standardized pair ID.
 * 
 * @param pairId Pair ID in format "pair_{id1}_{id2}"
 * @returns Tuple of [min_id, max_id]
 * 
 * @example
 * extractDeviceIdsFromPairId("pair_10_33") // [10, 33]
 */
export function extractDeviceIdsFromPairId(pairId: string): [number, number] {
  // Remove "pair_" prefix and split by underscore
  if (pairId.startsWith("pair_")) {
    const idsPart = pairId.substring(5); // Remove "pair_" prefix
    const parts = idsPart.split("_");
    
    if (parts.length >= 2) {
      try {
        const id1 = parseInt(parts[0], 10);
        const id2 = parseInt(parts[1], 10);
        
        if (!isNaN(id1) && !isNaN(id2)) {
          return [Math.min(id1, id2), Math.max(id1, id2)];
        }
      } catch (error) {
        // Fall through to error
      }
    }
  }
  
  throw new Error(`Invalid pair ID format: ${pairId}`);
}

/**
 * Check if a pair ID follows the standardized format.
 * 
 * @param pairId Pair ID to validate
 * @returns True if valid, false otherwise
 * 
 * @example
 * isValidPairId("pair_10_33") // true
 * isValidPairId("pair_33_10") // false (not sorted)
 * isValidPairId("invalid_format") // false
 */
export function isValidPairId(pairId: string): boolean {
  try {
    const [minId, maxId] = extractDeviceIdsFromPairId(pairId);
    // Check if IDs are properly sorted
    return minId <= maxId;
  } catch (error) {
    return false;
  }
}

/**
 * Create a pair ID from device objects (common frontend use case)
 * 
 * @param deviceA First device object with ip, device_id, or name
 * @param deviceB Second device object with ip, device_id, or name
 * @returns Standardized pair ID
 */
export function createPairIdFromDevices(
  deviceA: { ip?: string; device_id?: string; name?: string },
  deviceB: { ip?: string; device_id?: string; name?: string }
): string {
  // Prefer ip, then device_id, then name
  const deviceAId = deviceA.ip || deviceA.device_id || deviceA.name || 'unknown';
  const deviceBId = deviceB.ip || deviceB.device_id || deviceB.name || 'unknown';
  
  return generatePairId(deviceAId, deviceBId);
}

// Test cases for development/debugging
if (process.env.NODE_ENV === 'development') {
  // Test cases
  const testCases: Array<[string | number, string | number, string]> = [
    ["device_33", "device_10", "pair_10_33"],
    ["192.168.1.33", "192.168.1.10", "pair_10_33"],
    [33, 10, "pair_10_33"],
    ["machine_7", "machine_3", "pair_3_7"],
    ["12", "15", "pair_12_15"],
    ["host_99", "host_1", "pair_1_99"]
  ];
  
  console.log("Testing generatePairId function:");
  testCases.forEach(([device1, device2, expected]) => {
    const result = generatePairId(device1, device2);
    const status = result === expected ? "✅" : "❌";
    console.log(`${status} generatePairId(${device1}, ${device2}) = ${result} (expected: ${expected})`);
  });
  
  console.log("\nTesting validation functions:");
  const validIds = ["pair_10_33", "pair_3_7", "pair_1_99"];
  const invalidIds = ["pair_33_10", "invalid_format", "pair_abc_def"];
  
  validIds.forEach(pairId => {
    const result = isValidPairId(pairId);
    const status = result ? "✅" : "❌";
    console.log(`${status} isValidPairId(${pairId}) = ${result}`);
  });
  
  invalidIds.forEach(pairId => {
    const result = isValidPairId(pairId);
    const status = !result ? "✅" : "❌";
    console.log(`${status} isValidPairId(${pairId}) = ${result}`);
  });
}