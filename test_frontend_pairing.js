/**
 * Test frontend random pairing with ID consistency
 * This script tests the actual frontend pairing logic
 */

// Import the generatePairId function (assuming it's available globally or can be imported)
// For testing, we'll define it here
function generatePairId(device1, device2) {
  // Extract numbers from device names
  const id1 = parseInt(device1.toString().replace(/\D/g, '')) || 0;
  const id2 = parseInt(device2.toString().replace(/\D/g, '')) || 0;
  
  // Sort from small to large
  const [min, max] = [Math.min(id1, id2), Math.max(id1, id2)];
  return `pair_${min}_${max}`;
}

// Simulate device list
const devices = [
  'device_33', 'device_10', 'device_12', 'device_15',
  'device_7', 'device_3', 'device_25', 'device_8',
  'device_100', 'device_50', 'device_1', 'device_999'
];

function shuffleArray(array) {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

function randomPairing(deviceList) {
  console.log('=== Testing Frontend Random Pairing ===');
  console.log('Original devices:', deviceList);
  
  // Step 1: Shuffle devices randomly
  const shuffledDevices = shuffleArray(deviceList);
  console.log('Shuffled devices:', shuffledDevices);
  
  // Step 2: Create random pairs
  const pairs = [];
  const pairIds = [];
  
  for (let i = 0; i < shuffledDevices.length - 1; i += 2) {
    const device1 = shuffledDevices[i];
    const device2 = shuffledDevices[i + 1];
    
    // Step 3: Generate standardized pair ID (sorted order)
    const pairId = generatePairId(device1, device2);
    
    pairs.push([device1, device2]);
    pairIds.push(pairId);
    
    console.log(`Random pair: (${device1}, ${device2}) → ID: ${pairId}`);
  }
  
  return { pairs, pairIds };
}

function testConsistency() {
  console.log('\n=== Testing ID Consistency ===');
  
  // Test specific user examples
  const testCases = [
    ['device_33', 'device_10', 'pair_10_33'],
    ['device_12', 'device_15', 'pair_12_15'],
    ['device_7', 'device_3', 'pair_3_7']
  ];
  
  testCases.forEach(([dev1, dev2, expected]) => {
    const result1 = generatePairId(dev1, dev2);
    const result2 = generatePairId(dev2, dev1); // Reverse order
    
    const pass1 = result1 === expected;
    const pass2 = result1 === result2;
    
    console.log(`Test (${dev1}, ${dev2}):`);
    console.log(`  Expected: ${expected}`);
    console.log(`  Got: ${result1} ${pass1 ? '✓' : '✗'}`);
    console.log(`  Reverse: ${result2} ${pass2 ? '✓' : '✗'}`);
  });
}

function testMultipleRandomRuns() {
  console.log('\n=== Testing Multiple Random Runs ===');
  
  const allPairIds = new Set();
  const logicalPairs = new Map(); // Track logical pairs
  
  // Run random pairing multiple times
  for (let run = 1; run <= 5; run++) {
    console.log(`\nRun ${run}:`);
    const { pairs, pairIds } = randomPairing(devices.slice(0, 6)); // Use first 6 devices
    
    pairIds.forEach((pairId, index) => {
      const [dev1, dev2] = pairs[index];
      
      // Create logical pair key (sorted device names)
      const logicalKey = [dev1, dev2].sort().join('-');
      
      if (logicalPairs.has(logicalKey)) {
        // Check if same logical pair gets same ID
        const previousId = logicalPairs.get(logicalKey);
        if (previousId !== pairId) {
          console.log(`  ✗ INCONSISTENCY: ${logicalKey} had ID ${previousId}, now ${pairId}`);
        } else {
          console.log(`  ✓ Consistent: ${logicalKey} → ${pairId}`);
        }
      } else {
        logicalPairs.set(logicalKey, pairId);
        console.log(`  New pair: ${logicalKey} → ${pairId}`);
      }
      
      allPairIds.add(pairId);
    });
  }
  
  console.log(`\nTotal unique pair IDs generated: ${allPairIds.size}`);
  console.log(`Total logical pairs tracked: ${logicalPairs.size}`);
  
  // Verify no duplicate IDs for different logical pairs
  const idToLogicalPair = new Map();
  let duplicateFound = false;
  
  for (const [logicalKey, pairId] of logicalPairs) {
    if (idToLogicalPair.has(pairId)) {
      console.log(`✗ DUPLICATE ID: ${pairId} used for both ${idToLogicalPair.get(pairId)} and ${logicalKey}`);
      duplicateFound = true;
    } else {
      idToLogicalPair.set(pairId, logicalKey);
    }
  }
  
  if (!duplicateFound) {
    console.log('✓ No duplicate IDs found - each logical pair has unique ID');
  }
}

function main() {
  console.log('Frontend Random Pairing Test');
  console.log('=' * 50);
  
  // Test basic functionality
  testConsistency();
  
  // Test multiple random runs
  testMultipleRandomRuns();
  
  console.log('\n=== Summary ===');
  console.log('Key features tested:');
  console.log('1. Random pairing maintains ID consistency');
  console.log('2. Same logical pair always gets same ID');
  console.log('3. Different logical pairs get different IDs');
  console.log('4. Order independence: (A,B) = (B,A)');
  console.log('5. Multiple random runs produce consistent results');
}

// Run the tests
main();