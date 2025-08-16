-- LawVriksh Credit Management Database Schema
-- PostgreSQL Schema for Backend Intern Assignment

-- Create database (run this separately if needed)
-- CREATE DATABASE lawvriksh_credits;

-- Enable UUID extension (optional, for future use)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Credits table
CREATE TABLE IF NOT EXISTS credits (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    credits INTEGER NOT NULL DEFAULT 0 CHECK (credits >= 0),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Credit transactions audit table
CREATE TABLE IF NOT EXISTS credit_transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('ADD', 'DEDUCT', 'RESET', 'DAILY_BONUS')),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_credits_user_id ON credits(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON credit_transactions(created_at);

-- Function to automatically update last_updated timestamp
CREATE OR REPLACE FUNCTION update_last_updated_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update last_updated on credits table
DROP TRIGGER IF EXISTS update_credits_last_updated ON credits;
CREATE TRIGGER update_credits_last_updated
    BEFORE UPDATE ON credits
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated_column();

-- Trigger to automatically update updated_at on users table
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated_column();

-- Sample data insertion
INSERT INTO users (email, name) VALUES 
    ('admin@lawvriksh.com', 'Admin User'),
    ('test.user@lawvriksh.com', 'Test User'),
    ('john.doe@lawvriksh.com', 'John Doe'),
    ('jane.smith@lawvriksh.com', 'Jane Smith');

-- Initialize credits for sample users
INSERT INTO credits (user_id, credits) VALUES 
    (1, 100),
    (2, 50),
    (3, 75),
    (4, 200);

-- Sample transactions
INSERT INTO credit_transactions (user_id, amount, transaction_type, description) VALUES 
    (1, 100, 'ADD', 'Initial credit allocation'),
    (2, 50, 'ADD', 'Welcome bonus'),
    (3, 75, 'ADD', 'Article publication reward'),
    (4, 200, 'ADD', 'Mentorship program bonus');

-- View for user credit summary
CREATE OR REPLACE VIEW user_credit_summary AS
SELECT 
    u.user_id,
    u.email,
    u.name,
    COALESCE(c.credits, 0) as current_credits,
    c.last_updated,
    COUNT(ct.transaction_id) as total_transactions,
    SUM(CASE WHEN ct.transaction_type = 'ADD' THEN ct.amount ELSE 0 END) as total_credits_added,
    SUM(CASE WHEN ct.transaction_type = 'DEDUCT' THEN ct.amount ELSE 0 END) as total_credits_deducted
FROM users u
LEFT JOIN credits c ON u.user_id = c.user_id
LEFT JOIN credit_transactions ct ON u.user_id = ct.user_id
GROUP BY u.user_id, u.email, u.name, c.credits, c.last_updated;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;

-- Comments for documentation
COMMENT ON TABLE users IS 'Stores user information for the credit management system';
COMMENT ON TABLE credits IS 'Stores current credit balances for users';
COMMENT ON TABLE credit_transactions IS 'Audit trail for all credit transactions';
COMMENT ON COLUMN credits.credits IS 'Current credit balance, must be non-negative';
COMMENT ON COLUMN credit_transactions.transaction_type IS 'Type of transaction: ADD, DEDUCT, RESET, DAILY_BONUS';
