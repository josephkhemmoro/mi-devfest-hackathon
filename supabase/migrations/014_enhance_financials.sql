-- ============================================
-- Enhanced Financial Tracking System
-- Add expense categories beyond just payroll
-- ============================================

-- Add new columns to weekly_financials table
ALTER TABLE weekly_financials
ADD COLUMN IF NOT EXISTS cogs DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS rent DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS utilities DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS supplies DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS marketing DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS maintenance DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS insurance DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS processing_fees DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS other_expenses DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_expenses DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS net_profit DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS profit_margin DECIMAL(5, 2) DEFAULT 0;

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_weekly_financials_business_week 
ON weekly_financials(business_id, week_start DESC);

-- Add comments
COMMENT ON COLUMN weekly_financials.cogs IS 'Cost of Goods Sold - direct product costs';
COMMENT ON COLUMN weekly_financials.rent IS 'Rent or lease payments';
COMMENT ON COLUMN weekly_financials.utilities IS 'Utilities (electric, water, internet, etc.)';
COMMENT ON COLUMN weekly_financials.supplies IS 'Operating supplies';
COMMENT ON COLUMN weekly_financials.marketing IS 'Marketing and advertising expenses';
COMMENT ON COLUMN weekly_financials.maintenance IS 'Maintenance and repairs';
COMMENT ON COLUMN weekly_financials.insurance IS 'Business insurance';
COMMENT ON COLUMN weekly_financials.processing_fees IS 'Credit card and payment processing fees';
COMMENT ON COLUMN weekly_financials.other_expenses IS 'Other miscellaneous expenses';
COMMENT ON COLUMN weekly_financials.total_expenses IS 'Sum of all expenses';
COMMENT ON COLUMN weekly_financials.net_profit IS 'Revenue - Total Expenses';
COMMENT ON COLUMN weekly_financials.profit_margin IS 'Net Profit / Revenue * 100';
