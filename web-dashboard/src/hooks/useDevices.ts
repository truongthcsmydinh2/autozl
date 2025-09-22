import { useState, useEffect, useRef, useCallback } from 'react'
import { supabase, Device } from '../lib/supabase'
import { apiService, API_BASE_URL } from '../lib/api'

export function useDevices() {
  const [devices, setDevices] = useState<Device[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const lastFetchRef = useRef<number>(0)

  const fetchDevices = useCallback(async (silent = false) => {
    try {
      // Prevent too frequent requests
      const now = Date.now()
      if (now - lastFetchRef.current < 1000) {
        return
      }
      lastFetchRef.current = now

      if (!silent) {
        setLoading(true)
      } else {
        setIsRefreshing(true)
      }
      
      const response = await apiService.getDevices()
      
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch devices')
      }
      
      // Transform API response to match Device interface
      const transformedDevices = (response.data?.data || []).map((device: any) => ({
        id: device.device_id,
        device_id: device.device_id,
        name: device.name || device.device_id, // Use custom name from backend or fallback to device_id
        ip: device.ip,
        ip_address: device.ip, // Add ip_address field for DeviceGrid compatibility
        phone_number: device.phone,
        phone: device.phone, // Add phone field for NuoiZaloPanel compatibility
        note: device.note, // Add note field for NuoiZaloPanel compatibility
        status: device.status || 'disconnected', // Use actual status from backend
        message: device.note || '',
        progress: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }))
      
      // Optimistic update: only update if data actually changed
      setDevices(prevDevices => {
        const hasChanged = JSON.stringify(prevDevices) !== JSON.stringify(transformedDevices)
        return hasChanged ? transformedDevices : prevDevices
      })
    } catch (err) {
      if (!silent) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      }
    } finally {
      if (!silent) {
        setLoading(false)
      } else {
        setIsRefreshing(false)
      }
    }
  }, [])

  const updateDevice = useCallback(async (deviceId: string, updates: any) => {
    try {
      let response;
      
      // Check if updating device name
      if (updates.name !== undefined) {
        response = await apiService.updateDeviceName(deviceId, updates.name);
      } else {
        // Default to note update for backward compatibility
        response = await apiService.updateDeviceNote(deviceId, updates.note || updates.message || '');
      }

      if (!response.success) {
        throw new Error(response.error || 'Failed to update device');
      }

      // Refresh data from server to ensure UI shows latest data
      await fetchDevices(true);

      return true;
    } catch (error) {
      console.error('Error updating device:', error);
      setError(error instanceof Error ? error.message : 'Failed to update device');
      return false;
    }
  }, [fetchDevices])

  const updateDevicePhone = useCallback(async (deviceId: string, phoneNumber: string) => {
    try {
      console.log('useDevices updateDevicePhone called with:', { deviceId, phoneNumber });
      
      const response = await apiService.updateDevicePhone(deviceId, phoneNumber);
      console.log('useDevices updateDevicePhone response:', response);

      if (!response.success) {
        throw new Error(response.error || 'Failed to update device phone');
      }

      // Refresh data from server to ensure UI shows latest data
      await fetchDevices(true);

      return true;
    } catch (error) {
      console.error('Error updating device phone:', error);
      setError(error instanceof Error ? error.message : 'Failed to update device phone');
      return false;
    }
  }, [fetchDevices])

  useEffect(() => {
    fetchDevices(false) // Initial load with loading state

    // Subscribe to real-time changes
    const subscription = supabase
      .channel('devices')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'devices'
      }, () => {
        fetchDevices(true) // Silent refresh for real-time updates
      })
      .subscribe()

    return () => {
      subscription.unsubscribe()
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [fetchDevices])

  const syncDevices = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await apiService.syncDevices()
      
      if (!response.success) {
        throw new Error(response.error || 'Failed to sync devices')
      }
      
      // Refresh devices from Supabase after sync
      await fetchDevices(false)
      
      return response.data
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to sync devices'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Manual refresh function that also resets the auto-refresh timer
  const manualRefresh = async () => {
    // Clear existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }
    
    // Fetch devices immediately with loading state
    await fetchDevices(false)
    
    // Restart auto-refresh timer
    intervalRef.current = setInterval(() => {
      fetchDevices(true) // Silent refresh for auto-updates
    }, 5000)
  }

  return {
    devices,
    loading,
    error,
    isRefreshing,
    refetch: manualRefresh,
    updateDevice,
    updateDevicePhone,
    syncDevices
  }
}