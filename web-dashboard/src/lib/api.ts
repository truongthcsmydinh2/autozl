// API service for communicating with Python backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export interface SyncDevicesResponse {
  success: boolean;
  message: string;
  devices_synced: number;
  devices: Array<{
    device_id: string;
    name: string;
    phone_number?: string;
    status: string;
  }>;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error('API request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // Sync devices from ADB to Supabase
  async syncDevices(): Promise<ApiResponse<SyncDevicesResponse>> {
    return this.request<SyncDevicesResponse>('/api/sync-devices', {
      method: 'POST',
    });
  }

  // Get current devices from backend
  async getDevices(): Promise<ApiResponse<any[]>> {
    return this.request<any[]>('/api/devices');
  }

  // Get phone mapping
  async getPhoneMapping(): Promise<ApiResponse<Record<string, string>>> {
    return this.request<Record<string, string>>('/api/phone-mapping');
  }

  // Update phone mapping
  async updatePhoneMapping(
    mapping: Record<string, string>
  ): Promise<ApiResponse<any>> {
    return this.request('/api/phone-mapping', {
      method: 'POST',
      body: JSON.stringify({ mapping }),
    });
  }

  // Update device name
  async updateDeviceName(
    deviceId: string,
    name: string
  ): Promise<ApiResponse<any>> {
    return this.request(`/api/devices/${deviceId}/name`, {
      method: 'PUT',
      body: JSON.stringify({ name }),
    });
  }

  // Update device note
  async updateDeviceNote(
    deviceId: string,
    note: string
  ): Promise<ApiResponse<any>> {
    return this.request(`/api/devices/${deviceId}/note`, {
      method: 'POST',
      body: JSON.stringify({ note }),
    });
  }

  // Update device phone number
  async updateDevicePhone(
    deviceId: string,
    phoneNumber: string
  ): Promise<ApiResponse<any>> {
    return this.request(`/api/devices/${deviceId}/phone`, {
      method: 'PUT',
      body: JSON.stringify({ phone_number: phoneNumber }),
    });
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{ status: string }>> {
    return this.request<{ status: string }>('/health');
  }
}

export const apiService = new ApiService();
export { API_BASE_URL };
export default apiService;