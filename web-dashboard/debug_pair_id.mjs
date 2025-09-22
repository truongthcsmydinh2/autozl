// Test pair ID generation with actual device data

// Updated Frontend logic (from pairUtils.ts after fix)
function extractNumericId(device) {
    if (typeof device === 'number') {
        return device;
    }
    
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

function generatePairId(device1, device2) {
    const id1 = extractNumericId(device1);
    const id2 = extractNumericId(device2);
    
    // Sort to ensure consistent ordering (string comparison for complex IDs)
    const ids = [String(id1), String(id2)].sort();
    
    return `pair_${ids[0]}_${ids[1]}`;
}

// Backend logic (from pair_utils.py)
function extractNumericIdBackend(device) {
    if (typeof device === 'number') {
        return String(device);
    }
    
    const deviceStr = String(device);
    
    // For IP:port format (e.g., "192.168.4.160:5555"), extract IP part
    if (deviceStr.includes(':')) {
        const ipPart = deviceStr.split(':')[0];
        // Extract the last octet of IP (e.g., "160" from "192.168.4.160")
        const ipNumbers = ipPart.match(/\d+/g);
        if (ipNumbers) {
            return ipNumbers[ipNumbers.length - 1];
        }
    }
    
    // For device names like "device_1758355653_1", extract the part after last underscore
    if (deviceStr.includes('_')) {
        const parts = deviceStr.split('_');
        const lastPart = parts[parts.length - 1];
        if (/^\d+$/.test(lastPart)) {
            return lastPart;
        }
    }
    
    // Fallback: find all numbers and use the last one
    const numbers = deviceStr.match(/\d+/g);
    if (numbers) {
        return numbers[numbers.length - 1];
    } else {
        // Fallback: use hash of the string if no numbers found
        return String(Math.abs(deviceStr.split('').reduce((a, b) => {
            a = ((a << 5) - a) + b.charCodeAt(0);
            return a & a;
        }, 0)) % 10000);
    }
}

function generatePairIdBackend(device1, device2) {
    const id1 = extractNumericIdBackend(device1);
    const id2 = extractNumericIdBackend(device2);
    
    const ids = [id1, id2].sort();
    return `pair_${ids[0]}_${ids[1]}`;
}

// Test with actual device data
const testDevices = [
    { device_id: "192.168.5.76:5555", ip: "192.168.5.76", name: "Máy 5" },
    { device_id: "192.168.5.93:5555", ip: "192.168.5.93", name: "Máy 20" },
    { device_id: "192.168.4.156:5555", ip: "192.168.4.156", name: "Máy 33" },
    { device_id: "192.168.5.88:5555", ip: "192.168.5.88", name: "Máy 10" }
];

console.log('=== FRONTEND LOGIC TEST (FINAL) ===');
const device1 = testDevices[0]; // 192.168.5.76:5555
const device2 = testDevices[1]; // 192.168.5.93:5555

console.log(`Device 1: ${device1.device_id}`);
console.log(`Device 2: ${device2.device_id}`);

// Frontend uses device.id (which is device_id from useDevices.ts)
const frontendPairId = generatePairId(device1.device_id, device2.device_id);
console.log(`Frontend pair ID: ${frontendPairId}`);

console.log('\n=== BACKEND LOGIC TEST ===');
const backendPairId = generatePairIdBackend(device1.device_id, device2.device_id);
console.log(`Backend pair ID: ${backendPairId}`);

console.log('\n=== COMPARISON ===');
console.log(`Frontend: ${frontendPairId}`);
console.log(`Backend:  ${backendPairId}`);
console.log(`Match: ${frontendPairId === backendPairId}`);

console.log('\n=== EXTRACT DETAILS ===');
console.log(`Frontend extract from "${device1.device_id}": ${extractNumericId(device1.device_id)}`);
console.log(`Backend extract from "${device1.device_id}": ${extractNumericIdBackend(device1.device_id)}`);
console.log(`Frontend extract from "${device2.device_id}": ${extractNumericId(device2.device_id)}`);
console.log(`Backend extract from "${device2.device_id}": ${extractNumericIdBackend(device2.device_id)}`);

console.log('\n=== TEST ALL CASES ===');
const testCases = [
    ["192.168.5.76:5555", "192.168.5.93:5555"],
    ["192.168.4.156:5555", "192.168.5.88:5555"],
    ["device_1758355653_1", "device_1758355653_2"],
    ["192.168.1.10", "192.168.1.33"],
    ["device_33", "device_10"]
];

testCases.forEach(([dev1, dev2], index) => {
    const frontendResult = generatePairId(dev1, dev2);
    const backendResult = generatePairIdBackend(dev1, dev2);
    const match = frontendResult === backendResult;
    console.log(`Test ${index + 1}: ${dev1} + ${dev2}`);
    console.log(`  Frontend: ${frontendResult}`);
    console.log(`  Backend:  ${backendResult}`);
    console.log(`  Match: ${match ? '✅' : '❌'}`);
});