-- =============================================================================
-- MySQL Schema – Polyglot Persistence Demo
-- Responsibility: Order & Sales data (transactional, aggregation, reporting)
-- =============================================================================

-- Create database (run as admin before applying this file)
-- CREATE DATABASE polyglot_orders CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE polyglot_orders;

-- =============================================================================
-- ORDERS
-- Order header table.
-- MySQL chosen for:
--   • Wide adoption in e-commerce / transactional workloads
--   • Excellent aggregation / GROUP BY performance
--   • Easy integration with reporting tools
--   • ACID transactions via InnoDB
-- Note: product_id is an integer reference only (no FK cross-DB constraint).
--       Referential integrity across databases is enforced at application level.
-- =============================================================================
CREATE TABLE IF NOT EXISTS orders (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    status       ENUM('pending', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(14, 2) NOT NULL DEFAULT 0.00,
    notes        TEXT,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_orders_status     (status),
    INDEX idx_orders_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- ORDER ITEMS
-- Line items per order.
-- • Stores denormalized product_name so order history is self-contained
--   even if the product is later renamed or deleted in PostgreSQL.
-- • subtotal = quantity × unit_price (computed and stored for fast reporting)
-- =============================================================================
CREATE TABLE IF NOT EXISTS order_items (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id     INT UNSIGNED NOT NULL,
    product_id   INT UNSIGNED NOT NULL,   -- cross-DB reference (no FK)
    product_name VARCHAR(255) NOT NULL,   -- denormalized snapshot
    quantity     INT UNSIGNED NOT NULL CHECK (quantity > 0),
    unit_price   DECIMAL(12, 2) NOT NULL,
    subtotal     DECIMAL(14, 2) NOT NULL, -- quantity * unit_price

    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id)
        REFERENCES orders(id) ON DELETE CASCADE,

    INDEX idx_order_items_order_id   (order_id),
    INDEX idx_order_items_product_id (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- USEFUL VIEWS (optional – for quick reporting)
-- =============================================================================

-- Sales summary per product: total quantity sold + total revenue
CREATE OR REPLACE VIEW v_product_sales AS
SELECT
    oi.product_id,
    oi.product_name,
    SUM(oi.quantity)  AS total_quantity_sold,
    SUM(oi.subtotal)  AS total_revenue,
    COUNT(DISTINCT oi.order_id) AS order_count
FROM order_items oi
JOIN orders o ON o.id = oi.order_id
WHERE o.status = 'completed'
GROUP BY oi.product_id, oi.product_name;
