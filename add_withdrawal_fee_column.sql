-- Migration script to add withdrawal_fee column to partner_payouts table
-- Run this SQL script directly on your PostgreSQL database

ALTER TABLE partner_payouts 
ADD COLUMN IF NOT EXISTS withdrawal_fee NUMERIC(10, 2) DEFAULT 0.00;

-- Update existing records to have 0.00 as default
UPDATE partner_payouts 
SET withdrawal_fee = 0.00 
WHERE withdrawal_fee IS NULL;

