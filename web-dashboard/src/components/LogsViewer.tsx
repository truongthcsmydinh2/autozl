'use client';

import { useState, useEffect, useRef } from 'react';
import { LogEntry } from '@/types';
import { formatDate, getLogLevelColor, getLogLevelBadge } from '@/utils';
import { Search, Download, Trash2, Pause, Play, ScrollText, RefreshCw, AlertCircle } from 'lucide-react';

interface LogsViewerProps {
  logs: LogEntry[];
  isLoading?: boolean;
  error?: string | null;
  isConnected?: boolean;
  isPaused?: boolean;
  onPause?: () => void;
  onResume?: () => void;
  onClear?: () => void;
  onExport?: () => void;
  onRefresh?: () => void;
  maxLogs?: number;
}

export default function LogsViewer({
  logs,
  isLoading = false,
  error = null,
  isConnected = false,
  isPaused = false,
  onPause,
  onResume,
  onClear,
  onExport,
  onRefresh,
  maxLogs = 1000
}: LogsViewerProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [levelFilter, setLevelFilter] = useState<'all' | 'error' | 'warn' | 'info' | 'debug'>('all');
  const [deviceFilter, setDeviceFilter] = useState<string>('all');
  const [autoScroll, setAutoScroll] = useState(true);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const logsContainerRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  // Check if user scrolled up to disable auto-scroll
  const handleScroll = () => {
    if (logsContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = logsContainerRef.current;
      const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
      setAutoScroll(isAtBottom);
    }
  };

  const filteredLogs = logs.filter(log => {
    const matchesSearch = (log.message || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (log.device_id || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (log.deviceId || '').toLowerCase().includes(searchTerm.toLowerCase());
    
    // Map Supabase log_level to legacy level for filtering
    const legacyLevel = log.log_level ? log.log_level.toLowerCase() : (log.level || '').toLowerCase();
    const matchesLevel = levelFilter === 'all' || legacyLevel === levelFilter;
    
    const deviceId = log.device_id || log.deviceId;
    const matchesDevice = deviceFilter === 'all' || deviceId === deviceFilter;
    
    return matchesSearch && matchesLevel && matchesDevice;
  });

  const uniqueDevices = Array.from(new Set(logs.map(log => log.device_id || log.deviceId).filter(Boolean)));
  const logCounts = {
    total: logs.length,
    error: logs.filter(l => (l.log_level || l.level || '').toLowerCase() === 'error').length,
    warn: logs.filter(l => {
      const level = (l.log_level || l.level || '').toLowerCase();
      return level === 'warn' || level === 'warning';
    }).length,
    info: logs.filter(l => (l.log_level || l.level || '').toLowerCase() === 'info').length,
    debug: logs.filter(l => (l.log_level || l.level || '').toLowerCase() === 'debug').length
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center space-x-2">
            <ScrollText className="h-5 w-5" />
            <span>Real-time Logs</span>
          </h3>
          
          <div className="flex items-center space-x-2">
            <div className={`h-2 w-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {isConnected ? 'Kết nối' : 'Mất kết nối'}
            </span>
          </div>
        </div>
        
        <div className="flex space-x-2">
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="px-3 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50 flex items-center space-x-2 transition-colors"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Làm mới</span>
            </button>
          )}
          
          <button
            onClick={isPaused ? onResume : onPause}
            className={`px-3 py-2 rounded-md text-white flex items-center space-x-2 transition-colors ${
              isPaused 
                ? 'bg-green-600 hover:bg-green-700' 
                : 'bg-yellow-600 hover:bg-yellow-700'
            }`}
          >
            {isPaused ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
            <span>{isPaused ? 'Tiếp tục' : 'Tạm dừng'}</span>
          </button>
          
          <button
            onClick={onExport}
            className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2 transition-colors"
          >
            <Download className="h-4 w-4" />
            <span>Xuất</span>
          </button>
          
          <button
            onClick={onClear}
            className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 flex items-center space-x-2 transition-colors"
          >
            <Trash2 className="h-4 w-4" />
            <span>Xóa</span>
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="flex flex-wrap gap-4 p-4 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
        <div className="text-sm">
          <span className="text-gray-600 dark:text-gray-400">Tổng: </span>
          <span className="font-medium text-gray-900 dark:text-white">{logCounts.total}</span>
        </div>
        <div className="text-sm">
          <span className="text-gray-600 dark:text-gray-400">Lỗi: </span>
          <span className="font-medium text-red-600">{logCounts.error}</span>
        </div>
        <div className="text-sm">
          <span className="text-gray-600 dark:text-gray-400">Cảnh báo: </span>
          <span className="font-medium text-yellow-600">{logCounts.warn}</span>
        </div>
        <div className="text-sm">
          <span className="text-gray-600 dark:text-gray-400">Thông tin: </span>
          <span className="font-medium text-blue-600">{logCounts.info}</span>
        </div>
        <div className="text-sm">
          <span className="text-gray-600 dark:text-gray-400">Debug: </span>
          <span className="font-medium text-gray-600">{logCounts.debug}</span>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 p-4 border-b border-gray-200 dark:border-gray-700">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Tìm kiếm logs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        {/* Level Filter */}
        <select
          value={levelFilter}
          onChange={(e) => setLevelFilter(e.target.value as 'all' | 'error' | 'warn' | 'info' | 'debug')}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">Tất cả mức độ</option>
          <option value="error">Lỗi</option>
          <option value="warn">Cảnh báo</option>
          <option value="warning">Cảnh báo</option>
          <option value="info">Thông tin</option>
          <option value="debug">Debug</option>
        </select>
        
        {/* Device Filter */}
        <select
          value={deviceFilter}
          onChange={(e) => setDeviceFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">Tất cả thiết bị</option>
          {uniqueDevices.map(deviceId => (
            <option key={deviceId} value={deviceId}>{deviceId}</option>
          ))}
        </select>
        
        {/* Auto Scroll Toggle */}
        <label className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
          <input
            type="checkbox"
            checked={autoScroll}
            onChange={(e) => setAutoScroll(e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span>Tự động cuộn</span>
        </label>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-4 mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
            <span className="text-sm font-medium text-red-800 dark:text-red-200">Lỗi tải logs:</span>
          </div>
          <p className="mt-1 text-sm text-red-700 dark:text-red-300">{error}</p>
        </div>
      )}

      {/* Logs Content */}
      <div 
        ref={logsContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto p-4 space-y-2 font-mono text-sm"
        style={{ maxHeight: '400px' }}
      >
        {isLoading ? (
          <div className="text-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin mx-auto text-gray-400 mb-2" />
            <p className="text-gray-500 dark:text-gray-400">Đang tải logs...</p>
          </div>
        ) : filteredLogs.length > 0 ? (
          filteredLogs.map((log) => (
            <div
              key={log.id}
              className="flex items-start space-x-3 p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <span className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
                {formatDate(log.timestamp || log.created_at)}
              </span>
              
              <span className={`px-2 py-1 rounded text-xs font-medium whitespace-nowrap ${
                getLogLevelBadge((log.log_level || log.level || '').toLowerCase())
              }`}>
                {(log.log_level || log.level || '').toUpperCase()}
              </span>
              
              <span className="text-xs text-blue-600 dark:text-blue-400 whitespace-nowrap">
                {log.device_id || log.deviceId}
              </span>
              
              <span className={`flex-1 ${getLogLevelColor((log.log_level || log.level || '').toLowerCase())}`}>
                {log.message}
              </span>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            {logs.length === 0 ? 'Chưa có logs nào' : 'Không tìm thấy logs phù hợp với bộ lọc'}
          </div>
        )}
        
        <div ref={logsEndRef} />
      </div>
      
      {/* Footer */}
      {logs.length >= maxLogs && (
        <div className="p-2 bg-yellow-50 dark:bg-yellow-900/20 border-t border-yellow-200 dark:border-yellow-800 text-center">
          <span className="text-sm text-yellow-800 dark:text-yellow-200">
            Đã đạt giới hạn {maxLogs} logs. Logs cũ sẽ bị xóa tự động.
          </span>
        </div>
      )}
    </div>
  );
}