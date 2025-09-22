'use client';

import { useState, useEffect } from 'react';
import { Device } from '@/types';
import { 
  Smartphone, 
  Link, 
  MessageCircle, 
  Play, 
  Square, 
  RefreshCw, 
  CheckSquare, 
  Square as SquareIcon,
  Search,
  Users,
  Settings,
  Trash2,
  Plus,
  X,
  Copy
} from 'lucide-react';
import ConversationInputComponent from './ConversationInputComponent';
import { DevicePair, ConversationData } from '@/types/conversation';
import { toast } from 'sonner';
import { generatePairId } from '@/utils/pairUtils';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Summary {
  noidung: string;
  hoancanh: string;
  so_cau: number;
  createdAt: Date;
}



interface AutomationProgress {
  pairId: string;
  status: 'running' | 'completed' | 'error';
  progress: number;
  message: string;
}

interface NuoiZaloPanelProps {
  devices: Device[];
  onRefreshDevices: () => void;
  isLoading?: boolean;
}

export default function NuoiZaloPanel({ devices, onRefreshDevices, isLoading = false }: NuoiZaloPanelProps) {
  const [activeSection, setActiveSection] = useState<'devices' | 'pair' | 'conversations' | 'control'>('devices');
  const [selectedDevices, setSelectedDevices] = useState<Device[]>([]);
  const [devicePairs, setDevicePairs] = useState<DevicePair[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showOnlyWithPhone, setShowOnlyWithPhone] = useState(true);
  const [isAutomationRunning, setIsAutomationRunning] = useState(false);
  const [automationProgress, setAutomationProgress] = useState<AutomationProgress[]>([]);
  const [logs, setLogs] = useState<string[]>([]);

  // New conversation management states
  const [pairSummaries, setPairSummaries] = useState<Record<string, Summary[]>>({});
  
  // State for historical summaries from demo.json
  const [historicalSummaries, setHistoricalSummaries] = useState<Array<{
    noidung: string;
    hoancanh: string;
    so_cau: number;
  }>>([]);
  
  // State to manage history visibility for each pair
  const [pairHistoryVisibility, setPairHistoryVisibility] = useState<Record<string, boolean>>({});
  const [tempConversationData, setTempConversationData] = useState<ConversationData | null>(null);
  const [showConversationInput, setShowConversationInput] = useState(false);
  
  // State for pairing mode
  const [pairingMode, setPairingMode] = useState<'add' | 'replace'>('add');

  // Filter devices based on search query and phone filter
  const filteredDevices = devices.filter(device => {
    const query = searchQuery.toLowerCase();
    const matchesSearch = (
      device.ip.toLowerCase().includes(query) ||
      (device.phone || '').toLowerCase().includes(query) ||
      (device.note || '').toLowerCase().includes(query) ||
      (device.name || '').toLowerCase().includes(query) ||
      (device.device_id || '').toLowerCase().includes(query)
    );
    
    // Phone filter: only show devices with phone numbers if enabled
    const hasPhone = device.phone && device.phone.trim() !== '' && device.phone !== 'Chưa có số';
    const matchesPhoneFilter = !showOnlyWithPhone || hasPhone;
    
    // Debug logging
    if (showOnlyWithPhone) {
      console.log(`🔍 Filter Debug - Device: ${device.name || device.ip}`);
      console.log(`  Phone: "${device.phone}"`);
      console.log(`  HasPhone: ${hasPhone}`);
      console.log(`  MatchesPhoneFilter: ${matchesPhoneFilter}`);
    }
    
    return matchesSearch && matchesPhoneFilter;
  });
  
  // Debug logging for filter state
  console.log(`📊 Filter State - showOnlyWithPhone: ${showOnlyWithPhone}`);
  console.log(`📊 Total devices: ${devices.length}, Filtered devices: ${filteredDevices.length}`);

  // Handle device selection
  const handleDeviceToggle = (device: Device) => {
    setSelectedDevices(prev => {
      const isSelected = prev.some(d => d.id === device.id);
      if (isSelected) {
        return prev.filter(d => d.id !== device.id);
      } else {
        return [...prev, device];
      }
    });
  };

  // Select all devices
  const handleSelectAll = () => {
    setSelectedDevices(filteredDevices);
  };

  // Deselect all devices
  const handleSelectNone = () => {
    setSelectedDevices([]);
  };

  // Create device pairs
  const handleCreatePairs = async () => {
    // Enhanced validation with better user feedback
    if (selectedDevices.length === 0) {
      alert('⚠️ Chưa chọn thiết bị nào! Vui lòng chọn ít nhất 2 thiết bị từ tab "Thiết bị" trước khi ghép cặp.');
      addLog('❌ Không thể ghép cặp: Chưa chọn thiết bị nào');
      return;
    }
    if (selectedDevices.length < 2) {
      alert('⚠️ Cần chọn ít nhất 2 thiết bị để ghép cặp.');
      addLog(`❌ Không thể ghép cặp: Chỉ chọn ${selectedDevices.length} thiết bị`);
      return;
    }
    if (selectedDevices.length % 2 !== 0) {
      alert('⚠️ Số lượng thiết bị phải là số chẵn để ghép cặp.');
      addLog(`❌ Không thể ghép cặp: Số thiết bị lẻ (${selectedDevices.length})`);
      return;
    }
    
    addLog(`🔄 Bắt đầu ghép ${selectedDevices.length} thiết bị thành ${selectedDevices.length / 2} cặp...`);

    // Handle pairing based on selected mode
    if (pairingMode === 'replace') {
      setDevicePairs([]);
      addLog('🔄 Đang thay thế tất cả cặp hiện tại bằng cặp mới...');
    } else {
      addLog('🔄 Đang tạo cặp mới và thêm vào danh sách hiện tại...');
    }

    try {
      // Create pairs locally with standardized IDs first
      const localPairs: DevicePair[] = [];
      
      for (let i = 0; i < selectedDevices.length - 1; i += 2) {
        const device1 = selectedDevices[i];
        const device2 = selectedDevices[i + 1];
        
        // Create standardized pair ID
        const device1Id = device1.id || device1.ip;
        const device2Id = device2.id || device2.ip;
        console.log(`🔍 Creating pair ID for devices:`);
        console.log(`  Device 1: ${device1Id} (from device:`, device1, `)`);
        console.log(`  Device 2: ${device2Id} (from device:`, device2, `)`);
        
        const pairId = generatePairId(device1Id, device2Id);
        console.log(`  Generated pair ID: ${pairId}`);
        addLog(`🔍 Tạo pair ID: ${pairId} cho ${device1Id} ↔ ${device2Id}`);
        
        localPairs.push({
          id: pairId,
          deviceA: device1,
          deviceB: device2,
          createdAt: new Date()
        });
      }
      
      // Send to backend for persistence
      const response = await fetch('http://localhost:8001/api/devices/pair', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          devices: selectedDevices
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Use backend response but ensure we have standardized IDs
        console.log(`🔍 Backend response pairs:`, result.data.pairs);
        const backendPairs: DevicePair[] = result.data.pairs.map((pair: any) => {
          const device1Id = pair.device1.id || pair.device1.ip;
          const device2Id = pair.device2.id || pair.device2.ip;
          const standardizedId = generatePairId(device1Id, device2Id);
          console.log(`🔍 Backend pair mapping:`);
          console.log(`  Backend temp_pair_id: ${pair.temp_pair_id}`);
          console.log(`  Device1: ${device1Id}, Device2: ${device2Id}`);
          console.log(`  Standardized ID: ${standardizedId}`);
          addLog(`🔍 Backend pair: ${pair.temp_pair_id} → ${standardizedId}`);
          return {
            id: standardizedId,
            temp_pair_id: pair.temp_pair_id,
            deviceA: pair.device1,
            deviceB: pair.device2,
            createdAt: new Date()
          };
        });
        
        // Handle pairs based on pairing mode
        if (pairingMode === 'replace') {
          setDevicePairs(backendPairs);
          addLog(`🔄 Đã thay thế tất cả cặp cũ. Hiện có ${backendPairs.length} cặp mới.`);
        } else {
          // Add mode: merge new pairs with existing ones (no database reload)
          setDevicePairs(prev => [...prev, ...backendPairs]);
          addLog(`🔄 Đã thêm ${backendPairs.length} cặp mới. Tổng cộng: ${devicePairs.length + backendPairs.length} cặp.`);
        }
        
        let message = `✅ Đã tạo ${result.data.total_pairs} cặp thiết bị`;
        if (result.data.unpaired && result.data.unpaired.length > 0) {
          message += ` (${result.data.unpaired.length} thiết bị lẻ)`;
        }
        addLog(message);
        
        // Log the standardized pair IDs
        backendPairs.forEach(pair => {
          addLog(`📝 Cặp: ${pair.id} (${pair.deviceA.ip} ↔ ${pair.deviceB.ip})`);
        });
      } else {
        addLog(`❌ Lỗi ghép cặp: ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ Lỗi kết nối: ${error}`);
    }
  };

  // Clear all pairs
  const handleClearPairs = () => {
    setDevicePairs([]);
    addLog('🗑️ Đã xóa tất cả cặp thiết bị');
  };

  // Handle conversation applied from ConversationInputComponent
  const handleConversationApplied = async (pairId: string, data: ConversationData) => {
    setTempConversationData(data);
    
    addLog(`✅ Đã áp dụng conversation cho cặp ${pairId}`);
    addLog(`📝 Đã lưu summary: ${data.summary.noidung.substring(0, 50)}...`);
    
    // Reload summaries from database to get the latest data
    setTimeout(() => {
      loadPairSummaries();
    }, 1000); // Wait 1 second for backend to process
  };

  // Handle error from ConversationInputComponent
  const handleConversationError = (error: string) => {
    addLog(`❌ Lỗi: ${error}`);
  };



  // Add log entry
  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  // Load demo data and pair summaries on component mount
  useEffect(() => {
    console.log('🚀 NuoiZaloPanel component mounted!');
    loadHistoricalSummaries();
    // Do NOT auto-load pairs from database - start with empty list
  }, []);
  
  useEffect(() => {
    console.log('📊 Device pairs changed:', devicePairs.length, 'pairs');
    if (devicePairs.length > 0) {
      devicePairs.forEach(pair => {
        console.log('🔄 Will load summaries for pair:', pair.temp_pair_id || pair.id);
      });
      loadPairSummaries();
    }
  }, [devicePairs]);
  
  // Note: loadDevicePairsFromAPI function removed - tab starts with empty pairs list
  // Pairs are only shown when user manually creates them by selecting devices and clicking pair button
  
  // Function to load summaries for all device pairs from API
  const loadPairSummaries = async () => {
    if (devicePairs.length === 0) return;
    
    try {
      const summariesData: Record<string, Summary[]> = {};
      
      for (const pair of devicePairs) {
        try {
          // Use temp_pair_id instead of id for API call
          const pairId = pair.temp_pair_id || pair.id;
          console.log(`📡 Fetching summaries for pair ${pair.id} using temp_pair_id: ${pairId}`);
          const response = await fetch(`http://localhost:8001/api/summaries/latest/${pairId}`);
          if (response.ok) {
            const result = await response.json();
            if (result.success && result.summary) {
              const summaryWithDate: Summary = {
                ...result.summary,
                createdAt: new Date(result.summary.created_at || Date.now())
              };
              summariesData[pair.id] = [summaryWithDate];
            }
          } else {
            console.log(`❌ Failed to fetch summaries for pair ${pair.id} (temp_pair_id: ${pairId}): ${response.status}`);
          }
        } catch (error) {
          console.error(`Error loading summary for pair ${pair.id}:`, error);
        }
      }
      
      if (Object.keys(summariesData).length > 0) {
        setPairSummaries(summariesData);
        addLog(`✅ Đã tải summaries cho ${Object.keys(summariesData).length} cặp thiết bị`);
      }
    } catch (error) {
      console.error('Error loading pair summaries:', error);
      addLog(`⚠️ Lỗi khi tải summaries: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Function to load historical summaries from demo.json
  const loadHistoricalSummaries = async () => {
    try {
      const response = await fetch('/zaloauto/demo.json');
      
      // Check if response is ok
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Response is not JSON format');
      }
      
      const data = await response.json();
      
      if (data.conversations && Array.isArray(data.conversations)) {
        const summaries = data.conversations.map((conv: any) => conv.summary).filter(Boolean);
        setHistoricalSummaries(summaries);
        addLog(`✅ Đã tải ${summaries.length} lịch sử summaries từ demo.json`);
      } else {
        // Fallback: use empty array if no conversations found
        setHistoricalSummaries([]);
        addLog('⚠️ Không tìm thấy conversations trong demo.json');
      }
    } catch (error) {
      console.error('Lỗi khi tải historical summaries:', error);
      
      // Fallback: use demo data if API fails
      const fallbackSummaries = [
        {
          noidung: "Máy A than phiền chuyện nhóm không hợp tác, Máy B thì bận báo cáo. Cả hai đều mệt mỏi vì áp lực. Cuối cùng họ hẹn mai đi ăn cơm gà để xả stress.",
          hoancanh: "Hai người bạn nhắn tin buổi tối, vừa than việc học vừa hẹn gặp để đi ăn.",
          so_cau: 65
        },
        {
          noidung: "Máy A rủ Máy B đi xem bóng đá Việt Nam gặp Thái Lan. Không có vé nên hai người quyết định đi quán nhậu coi chung màn hình lớn.",
          hoancanh: "Cuộc trò chuyện sôi nổi trước một trận bóng quan trọng.",
          so_cau: 63
        }
      ];
      
      setHistoricalSummaries(fallbackSummaries);
      addLog(`⚠️ Lỗi khi tải demo.json, sử dụng dữ liệu mẫu: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Start automation
  const handleStartAutomation = async () => {
    if (devicePairs.length === 0) {
      alert('Cần có ít nhất 1 cặp thiết bị để bắt đầu automation.');
      return;
    }

    setIsAutomationRunning(true);
    addLog('🚀 Bắt đầu automation Nuôi Zalo...');
    
    // Initialize progress for each pair
    const initialProgress: AutomationProgress[] = devicePairs.map(pair => ({
      pairId: pair.id,
      status: 'running',
      progress: 0,
      message: 'Đang khởi tạo...'
    }));
    setAutomationProgress(initialProgress);

    try {
      // Extract devices from devicePairs for API compatibility
      const devices = devicePairs.flatMap(pair => [
        {
          id: pair.deviceA.id || pair.deviceA.ip,
          ip: pair.deviceA.ip,
          name: pair.deviceA.name || pair.deviceA.device_id,
          device_id: pair.deviceA.device_id || pair.deviceA.ip
        },
        {
          id: pair.deviceB.id || pair.deviceB.ip,
          ip: pair.deviceB.ip,
          name: pair.deviceB.name || pair.deviceB.device_id,
          device_id: pair.deviceB.device_id || pair.deviceB.ip
        }
      ]);
      
      // Remove duplicates based on device ID
      const uniqueDevices = devices.filter((device, index, self) => 
        index === self.findIndex(d => d.id === device.id)
      );
      
      addLog(`📤 Gửi ${uniqueDevices.length} thiết bị đến API automation`);
      
      const response = await fetch('http://localhost:8001/api/automation/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          devices: uniqueDevices,
          conversations: [] // Tạm thời gửi rỗng, sẽ implement sau
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        addLog(result.message);
        
        // Simulate automation progress
        for (let i = 0; i < devicePairs.length; i++) {
          const pair = devicePairs[i];
          addLog(`🔄 Bắt đầu xử lý cặp ${i + 1}: ${pair.deviceA.ip} ↔ ${pair.deviceB.ip}`);
          
          // Simulate progress updates
          for (let progress = 0; progress <= 100; progress += 20) {
            await new Promise(resolve => setTimeout(resolve, 500));
            
            setAutomationProgress(prev => prev.map(p => 
              p.pairId === pair.id 
                ? { ...p, progress, message: `Đang xử lý... ${progress}%` }
                : p
            ));
          }
          
          setAutomationProgress(prev => prev.map(p => 
            p.pairId === pair.id 
              ? { ...p, status: 'completed', message: 'Hoàn thành' }
              : p
          ));
          
          addLog(`✅ Hoàn thành cặp ${i + 1}`);
        }
        
        addLog('🎉 Automation hoàn thành!');
      } else {
        addLog(`❌ Lỗi: ${result.error}`);
        setAutomationProgress(prev => prev.map(p => ({ ...p, status: 'error', message: 'Lỗi' })));
      }
    } catch (error) {
      addLog(`❌ Lỗi kết nối: ${error}`);
      setAutomationProgress(prev => prev.map(p => ({ ...p, status: 'error', message: 'Lỗi kết nối' })));
    }

    setIsAutomationRunning(false);
  };

  // Stop automation
  const handleStopAutomation = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/automation/stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        setIsAutomationRunning(false);
        setAutomationProgress([]);
        addLog(`⏹️ ${result.message}`);
      } else {
        addLog(`❌ Lỗi dừng automation: ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ Lỗi kết nối: ${error}`);
      setIsAutomationRunning(false);
      setAutomationProgress([]);
    }
  };

  // Clear logs
  const handleClearLogs = () => {
    setLogs([]);
  };

  // Copy functions
  const copyToClipboard = async (text: string, successMessage: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success(successMessage);
    } catch (error) {
      console.error('Failed to copy:', error);
      toast.error('Không thể copy. Vui lòng thử lại.');
    }
  };

  const copyFullSummary = (summary: any) => {
    const fullText = `Nội dung: ${summary.noidung}\n\nHoàn cảnh: ${summary.hoancanh}\n\nSố câu: ${summary.so_cau}`;
    copyToClipboard(fullText, 'Đã copy toàn bộ summary!');
  };

  const copyField = (fieldValue: string, fieldName: string) => {
    copyToClipboard(fieldValue, `Đã copy ${fieldName}!`);
  };

  const sections = [
    { id: 'devices', label: 'Thiết bị', icon: Smartphone },
    { id: 'pair', label: 'Ghép cặp', icon: Link },
    { id: 'conversations', label: 'Hội thoại', icon: MessageCircle },
    { id: 'control', label: 'Điều khiển', icon: Settings }
  ];

  return (
    <div className="space-y-6">
      {/* Section Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
        <div className="flex overflow-x-auto">
          {sections.map((section) => {
            const Icon = section.icon;
            const isActive = activeSection === section.id;
            return (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id as any)}
                className={`flex items-center space-x-2 px-6 py-4 font-medium transition-all duration-200 whitespace-nowrap ${
                  isActive
                    ? 'bg-blue-500 text-white border-b-2 border-blue-400'
                    : 'text-gray-600 dark:text-gray-400 hover:text-blue-500 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span>{section.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
        {/* Devices Section */}
        {activeSection === 'devices' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Quản lý thiết bị</h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => {
                    handleCreatePairs();
                    setActiveSection('pair');
                  }}
                  disabled={selectedDevices.length < 2}
                  className="flex items-center space-x-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 transition-colors"
                >
                  <Link className="h-4 w-4" />
                  <span>Ghép cặp</span>
                </button>
                <button
                  onClick={onRefreshDevices}
                  disabled={isLoading}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors"
                >
                  <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                  <span>Refresh</span>
                </button>
              </div>
            </div>

            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Tìm theo tên máy, IP, số điện thoại hoặc ghi chú..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Phone Filter */}
            <div className="flex items-center space-x-2">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showOnlyWithPhone}
                  onChange={(e) => setShowOnlyWithPhone(e.target.checked)}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Chỉ hiển thị máy có số điện thoại
                </span>
              </label>
            </div>

            {/* Selection Controls */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleSelectAll}
                  className="flex items-center space-x-2 px-3 py-1 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors text-sm"
                >
                  <CheckSquare className="h-4 w-4" />
                  <span>Chọn tất cả</span>
                </button>
                <button
                  onClick={handleSelectNone}
                  className="flex items-center space-x-2 px-3 py-1 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors text-sm"
                >
                  <SquareIcon className="h-4 w-4" />
                  <span>Bỏ chọn</span>
                </button>

              </div>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Đã chọn {selectedDevices.length} / {filteredDevices.length} thiết bị
                {showOnlyWithPhone && (
                  <span className="ml-2 text-blue-600 dark:text-blue-400">
                    (chỉ hiển thị máy có số)
                  </span>
                )}
              </span>
            </div>

            {/* Device List */}
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {filteredDevices.map((device) => {
                const isSelected = selectedDevices.some(d => d.id === device.id);
                const note = device.note?.trim() || 'Không có';
                const phone = device.phone || 'Chưa có số';
                
                return (
                  <div
                    key={device.id}
                    onClick={() => handleDeviceToggle(device)}
                    className={`flex items-center space-x-3 p-3 rounded-lg border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-600'
                        : 'bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600'
                    }`}
                  >
                    <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                      isSelected
                        ? 'bg-blue-500 border-blue-500'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}>
                      {isSelected && <CheckSquare className="h-3 w-3 text-white" />}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium flex items-center space-x-2">
                        <span className="text-blue-700 dark:text-blue-300">
                          {device.name || device.device_id || 'Máy xxx'}
                        </span>
                        <span className="text-gray-600 dark:text-gray-400">-</span>
                        <span className="text-gray-600 dark:text-gray-400">
                          {device.ip}
                        </span>
                        <span className="text-gray-600 dark:text-gray-400">-</span>
                        <span className="text-purple-600 dark:text-purple-400">
                          {phone}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        Trạng thái: {device.status === 'connected' ? '✅ Kết nối' : '❌ Ngắt kết nối'}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {filteredDevices.length === 0 && (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                {searchQuery || showOnlyWithPhone ? (
                  <div>
                    <div>Không tìm thấy thiết bị nào phù hợp</div>
                    {showOnlyWithPhone && (
                      <div className="text-sm mt-1">Thử bỏ chọn "Chỉ hiển thị máy có số điện thoại"</div>
                    )}
                  </div>
                ) : (
                  'Không có thiết bị nào'
                )}
              </div>
            )}
          </div>
        )}

        {/* Pair Section */}
        {activeSection === 'pair' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Ghép cặp thiết bị</h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleCreatePairs}
                  disabled={selectedDevices.length < 2}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors"
                  title={pairingMode === 'add' ? 'Thêm cặp mới vào danh sách hiện tại' : 'Thay thế tất cả cặp hiện tại'}
                >
                  <Link className="h-4 w-4" />
                  <span>{pairingMode === 'add' ? 'Thêm cặp mới' : 'Thay thế cặp'}</span>
                </button>
                <button
                  onClick={handleClearPairs}
                  className="flex items-center space-x-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                  <span>Xóa cặp</span>
                </button>

              </div>
            </div>

            {/* Pairing Mode Selection */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Chế độ ghép cặp:</h4>
              <div className="flex space-x-4">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="pairingMode"
                    value="add"
                    checked={pairingMode === 'add'}
                    onChange={(e) => setPairingMode(e.target.value as 'add' | 'replace')}
                    className="text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    ➕ <strong>Thêm vào</strong> - Giữ cặp cũ, thêm cặp mới
                  </span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="pairingMode"
                    value="replace"
                    checked={pairingMode === 'replace'}
                    onChange={(e) => setPairingMode(e.target.value as 'add' | 'replace')}
                    className="text-red-600 focus:ring-red-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    🔄 <strong>Thay thế</strong> - Xóa tất cả cặp cũ, chỉ giữ cặp mới
                  </span>
                </label>
              </div>
            </div>

            <div className="text-sm text-gray-600 dark:text-gray-400">
              Đã chọn {selectedDevices.length} thiết bị. Cần số lượng chẵn để ghép cặp.
            </div>

            {/* Pair List */}
            <div className="space-y-2">
              {devicePairs.map((pair, index) => {
                // Check if this pair actually has historical summaries
                const pairActualSummaries = pairSummaries[pair.id] || [];
                const hasRealHistory = pairActualSummaries.length > 0;
                const pairHistoricalSummary = hasRealHistory ? pairActualSummaries[0] : null;
                const showHistory = pairHistoryVisibility[pair.id] || false;
                
                const toggleHistory = () => {
                  setPairHistoryVisibility(prev => ({
                    ...prev,
                    [pair.id]: !prev[pair.id]
                  }));
                };
                
                return (
                  <div key={pair.id} className="bg-gradient-to-r from-blue-50 to-green-50 dark:from-blue-900/20 dark:to-green-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 text-lg">
                        <span className="font-bold text-blue-600 dark:text-blue-400 text-xl">
                          🔗 Cặp {index + 1}
                        </span>
                        <span className="text-gray-500 dark:text-gray-400">-</span>
                        <span className="font-medium text-green-700 dark:text-green-300 text-lg">
                          {pair.deviceA.name || pair.deviceA.device_id || 'Máy A'}
                        </span>
                        <span className="text-cyan-600 dark:text-cyan-400">
                          ({pair.deviceA.phone || 'N/A'})
                        </span>
                        <span className="text-gray-500 dark:text-gray-400">-</span>
                        <span className="font-medium text-purple-700 dark:text-purple-300 text-lg">
                          {pair.deviceB.name || pair.deviceB.device_id || 'Máy B'}
                        </span>
                        <span className="text-cyan-600 dark:text-cyan-400">
                          ({pair.deviceB.phone || 'N/A'})
                        </span>
                        <span className="text-gray-500 dark:text-gray-400">(</span>
                        <span className="text-orange-600 dark:text-orange-400 font-mono">
                          {pair.deviceA.ip}
                        </span>
                        <span className="text-gray-500 dark:text-gray-400">-</span>
                        <span className="text-orange-600 dark:text-orange-400 font-mono">
                          {pair.deviceB.ip}
                        </span>
                        <span className="text-gray-500 dark:text-gray-400">)</span>
                      </div>
                      
                      {/* History Toggle Button or No History Message */}
                      {hasRealHistory ? (
                        <button
                          onClick={toggleHistory}
                          className="flex items-center space-x-1 px-3 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-md hover:bg-indigo-200 dark:hover:bg-indigo-900/50 transition-colors text-sm"
                        >
                          <span>📚 Có lịch sử</span>
                          <span className={`transform transition-transform ${showHistory ? 'rotate-180' : ''}`}>
                            ▼
                          </span>
                        </button>
                      ) : (
                        <span className="text-xs text-gray-500 dark:text-gray-400 italic">
                          📝 Chưa có lịch sử
                        </span>
                      )}
                    </div>
                    
                    {/* Historical Summary Display */}
                    {showHistory && hasRealHistory && pairHistoricalSummary && (
                      <div className="mt-3 p-3 bg-white dark:bg-gray-800 rounded-md border border-indigo-200 dark:border-indigo-700">
                        <div className="flex items-center justify-between mb-2">
                          <h5 className="text-sm font-medium text-indigo-800 dark:text-indigo-200">📖 Lịch sử Summary:</h5>
                          <button
                            onClick={() => copyFullSummary(pairHistoricalSummary)}
                            className="flex items-center space-x-1 px-2 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded hover:bg-indigo-200 dark:hover:bg-indigo-900/50 transition-colors text-xs"
                            title="Copy toàn bộ summary"
                          >
                            <Copy className="h-3 w-3" />
                            <span>Copy All</span>
                          </button>
                        </div>
                        <div className="space-y-2 text-sm">
                          <div className="flex items-start justify-between group">
                            <div className="flex-1">
                              <span className="font-medium text-gray-700 dark:text-gray-300">Nội dung:</span>
                              <span className="ml-2 text-gray-600 dark:text-gray-400">{pairHistoricalSummary.noidung}</span>
                            </div>
                            <button
                              onClick={() => copyField(pairHistoricalSummary.noidung, 'nội dung')}
                              className="ml-2 p-1 text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 opacity-0 group-hover:opacity-100 transition-all"
                              title="Copy nội dung"
                            >
                              <Copy className="h-3 w-3" />
                            </button>
                          </div>
                          <div className="flex items-start justify-between group">
                            <div className="flex-1">
                              <span className="font-medium text-gray-700 dark:text-gray-300">Hoàn cảnh:</span>
                              <span className="ml-2 text-gray-600 dark:text-gray-400">{pairHistoricalSummary.hoancanh}</span>
                            </div>
                            <button
                              onClick={() => copyField(pairHistoricalSummary.hoancanh, 'hoàn cảnh')}
                              className="ml-2 p-1 text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 opacity-0 group-hover:opacity-100 transition-all"
                              title="Copy hoàn cảnh"
                            >
                              <Copy className="h-3 w-3" />
                            </button>
                          </div>
                          <div className="flex items-center justify-between group">
                            <div>
                              <span className="font-medium text-gray-700 dark:text-gray-300">Số câu:</span>
                              <span className="ml-2 text-indigo-600 dark:text-indigo-400 font-mono">{pairHistoricalSummary.so_cau}</span>
                            </div>
                            <button
                              onClick={() => copyField(pairHistoricalSummary.so_cau.toString(), 'số câu')}
                              className="ml-2 p-1 text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 opacity-0 group-hover:opacity-100 transition-all"
                              title="Copy số câu"
                            >
                              <Copy className="h-3 w-3" />
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {devicePairs.length === 0 && (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                Chưa có cặp thiết bị nào. Chọn thiết bị ở tab Thiết bị và nhấn Ghép cặp.
              </div>
            )}
          </div>
        )}

        {/* Conversations Section */}
        {activeSection === 'conversations' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Quản lý Conversation</h3>
            </div>

            {/* Conversation JSON Input Section */}
            <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">Nhập Conversation JSON</h4>
              
              <ConversationInputComponent
                devicePairs={devicePairs}
                onConversationApplied={handleConversationApplied}
                onError={handleConversationError}
                onLog={addLog}
              />
            </div>

            {/* Summaries Display */}
            {Object.keys(pairSummaries).length > 0 && (
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
                <h4 className="text-md font-medium text-gray-900 dark:text-white mb-3">
                  Summaries đã lưu:
                </h4>
                <div className="space-y-4">
                  {Object.entries(pairSummaries).map(([pairId, summaries]) => {
                    const pair = devicePairs.find(p => p.id === pairId);
                    if (!pair) return null;
                    return (
                      <div key={pairId} className="bg-white dark:bg-gray-700 rounded-md p-3 border border-gray-200 dark:border-gray-600">
                        <div className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                          Cặp: {pair.deviceA.ip} ↔ {pair.deviceB.ip}
                        </div>
                        <div className="space-y-1">
                          {summaries.map((summary, index) => (
                            <div key={index} className="text-xs text-gray-600 dark:text-gray-400">
                              {index + 1}. {summary.noidung} ({summary.so_cau} câu) - {summary.createdAt.toLocaleString()}
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Current Conversation Data Display */}
            {tempConversationData && (
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg p-4">
                <h4 className="text-md font-medium text-gray-900 dark:text-white mb-3">Dữ liệu Conversation hiện tại:</h4>
                <div className="text-sm text-gray-700 dark:text-gray-300">
                  <div><strong>Số tin nhắn:</strong> {tempConversationData.conversation.length}</div>
                  <div><strong>Summary:</strong> {tempConversationData.summary.noidung}</div>
                  <div><strong>Hoàn cảnh:</strong> {tempConversationData.summary.hoancanh}</div>
                  <div><strong>Số câu:</strong> {tempConversationData.summary.so_cau}</div>
                </div>
              </div>
            )}


          </div>
        )}

        {/* Control Section */}
        {activeSection === 'control' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Điều khiển Automation</h3>
              <div className="flex items-center space-x-2">
                {!isAutomationRunning ? (
                  <button
                    onClick={handleStartAutomation}
                    disabled={devicePairs.length === 0}
                    className="flex items-center space-x-2 px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 transition-colors font-medium"
                  >
                    <Play className="h-5 w-5" />
                    <span>Bắt đầu Automation</span>
                  </button>
                ) : (
                  <button
                    onClick={handleStopAutomation}
                    className="flex items-center space-x-2 px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium"
                  >
                    <Square className="h-5 w-5" />
                    <span>Dừng Automation</span>
                  </button>
                )}
              </div>
            </div>

            {/* Status Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                <div className="text-blue-700 dark:text-blue-300 font-medium">Cặp thiết bị</div>
                <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">{devicePairs.length}</div>
              </div>
              <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                <div className="text-purple-700 dark:text-purple-300 font-medium">Trạng thái</div>
                <div className="text-lg font-bold text-purple-900 dark:text-purple-100">
                  {isAutomationRunning ? '🟢 Đang chạy' : '🔴 Dừng'}
                </div>
              </div>
            </div>

            {/* Progress */}
            {automationProgress.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white">Tiến độ xử lý:</h4>
                {automationProgress.map((progress) => {
                  const pair = devicePairs.find(p => p.id === progress.pairId);
                  if (!pair) return null;
                  
                  return (
                    <div key={progress.pairId} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {pair.deviceA.ip} ↔ {pair.deviceB.ip}
                        </span>
                        <span className={`text-sm font-medium ${
                          progress.status === 'completed' ? 'text-green-600 dark:text-green-400' :
                          progress.status === 'error' ? 'text-red-600 dark:text-red-400' :
                          'text-blue-600 dark:text-blue-400'
                        }`}>
                          {progress.message}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-300 ${
                            progress.status === 'completed' ? 'bg-green-500' :
                            progress.status === 'error' ? 'bg-red-500' :
                            'bg-blue-500'
                          }`}
                          style={{ width: `${progress.progress}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Logs */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-gray-900 dark:text-white">Logs hoạt động:</h4>
                <button
                  onClick={handleClearLogs}
                  className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  Xóa logs
                </button>
              </div>
              <div className="bg-gray-900 text-green-400 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
                {logs.length === 0 ? (
                  <div className="text-gray-500">Chưa có logs nào...</div>
                ) : (
                  logs.map((log, index) => (
                    <div key={index} className="mb-1">
                      {log}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}