'use client';

import React, { useState, memo, useMemo } from 'react';
import { Device } from '../lib/supabase';
import { useDevices } from '../hooks/useDevices';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { TableSkeletonLoader } from './SkeletonLoader';
import DeviceCard from './DeviceCard';
import EditableDeviceName from './EditableDeviceName';
import EditablePhoneNumber from './EditablePhoneNumber';
import { RefreshCw, Smartphone, Wifi, WifiOff, AlertCircle, Play, Square, Search, Plus } from 'lucide-react';

interface DeviceGridProps {
  onAddDevice?: () => void;
  onConnect?: (deviceId: string) => void;
  onDisconnect?: (deviceId: string) => void;
  onStartAutomation?: (deviceId: string) => void;
  onStopAutomation?: (deviceId: string) => void;
  onViewScreen?: (deviceId: string) => void;
}

// Helper functions for status styling
const getStatusColor = (status: string) => {
  switch (status) {
    case 'idle':
      return 'bg-green-500';
    case 'running':
      return 'bg-blue-500';
    case 'connected':
      return 'bg-green-500';
    case 'disconnected':
      return 'bg-gray-400';
    case 'offline':
      return 'bg-gray-400';
    case 'error':
      return 'bg-red-500';
    default:
      return 'bg-gray-400';
  }
};

const getStatusBadgeColor = (status: string) => {
  switch (status) {
    case 'idle':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    case 'running':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
    case 'connected':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    case 'disconnected':
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    case 'offline':
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    case 'error':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case 'idle':
      return 'Sẵn sàng';
    case 'running':
      return 'Đang chạy';
    case 'connected':
      return 'Đã kết nối';
    case 'disconnected':
      return 'Ngắt kết nối';
    case 'offline':
      return 'Offline';
    case 'error':
      return 'Lỗi';
    default:
      return 'Không xác định';
  }
};

