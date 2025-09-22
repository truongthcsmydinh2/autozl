/**
 * Automation flow management API routes
 * Handle automation flows, start/stop operations
 */
import { Router, type Request, type Response } from 'express'
import { spawn } from 'child_process'
import path from 'path'

const router = Router()

/**
 * Get all automation flows
 * GET /api/automation/flows
 */
router.get('/flows', async (req: Request, res: Response): Promise<void> => {
  try {
    const pythonScript = path.join(process.cwd(), 'core1.py')
    const python = spawn('python', [pythonScript, 'get_flows'])
    
    let data = ''
    python.stdout.on('data', (chunk) => {
      data += chunk.toString()
    })
    
    python.on('close', (code) => {
      if (code === 0) {
        try {
          const flows = JSON.parse(data)
          res.json({ success: true, data: flows })
        } catch (error) {
          res.status(500).json({ success: false, error: 'Failed to parse automation flows data' })
        }
      } else {
        res.status(500).json({ success: false, error: 'Failed to get automation flows' })
      }
    })
  } catch (error) {
    res.status(500).json({ success: false, error: 'Internal server error' })
  }
})

/**
 * Start an automation flow
 * POST /api/automation/flows/start
 */
router.post('/flows/start', async (req: Request, res: Response): Promise<void> => {
  try {
    const { flowId, parameters } = req.body
    
    if (!flowId) {
      res.status(400).json({ success: false, error: 'Flow ID is required' })
      return
    }
    
    const pythonScript = path.join(process.cwd(), 'core1.py')
    const args = ['start_flow', flowId]
    
    if (parameters) {
      args.push(JSON.stringify(parameters))
    }
    
    const python = spawn('python', [pythonScript, ...args])
    
    let data = ''
    python.stdout.on