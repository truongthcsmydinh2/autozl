// Device types - Updated for Supabase compatibility
export interface Device {
  id: string;
  device_id: string;
  name: string;
  phone_number?: string;
  phone?: string; // For NuoiZaloPanel compatibility
  note?: string; // For NuoiZaloPanel compatibility
  ip_address?: string; // For DeviceGrid compatibility
  status: 'idle' | 'running' | 'error' | 'offline' | 'connected' | 'disconnected';
  message?: string;
  progress?: number;
  current_message_id?: string;
  created_at: string;
  updated_at: string;
  // Legacy fields for backward compatibility
  ip?: string;
  port?: number;
  lastSeen?: Date;
  platform?: string;
  version?: string;
  isActive?: boolean;
}

// Automation types
export interface AutomationFlow {
  id: string;
  name: string;
  description: string;
  steps: AutomationStep[];
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface AutomationStep {
  action: string;
  target: string;
  params: Record<string, string | number | boolean>;
}

// Log types - Updated for Supabase compatibility
export interface LogEntry {
  id: string;
  device_id?: string;
  session_id?: string;
  log_level: 'INFO' | 'ERROR' | 'DEBUG' | 'WARNING';
  message: string;
  metadata?: any;
  created_at: string;
  // Legacy fields for backward compatibility
  timestamp?: Date;
  level?: 'info' | 'warn' | 'error' | 'debug';
  deviceId?: string;
  flowId?: string;
}

// Configuration types
export interface AppConfig {
  devices: Device[];
  flows: AutomationFlow[];
  settings: {
    autoConnect: boolean;
    logLevel: string;
    maxLogEntries: number;
  };
}

// API Response types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// WebSocket message types
export interface WSMessage {
  type: 'device_status' | 'log_entry' | 'flow_update' | 'screenshot';
  payload: unknown;
  timestamp: Date;
}