import { useState, useEffect } from 'react'
import { supabase, AutomationLog } from '../lib/supabase'

export function useLogs(limit: number = 100) {
  const [logs, setLogs] = useState<AutomationLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchLogs = async () => {
    try {
      setLoading(true)
      const { data, error } = await supabase
        .from('automation_logs')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(limit)

      if (error) throw error
      setLogs(data || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const fetchLogsByLevel = async (level: string) => {
    try {
      setLoading(true)
      const { data, error } = await supabase
        .from('automation_logs')
        .select('*')
        .eq('log_level', level)
        .order('created_at', { ascending: false })
        .limit(limit)

      if (error) throw error
      setLogs(data || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch logs by level')
    } finally {
      setLoading(false)
    }
  }

  const fetchLogsByDevice = async (deviceId: string) => {
    try {
      setLoading(true)
      const { data, error } = await supabase
        .from('automation_logs')
        .select('*')
        .eq('device_id', deviceId)
        .order('created_at', { ascending: false })
        .limit(limit)

      if (error) throw error
      setLogs(data || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch logs by device')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs()

    // Subscribe to real-time changes
    const subscription = supabase
      .channel('automation_logs')
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'automation_logs'
      }, () => {
        fetchLogs()
      })
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }, [limit])

  return {
    logs,
    loading,
    error,
    refetch: fetchLogs,
    fetchLogsByLevel,
    fetchLogsByDevice
  }
}