import { Device, LogEntry } from '@/types';
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Format date utilities
export const formatDate = (date: Date): string => {
  return date.toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export const formatTime = (date: Date | string | number | undefined): string => {
  try {
    if (!date) {
      return 'N/A';
    }
    
    const dateObj = date instanceof Date ? date : new Date(date);
    
    if (isNaN(dateObj.getTime())) {
      return 'Invalid Time';
    }
    
    return new Intl.DateTimeFormat('vi-VN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(dateObj);
  } catch (error) {
    return 'Invalid Time';
  }
};

export const formatDateTime = (date: Date | string | number | undefined): string => {
  try {
    if (!date) {
      return 'N/A';
    }
    
    const dateObj = date instanceof Date ? date : new Date(date);
    
    if (isNaN(dateObj.getTime())) {
      return 'Invalid DateTime';
    }
    
    return new Intl.DateTimeFormat('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(dateObj);
  } catch (error) {
    return 'Invalid DateTime';
  }
};

// Device utilities
export const getDeviceStatusColor = (status: Device['status']): string => {
  switch (status) {
    case 'connected':
      return 'text-green-500';
    case 'disconnected':
      return 'text-gray-500';
    case 'error':
      return 'text-red-500';
    default:
      return 'text-gray-500';
  }
};

export const getDeviceStatusBadge = (status: Device['status']): string => {
  switch (status) {
    case 'connected':
      return 'bg-green-100 text-green-800';
    case 'disconnected':
      return 'bg-gray-100 text-gray-800';
    case 'error':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

// Log utilities
export const getLogLevelColor = (level: LogEntry['level']): string => {
  switch (level) {
    case 'info':
      return 'text-blue-500';
    case 'warn':
      return 'text-yellow-500';
    case 'error':
      return 'text-red-500';
    case 'debug':
      return 'text-gray-500';
    default:
      return 'text-gray-500';
  }
};

export const getLogLevelBadge = (level: LogEntry['level']): string => {
  switch (level) {
    case 'info':
      return 'bg-blue-100 text-blue-800';
    case 'warn':
      return 'bg-yellow-100 text-yellow-800';
    case 'error':
      return 'bg-red-100 text-red-800';
    case 'debug':
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

// API utilities
export const apiCall = async <T>(url: string, options?: RequestInit): Promise<T> => {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers
    },
    ...options
  });

  if (!response.ok) {
    throw new Error(`API call failed: ${response.statusText}`);
  }

  return response.json();
};

// WebSocket utilities
export const createWebSocketConnection = (url: string): WebSocket => {
  const ws = new WebSocket(url);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };
  
  return ws;
};

// Local storage utilities
export const storage = {
  get: <T>(key: string, defaultValue?: T): T | null => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue || null;
    } catch {
      return defaultValue || null;
    }
  },
  
  set: <T>(key: string, value: T): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  },
  
  remove: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to remove from localStorage:', error);
    }
  }
};