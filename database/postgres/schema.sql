-- =============================================================================
-- PostgreSQL Schema – Polyglot Persistence Demo
-- Responsibility: Core product catalog data (relational, ACID, FK constraints)
-- =============================================================================

-- Create database (run as superuser / admin before applying this file)
-- CREATE DATABASE polyglot_db;
-- \c polyglot_db;

-- =============================================================================
-- CATEGORIES
-- Master data for product classification.
-- Using PostgreSQL because categories have strict referential integrity
-- requirements with products.
-- =============================================================================
CREATE TABLE IF NOT EXISTS categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- SUPPLIERS
-- Supplier master data.
-- Using PostgreSQL to maintain FK integrity with products.
-- =============================================================================
CREATE TABLE IF NOT EXISTS suppliers (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(150) NOT NULL,
    contact_email VARCHAR(255),
    phone         VARCHAR(30),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- PRODUCTS
-- Core product table – primary business entity.
-- PostgreSQL chosen for:
--   • ACID transactions
--   • Foreign key constraints (category_id, supplier_id)
--   • CHECK constraints (price >= 0, stock >= 0)
--   • Full-text search capability (description)
--   • Complex JOIN queries with categories & suppliers
-- =============================================================================
CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    sku         VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    price       NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
    stock       INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Update updated_at automatically on row change
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_products_updated_at ON products;
CREATE TRIGGER trg_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_supplier_id ON products(supplier_id);
CREATE INDEX IF NOT EXISTS idx_products_sku        ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at DESC);

-- =============================================================================
-- SAMPLE CATEGORIES (optional bootstrap data)
-- =============================================================================
INSERT INTO categories (name, description) VALUES
    ('Electronics',    'Electronic devices and accessories'),
    ('Clothing',       'Apparel and fashion items'),
    ('Food & Beverage','Food products and drinks'),
    ('Office Supplies', 'Stationery and office equipment')
ON CONFLICT (name) DO NOTHING;
