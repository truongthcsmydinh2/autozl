/**
 * Device management API routes
 * Handle device connections, status, and control
 */
import { Router, type Request, type Response } from 'express'
import { spawn } from 'child_process'
import path from 'path'

const router = Router()

/**
 * Get all connected devices
 * GET /api/devices
 */
router.get('/', async (req: Request, res: Response): Promise<void> => {
  try {
    // Call Python script to get device data
    const pythonScript = path.join(process.cwd(), 'device_manager.py')
    const python = spawn('python', [pythonScript, 'get_devices'])
    
    let data = ''
    python.stdout.on('data', (chunk) => {
      data += chunk.toString()
    })
    
    python.on('close', (code) => {
      if (code === 0) {
        try {
          const devices = JSON.parse(data)
          res.json({ success: true, data: devices })
        } catch (error) {
          res.status(500).json({ success: false, error: 'Failed to parse device data' })
        }
      } else {
        res.status(500).json({ success: false, error: 'Failed to get device data' })
      }
    })
  } catch (error) {
    res.status(500).json({ success: false, error: 'Internal server error' })
  }
})

/**
 * Connect to a device
 * POST /api/devices/connect
 */
router.post('/connect', async (req: Request, res: Response): Promise<void> => {
  try {
    const { deviceId, deviceType } = req.body
    
    if (!deviceId || !deviceType) {
      res.status(400).json({ success: false, error: 'Device ID and type are required' })
      return
    }
    
    const pythonScript = path.join(process.cwd(), 'device_manager.py')
    const python = spawn('python', [pythonScript, 'connect_device', deviceId, deviceType])
    
    let data = ''
    python.stdout.on('data', (chunk) => {
      data += chunk.toString()
    })
    
    python.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(data)
          res.json({ success: true, data: result })
        } catch (error) {
          res.status(500).json({ success: false, error: 'Failed to parse response' })
        }
      } else {
        res.status(500).json({ success: false, error: 'Failed to connect device' })
      }
    })
  } catch (error) {
    res.status(500).json({ success: false, error: 'Internal server error' })
  }
})

/**
 * Disconnect from a device
 * POST /api/devices/disconnect
 */
router.post('/disconnect', async (req: Request, res: Response): Promise<void> => {
  try {
    const { deviceId } = req.body
    
    if (!deviceId) {
      res.status(400).json({ success: false, error: 'Device ID is required' })
      return
    }
    
    const pythonScript = path.join(process.cwd(), 'device_manager.py')
    const python = spawn('python', [pythonScript, 'disconnect_device', deviceId])
    
    let data = ''
    python.stdout.on('data', (chunk) => {
      data += chunk.toString()
    })
    
    python.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(data)
          res.json({ success: true, data: result })
        } catch (error) {
          res.status(500).json({ success: false, error: 'Failed to parse response' })
        }
      } else {
        res.status(500).json({ success: false, error: 'Failed to disconnect device' })
      }
    })
  } catch (error) {
    res.status(500).json({ success: false, error: 'Internal server error' })
  }
})

export default router