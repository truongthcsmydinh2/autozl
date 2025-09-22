import React, { memo } from 'react'
import { Device } from '../lib/supabase'
import { Smartphone, Wifi, WifiOff, AlertCircle, Play, Square } from 'lucide-react'

interface DeviceCardProps {
  device: Device
  onConnect?: (id: string) => void
  onDisconnect?: (id: string) => void
  onStartAutomation?: (id: string) => void
  onStopAutomation?: (id: string) => void
  onViewScreen?: (id: string) => void
}

const DeviceCard = memo(({ 
  device, 
  onConnect, 
  onDisconnect, 
  onStartAutomation, 
  onStopAutomation, 
  onViewScreen 
}: DeviceCardProps) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
      case 'running':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
      case 'offline':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'idle':
        return 'Sẵn sàng'
      case 'running':
        return 'Đang chạy'
      case 'offline':
        return 'Offline'
      case 'error':
        return 'Lỗi'
      default:
        return 'Không xác định'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'idle':
        return <Wifi className="h-4 w-4 text-green-600" />
      case 'running':
        return <Play className="h-4 w-4 text-blue-600" />
      case 'offline':
        return <WifiOff className="h-4 w-4 text-gray-600" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-600" />
      default:
        return <AlertCircle className="h-4 w-4 text-gray-600" />
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700 p-6 hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02]">
      {/* Device Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
            <Smartphone className="h-5 w-5 text-white" />
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white truncate">
              {device.name || device.device_id || 'Không có tên'}
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
              {device.device_id || 'N/A'}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-1">
          {getStatusIcon(device.status)}
        </div>
      </div>

      {/* Device Info */}
      <div className="space-y-2 mb-4">
        <div className="flex justify-between items-center">
          <span className="text-xs text-gray-500 dark:text-gray-400">IP Address:</span>
          <span className="text-xs font-medium text-gray-900 dark:text-white truncate ml-2">
            {device.ip_address || 'N/A'}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-xs text-gray-500 dark:text-gray-400">Số điện thoại:</span>
          <span className="text-xs font-medium text-gray-900 dark:text-white truncate ml-2">
            {device.phone_number || 'N/A'}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-xs text-gray-500 dark:text-gray-400">Trạng thái:</span>
          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(device.status)}`}>
            {getStatusText(device.status)}
          </span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col space-y-2">
        <div className="flex space-x-2">
          {device.status === 'offline' ? (
            <button
              onClick={() => onConnect?.(device.id)}
              className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-transparent text-xs font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200"
            >
              Kết nối
            </button>
          ) : (
            <button
              onClick={() => onDisconnect?.(device.id)}
              className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-transparent text-xs font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200"
            >
              Ngắt kết nối
            </button>
          )}
          
          {device.status === 'idle' && (
            <button
              onClick={() => onStartAutomation?.(device.id)}
              className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
            >
              <Play className="h-3 w-3 mr-1" />
              Bắt đầu
            </button>
          )}
          
          {device.status === 'running' && (
            <button
              onClick={() => onStopAutomation?.(device.id)}
              className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-transparent text-xs font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition-colors duration-200"
            >
              <Square className="h-3 w-3 mr-1" />
              Dừng
            </button>
          )}
        </div>
        
        {onViewScreen && (
          <button
            onClick={() => onViewScreen(device.id)}
            className="w-full inline-flex items-center justify-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-xs font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
          >
            Xem màn hình
          </button>
        )}
      </div>
    </div>
  )
})

DeviceCard.displayName = 'DeviceCard'

export default DeviceCard