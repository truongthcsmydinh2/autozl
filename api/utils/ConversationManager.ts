import { SupabaseClient } from '@supabase/supabase-js'
import crypto from 'crypto'

export interface DevicePair {
  id?: string
  device_a: string
  device_b: string
  pair_hash: string
  temp_pair_id: string
  created_at?: string
}

export interface ConversationMessage {
  sender: string
  text: string
  timestamp?: string
}

export interface ConversationContent {
  messages: ConversationMessage[]
  metadata?: Record<string, any>
}

export interface ConversationSummary {
  id?: string
  noidung: string
  hoancanh: string
  so_cau: number
  created_at?: string
}

export interface ConversationInput {
  content: ConversationContent
  summary: ConversationSummary
}

export interface ValidationResult {
  isValid: boolean
  errors: string[]
}

export class ConversationValidator {
  static validateConversationData(data: any): ValidationResult {
    const errors: string[] = []
    
    try {
      // Check top-level structure
      if (!data || typeof data !== 'object') {
        errors.push('Input must be a JSON object')
        return { isValid: false, errors }
      }
      
      if (!data.content || !data.summary) {
        errors.push('Missing required fields: content and summary')
        return { isValid: false, errors }
      }
      
      // Validate content structure
      const content = data.content
      if (!content || typeof content !== 'object') {
        errors.push('Content must be an object')
      } else {
        if (!Array.isArray(content.messages)) {
          errors.push('Content must contain messages array')
        } else {
          // Validate message structure
          content.messages.forEach((message: any, index: number) => {
            if (!message || typeof message !== 'object') {
              errors.push(`Message ${index} must be an object`)
            } else {
              if (!message.sender || typeof message.sender !== 'string') {
                errors.push(`Message ${index} missing or invalid sender field`)
              }
              if (!message.text || typeof message.text !== 'string') {
                errors.push(`Message ${index} missing or invalid text field`)
              }
            }
          })
        }
      }
      
      // Validate summary structure
      const summary = data.summary
      if (!summary || typeof summary !== 'object') {
        errors.push('Summary must be an object')
      } else {
        if (!summary.noidung || typeof summary.noidung !== 'string') {
          errors.push('Summary missing or invalid noidung field')
        }
        if (!summary.hoancanh || typeof summary.hoancanh !== 'string') {
          errors.push('Summary missing or invalid hoancanh field')
        }
        if (typeof summary.so_cau !== 'number') {
          errors.push('Summary missing or invalid so_cau field')
        }
      }
      
      return { isValid: errors.length === 0, errors }
      
    } catch (error) {
      errors.push(`Validation error: ${error instanceof Error ? error.message : 'Unknown error'}`)
      return { isValid: false, errors }
    }
  }
}

export class DevicePairManager {
  private supabase: SupabaseClient
  private tempMapping: Map<string, string> = new Map() // temp_pair_id -> pair_id
  private conversationMapping: Map<string, string> = new Map() // temp_conversation_id -> conversation_id
  
  constructor(supabase: SupabaseClient) {
    this.supabase = supabase
  }
  
  generateTempPairId(): string {
    const timestamp = Date.now()
    const randomStr = Math.random().toString(36).substring(2, 10)
    return `pair_temp_${timestamp}_${randomStr}`
  }
  
  generateTempConversationId(): string {
    const timestamp = Date.now()
    const randomStr = Math.random().toString(36).substring(2, 10)
    return `conv_temp_${timestamp}_${randomStr}`
  }
  
  createPairHash(deviceA: string, deviceB: string): string {
    // Sort devices to ensure AB = BA
    const devices = [deviceA, deviceB].sort()
    return crypto.createHash('md5').update(devices.join('_')).digest('hex')
  }
  
  createPairId(deviceA: string, deviceB: string): string {
    // Sort devices to ensure consistent pair ID format: pair_device1_device2
    const devices = [deviceA, deviceB].sort()
    return `pair_${devices.join('_')}`
  }
  
