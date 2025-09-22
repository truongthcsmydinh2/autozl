-- Conversation Management System Migration
-- Creates tables for device pairs, conversations, and summaries

-- Device Pairs Table
CREATE TABLE IF NOT EXISTS device_pairs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_a VARCHAR(50) NOT NULL,
    device_b VARCHAR(50) NOT NULL,
    pair_hash VARCHAR(64) UNIQUE NOT NULL, -- MD5(sorted(deviceA, deviceB))
    temp_pair_id VARCHAR(100) UNIQUE, -- Format: pair_temp_{timestamp}_{random}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations Table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pair_id UUID REFERENCES device_pairs(id) ON DELETE CASCADE,
    temp_conversation_id VARCHAR(100) UNIQUE, -- Format: conv_temp_{timestamp}_{random}
    content JSONB, -- Temporary storage for messages and metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversation Summaries Table
CREATE TABLE IF NOT EXISTS conversation_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pair_id UUID REFERENCES device_pairs(id) ON DELETE CASCADE,
    noidung TEXT NOT NULL,
    hoancanh TEXT NOT NULL,
    so_cau INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_device_pairs_hash ON device_pairs(pair_hash);
CREATE INDEX IF NOT EXISTS idx_device_pairs_temp_id ON device_pairs(temp_pair_id);
CREATE INDEX IF NOT EXISTS idx_conversations_pair ON conversations(pair_id);
CREATE INDEX IF NOT EXISTS idx_conversations_temp_id ON conversations(temp_conversation_id);
CREATE INDEX IF NOT EXISTS idx_summaries_pair_created ON conversation_summaries(pair_id, created_at DESC);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_device_pairs_updated_at BEFORE UPDATE ON device_pairs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions to anon and authenticated roles
GRANT SELECT, INSERT, UPDATE, DELETE ON device_pairs TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON conversations TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON conversation_summaries TO anon, authenticated;

-- Grant usage on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Row Level Security (RLS) policies
ALTER TABLE device_pairs ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_summaries ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (allow all for now, can be refined later)
CREATE POLICY "Allow all operations on device_pairs" ON device_pairs
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on conversations" ON conversations
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on conversation_summaries" ON conversation_summaries
    FOR ALL USING (true) WITH CHECK (true);

-- Function to cleanup old summaries (keep only 3 latest per pair)
CREATE OR REPLACE FUNCTION cleanup_old_summaries(target_pair_id UUID)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM conversation_summaries 
    WHERE pair_id = target_pair_id 
    AND id NOT IN (
        SELECT id FROM conversation_summaries 
        WHERE pair_id = target_pair_id 
        ORDER BY created_at DESC 
        LIMIT 3
    );
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to find or create device pair
CREATE OR REPLACE FUNCTION find_or_create_device_pair(
    device_a_param VARCHAR(50),
    device_b_param VARCHAR(50)
)
RETURNS UUID AS $$
DECLARE
    pair_id UUID;
    sorted_devices TEXT[];
    pair_hash_value VARCHAR(64);
    temp_pair_id_value VARCHAR(100);
BEGIN
    -- Sort devices to ensure AB = BA
    IF device_a_param <= device_b_param THEN
        sorted_devices := ARRAY[device_a_param, device_b_param];
    ELSE
        sorted_devices := ARRAY[device_b_param, device_a_param];
    END IF;
    
    -- Generate hash
    pair_hash_value := md5(array_to_string(sorted_devices, '_'));
    
    -- Try to find existing pair
    SELECT id INTO pair_id FROM device_pairs WHERE pair_hash = pair_hash_value;
    
    -- Create new pair if not found
    IF pair_id IS NULL THEN
        temp_pair_id_value := 'pair_temp_' || extract(epoch from now())::bigint || '_' || substr(md5(random()::text), 1, 8);
        
        INSERT INTO device_pairs (device_a, device_b, pair_hash, temp_pair_id)
        VALUES (sorted_devices[1], sorted_devices[2], pair_hash_value, temp_pair_id_value)
        RETURNING id INTO pair_id;
    END IF;
    
    RETURN pair_id;
END;
$$ LANGUAGE plpgsql;

-- Function to generate temporary conversation ID
CREATE OR REPLACE FUNCTION generate_temp_conversation_id()
RETURNS VARCHAR(100) AS $$
BEGIN
    RETURN 'conv_temp_' || extract(epoch from now())::bigint || '_' || substr(md5(random()::text), 1, 8);
END;
$$ LANGUAGE plpgsql;

COMMIT;