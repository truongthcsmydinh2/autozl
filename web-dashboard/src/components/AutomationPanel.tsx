'use client';

import { useState } from 'react';
import { AutomationFlow } from '@/types';
import AutomationFlowCard from './AutomationFlowCard';
import { Plus, Search, Play, Square, RefreshCw } from 'lucide-react';

interface AutomationPanelProps {
  flows: AutomationFlow[];
  runningFlows: string[];
  onCreateFlow?: () => void;
  onStartFlow?: (flowId: string) => void;
  onStopFlow?: (flowId: string) => void;
  onEditFlow?: (flowId: string) => void;
  onDeleteFlow?: (flowId: string) => void;
  onDuplicateFlow?: (flowId: string) => void;
  onConfigureFlow?: (flowId: string) => void;
  onStartAll?: () => void;
  onStopAll?: () => void;
  onRefresh?: () => void;
  isLoading?: boolean;
}

export default function AutomationPanel({
  flows,
  runningFlows,
  onCreateFlow,
  onStartFlow,
  onStopFlow,
  onEditFlow,
  onDeleteFlow,
  onDuplicateFlow,
  onConfigureFlow,
  onStartAll,
  onStopAll,
  onRefresh,
  isLoading = false
}: AutomationPanelProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive' | 'running'>('all');

  const filteredFlows = flows.filter(flow => {
    const matchesSearch = flow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         flow.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    let matchesStatus = true;
    switch (statusFilter) {
      case 'active':
        matchesStatus = flow.isActive;
        break;
      case 'inactive':
        matchesStatus = !flow.isActive;
        break;
      case 'running':
        matchesStatus = runningFlows.includes(flow.id);
        break;
    }
    
    return matchesSearch && matchesStatus;
  });

  const activeCount = flows.filter(f => f.isActive).length;
  const runningCount = runningFlows.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Automation Control
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {flows.length} flows • {activeCount} hoạt động • {runningCount} đang chạy
          </p>
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-colors"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Làm mới</span>
          </button>
          
          <button
            onClick={onCreateFlow}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center space-x-2 transition-colors"
          >
            <Plus className="h-4 w-4" />
            <span>Tạo Flow</span>
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Tìm kiếm flow..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as 'all' | 'active' | 'inactive' | 'running')}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">Tất cả</option>
          <option value="active">Hoạt động</option>
          <option value="inactive">Tạm dừng</option>
          <option value="running">Đang chạy</option>
        </select>
        
        {/* Bulk Actions */}
        <div className="flex space-x-2">
          <button
            onClick={onStartAll}
            disabled={activeCount === 0 || runningCount === activeCount}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-colors"
          >
            <Play className="h-4 w-4" />
            <span>Chạy tất cả</span>
          </button>
          
          <button
            onClick={onStopAll}
            disabled={runningCount === 0}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-colors"
          >
            <Square className="h-4 w-4" />
            <span>Dừng tất cả</span>
          </button>
        </div>
      </div>

      {/* Flow Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 animate-pulse">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1 space-y-2">
                  <div className="h-5 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
                  <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-full"></div>
                </div>
                <div className="h-6 w-16 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
              </div>
              <div className="space-y-3 mb-4">
                <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded"></div>
                <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-2/3"></div>
              </div>
              <div className="flex space-x-2">
                <div className="h-8 bg-gray-300 dark:bg-gray-600 rounded flex-1"></div>
                <div className="h-8 w-8 bg-gray-300 dark:bg-gray-600 rounded"></div>
                <div className="h-8 w-8 bg-gray-300 dark:bg-gray-600 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      ) : filteredFlows.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredFlows.map((flow) => (
            <AutomationFlowCard
              key={flow.id}
              flow={flow}
              isRunning={runningFlows.includes(flow.id)}
              onStart={onStartFlow}
              onStop={onStopFlow}
              onEdit={onEditFlow}
              onDelete={onDeleteFlow}
              onDuplicate={onDuplicateFlow}
              onConfigure={onConfigureFlow}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="mx-auto h-24 w-24 text-gray-400 dark:text-gray-600 mb-4">
            <Search className="h-full w-full" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Không tìm thấy automation flow
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {searchTerm || statusFilter !== 'all' 
              ? 'Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm'
              : 'Chưa có automation flow nào được tạo'
            }
          </p>
          {!searchTerm && statusFilter === 'all' && (
            <button
              onClick={onCreateFlow}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Tạo flow đầu tiên
            </button>
          )}
        </div>
      )}
    </div>
  );
}