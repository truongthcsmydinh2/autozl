-- Update device_pairs table to use text ID instead of UUID
-- This allows standardized pair IDs like 'pair_10_33'

-- First, drop foreign key constraints
ALTER TABLE conversations DROP CONSTRAINT IF EXISTS conversations_pair_id_fkey;
ALTER TABLE conversation_summaries DROP CONSTRAINT IF EXISTS conversation_summaries_pair_id_fkey;

-- Change the ID column type from UUID to TEXT
ALTER TABLE device_pairs 
ALTER COLUMN id DROP DEFAULT,
ALTER COLUMN id TYPE TEXT USING id::TEXT;

-- Update conversations table pair_id column to TEXT
ALTER TABLE conversations 
ALTER COLUMN pair_id TYPE TEXT USING pair_id::TEXT;

-- Update conversation_summaries table pair_id column to TEXT
ALTER TABLE conversation_summaries 
ALTER COLUMN pair_id TYPE TEXT USING pair_id::TEXT;

-- Recreate foreign key constraints
ALTER TABLE conversations 
ADD CONSTRAINT conversations_pair_id_fkey 
FOREIGN KEY (pair_id) REFERENCES device_pairs(id) ON DELETE CASCADE;

ALTER TABLE conversation_summaries 
ADD CONSTRAINT conversation_summaries_pair_id_fkey 
FOREIGN KEY (pair_id) REFERENCES device_pairs(id) ON DELETE CASCADE;

-- Add index for better performance on text-based lookups
CREATE INDEX IF NOT EXISTS idx_device_pairs_id ON device_pairs(id);
CREATE INDEX IF NOT EXISTS idx_conversations_pair_id ON conversations(pair_id);
CREATE INDEX IF NOT EXISTS idx_conversation_summaries_pair_id ON conversation_summaries(pair_id);