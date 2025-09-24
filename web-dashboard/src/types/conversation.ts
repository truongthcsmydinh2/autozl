export interface DevicePair {
  id: string;
  temp_pair_id?: string;
  backend_id?: string; // Backend's internal pair ID
  deviceA: {
    id: string;
    ip: string;
    phone?: string;
    name?: string;
    note?: string;
    device_id?: string;
  };
  deviceB: {
    id: string;
    ip: string;
    phone?: string;
    name?: string;
    note?: string;
    device_id?: string;
  };
  temp_id?: string; // Keep for backward compatibility
  createdAt: Date;
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ConversationSummary {
  noidung: string;
  hoancanh: string;
  so_cau: number;
}

export interface ConversationData {
  conversation: ConversationMessage[];
  summary: ConversationSummary;
}

export interface ConversationSummaryRecord {
  id: string;
  pair_id: string;
  summary_data: ConversationSummary;
  created_at: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ConversationInputProps {
  devicePairs: DevicePair[];
  onConversationApplied: (pairId: string, data: ConversationData) => void;
  onError: (error: string) => void;
  onLog: (message: string) => void;
}

export interface SummaryDisplayProps {
  pairId: string;
  summaries: ConversationSummaryRecord[];
  devicePairs: DevicePair[];
}