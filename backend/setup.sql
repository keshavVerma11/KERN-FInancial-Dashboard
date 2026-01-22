-- KERN Financial AI Database Setup
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Users table (synced with Supabase Auth)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) DEFAULT 'client',
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    storage_path VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Categories (Chart of Accounts)
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id),
    code VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    parent_category_id UUID REFERENCES categories(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) NOT NULL,
    source_document_id UUID REFERENCES documents(id),
    date DATE NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    description VARCHAR(500),
    merchant VARCHAR(255),
    category_id UUID REFERENCES categories(id),
    confidence_score NUMERIC(3, 2),
    status VARCHAR(50) DEFAULT 'pending',
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    tags VARCHAR(500),
    is_transfer BOOLEAN DEFAULT FALSE,
    is_owner_draw BOOLEAN DEFAULT FALSE,
    payment_method VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Classification history
CREATE TABLE IF NOT EXISTS classification_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID REFERENCES transactions(id),
    suggested_category_id UUID REFERENCES categories(id),
    confidence_score NUMERIC(3, 2),
    rationale TEXT,
    was_accepted BOOLEAN,
    actual_category_id UUID REFERENCES categories(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_transactions_org_id ON transactions(organization_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_documents_org_id ON documents(organization_id);
CREATE INDEX IF NOT EXISTS idx_users_org_id ON users(organization_id);

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their organization's data
CREATE POLICY "Users can view own organization" ON organizations
    FOR SELECT
    USING (id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));

CREATE POLICY "Users can view own profile" ON users
    FOR SELECT
    USING (id = auth.uid() OR organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));

CREATE POLICY "Users can view own documents" ON documents
    FOR ALL
    USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));

CREATE POLICY "Users can view own transactions" ON transactions
    FOR ALL
    USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));

CREATE POLICY "Users can view categories" ON categories
    FOR SELECT
    USING (
        organization_id IS NULL OR 
        organization_id IN (
            SELECT organization_id FROM users WHERE id = auth.uid()
        )
    );

-- Insert default categories (basic Chart of Accounts)
INSERT INTO categories (code, name, type, organization_id) VALUES
    -- Revenue
    ('4000', 'Sales Revenue', 'revenue', NULL),
    ('4100', 'Service Revenue', 'revenue', NULL),
    ('4200', 'Other Income', 'revenue', NULL),
    
    -- Cost of Goods Sold
    ('5000', 'Cost of Goods Sold', 'expense', NULL),
    
    -- Operating Expenses
    ('6000', 'Advertising & Marketing', 'expense', NULL),
    ('6100', 'Bank Fees', 'expense', NULL),
    ('6200', 'Insurance', 'expense', NULL),
    ('6300', 'Office Supplies', 'expense', NULL),
    ('6400', 'Rent', 'expense', NULL),
    ('6500', 'Utilities', 'expense', NULL),
    ('6600', 'Salaries & Wages', 'expense', NULL),
    ('6700', 'Professional Services', 'expense', NULL),
    ('6800', 'Travel & Entertainment', 'expense', NULL),
    ('6900', 'Software & Technology', 'expense', NULL),
    ('6950', 'Meals & Entertainment', 'expense', NULL),
    
    -- Assets
    ('1000', 'Cash', 'asset', NULL),
    ('1100', 'Accounts Receivable', 'asset', NULL),
    ('1200', 'Inventory', 'asset', NULL),
    ('1500', 'Equipment', 'asset', NULL),
    
    -- Liabilities
    ('2000', 'Accounts Payable', 'liability', NULL),
    ('2100', 'Credit Card Payable', 'liability', NULL),
    ('2500', 'Loans Payable', 'liability', NULL),
    
    -- Equity
    ('3000', 'Owner''s Equity', 'equity', NULL),
    ('3100', 'Retained Earnings', 'equity', NULL),
    ('3200', 'Owner Draws', 'equity', NULL)
ON CONFLICT DO NOTHING;

-- Function to automatically create user record when auth user is created
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Create a new organization for the user
    INSERT INTO public.organizations (id, name)
    VALUES (NEW.id, COALESCE(NEW.raw_user_meta_data->>'company_name', NEW.email));
    
    -- Create user record
    INSERT INTO public.users (id, organization_id, email, full_name)
    VALUES (
        NEW.id,
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to call the function when a new user signs up
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
