# Kế hoạch Migration từ JSON sang Supabase

## 1. Phân tích Dữ liệu Hiện tại

### 1.1 Các File JSON Hiện tại
Hệ thống hiện tại sử dụng các file JSON sau để lưu trữ dữ liệu:

| File | Mục đích | Cấu trúc dữ liệu |
|------|----------|------------------|
| `phone_mapping.json` | Ánh xạ device IP/ID với số điện thoại | `{"phone_mapping": {"device_id": "phone_number"}, "timestamp": number, "created_by": string}` |
| `status.json` | Trạng thái thực thi automation của từng device | `{"devices": {"device_id": {"status", "message", "progress", "current_message_id", "last_update", "timestamp"}}, "overall_status": string, "last_update": number}` |
| `conversations.json` | Template hội thoại cho automation | `[{"group_id": number, "messages": [{"content": string, "delay": number, "device_role": string}]}]` |
| `conversation_data.json` | Dữ liệu hội thoại thực tế được thực thi | `{"timestamp": string, "total_pairs": number, "conversations": {"pair_id": {"devices": [string], "conversation": [{"message_id": number, "device_number": number, "content": string}]}}}` |
| `config/app_config.json` | Cấu hình ứng dụng | `{"config": {"app": {}, "device": {}, "flow": {}, "ui": {}, "logging": {}}}` |

### 1.2 Patterns Truy cập Dữ liệu
- **Read-heavy**: Đọc configuration, phone mapping, conversation templates
- **Write-heavy**: Cập nhật status, logs thực thi
- **Real-time**: Status updates cần hiển thị real-time trên dashboard
- **Concurrent**: Nhiều devices cập nhật status đồng thời

## 2. Thiết kế Schema Supabase

### 2.1 Bảng Devices
```sql
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(50) UNIQUE NOT NULL, -- IP:port hoặc device identifier
    phone_number VARCHAR(20),
    status VARCHAR(20) DEFAULT 'idle', -- idle, running, completed, error
    message TEXT,
    progress INTEGER DEFAULT 0,
    current_message_id INTEGER,
    last_update TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.2 Bảng Conversation Templates
```sql
CREATE TABLE conversation_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id INTEGER NOT NULL,
    name VARCHAR(100),
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID REFERENCES conversation_templates(id) ON DELETE CASCADE,
    sequence_order INTEGER NOT NULL,
    content TEXT NOT NULL,
    delay_seconds INTEGER DEFAULT 2,
    device_role VARCHAR(20) NOT NULL, -- device_a, device_b
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.3 Bảng Execution Sessions
```sql
CREATE TABLE execution_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_name VARCHAR(100),
    template_id UUID REFERENCES conversation_templates(id),
    total_pairs INTEGER,
    overall_status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, error
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE execution_pairs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES execution_sessions(id) ON DELETE CASCADE,
    pair_name VARCHAR(50) NOT NULL,
    device_1_id UUID REFERENCES devices(id),
    device_2_id UUID REFERENCES devices(id),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE execution_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pair_id UUID REFERENCES execution_pairs(id) ON DELETE CASCADE,
    message_id INTEGER NOT NULL,
    device_number INTEGER NOT NULL, -- 1 or 2
    content TEXT NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.4 Bảng Configuration
```sql
CREATE TABLE app_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.5 Bảng Logs
```sql
CREATE TABLE automation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES devices(id),
    session_id UUID REFERENCES execution_sessions(id),
    log_level VARCHAR(10) NOT NULL, -- INFO, ERROR, DEBUG, WARNING
    message TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.6 Indexes và Constraints
```sql
-- Indexes for performance
CREATE INDEX idx_devices_device_id ON devices(device_id);
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_last_update ON devices(last_update DESC);
CREATE INDEX idx_conversation_messages_template_id ON conversation_messages(template_id);
CREATE INDEX idx_conversation_messages_sequence ON conversation_messages(template_id, sequence_order);
CREATE INDEX idx_execution_pairs_session_id ON execution_pairs(session_id);
CREATE INDEX idx_execution_messages_pair_id ON execution_messages(pair_id);
CREATE INDEX idx_automation_logs_device_id ON automation_logs(device_id);
CREATE INDEX idx_automation_logs_created_at ON automation_logs(created_at DESC);

