'use client';

import React, { useState, useEffect } from 'react';
import { Upload, Save, Trash2, AlertCircle, Plus, Loader2 } from 'lucide-react';
import { DevicePair } from '../types/device';
import { toast } from 'sonner';

interface ConversationInputProps {
  devicePairs: DevicePair[];
  onConversationApplied: (data: any) => void;
  onError: (error: string) => void;
  onLog: (message: string) => void;
}

interface Summary {
  noidung: string;
  hoancanh: string;
  so_cau: number;
}

interface Message {
  role: string;
  content: string;
}

interface PairFormData {
  messages: Message[];
  summary: Summary;
}

const ConversationInputComponent: React.FC<ConversationInputProps> = ({
  devicePairs,
  onConversationApplied,
  onError,
  onLog
}) => {
  const [jsonInputs, setJsonInputs] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [validationError, setValidationError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [availablePairs, setAvailablePairs] = useState<string[]>([]);

  // Fetch available pairs for suggestions
  const fetchAvailablePairs = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/pairs');
      if (response.ok) {
        const data = await response.json();
        const pairIds = data.pairs?.map((pair: any) => pair.id) || [];
        setAvailablePairs(pairIds);
      }
    } catch (error) {
      console.error('Error fetching available pairs:', error);
    }
  };

  // Debug logs
  useEffect(() => {
    console.log('🔄 ConversationInputComponent rendered with:', {
      devicePairsCount: devicePairs.length,
      devicePairs: devicePairs.map(p => ({ id: p.id, deviceA: p.deviceA?.ip, deviceB: p.deviceB?.ip })),
      jsonInputsKeys: Object.keys(jsonInputs)
    });
    
    // Fetch available pairs on component mount
    fetchAvailablePairs();
  }, [devicePairs, jsonInputs]);
  
  // Component mounted log
  useEffect(() => {
    console.log('🎯 ConversationInputComponent MOUNTED!');
  }, []);

  const handleLoadFromFile = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const data = JSON.parse(content);
        
        if ((data.messages && Array.isArray(data.messages)) || (data.conversation && Array.isArray(data.conversation))) {
          // Load into the first available pair or selected pair
          const firstPairId = devicePairs[0]?.id;
          if (firstPairId) {
            setJsonInputs(prev => ({ ...prev, [firstPairId]: content }));
            onLog('File loaded successfully');
          }
        } else {
          onError('Invalid file format. Expected JSON with messages or conversation array.');
        }
      } catch (error) {
        onError('Failed to parse JSON file');
      }
    };
    reader.readAsText(file);
  };





  // Handle Apply button for all pairs
  const handleApply = async () => {
    console.log('🚀 Bắt đầu gửi dữ liệu cho tất cả pairs');
    console.log('handleApply called with devicePairs length:', devicePairs.length);
    console.log('jsonInputs:', jsonInputs);
    
    setIsLoading(true);
    setIsSubmitting(true);
    setValidationError('');

    try {
      let hasValidData = false;
      
      for (const [pairId, jsonInput] of Object.entries(jsonInputs)) {
        if (!jsonInput.trim()) continue;
        
        try {
          console.log('📝 Dữ liệu JSON đầu vào cho', pairId, ':', jsonInput);
          const conversationData = JSON.parse(jsonInput);
          console.log('✅ Parse JSON thành công cho', pairId, ':', conversationData);
          
          // Validate structure - support both formats
          let hasMessages = conversationData.messages && Array.isArray(conversationData.messages);
          let hasConversation = conversationData.conversation && Array.isArray(conversationData.conversation);
          
          if (!hasMessages && !hasConversation) {
            const errorMsg = `Invalid JSON structure for pair ${pairId}: either messages or conversation array is required`;
            onError(errorMsg);
            toast.error(errorMsg);
            return;
          }
          
          if (!conversationData.summary || !conversationData.summary.noidung || !conversationData.summary.hoancanh) {
            const errorMsg = `Invalid JSON structure for pair ${pairId}: summary with noidung and hoancanh is required`;
            onError(errorMsg);
            toast.error(errorMsg);
            return;
          }
          
          // Handle demo data format (conversation array)
          if (hasConversation && !hasMessages) {
            // Convert conversation format to messages format for display
            const messageCount = conversationData.conversation.length;
            
            // Fix socau -> so_cau if needed
            if (conversationData.summary.socau && !conversationData.summary.so_cau) {
              conversationData.summary.so_cau = conversationData.summary.socau;
              delete conversationData.summary.socau;
            }
            
            // Update so_cau to match conversation length
            conversationData.summary.so_cau = messageCount;
          } else if (hasMessages) {
            // Update so_cau to match messages length
            conversationData.summary.so_cau = conversationData.messages.length;
          }
          
          onLog(`Applying conversation for pair ${pairId}...`);
          
          // Use demo endpoint if pairId is 'demo'
          const endpoint = pairId === 'demo' 
            ? 'http://localhost:8001/api/conversation/demo'
        : `http://localhost:8001/api/conversation/${pairId}`;
          
          console.log(`📡 Gửi request đến: ${endpoint}`);
          
          const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(conversationData)
          });

          console.log('📨 Response status:', response.status);
          
          if (!response.ok) {
            let errorMessage = `HTTP ${response.status}`;
            try {
              // Try to get error message from response
              const errorText = await response.text();
              console.error('❌ Response error:', errorText);
              
              // Handle specific error cases
               if (response.status === 404) {
                 if (pairId === 'demo') {
                   errorMessage = 'Demo endpoint không khả dụng';
                 } else {
                   let suggestion = '';
                   if (availablePairs.length > 0) {
                     const firstFewPairs = availablePairs.slice(0, 3);
                     suggestion = ` Các ID có sẵn: ${firstFewPairs.join(', ')}${availablePairs.length > 3 ? '...' : ''}`;
                   }
                   errorMessage = `Không tìm thấy device pair với ID: ${pairId}.${suggestion} Vui lòng kiểm tra lại ID hoặc tạo pair mới.`;
                 }
               } else {
                 errorMessage = errorText || `HTTP error! status: ${response.status}`;
               }
            } catch (textError) {
              console.error('❌ Error reading response text:', textError);
              errorMessage = `HTTP error! status: ${response.status}`;
            }
            
            throw new Error(errorMessage);
          }

          const result = await response.json();
          console.log('✅ Gửi dữ liệu thành công cho', pairId, ':', result);
          onLog(`Conversation applied successfully for ${pairId}: ${JSON.stringify(result)}`);
          onConversationApplied(pairId, conversationData);
          hasValidData = true;
          
        } catch (parseError) {
          const errorMsg = `Invalid JSON format for pair ${pairId}: ${parseError instanceof Error ? parseError.message : 'Unknown error'}`;
          console.error('❌ Lỗi parse JSON:', parseError);
          onError(errorMsg);
          toast.error(errorMsg);
          return;
        }
      }
      
      if (!hasValidData) {
        const errorMsg = 'Vui lòng nhập dữ liệu JSON hợp lệ cho ít nhất một cặp thiết bị';
        onError(errorMsg);
        toast.error(errorMsg);
        return;
      }
      
      toast.success('Gửi dữ liệu conversation thành công cho tất cả pairs!');
      
      // Clear all inputs after successful application
      setJsonInputs({});
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      console.error('❌ Lỗi khi xử lý dữ liệu:', error);
      onError(`Failed to apply conversation: ${errorMessage}`);
      onLog(`Error applying conversation: ${errorMessage}`);
      toast.error(`Có lỗi xảy ra: ${errorMessage}`);
    } finally {
      setIsLoading(false);
      setIsSubmitting(false);
      console.log('🏁 Hoàn thành xử lý request cho tất cả pairs');
    }
  };

  // Handle Clear button for all forms
  const handleClear = () => {
    setJsonInputs({});
    setValidationError('');
    onLog('🗑️ Đã xóa tất cả dữ liệu form');
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          Nhập Conversation cho tất cả cặp thiết bị
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Nhập dữ liệu conversation cho từng cặp thiết bị. Chỉ những cặp có đầy đủ dữ liệu sẽ được áp dụng.
        </p>
      </div>

      {/* Device Pairs List */}
      <div className="space-y-6">
        {devicePairs.length === 0 ? (
          <div className="border border-yellow-200 dark:border-yellow-700 rounded-lg p-6 bg-yellow-50 dark:bg-yellow-900/20">
            <div className="flex items-center space-x-2 mb-4">
              <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
              <h4 className="text-md font-medium text-yellow-800 dark:text-yellow-200">
                Chưa có cặp thiết bị nào
              </h4>
            </div>
            <p className="text-sm text-yellow-700 dark:text-yellow-300 mb-4">
              Bạn cần tạo cặp thiết bị trước hoặc có thể test với demo data bên dưới:
            </p>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-2">
                Demo Data (Test):
              </label>
              <textarea
                value={jsonInputs['demo'] || ''}
                onChange={(e) => setJsonInputs(prev => ({ ...prev, 'demo': e.target.value }))}
                placeholder={`{
  "conversation": [
    {
      "role": "device_a",
      "content": "ê"
    },
    {
      "role": "device_b",
      "content": "gì đó"
    },
    {
      "role": "device_a",
      "content": "ăn cơm chưa"
    }
  ],
  "summary": {
    "noidung": "Cuộc trò chuyện thường ngày",
    "hoancanh": "Hai người bạn hỏi thăm nhau",
    "so_cau": 3
  }
}`}
                className="w-full h-64 px-3 py-2 border border-yellow-300 dark:border-yellow-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 font-mono text-sm"
              />
            </div>
          </div>
        ) : (
          devicePairs.map((pair) => {
            return (
              <div key={pair.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <h4 className="text-md font-medium text-gray-900 dark:text-white mb-2">
                  {pair.deviceA?.ip || 'N/A'} ↔ {pair.deviceB?.ip || 'N/A'}
                </h4>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                  ID: {pair.id}
                </p>
                
                <div className="mb-4">
                  <textarea
                    value={jsonInputs[pair.id] || ''}
                    onChange={(e) => setJsonInputs(prev => ({ ...prev, [pair.id]: e.target.value }))}
                    placeholder={`{
  "conversation": [
    {
      "role": "device_a",
      "content": "Tin nhắn từ thiết bị A"
    },
    {
      "role": "device_b", 
      "content": "Tin nhắn từ thiết bị B"
    }
  ],
  "summary": {
    "noidung": "Tóm tắt nội dung cuộc trò chuyện",
    "hoancanh": "Mô tả hoàn cảnh cuộc trò chuyện",
    "socau": 2
  }
}`}
                    className="w-full h-64 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 font-mono text-sm"
                  />
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Validation Error */}
      {validationError && (
        <div className="mt-4 flex items-center space-x-2 text-red-600 dark:text-red-400 text-sm">
          <AlertCircle className="h-4 w-4" />
          <span>{validationError}</span>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center space-x-3">
        <button
          onClick={handleApply}
          disabled={isLoading || isSubmitting}
          className="flex items-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50 transition-colors"
        >
          {(isLoading || isSubmitting) ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Đang xử lý...</span>
            </>
          ) : (
            <>
              <Save className="h-4 w-4" />
              <span>Áp dụng tất cả</span>
            </>
          )}
        </button>
        
        <button
          onClick={handleClear}
          disabled={isLoading}
          className="flex items-center space-x-2 px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 disabled:opacity-50 transition-colors"
        >
          <Trash2 className="h-4 w-4" />
          <span>Xóa tất cả</span>
        </button>
      </div>
    </div>
  );
};

export default ConversationInputComponent;