  async findOrCreatePair(deviceA: string, deviceB: string): Promise<DevicePair> {
    try {
      const pairId = this.createPairId(deviceA, deviceB)
      const pairHash = this.createPairHash(deviceA, deviceB)
      
      // Try to find existing pair by pair_id first, then fallback to pair_hash
      let existingPair = null
      let findError = null
      
      // First try to find by pair_id
      const { data: pairByIdData, error: pairByIdError } = await this.supabase
        .from('device_pairs')
        .select('*')
        .eq('id', pairId)
        .single()
      
      if (pairByIdData && !pairByIdError) {
        existingPair = pairByIdData
      } else {
        // Fallback to pair_hash for backward compatibility
        const { data: pairByHashData, error: pairByHashError } = await this.supabase
          .from('device_pairs')
          .select('*')
          .eq('pair_hash', pairHash)
          .single()
        
        if (pairByHashData && !pairByHashError) {
          existingPair = pairByHashData
        }
      }
      
      if (existingPair) {
        return {
          id: existingPair.id,
          device_a: existingPair.device_a,
          device_b: existingPair.device_b,
          pair_hash: existingPair.pair_hash,
          temp_pair_id: existingPair.temp_pair_id,
          created_at: existingPair.created_at
        }
      }
      
      // Create new pair with standardized pair_id
      const tempPairId = this.generateTempPairId()
      const { data: newPair, error: createError } = await this.supabase
        .from('device_pairs')
        .upsert({
          id: pairId,
          device_a: deviceA,
          device_b: deviceB,
          pair_hash: pairHash,
          temp_pair_id: tempPairId
        })
        .select()
        .single()
      
      if (createError || !newPair) {
        throw new Error(`Failed to create device pair: ${createError?.message}`)
      }
      
      return {
        id: newPair.id,
        device_a: newPair.device_a,
        device_b: newPair.device_b,
        pair_hash: newPair.pair_hash,
        temp_pair_id: newPair.temp_pair_id,
        created_at: newPair.created_at
      }
      
    } catch (error) {
      console.error('Error finding/creating device pair:', error)
      throw error
    }
  }
  
  async getPairById(pairId: string): Promise<DevicePair | null> {
    try {
      const { data, error } = await this.supabase
        .from('device_pairs')
        .select('*')
        .eq('id', pairId)
        .single()
      
      if (error || !data) {
        return null
      }
      
      return {
        id: data.id,
        device_a: data.device_a,
        device_b: data.device_b,
        pair_hash: data.pair_hash,
        temp_pair_id: data.temp_pair_id,
        created_at: data.created_at
      }
      
    } catch (error) {
      console.error('Error getting pair by ID:', error)
      return null
    }
  }

  async getPairByTempId(tempPairId: string): Promise<DevicePair | null> {
    try {
      const { data, error } = await this.supabase
        .from('device_pairs')
        .select('*')
        .eq('temp_pair_id', tempPairId)
        .single()
      
      if (error || !data) {
        return null
      }
      
      return {
        id: data.id,
        device_a: data.device_a,
        device_b: data.device_b,
        pair_hash: data.pair_hash,
        temp_pair_id: data.temp_pair_id,
        created_at: data.created_at
      }
      
    } catch (error) {
      console.error('Error getting pair by temp ID:', error)
      return null
    }
  }

  async getPairByIdentifier(pairIdentifier: string): Promise<DevicePair | null> {
    try {
      // Try to get pair by standardized pair_id first
      let pair = await this.getPairById(pairIdentifier)
      if (!pair) {
        // Fallback to temp_pair_id for backward compatibility
        pair = await this.getPairByTempId(pairIdentifier)
      }
      return pair
    } catch (error) {
      console.error('Error getting pair by identifier:', error)
      return null
    }
  }
}

export class SummaryManager {
  private static readonly MAX_SUMMARIES_PER_PAIR = 3
  private supabase: SupabaseClient
  
  constructor(supabase: SupabaseClient) {
    this.supabase = supabase
  }
  
  async saveSummary(pairId: string, summary: ConversationSummary): Promise<string> {
    try {
      // Insert new summary
      const { data, error } = await this.supabase
        .from('conversation_summaries')
        .insert({
          pair_id: pairId,
          noidung: summary.noidung,
          hoancanh: summary.hoancanh,
          so_cau: summary.so_cau
        })
        .select()
        .single()
      
      if (error || !data) {
        throw new Error(`Failed to save summary: ${error?.message}`)
      }
      
      const summaryId = data.id
      
      // Cleanup old summaries
      await this.cleanupOldSummaries(pairId)
      
      console.log(`Summary saved and cleanup completed for pair ${pairId}`)
      return summaryId
      
    } catch (error) {
      console.error('Error saving summary:', error)
      throw error
    }
  }
  
  async getLatestSummaries(pairId: string, limit: number = 3): Promise<{ success: boolean; data?: ConversationSummary[]; error?: string }> {
    try {
      const { data, error } = await this.supabase
        .from('conversation_summaries')
        .select('*')
        .eq('pair_id', pairId)
        .order('created_at', { ascending: false })
        .limit(limit)
      
      if (error) {
        return { success: false, error: error.message }
      }
      
      const summaries: ConversationSummary[] = (data || []).map(item => ({
        id: item.id,
        noidung: item.noidung,
        hoancanh: item.hoancanh,
        so_cau: item.so_cau,
        created_at: item.created_at
      }))
      
      return { success: true, data: summaries }
      
    } catch (error) {
      console.error('Error getting latest summaries:', error)
      return { success: false, error: 'Internal server error' }
    }
  }
  