-- RLS Policies
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE execution_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE execution_pairs ENABLE ROW LEVEL SECURITY;
ALTER TABLE execution_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE app_configurations ENABLE ROW LEVEL SECURITY;
ALTER TABLE automation_logs ENABLE ROW LEVEL SECURITY;

-- Grant permissions
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO authenticated;
```

## 3. Chiến lược Migration

### Phase 1: Setup Supabase Project và Schema
**Timeline: 1-2 ngày**

1. **Tạo Supabase Project**
   - Đăng ký tài khoản Supabase
   - Tạo project mới
   - Lấy API keys và database URL

2. **Thiết lập Database Schema**
   - Chạy các script SQL tạo bảng
   - Thiết lập RLS policies
   - Tạo indexes cho performance

3. **Cấu hình Environment**
   - Tạo file `.env` với Supabase credentials
   - Cài đặt Supabase client libraries

### Phase 2: Tạo Database Access Layer
**Timeline: 2-3 ngày**

1. **Python Database Layer**
   ```python
   # core/database.py
   from supabase import create_client, Client
   import os
   
   class SupabaseManager:
       def __init__(self):
           url = os.environ.get("SUPABASE_URL")
           key = os.environ.get("SUPABASE_ANON_KEY")
           self.supabase: Client = create_client(url, key)
   ```

2. **Device Management Layer**
   ```python
   # core/device_repository.py
   class DeviceRepository:
       def get_device_by_id(self, device_id: str)
       def update_device_status(self, device_id: str, status: dict)
       def get_all_devices(self)
       def create_device(self, device_data: dict)
   ```

3. **Configuration Management Layer**
   ```python
   # core/config_repository.py
   class ConfigRepository:
       def get_config(self, key: str)
       def update_config(self, key: str, value: dict)
       def get_all_configs(self)
   ```

### Phase 3: Migration Core Functions
**Timeline: 3-4 ngày**

1. **Migrate Device Management**
   - Cập nhật `core/device_manager.py`
   - Thay thế JSON reads/writes bằng Supabase calls
   - Implement real-time status updates

2. **Migrate Configuration Management**
   - Cập nhật `core/config_manager.py`
   - Load config từ Supabase thay vì JSON
   - Implement config caching

3. **Migrate Conversation Management**
   - Tạo `core/conversation_repository.py`
   - Load conversation templates từ database
   - Implement conversation execution tracking

### Phase 4: Update Web Dashboard
**Timeline: 2-3 ngày**

1. **Frontend Supabase Integration**
   ```javascript
   // lib/supabase.js
   import { createClient } from '@supabase/supabase-js'
   
   const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
   const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
   
   export const supabase = createClient(supabaseUrl, supabaseAnonKey)
   ```

2. **Real-time Data Subscriptions**
   ```javascript
   // hooks/useDeviceStatus.js
   const subscription = supabase
     .channel('device-status')
     .on('postgres_changes', {
       event: 'UPDATE',
       schema: 'public',
       table: 'devices'
     }, (payload) => {
       setDevices(prev => updateDeviceInList(prev, payload.new))
     })
     .subscribe()
   ```

3. **API Endpoints Update**
   - Thay thế mock data bằng Supabase queries
   - Implement real-time dashboard updates
   - Add error handling và loading states

### Phase 5: Remove JSON Dependencies
**Timeline: 1 ngày**

1. **Data Migration Script**
   ```python
   # scripts/migrate_json_to_supabase.py
   def migrate_phone_mapping():
   def migrate_device_status():
   def migrate_conversations():
   def migrate_configurations():
   ```

2. **Cleanup**
   - Remove JSON file dependencies
   - Update documentation
   - Remove old backup files

## 4. Implementation Plan

### 4.1 Required Dependencies

**Python Backend:**
```txt
supabase==2.3.4
python-dotenv==1.0.0
```

**Frontend Dashboard:**
```json
{
  "@supabase/supabase-js": "^2.39.0",
  "@supabase/auth-helpers-nextjs": "^0.8.7"
}
```

### 4.2 Environment Configuration

```env
# .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# .env.local (for Next.js)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### 4.3 Data Migration Scripts

