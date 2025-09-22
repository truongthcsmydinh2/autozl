'use client';

import { AutomationFlow } from '@/types';
import { formatDate } from '@/utils';
import { Play, Square, Edit, Trash2, Copy, Settings } from 'lucide-react';

interface AutomationFlowCardProps {
  flow: AutomationFlow;
  isRunning?: boolean;
  onStart?: (flowId: string) => void;
  onStop?: (flowId: string) => void;
  onEdit?: (flowId: string) => void;
  onDelete?: (flowId: string) => void;
  onDuplicate?: (flowId: string) => void;
  onConfigure?: (flowId: string) => void;
}

export default function AutomationFlowCard({
  flow,
  isRunning = false,
  onStart,
  onStop,
  onEdit,
  onDelete,
  onDuplicate,
  onConfigure
}: AutomationFlowCardProps) {
  const handleToggleRun = () => {
    if (isRunning) {
      onStop?.(flow.id);
    } else {
      onStart?.(flow.id);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {flow.name}
            </h3>
            {isRunning && (
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-green-600 dark:text-green-400 font-medium">
                  Đang chạy
                </span>
              </div>
            )}
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
            {flow.description}
          </p>
        </div>
        
        <div className="flex items-center space-x-1">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            flow.isActive 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
              : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
          }`}>
            {flow.isActive ? 'Hoạt động' : 'Tạm dừng'}
          </span>
        </div>
      </div>

      {/* Flow Info */}
      <div className="mb-4 space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">Số bước:</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {flow.steps.length} bước
          </span>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">Cập nhật:</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {formatDate(flow.updatedAt)}
          </span>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">Tạo lúc:</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {formatDate(flow.createdAt)}
          </span>
        </div>
      </div>

      {/* Steps Preview */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Các bước thực hiện:
        </h4>
        <div className="space-y-1 max-h-24 overflow-y-auto">
          {flow.steps.slice(0, 3).map((step, index) => (
            <div key={index} className="flex items-center space-x-2 text-xs">
              <span className="w-4 h-4 bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded-full flex items-center justify-center font-medium">
                {index + 1}
              </span>
              <span className="text-gray-600 dark:text-gray-400 truncate">
                {`${step.action}: ${step.target || 'N/A'}`}
              </span>
            </div>
          ))}
          {flow.steps.length > 3 && (
            <div className="text-xs text-gray-500 dark:text-gray-400 pl-6">
              ... và {flow.steps.length - 3} bước khác
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-2">
        {/* Run/Stop Button */}
        <button
          onClick={handleToggleRun}
          disabled={!flow.isActive}
          className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center justify-center space-x-1 ${
            isRunning
              ? 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-300'
              : 'bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900 dark:text-green-300'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isRunning ? (
            <>
              <Square className="h-3 w-3" />
              <span>Dừng</span>
            </>
          ) : (
            <>
              <Play className="h-3 w-3" />
              <span>Chạy</span>
            </>
          )}
        </button>
        
        {/* Edit Button */}
        <button
          onClick={() => onEdit?.(flow.id)}
          className="px-3 py-2 bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-300 rounded-md text-sm font-medium transition-colors"
          title="Chỉnh sửa"
        >
          <Edit className="h-4 w-4" />
        </button>
        
        {/* Configure Button */}
        <button
          onClick={() => onConfigure?.(flow.id)}
          className="px-3 py-2 bg-purple-100 text-purple-700 hover:bg-purple-200 dark:bg-purple-900 dark:text-purple-300 rounded-md text-sm font-medium transition-colors"
          title="Cấu hình"
        >
          <Settings className="h-4 w-4" />
        </button>
        
        {/* Duplicate Button */}
        <button
          onClick={() => onDuplicate?.(flow.id)}
          className="px-3 py-2 bg-yellow-100 text-yellow-700 hover:bg-yellow-200 dark:bg-yellow-900 dark:text-yellow-300 rounded-md text-sm font-medium transition-colors"
          title="Sao chép"
        >
          <Copy className="h-4 w-4" />
        </button>
        
        {/* Delete Button */}
        <button
          onClick={() => onDelete?.(flow.id)}
          className="px-3 py-2 bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-300 rounded-md text-sm font-medium transition-colors"
          title="Xóa"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}