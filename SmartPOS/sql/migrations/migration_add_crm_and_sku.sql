-- ============================================================
-- Migration: brings an older database up to the current schema.
--
-- Safe to run even if some of these columns already exist --
-- every ADD COLUMN uses IF NOT EXISTS, so this will only add
-- what's actually missing and won't error on what's already there.
--
-- Run this in phpMyAdmin (SQL tab, on the smartpos database).
-- ============================================================

USE smartpos;

ALTER TABLE products
    ADD COLUMN IF NOT EXISTS sku VARCHAR(20) NULL UNIQUE AFTER id,
    ADD COLUMN IF NOT EXISTS cost DECIMAL(10,2) NOT NULL DEFAULT 0 AFTER price,
    ADD COLUMN IF NOT EXISTS supplier_name VARCHAR(150) NULL AFTER low_stock_threshold,
    ADD COLUMN IF NOT EXISTS supplier_contact VARCHAR(100) NULL AFTER supplier_name,
    ADD COLUMN IF NOT EXISTS image_filename VARCHAR(255) NULL AFTER supplier_contact,
    ADD COLUMN IF NOT EXISTS image_url VARCHAR(500) NULL AFTER image_filename;

CREATE TABLE IF NOT EXISTS customers (
    phone       VARCHAR(20) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    join_date   DATE NOT NULL DEFAULT (CURRENT_DATE)
) ENGINE=InnoDB;

ALTER TABLE sales
    ADD COLUMN IF NOT EXISTS customer_phone VARCHAR(20) NULL AFTER payment_method;

-- Only add the foreign key if it doesn't already exist (MariaDB has no
-- IF NOT EXISTS for constraints, so this checks information_schema first).
SET @fk_exists = (
    SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'sales'
      AND CONSTRAINT_NAME = 'FK_sales_customer'
);
SET @sql = IF(@fk_exists = 0,
    'ALTER TABLE sales ADD CONSTRAINT FK_sales_customer FOREIGN KEY (customer_phone) REFERENCES customers(phone)',
    'SELECT "FK_sales_customer already exists, skipping"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(255) NULL AFTER role_id,
    ADD COLUMN IF NOT EXISTS shift_name VARCHAR(50) NULL AFTER profile_picture,
    ADD COLUMN IF NOT EXISTS shift_start TIME NULL AFTER shift_name,
    ADD COLUMN IF NOT EXISTS shift_end TIME NULL AFTER shift_start;

CREATE TABLE IF NOT EXISTS attendance (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    clock_in    DATETIME NOT NULL,
    clock_out   DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tasks (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(200) NOT NULL,
    description     TEXT NULL,
    assigned_to     INT NOT NULL,
    assigned_by     INT NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at    DATETIME NULL,
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    FOREIGN KEY (assigned_by) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS held_orders (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    cashier_id          INT NOT NULL,
    cart_json           TEXT NOT NULL,
    discount_percent    DECIMAL(5,2) NOT NULL DEFAULT 0,
    customer_phone      VARCHAR(20) NULL,
    customer_name       VARCHAR(100) NULL,
    note                VARCHAR(200) NULL,
    held_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cashier_id) REFERENCES users(id)
) ENGINE=InnoDB;

-- Safety net if held_orders already existed from an earlier version of
-- this migration, before customer_name was added.
ALTER TABLE held_orders
    ADD COLUMN IF NOT EXISTS customer_name VARCHAR(100) NULL AFTER customer_phone;

CREATE TABLE IF NOT EXISTS user_permissions (
    user_id         INT NOT NULL,
    permission_id   INT NOT NULL,
    granted_by      INT NOT NULL,
    granted_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, permission_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id),
    FOREIGN KEY (granted_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- Optional: run the INSERT block near the bottom of schema.sql
-- (starting at "100-item product catalog") if you want the demo
-- catalog added on top of whatever products you already have.

