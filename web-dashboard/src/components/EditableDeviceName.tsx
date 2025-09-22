import React, { useState, useRef, useEffect } from 'react';
import { Edit2, Check, X } from 'lucide-react';

interface EditableDeviceNameProps {
  deviceId: string;
  currentName: string;
  onSave: (deviceId: string, newName: string) => Promise<void>;
  className?: string;
}

const EditableDeviceName: React.FC<EditableDeviceNameProps> = ({
  deviceId,
  currentName,
  onSave,
  className = ''
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(currentName);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  useEffect(() => {
    setEditValue(currentName);
  }, [currentName]);

  const handleStartEdit = () => {
    setIsEditing(true);
    setError(null);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditValue(currentName);
    setError(null);
  };

  const handleSave = async () => {
    const trimmedValue = editValue.trim();
    
    // Validation
    if (!trimmedValue) {
      alert('Tên thiết bị không được để trống');
      return;
    }
    
    if (trimmedValue.length > 50) {
      alert('Tên thiết bị không được vượt quá 50 ký tự');
      return;
    }
    
    if (trimmedValue === currentName) {
      setIsEditing(false);
      return;
    }

    setIsSaving(true);
    try {
      await onSave(deviceId, trimmedValue);
      setIsEditing(false);
    } catch (error) {
      console.error('Error in handleSave:', error);
      alert('Không thể lưu tên thiết bị. Vui lòng thử lại.');
      // Reset to original value on error
      setEditValue(currentName);
    } finally {
      setIsSaving(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      handleCancel();
    }
  };

  if (isEditing) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className="flex-1">
          <input
            ref={inputRef}
            type="text"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full px-2 py-1 text-sm font-semibold text-gray-900 dark:text-white bg-white dark:bg-gray-700 border border-blue-300 dark:border-blue-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Nhập tên thiết bị..."
            disabled={isSaving}
          />
          {error && (
            <div className="text-xs text-red-500 mt-1">{error}</div>
          )}
        </div>
        <div className="flex items-center space-x-1">
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="p-1 text-green-600 hover:text-green-700 hover:bg-green-50 dark:hover:bg-green-900/20 rounded transition-colors duration-200 disabled:opacity-50"
            title="Lưu"
          >
            <Check className="h-4 w-4" />
          </button>
          <button
            onClick={handleCancel}
            disabled={isSaving}
            className="p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 rounded transition-colors duration-200 disabled:opacity-50"
            title="Hủy"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex items-center space-x-2 group ${className}`}>
      <div className="text-sm font-semibold text-gray-900 dark:text-white flex-1">
        {currentName}
      </div>
      <button
        onClick={handleStartEdit}
        className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-all duration-200"
        title="Chỉnh sửa tên"
      >
        <Edit2 className="h-3 w-3" />
      </button>
    </div>
  );
};

export default EditableDeviceName;