-- Add custom_name column to devices table
ALTER TABLE devices ADD COLUMN custom_name VARCHAR(255);

-- Grant permissions to anon and authenticated roles
GRANT SELECT, UPDATE ON devices TO anon;
GRANT ALL PRIVILEGES ON devices TO authenticated;

-- Add comment
COMMENT ON COLUMN devices.custom_name IS 'Custom name for the device set by user';