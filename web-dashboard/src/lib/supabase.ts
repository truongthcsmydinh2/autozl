import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types
export interface Device {
  id: string
  device_id: string
  name: string
  phone_number?: string
  status: 'idle' | 'running' | 'error' | 'offline'
  message?: string
  progress?: number
  current_message_id?: string
  created_at: string
  updated_at: string
}

export interface AutomationLog {
  id: string
  device_id?: string
  session_id?: string
  log_level: 'INFO' | 'ERROR' | 'DEBUG' | 'WARNING'
  message: string
  metadata?: any
  created_at: string
}

export interface ExecutionSession {
  id: string
  device_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at?: string
  completed_at?: string
  error_message?: string
  metadata?: any
  created_at: string
  updated_at: string
}

export interface ConversationTemplate {
  id: string
  name: string
  description?: string
  template_data: any
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AppConfiguration {
  id: string
  key: string
  value: any
  description?: string
  created_at: string
  updated_at: string
}