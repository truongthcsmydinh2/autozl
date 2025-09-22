'use client';

import { useState, useEffect } from 'react';
import { Device, AutomationFlow, LogEntry } from '@/types';
import DeviceGrid from '@/components/DeviceGrid';
import NuoiZaloPanel from '@/components/NuoiZaloPanel';
import LogsViewer from '@/components/LogsViewer';
import ScreenStreaming from '@/components/ScreenStreaming';
import { useDevices } from '@/hooks/useDevices';
import { useLogs } from '@/hooks/useLogs';
import { Monitor, Zap, ScrollText, Smartphone } from 'lucide-react';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'devices' | 'nuoi-zalo' | 'logs' | 'streaming'>('devices');
  const [automationFlows, setAutomationFlows] = useState<AutomationFlow[]>([]);
  const [runningFlows, setRunningFlows] = useState<string[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  // Use Supabase hooks
  const { devices, loading: devicesLoading, error: devicesError, updateDevice, syncDevices } = useDevices();
  const { logs, loading: logsLoading, error: logsError } = useLogs(100);

  // Mock automation flows (will be replaced with Supabase later)
  useEffect(() => {
    setAutomationFlows([
      {
        id: 'flow-001',
        name: 'Login Test Flow',
        description: 'Automated login testing for mobile app',
        steps: [
          { action: 'tap', target: 'login_button', params: {} },
          { action: 'input', target: 'username_field', params: { text: 'testuser' } },
          { action: 'input', target: 'password_field', params: { text: 'password123' } },
          { action: 'tap', target: 'submit_button', params: {} }
        ],
        isActive: true,
        createdAt: new Date(Date.now() - 86400000),
        updatedAt: new Date(Date.now() - 3600000)
      },
      {
        id: 'flow-002',
        name: 'UI Navigation Test',
        description: 'Test navigation through main app screens',
        steps: [
          { action: 'tap', target: 'menu_button', params: {} },
          { action: 'swipe', target: 'screen', params: { direction: 'left' } },
          { action: 'tap', target: 'settings_option', params: {} }
        ],
        isActive: false,
        createdAt: new Date(Date.now() - 172800000),
        updatedAt: new Date(Date.now() - 7200000)
      }
    ]);

    // Set first device as selected when devices are loaded
    if (devices.length > 0 && !selectedDevice) {
      setSelectedDevice(devices[0].id);
    }
  }, [devices, selectedDevice]);

  const tabs = [
    { id: 'devices', label: 'Thiết bị', icon: Smartphone },
    { id: 'nuoi-zalo', label: 'Nuôi Zalo', icon: Zap },
    { id: 'logs', label: 'Logs', icon: ScrollText },
    { id: 'streaming', label: 'Screen Streaming', icon: Monitor }
  ];

  const handleDeviceAction = (deviceId: string, action: string, _data?: unknown) => {
    console.log(`Device ${deviceId}: ${action}`);
    // Implement device actions
  };

  const handleSyncDevices = async () => {
    try {
      setIsSyncing(true);
      const result = await syncDevices();
      console.log('Devices synced successfully:', result);
      // Show success message or notification here
    } catch (error) {
      console.error('Failed to sync devices:', error);
      // Show error message or notification here
    } finally {
      setIsSyncing(false);
    }
  };

  const handleFlowAction = (flowId: string, action: string) => {
    console.log(`Flow ${flowId}: ${action}`);
    if (action === 'start') {
      setRunningFlows(prev => [...prev, flowId]);
    } else if (action === 'stop') {
      setRunningFlows(prev => prev.filter(id => id !== flowId));
    }
  };

  const selectedDeviceData = devices.find(d => d.id === selectedDevice);

  return (
    <div className="min-h-screen">
      {/* Header with Navigation Tabs */}
      <header className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg shadow-lg border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50 animate-fade-in">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4 animate-slide-in">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-lg">
                <Monitor className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-200 bg-clip-text text-transparent">
                  Mobile Automation Dashboard
                </h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              {/* Navigation Tabs */}
              <nav className="flex space-x-2">
                {tabs.map((tab, index) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center space-x-2 py-2 px-4 rounded-lg font-semibold text-sm transition-all duration-300 whitespace-nowrap ${
                        isActive
                          ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg'
                          : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100/80 dark:hover:bg-gray-700/50'
                      }`}
                    >
                      <Icon className={`h-4 w-4 transition-transform duration-200 ${
                        isActive ? 'scale-110' : 'group-hover:scale-105'
                      }`} />
                      <span className="font-medium">{tab.label}</span>
                    </button>
                  );
                })}
              </nav>
              
              <div className="flex items-center gap-3 px-3 py-1 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border border-green-200/50 dark:border-green-700/50">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-lg"></div>
                <span className="text-xs font-semibold text-green-700 dark:text-green-300">
                  {devices.filter(d => d.status === 'connected').length}/{devices.length}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 min-h-screen">
        <div className="animate-fade-in">
          {activeTab === 'devices' && (
            <DeviceGrid
              devices={devices}
              isLoading={devicesLoading}
              isSyncing={isSyncing}
              error={devicesError}
              onRefresh={() => window.location.reload()}
              onConnect={(id) => handleDeviceAction(id, 'connect')}
              onDisconnect={(id) => handleDeviceAction(id, 'disconnect')}
              onStartAutomation={(id) => handleDeviceAction(id, 'run_automation')}
              onStopAutomation={(id) => handleDeviceAction(id, 'stop_automation')}
              onSyncDevices={handleSyncDevices}
              onAddDevice={() => console.log('Add device')}
            />
          )}

          {activeTab === 'nuoi-zalo' && (
            <div>
              <div className="mb-4 p-2 bg-blue-100 rounded">
                <p>🔍 Debug: NuoiZaloPanel is mounting...</p>
              </div>
              <NuoiZaloPanel
                devices={devices}
                onRefreshDevices={() => window.location.reload()}
                isLoading={isLoading}
              />
            </div>
          )}

          {activeTab === 'logs' && (
            <LogsViewer
              logs={logs}
              isLoading={logsLoading}
              error={logsError}
              isConnected={true}
              isPaused={false}
              onPause={() => console.log('Pause logs')}
              onResume={() => console.log('Resume logs')}
              onClear={() => console.log('Clear logs')}
              onExport={() => console.log('Export logs')}
              onRefresh={() => window.location.reload()}
            />
          )}

          {activeTab === 'streaming' && (
            <div className="space-y-6">
              {/* Device Selector */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 border border-gray-200 dark:border-gray-700">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Chọn thiết bị để xem màn hình:
                </label>
                <select
                  value={selectedDevice}
                  onChange={(e) => setSelectedDevice(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {devices.map((device) => (
                    <option key={device.id} value={device.id}>
                      {device.name} ({device.ip}:{device.port}) - {device.status}
                    </option>
                  ))}
                </select>
              </div>

              {/* Screen Streaming */}
              {selectedDeviceData && (
                <ScreenStreaming
                  deviceId={selectedDeviceData.id}
                  deviceName={selectedDeviceData.name}
                  isConnected={selectedDeviceData.status === 'connected'}
                  isStreaming={false}
                  onStartStream={() => console.log('Start streaming', selectedDevice)}
                  onStopStream={() => console.log('Stop streaming', selectedDevice)}
                  onRotateScreen={() => console.log('Rotate screen', selectedDevice)}
                  onTakeScreenshot={() => console.log('Take screenshot', selectedDevice)}
                  onOpenSettings={() => console.log('Open settings', selectedDevice)}
                />
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
