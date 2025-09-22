// Test script for pair utils logic

function extractNumericId(device) {
  const deviceStr = String(device);
  
  // For IP:port format (e.g., "192.168.4.160:5555"), extract IP part
  if (deviceStr.includes(':')) {
    const ipPart = deviceStr.split(':')[0];
    // Extract the last octet of IP (e.g., "160" from "192.168.4.160")
    const ipNumbers = ipPart.match(/\d+/g);
    if (ipNumbers && ipNumbers.length > 0) {
      return ipNumbers[ipNumbers.length - 1];
    }
  }
  
  // Extract all numbers from the string
  const numbers = deviceStr.match(/\d+/g);
  if (numbers && numbers.length > 0) {
    // Use the last number found
    return numbers[numbers.length - 1];
  }
  
  // Fallback: use hash if no numbers found
  return String(Math.abs(deviceStr.split('').reduce((a, b) => {
    a = ((a << 5) - a) + b.charCodeAt(0);
    return a & a;
  }, 0)) % 10000);
}

function generatePairId(device1, device2) {
  const id1 = extractNumericId(device1);
  const id2 = extractNumericId(device2);
  
  // Sort to ensure consistent ordering
  const ids = [id1, id2].sort((a, b) => parseInt(a) - parseInt(b));
  
  return `pair_${ids[0]}_${ids[1]}`;
}

// Test cases
console.log('Test 1:', generatePairId('192.168.4.160:5555', '192.168.4.157:5555'));
console.log('Test 2:', generatePairId('192.168.5.82:5555', '192.168.5.76:5555'));
console.log('Test 3:', generatePairId('192.168.4.160:5555', '192.168.5.82:5555'));
console.log('Test 4:', generatePairId('192.168.5.88:5555', '192.168.5.81:5555'));