  private async cleanupOldSummaries(pairId: string): Promise<void> {
    try {
      // Get all summaries for this pair, ordered by creation date (newest first)
      const { data: summaries, error } = await this.supabase
        .from('conversation_summaries')
        .select('id')
        .eq('pair_id', pairId)
        .order('created_at', { ascending: false })
      
      if (error || !summaries) {
        console.error('Error fetching summaries for cleanup:', error)
        return
      }
      
      // If we have more than MAX_SUMMARIES_PER_PAIR, delete the oldest ones
      if (summaries.length > SummaryManager.MAX_SUMMARIES_PER_PAIR) {
        const summariesToDelete = summaries.slice(SummaryManager.MAX_SUMMARIES_PER_PAIR)
        const idsToDelete = summariesToDelete.map(s => s.id)
        
        const { error: deleteError } = await this.supabase
          .from('conversation_summaries')
          .delete()
          .in('id', idsToDelete)
        
        if (deleteError) {
          console.error('Error deleting old summaries:', deleteError)
        } else {
          console.log(`Deleted ${idsToDelete.length} old summaries for pair ${pairId}`)
        }
      }
      
    } catch (error) {
      console.error('Error in cleanup process:', error)
    }
  }
}

export class ConversationManager {
  private supabase: SupabaseClient
  private pairManager: DevicePairManager
  public summaryManager: SummaryManager
  public validator: ConversationValidator
  private temporaryContent: Map<string, ConversationContent> = new Map()
  
  constructor(supabase: SupabaseClient) {
    this.supabase = supabase
    this.pairManager = new DevicePairManager(supabase)
    this.summaryManager = new SummaryManager(supabase)
    this.validator = new ConversationValidator()
  }
  
  async processConversationInput(pairId: string, conversationData: any): Promise<{ success: boolean; data?: any; error?: string }> {
    try {
      // Validate input
      const validation = ConversationValidator.validateConversationData(conversationData)
      if (!validation.isValid) {
        return {
          success: false,
          error: `Invalid JSON format: ${validation.errors.join(', ')}`
        }
      }
      
      // Get pair by standardized pair_id or temp_pair_id
      const pair = await this.pairManager.getPairByIdentifier(pairId)
      if (!pair || !pair.id) {
        return {
          success: false,
          error: 'Device pair not found'
        }
      }
      
      // Generate temporary conversation ID
      const tempConversationId = this.pairManager.generateTempConversationId()
      
      // Store content temporarily
      this.temporaryContent.set(tempConversationId, conversationData.content)
      
      // Save summary persistently
      const summaryId = await this.summaryManager.saveSummary(pair.id, conversationData.summary)
      
      console.log(`Conversation processed successfully for pair ${pairId}`)
      
      return {
        success: true,
        data: {
          pair_id: pair.id,
          temp_pair_id: pair.temp_pair_id,
          temp_conversation_id: tempConversationId,
          summary_id: summaryId,
          message: 'Conversation data processed successfully'
        }
      }
      
    } catch (error) {
      console.error('Error processing conversation input:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Internal server error'
      }
    }
  }
  
  getTemporaryConversation(tempConversationId: string): ConversationContent | null {
    return this.temporaryContent.get(tempConversationId) || null
  }
  
  clearTemporaryConversation(tempConversationId: string): boolean {
    return this.temporaryContent.delete(tempConversationId)
  }
  
  async createDevicePair(deviceA: string, deviceB: string): Promise<{ success: boolean; data?: DevicePair; error?: string }> {
    try {
      const pair = await this.pairManager.findOrCreatePair(deviceA, deviceB)
      return { success: true, data: pair }
    } catch (error) {
      console.error('Error creating device pair:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Internal server error'
      }
    }
  }
  
  async getAllDevicePairs(): Promise<{ success: boolean; data?: DevicePair[]; error?: string }> {
    try {
      const { data, error } = await this.supabase
        .from('device_pairs')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) {
        return { success: false, error: error.message }
      }
      
      const pairs: DevicePair[] = (data || []).map(item => ({
        id: item.id,
        device_a: item.device_a,
        device_b: item.device_b,
        pair_hash: item.pair_hash,
        temp_pair_id: item.temp_pair_id,
        created_at: item.created_at
      }))
      
      return { success: true, data: pairs }
      
    } catch (error) {
      console.error('Error getting device pairs:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Internal server error'
      }
    }
  }
}