```python
# scripts/migrate_data.py
import json
from core.database import SupabaseManager

def migrate_existing_data():
    """Migrate all existing JSON data to Supabase"""
    db = SupabaseManager()
    
    # Migrate phone mapping
    with open('phone_mapping.json', 'r') as f:
        phone_data = json.load(f)
    
    for device_id, phone_number in phone_data['phone_mapping'].items():
        db.supabase.table('devices').upsert({
            'device_id': device_id,
            'phone_number': phone_number
        }).execute()
    
    # Migrate device status
    with open('status.json', 'r') as f:
        status_data = json.load(f)
    
    for device_id, status in status_data['devices'].items():
        db.supabase.table('devices').update({
            'status': status['status'],
            'message': status['message'],
            'progress': status['progress'],
            'current_message_id': status['current_message_id'],
            'last_update': status['last_update']
        }).eq('device_id', device_id).execute()
```

### 4.4 Real-time Features Integration

**Python Real-time Updates:**
```python
# core/realtime_manager.py
class RealtimeManager:
    def __init__(self, supabase_manager):
        self.db = supabase_manager
    
    def update_device_status(self, device_id: str, status_data: dict):
        """Update device status with real-time broadcast"""
        result = self.db.supabase.table('devices').update(status_data).eq('device_id', device_id).execute()
        return result
```

**Frontend Real-time Subscriptions:**
```javascript
// components/DeviceStatusMonitor.jsx
import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'

export default function DeviceStatusMonitor() {
  const [devices, setDevices] = useState([])
  
  useEffect(() => {
    // Initial load
    loadDevices()
    
    // Real-time subscription
    const subscription = supabase
      .channel('device-updates')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'devices'
      }, (payload) => {
        handleDeviceUpdate(payload)
      })
      .subscribe()
    
    return () => {
      subscription.unsubscribe()
    }
  }, [])
  
  const loadDevices = async () => {
    const { data } = await supabase.from('devices').select('*')
    setDevices(data || [])
  }
  
  const handleDeviceUpdate = (payload) => {
    if (payload.eventType === 'UPDATE') {
      setDevices(prev => prev.map(device => 
        device.id === payload.new.id ? payload.new : device
      ))
    }
  }
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {devices.map(device => (
        <DeviceCard key={device.id} device={device} />
      ))}
    </div>
  )
}
```

## 5. Testing Strategy

### 5.1 Unit Tests
- Test database repository functions
- Test data migration scripts
- Test real-time update mechanisms

### 5.2 Integration Tests
- Test Python-Supabase integration
- Test Frontend-Supabase integration
- Test real-time data flow

### 5.3 Performance Tests
- Test concurrent device status updates
- Test real-time subscription performance
- Test database query performance

## 6. Rollback Plan

### 6.1 Backup Strategy
- Backup all existing JSON files
- Export Supabase data before major changes
- Maintain parallel JSON writes during transition period

### 6.2 Rollback Procedure
1. Stop all automation processes
2. Restore JSON files from backup
3. Revert code changes to use JSON storage
4. Restart automation system

## 7. Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1 | 1-2 ngày | Supabase project setup, database schema |
| Phase 2 | 2-3 ngày | Python database access layer |
| Phase 3 | 3-4 ngày | Core function migration |
| Phase 4 | 2-3 ngày | Web dashboard update |
| Phase 5 | 1 ngày | JSON cleanup, final testing |
| **Total** | **9-13 ngày** | **Complete migration to Supabase** |

## 8. Success Criteria

- ✅ Tất cả dữ liệu được migrate thành công
- ✅ Real-time updates hoạt động ổn định
- ✅ Performance không giảm so với JSON storage
- ✅ Web dashboard hiển thị data real-time
- ✅ Automation system hoạt động bình thường
- ✅ Không có data loss trong quá trình migration
- ✅ Rollback plan được test và sẵn sàng

Việc migration này sẽ mang lại những lợi ích lớn:
- **Scalability**: Có thể handle nhiều devices và concurrent operations
- **Real-time**: Dashboard updates ngay lập tức
- **Reliability**: Database ACID compliance, backup tự động
- **Performance**: Optimized queries, indexing
- **Maintainability**: Structured data, easier to extend features