const DeviceGrid = memo(({
  onAddDevice,
  onConnect,
  onDisconnect,
  onStartAutomation,
  onStopAutomation,
  onViewScreen
}: DeviceGridProps) => {
  const { devices, loading: isLoading, error, isRefreshing, refetch: onRefresh, syncDevices, updateDevice, updateDevicePhone } = useDevices()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | 'connected' | 'disconnected' | 'error'>('all')
  const [isSyncing, setIsSyncing] = useState(false)

  const handleSync = async () => {
    try {
      setIsSyncing(true)
      await syncDevices()
    } catch (error) {
      console.error('Sync failed:', error)
    } finally {
      setIsSyncing(false)
    }
  }

  const handleSaveDeviceName = async (deviceId: string, newName: string) => {
    try {
      await updateDevice(deviceId, { name: newName })
    } catch (error) {
      console.error('Failed to update device name:', error)
      throw error
    }
  }

  const handleSavePhoneNumber = async (deviceId: string, newPhone: string) => {
    try {
      await updateDevicePhone(deviceId, newPhone)
    } catch (error) {
      console.error('Failed to update device phone:', error)
      throw error
    }
  }

  // Filter devices based on search term and status (memoized for performance)
  const filteredDevices = useMemo(() => {
    return devices.filter(device => {
      const matchesSearch = (device.name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
                           (device.device_id?.includes(searchTerm) || false) ||
                           (device.phone_number?.includes(searchTerm) || false);
      
      // Map Supabase status to legacy status for filtering
      const legacyStatus = (device.status === 'idle' || device.status === 'running' || device.status === 'connected') ? 'connected' : 
                          (device.status === 'offline' || device.status === 'disconnected') ? 'disconnected' : 
                          device.status === 'error' ? 'error' : 'disconnected';
      
      const matchesStatus = statusFilter === 'all' || legacyStatus === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [devices, searchTerm, statusFilter]);

  const connectedCount = devices.filter(d => d.status === 'idle' || d.status === 'running' || d.status === 'connected').length;
  const activeCount = devices.filter(d => d.status === 'running').length;

  return (
    <div className="space-y-6">
      {/* Silent refresh indicator */}
      {isRefreshing && !isLoading && (
        <div className="flex items-center justify-center text-sm text-blue-600 dark:text-blue-400 py-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 dark:border-blue-400 mr-2"></div>
          Đang cập nhật...
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-col lg:flex-row gap-4 lg:gap-6 p-6 lg:p-8 bg-gradient-to-r from-white to-gray-50/50 dark:from-gray-800 dark:to-gray-900/50 rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 mb-8 backdrop-blur-sm animate-fade-in">
        <div className="flex-1 animate-slide-in">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-5 h-5 transition-colors duration-300" />
            <input
              type="text"
              placeholder="Tìm kiếm thiết bị theo tên, IP hoặc model..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-4 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white/80 dark:bg-gray-700/80 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-300 shadow-sm hover:shadow-md backdrop-blur-sm font-medium"
            />
          </div>
        </div>
        
        <div className="flex gap-3 animate-fade-in">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as any)}
            className="px-4 py-4 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white/80 dark:bg-gray-700/80 text-gray-900 dark:text-white min-w-[180px] transition-all duration-300 shadow-sm hover:shadow-md backdrop-blur-sm font-medium cursor-pointer"
          >
            <option value="connected">🟢 Đã kết nối</option>
            <option value="all">🔍 Tất cả trạng thái</option>
            <option value="disconnected">🔴 Offline</option>
            <option value="error">⚠️ Lỗi</option>
          </select>
        </div>
      </div>

      {/* Device Table */}
        <div className={`transition-opacity duration-300 ${isRefreshing ? 'opacity-75' : 'opacity-100'}`}>
          {isLoading ? (
            <TableSkeletonLoader />
          ) : filteredDevices.length === 0 ? (
            <div className="text-center py-16 px-4">
              <div className="max-w-md mx-auto">
                <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center">
                  <Search className="h-10 w-10 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {devices.length === 0 ? 'Chưa có thiết bị nào' : 'Không tìm thấy thiết bị'}
                </h3>
                <p className="text-gray-500 mb-8 leading-relaxed">
                  {devices.length === 0 
                    ? 'Thêm thiết bị đầu tiên để bắt đầu quản lý automation của bạn'
                    : 'Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm để tìm thiết bị'
                  }
                </p>
                {devices.length === 0 && onAddDevice && (
                  <Button
                    onClick={onAddDevice}
                    className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-md hover:shadow-lg transform hover:scale-[1.02] font-semibold"
                  >
                    <Plus className="h-5 w-5 mr-2" />
                    Thêm thiết bị đầu tiên
                  </Button>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-2xl border border-gray-200/50 dark:border-gray-700/50 shadow-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50/80 dark:bg-gray-700/80">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                        Thiết bị
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                        IP Address
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                        Số điện thoại
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                        Trạng thái
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                        Lần cuối
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                        Thao tác
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                     {filteredDevices.map((device) => (
                       <tr key={device.id} className="hover:bg-gray-50/50 dark:hover:bg-gray-700/50 transition-colors duration-200">
                         <td className="px-6 py-4 whitespace-nowrap">
                           <div className="flex items-center space-x-3">
                             <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg shadow-md">
                               <Smartphone className="h-5 w-5 text-white" />
                             </div>
                             <div className="flex-1">
                               <EditableDeviceName
                                 deviceId={device.device_id}
                                 currentName={device.name || device.device_id || 'Thiết bị'}
                                 onSave={handleSaveDeviceName}
                               />
                             </div>
                           </div>
                         </td>
                         <td className="px-6 py-4 whitespace-nowrap">
                           <div className="text-sm font-mono text-gray-900 dark:text-white">
                             {device.ip_address}
                           </div>
                         </td>
                         <td className="px-6 py-4 whitespace-nowrap">
                           <EditablePhoneNumber
                             deviceId={device.device_id}
                             currentPhone={device.phone_number || ''}
                             onSave={handleSavePhoneNumber}
                           />
                         </td>
                         <td className="px-6 py-4 whitespace-nowrap">
                           <div className="flex items-center space-x-2">
                             <div className={`w-2 h-2 rounded-full ${getStatusColor(device.status)}`}></div>
                             <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusBadgeColor(device.status)}`}>
                               {getStatusText(device.status)}
                             </span>
                           </div>
                         </td>
                         <td className="px-6 py-4 whitespace-nowrap">
                           <div className="text-sm text-gray-900 dark:text-white">
                             {device.last_seen ? new Date(device.last_seen).toLocaleString('vi-VN') : '-'}
                           </div>
                         </td>
                         <td className="px-6 py-4 whitespace-nowrap">
                           <div className="flex space-x-2">
                             {(device.status === 'offline' || device.status === 'disconnected') ? (
                               <button
                                 onClick={() => onConnect?.(device.id)}
                                 className="px-3 py-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white text-xs font-semibold rounded-md transition-all duration-300"
                               >
                                 Kết nối
                               </button>
                             ) : (
                               <button
                                 onClick={() => onDisconnect?.(device.id)}
                                 className="px-3 py-1 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white text-xs font-semibold rounded-md transition-all duration-300"
                               >
                                 Ngắt
                               </button>
                             )}
                             {(device.status === 'idle' || device.status === 'connected') && (
                               <button
                                 onClick={() => onStartAutomation?.(device.id)}
                                 className="px-3 py-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white text-xs font-semibold rounded-md transition-all duration-300"
                               >
                                 Bắt đầu
                               </button>
                             )}
                             {device.status === 'running' && (
                               <button
                                 onClick={() => onStopAutomation?.(device.id)}
                                 className="px-3 py-1 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white text-xs font-semibold rounded-md transition-all duration-300"
                               >
                                 Dừng
                               </button>
                             )}
                           </div>
                         </td>
                       </tr>
                     ))}
                   </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

    </div>
  );
});

export default DeviceGrid;