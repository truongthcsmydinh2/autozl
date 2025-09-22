import { generatePairId } from './src/utils/pairUtils.ts';

console.log('Test 1:', generatePairId('192.168.5.81:5555', '192.168.5.85:5555'));
console.log('Test 2:', generatePairId('192.168.5.81', '192.168.5.85'));
console.log('Test 3:', generatePairId('device_81', 'device_85'));