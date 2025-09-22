import React, { useState, useRef, useEffect } from 'react';
import { Edit2, Check, X } from 'lucide-react';

interface EditablePhoneNumberProps {
  deviceId: string;
  currentPhone: string;
  onSave: (deviceId: string, newPhone: string) => Promise<void>;
  className?: string;
}

const EditablePhoneNumber: React.FC<EditablePhoneNumberProps> = ({
  deviceId,
  currentPhone,
  onSave,
  className = ''
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(currentPhone);
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
    setEditValue(currentPhone);
  }, [currentPhone]);

  const validatePhoneNumber = (phone: string): boolean => {
    // Remove all non-digit characters for validation
    const digitsOnly = phone.replace(/\D/g, '');
    
    // Check if it's a valid phone number (8-15 digits)
    if (digitsOnly.length < 8 || digitsOnly.length > 15) {
      return false;
    }
    
    // Basic phone number pattern (can start with + and contain digits, spaces, hyphens, parentheses)
    const phonePattern = /^[+]?[0-9\s\-\(\)]{8,20}$/;
    return phonePattern.test(phone.trim());
  };

  const handleStartEdit = () => {
    setIsEditing(true);
    setError(null);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditValue(currentPhone);
    setError(null);
  };

  const handleSave = async () => {
    const trimmedValue = editValue.trim();
    
    // Validation
    if (!trimmedValue) {
      setError('Số điện thoại không được để trống');
      return;
    }
    
    if (!validatePhoneNumber(trimmedValue)) {
      setError('Số điện thoại không hợp lệ (8-15 chữ số)');
      return;
    }
    
    if (trimmedValue === currentPhone) {
      setIsEditing(false);
      return;
    }

    setIsSaving(true);
    setError(null);
    try {
      console.log('EditablePhoneNumber handleSave called with:', { deviceId, newPhone: trimmedValue });
      await onSave(deviceId, trimmedValue);
      console.log('EditablePhoneNumber handleSave completed successfully');
      setIsEditing(false);
    } catch (error) {
      console.error('Error in EditablePhoneNumber handleSave:', error);
      setError('Không thể lưu số điện thoại. Vui lòng thử lại.');
      // Reset to original value on error
      setEditValue(currentPhone);
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
            type="tel"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full px-2 py-1 text-sm font-mono text-gray-900 dark:text-white bg-white dark:bg-gray-700 border border-blue-300 dark:border-blue-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Nhập số điện thoại..."
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
      <div className="text-sm font-mono text-gray-900 dark:text-white flex-1">
        {currentPhone || 'Chưa có số điện thoại'}
      </div>
      <button
        onClick={handleStartEdit}
        className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-all duration-200"
        title="Chỉnh sửa số điện thoại"
      >
        <Edit2 className="h-3 w-3" />
      </button>
    </div>
  );
};

export default EditablePhoneNumber;