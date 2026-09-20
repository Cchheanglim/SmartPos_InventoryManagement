-- Adds categories, suppliers, shift_templates, and notifications tables
-- to an existing database that was created before these were added to
-- schema.sql. Safe to run — purely additive, no existing table is
-- touched. Skip this if you're setting up a brand-new database from the
-- current schema.sql, which already includes these tables and seed data.

USE smartpos;

CREATE TABLE IF NOT EXISTS categories (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,
    description  VARCHAR(255) NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS suppliers (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(150) NOT NULL,
    contact_name  VARCHAR(100) NULL,
    phone         VARCHAR(50) NULL,
    email         VARCHAR(150) NULL,
    address       VARCHAR(255) NULL,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS shift_templates (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(50) NOT NULL UNIQUE,
    start_time  TIME NOT NULL,
    end_time    TIME NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS notifications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    message     VARCHAR(255) NOT NULL,
    category    VARCHAR(50) NOT NULL DEFAULT 'general',
    is_read     TINYINT(1) NOT NULL DEFAULT 0,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

INSERT IGNORE INTO categories (name, description) VALUES
    ('Snacks', 'Chips, cookies, candy, and other snack foods'),
    ('Beverages', 'Soft drinks, juices, water, and other drinks'),
    ('Dairy', 'Milk, cheese, yogurt, and other dairy products'),
    ('Household', 'Cleaning supplies and household essentials'),
    ('Personal Care', 'Soap, shampoo, and other personal care items'),
    ('Pantry', 'Cooking oil, canned goods, sauces, and dry goods');

INSERT IGNORE INTO shift_templates (name, start_time, end_time) VALUES
    ('Morning', '06:00:00', '14:00:00'),
    ('Afternoon', '10:00:00', '18:00:00'),
    ('Evening', '14:00:00', '22:00:00'),
    ('Night', '22:00:00', '06:00:00');
