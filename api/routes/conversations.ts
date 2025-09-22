/**
 * Conversation management API routes
 * Handle device pairs, conversations, and summaries
 */
import { Router, Request, Response } from 'express'
import { createClient } from '@supabase/supabase-js'
import { ConversationManager } from '../utils/ConversationManager'

const router = Router()

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL!
const supabaseKey = process.env.SUPABASE_ANON_KEY!
const supabase = createClient(supabaseUrl, supabaseKey)

// Initialize ConversationManager
const conversationManager = new ConversationManager(supabase)

/**
 * Create device pair
 * POST /api/conversations/pairs/create
 */
router.post('/pairs/create', async (req: Request, res: Response): Promise<void> => {
  try {
    const { deviceA, deviceB } = req.body
    
    if (!deviceA || !deviceB) {
      res.status(400).json({ 
        success: false, 
        error: 'Both deviceA and deviceB are required' 
      })
      return
    }
    
    // Create or find existing pair
    const result = await conversationManager.createDevicePair(deviceA, deviceB)
    
    if (result.success) {
      res.json({ 
        success: true, 
        data: result.data 
      })
    } else {
      res.status(500).json({ 
        success: false, 
        error: result.error 
      })
    }
  } catch (error) {
    console.error('Error creating device pair:', error)
    res.status(500).json({ 
      success: false, 
      error: 'Internal server error' 
    })
  }
})

/**
 * Get all device pairs
 * GET /api/conversations/pairs
 */
router.get('/pairs', async (req: Request, res: Response): Promise<void> => {
  try {
    const result = await conversationManager.getAllDevicePairs()
    
    if (result.success) {
      res.json({ 
        success: true, 
        data: result.data || [] 
      })
    } else {
      res.status(500).json({ 
        success: false, 
        error: result.error 
      })
    }
  } catch (error) {
    console.error('Error fetching device pairs:', error)
    res.status(500).json({ 
      success: false, 
      error: 'Internal server error' 
    })
  }
})

/**
 * Process conversation input
 * POST /api/conversations/input
 */
router.post('/input', async (req: Request, res: Response): Promise<void> => {
  try {
    const { pairId, jsonData } = req.body
    
    if (!pairId || !jsonData) {
      res.status(400).json({ 
        success: false, 
        error: 'Both pairId and jsonData are required' 
      })
      return
    }
    
    // Process conversation data (validation is done inside)
    const result = await conversationManager.processConversationInput(pairId, jsonData)
    
    if (result.success) {
      res.json({ 
        success: true, 
        data: result.data 
      })
    } else {
      res.status(400).json({ 
        success: false, 
        error: result.error 
      })
    }
  } catch (error) {
    console.error('Error processing conversation input:', error)
    res.status(500).json({ 
      success: false, 
      error: 'Internal server error' 
    })
  }
})

/**
 * Get latest summaries for a device pair
 * GET /api/conversations/summaries/latest/:pairId
 */
router.get('/summaries/latest/:pairId', async (req: Request, res: Response): Promise<void> => {
  try {
    const { pairId } = req.params
    const limit = parseInt(req.query.limit as string) || 3
    
    if (!pairId) {
      res.status(400).json({ 
        success: false, 
        error: 'Pair ID is required' 
      })
      return
    }
    
    const result = await conversationManager.summaryManager.getLatestSummaries(pairId, limit)
    
    if (result.success) {
      res.json({ 
        success: true, 
        data: result.data 
      })
    } else {
      res.status(500).json({ 
        success: false, 
        error: result.error 
      })
    }
  } catch (error) {
    console.error('Error fetching summaries:', error)
    res.status(500).json({ 
      success: false, 
      error: 'Internal server error' 
    })
  }
})

/**
 * Get conversation by temporary ID
 * GET /api/conversations/temp/:tempId
 */
router.get('/temp/:tempId', async (req: Request, res: Response): Promise<void> => {
  try {
    const { tempId } = req.params
    
    if (!tempId) {
      res.status(400).json({ 
        success: false, 
        error: 'Temporary ID is required' 
      })
      return
    }
    
    const conversation = conversationManager.getTemporaryConversation(tempId)
    
    if (conversation) {
      res.json({ 
        success: true, 
        data: conversation 
      })
    } else {
      res.status(404).json({ 
        success: false, 
        error: 'Conversation not found' 
      })
    }
  } catch (error) {
    console.error('Error fetching temporary conversation:', error)
    res.status(500).json({ 
      success: false, 
      error: 'Internal server error' 
    })
  }
})

/**
 * Clear temporary conversation data
 * DELETE /api/conversations/temp/:tempId
 */
router.delete('/temp/:tempId', async (req: Request, res: Response): Promise<void> => {
  try {
    const { tempId } = req.params
    
    if (!tempId) {
      res.status(400).json({ 
        success: false, 
        error: 'Temporary ID is required' 
      })
      return
    }
    
    conversationManager.clearTemporaryConversation(tempId)
    
    res.json({ 
      success: true, 
      message: 'Temporary conversation cleared' 
    })
  } catch (error) {
    console.error('Error clearing temporary conversation:', error)
    res.status(500).json({ 
      success: false, 
      error: 'Internal server error' 
    })
  }
})

export default router