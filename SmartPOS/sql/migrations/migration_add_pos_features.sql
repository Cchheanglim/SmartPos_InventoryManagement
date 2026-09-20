-- ============================================================
-- Migration: adds Refunds/Voids, Tax, Purchase Orders, and
-- Shift Cash Reconciliation.
--
-- Safe to run even if some of this already exists -- uses
-- IF NOT EXISTS / existence checks throughout.
--
-- Run this in phpMyAdmin (SQL tab, on the smartpos database).
-- ============================================================

USE smartpos;

-- ---------- 1. Refunds / Voids ----------

CREATE TABLE IF NOT EXISTS refunds (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    sale_id         INT NOT NULL,
    processed_by    INT NOT NULL,
    reason          VARCHAR(255) NULL,
    refund_amount   DECIMAL(10,2) NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_id) REFERENCES sales(id),
    FOREIGN KEY (processed_by) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS refund_items (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    refund_id       INT NOT NULL,
    sale_item_id    INT NOT NULL,
    quantity        INT NOT NULL,
    FOREIGN KEY (refund_id) REFERENCES refunds(id) ON DELETE CASCADE,
    FOREIGN KEY (sale_item_id) REFERENCES sale_items(id)
) ENGINE=InnoDB;

-- New permission for who's allowed to process a refund. Defaults to
-- Admin only (the dynamic "Admin: all permissions" INSERT in schema.sql
-- only fires on a brand-new install, so on an existing database we grant
-- it explicitly here). An Admin can extend it to other roles anytime via
-- Manage Staff -> Permissions.
INSERT INTO permissions (name)
SELECT 'process_refund' WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE name = 'process_refund');

INSERT INTO role_permissions (role_id, permission_id)
SELECT (SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'process_refund')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permissions
    WHERE role_id = (SELECT id FROM roles WHERE name = 'admin')
      AND permission_id = (SELECT id FROM permissions WHERE name = 'process_refund')
);

-- ---------- 2. Tax ----------

ALTER TABLE sales
    ADD COLUMN IF NOT EXISTS tax_percent DECIMAL(5,2) NOT NULL DEFAULT 0 AFTER discount_percent;

-- ---------- 4. Purchase Orders / Restocking workflow ----------

CREATE TABLE IF NOT EXISTS purchase_orders (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    product_id          INT NOT NULL,
    supplier_name       VARCHAR(150) NULL,
    supplier_contact    VARCHAR(100) NULL,
    quantity_ordered    INT NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'ordered', -- ordered, received, cancelled
    ordered_by          INT NOT NULL,
    received_by         INT NULL,
    ordered_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    received_at         DATETIME NULL,
    notes               VARCHAR(255) NULL,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (ordered_by) REFERENCES users(id),
    FOREIGN KEY (received_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- ---------- 6. Shift / Cash Reconciliation ----------

ALTER TABLE attendance
    ADD COLUMN IF NOT EXISTS starting_cash   DECIMAL(10,2) NULL AFTER clock_out,
    ADD COLUMN IF NOT EXISTS counted_cash    DECIMAL(10,2) NULL AFTER starting_cash,
    ADD COLUMN IF NOT EXISTS expected_cash   DECIMAL(10,2) NULL AFTER counted_cash,
    ADD COLUMN IF NOT EXISTS cash_difference DECIMAL(10,2) NULL AFTER expected_cash;
