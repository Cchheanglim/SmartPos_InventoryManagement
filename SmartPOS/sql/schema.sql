-- ============================================================
-- SmartPOS Database Schema (MySQL)
-- Matches Section 10 (Database Plan) of the project proposal.
-- ============================================================

CREATE DATABASE IF NOT EXISTS smartpos CHARACTER SET utf8mb4;
USE smartpos;

-- ---------- RBAC tables ----------

CREATE TABLE roles (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    name    VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE permissions (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    name    VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE role_permissions (
    role_id         INT NOT NULL,
    permission_id   INT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------- Core business tables ----------

CREATE TABLE users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    phone           VARCHAR(20) NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    reset_token_hash        VARCHAR(255) NULL,
    reset_token_expires_at  DATETIME NULL,
    role_id         INT NOT NULL,
    profile_picture VARCHAR(255) NULL,
    shift_name      VARCHAR(50) NULL,
    shift_start     TIME NULL,
    shift_end       TIME NULL,
    is_active       TINYINT(1) NOT NULL DEFAULT 1,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=InnoDB;

CREATE TABLE products (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    sku                 VARCHAR(20) NULL UNIQUE,
    name                VARCHAR(150) NOT NULL,
    category            VARCHAR(100) NULL,
    price               DECIMAL(10,2) NOT NULL,
    cost                DECIMAL(10,2) NOT NULL DEFAULT 0,
    quantity_in_stock   INT NOT NULL DEFAULT 0,
    low_stock_threshold INT NOT NULL DEFAULT 5,
    supplier_name       VARCHAR(150) NULL,
    supplier_contact    VARCHAR(100) NULL,
    image_filename      VARCHAR(255) NULL,
    image_url           VARCHAR(500) NULL,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Customers are looked up by phone for the CRM feature. Only a masked tag
-- (first name + first 3 digits of phone, e.g. "Sara012") is ever shown in
-- the UI -- the full phone number stays server-side only.
CREATE TABLE customers (
    phone       VARCHAR(20) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    join_date   DATE NOT NULL DEFAULT (CURRENT_DATE)
) ENGINE=InnoDB;

CREATE TABLE sales (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    cashier_id          INT NOT NULL,
    discount_percent    DECIMAL(5,2) NOT NULL DEFAULT 0,
    tax_percent         DECIMAL(5,2) NOT NULL DEFAULT 0,
    payment_method      VARCHAR(20) NOT NULL DEFAULT 'cash',
    customer_phone      VARCHAR(20) NULL,
    total_amount        DECIMAL(10,2) NOT NULL,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cashier_id) REFERENCES users(id),
    FOREIGN KEY (customer_phone) REFERENCES customers(phone)
) ENGINE=InnoDB;

CREATE TABLE sale_items (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    sale_id     INT NOT NULL,
    product_id  INT NOT NULL,
    quantity    INT NOT NULL,
    unit_price  DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB;

CREATE TABLE stock_movements (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    product_id      INT NOT NULL,
    change_amount   INT NOT NULL,
    reason          VARCHAR(255) NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB;

-- A refund against a completed sale. Supports partial refunds — an
-- Admin (by default) picks which sale_items and how many of each to
-- reverse. Restores stock and is logged like any other stock movement.
CREATE TABLE refunds (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    sale_id         INT NOT NULL,
    processed_by    INT NOT NULL,
    reason          VARCHAR(255) NULL,
    refund_amount   DECIMAL(10,2) NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_id) REFERENCES sales(id),
    FOREIGN KEY (processed_by) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE refund_items (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    refund_id       INT NOT NULL,
    sale_item_id    INT NOT NULL,
    quantity        INT NOT NULL,
    FOREIGN KEY (refund_id) REFERENCES refunds(id) ON DELETE CASCADE,
    FOREIGN KEY (sale_item_id) REFERENCES sale_items(id)
) ENGINE=InnoDB;

-- A formal "ordered X units from this supplier, awaiting delivery"
-- record — separate from the instant manual stock adjustment, which
-- stays for corrections/damage/etc. Receiving a PO is what actually
-- adds the stock and logs a stock_movement.
CREATE TABLE purchase_orders (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    product_id          INT NOT NULL,
    supplier_name       VARCHAR(150) NULL,
    supplier_contact    VARCHAR(100) NULL,
    quantity_ordered    INT NOT NULL,
    unit_cost           DECIMAL(10,2) NULL,
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

-- Clock in/out history. A NULL clock_out means the staff member is
-- currently clocked in (their shift is still open).
CREATE TABLE attendance (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    clock_in    DATETIME NOT NULL,
    clock_out   DATETIME NULL,
    starting_cash   DECIMAL(10,2) NULL,
    counted_cash    DECIMAL(10,2) NULL,
    expected_cash   DECIMAL(10,2) NULL,
    cash_difference DECIMAL(10,2) NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

-- Tasks an Admin (or anyone with manage_users) assigns to a specific
-- staff member, e.g. "Restock shelf 3" or "Add new snack items".
CREATE TABLE tasks (
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

-- A cart parked mid-sale ("Hold Order") so a cashier can serve someone
-- else and come back to it. cart_json stores the item list exactly as
-- the checkout page had it; nothing here touches stock or the sales
-- table until the order is resumed and actually completed.
CREATE TABLE held_orders (
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

-- Extra permissions an Admin grants to one specific, trusted person, on
-- top of whatever their role already gives them. This never removes a
-- role permission — it only ever adds. E.g. a Cashier you trust could be
-- individually granted "manage_products" without touching the Cashier
-- role itself or affecting any other cashier.
CREATE TABLE user_permissions (
    user_id         INT NOT NULL,
    permission_id   INT NOT NULL,
    granted_by      INT NOT NULL,
    granted_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, permission_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id),
    FOREIGN KEY (granted_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- ---------- Added: categories, suppliers, shift templates, notifications ----------
-- These are additive, standalone lookup/management tables. products.category
-- and products.supplier_name/supplier_contact remain plain text columns for
-- backward compatibility (no existing data or code path changes) — the
-- product form's dropdowns now pull their options from these tables instead
-- of a hardcoded list, but nothing about the products table itself changed.

CREATE TABLE categories (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,
    description  VARCHAR(255) NULL,
    icon         VARCHAR(40) NULL
) ENGINE=InnoDB;

CREATE TABLE suppliers (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(150) NOT NULL,
    contact_name  VARCHAR(100) NULL,
    phone         VARCHAR(50) NULL,
    email         VARCHAR(150) NULL,
    address       VARCHAR(255) NULL,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE shift_templates (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(50) NOT NULL UNIQUE,
    start_time  TIME NOT NULL,
    end_time    TIME NOT NULL
) ENGINE=InnoDB;

CREATE TABLE notifications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    message     VARCHAR(255) NOT NULL,
    category    VARCHAR(50) NOT NULL DEFAULT 'general',
    is_read     TINYINT(1) NOT NULL DEFAULT 0,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

-- ============================================================
-- Seed data
-- ============================================================

INSERT INTO roles (name) VALUES
    ('admin'), ('admin_assistant'), ('inventory_manager'), ('cashier');

INSERT INTO permissions (name) VALUES
    ('manage_users'), ('manage_products'), ('adjust_stock'),
    ('process_sale'), ('view_reports'), ('manage_cashier_accounts'),
    ('process_refund');

-- Admin: all permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT (SELECT id FROM roles WHERE name = 'admin'), id FROM permissions;

-- Admin Assistant: view_reports, manage_cashier_accounts
INSERT INTO role_permissions (role_id, permission_id)
SELECT (SELECT id FROM roles WHERE name = 'admin_assistant'), id
FROM permissions WHERE name IN ('view_reports', 'manage_cashier_accounts');

-- Inventory Manager: manage_products, adjust_stock
INSERT INTO role_permissions (role_id, permission_id)
SELECT (SELECT id FROM roles WHERE name = 'inventory_manager'), id
FROM permissions WHERE name IN ('manage_products', 'adjust_stock');

-- Cashier: process_sale
INSERT INTO role_permissions (role_id, permission_id)
SELECT (SELECT id FROM roles WHERE name = 'cashier'), id
FROM permissions WHERE name = 'process_sale';

-- Default users (password for all: "password123")
-- Password hashes are generated at first run by seed_admin.py instead of
-- hardcoded here, since Werkzeug salts every hash differently.

-- 100-item product catalog (Cambodian mini-mart inventory)
INSERT INTO products (sku, name, category, price, cost, quantity_in_stock, low_stock_threshold) VALUES
    ('PRD-001', 'Cheetos Crunchy Flamin'' Hot (28g)', 'Snacks', 4.00, 2.40, 67, 20),
    ('PRD-002', 'Doritos Tortilla Chips', 'Snacks', 5.00, 3.0, 50, 15),
    ('PRD-003', 'Oreo Cookies Original', 'Snacks', 2.00, 1.2, 40, 15),
    ('PRD-004', 'Takis Fuego', 'Snacks', 4.00, 2.4, 40, 15),
    ('PRD-005', 'Pringles Original', 'Snacks', 2.50, 1.5, 50, 15),
    ('PRD-006', 'Lays Classic Potato Chips', 'Snacks', 1.50, 0.9, 45, 15),
    ('PRD-007', 'Lays Nori Seaweed Flavor', 'Snacks', 1.50, 0.9, 55, 15),
    ('PRD-008', 'Samyang Buldak Hot Chicken Snack', 'Snacks', 1.20, 0.72, 80, 25),
    ('PRD-009', 'Lyly Rice Crackers', 'Snacks', 0.80, 0.48, 60, 20),
    ('PRD-010', 'Dongwon Yangban Seaweed', 'Snacks', 1.50, 0.9, 40, 15),
    ('PRD-011', 'Pocky Chocolate', 'Snacks', 1.00, 0.6, 50, 15),
    ('PRD-012', 'Pocky Strawberry', 'Snacks', 1.00, 0.6, 45, 15),
    ('PRD-013', 'Hello Panda Chocolate', 'Snacks', 0.90, 0.54, 35, 10),
    ('PRD-014', 'Snickers Bar', 'Snacks', 1.20, 0.72, 40, 15),
    ('PRD-015', 'M&M''s Peanut', 'Snacks', 1.50, 0.90, 30, 10),
    ('PRD-016', 'Skittles Original', 'Snacks', 1.20, 0.72, 25, 10),
    ('PRD-017', 'KitKat 4-Finger', 'Snacks', 1.00, 0.6, 50, 15),
    ('PRD-018', 'Toblerone Milk Chocolate', 'Snacks', 2.50, 1.5, 20, 5),
    ('PRD-019', 'Ferrero Rocher (3-piece)', 'Snacks', 2.00, 1.2, 30, 10),
    ('PRD-020', 'Kinder Joy', 'Snacks', 1.50, 0.9, 25, 10),
    ('PRD-021', 'LOTTE Choco Pie (Single)', 'Snacks', 0.50, 0.3, 60, 20),
    ('PRD-022', 'LOTTE Pepero', 'Snacks', 1.20, 0.72, 40, 15),
    ('PRD-023', 'Roller Coaster Potato Rings', 'Snacks', 0.80, 0.48, 45, 15),
    ('PRD-024', 'Planters Salted Peanuts', 'Snacks', 1.50, 0.9, 35, 10),
    ('PRD-025', 'Mentos Mint Roll', 'Snacks', 0.60, 0.36, 55, 20),
    ('PRD-026', 'Halls Mentholyptus Candy (Stick)', 'Snacks', 0.50, 0.3, 60, 20),
    ('PRD-027', 'Kopiko Coffee Candies (Pack)', 'Snacks', 1.00, 0.6, 40, 15),
    ('PRD-028', 'Haribo Goldbears', 'Snacks', 1.50, 0.9, 30, 10),
    ('PRD-029', 'Yupi Gummy Bears', 'Snacks', 1.00, 0.6, 40, 15),
    ('PRD-030', 'Sugus Fruit Chews', 'Snacks', 0.80, 0.48, 35, 10),
    ('PRD-031', 'Vital Premium Water (500ml)', 'Beverages', 0.25, 0.15, 100, 30),
    ('PRD-032', 'Dasani Purified Water (500ml)', 'Beverages', 0.30, 0.18, 80, 25),
    ('PRD-033', 'Coca-Cola Can (330ml)', 'Beverages', 0.60, 0.36, 90, 30),
    ('PRD-034', 'Sprite Can (330ml)', 'Beverages', 0.60, 0.36, 70, 20),
    ('PRD-035', 'Fanta Orange Can (330ml)', 'Beverages', 0.60, 0.36, 60, 20),
    ('PRD-036', 'Bacchus Energy Drink', 'Beverages', 0.70, 0.42, 120, 40),
    ('PRD-037', 'Sting Energy Drink (Strawberry)', 'Beverages', 0.50, 0.3, 100, 30),
    ('PRD-038', 'Champion Energy Drink', 'Beverages', 0.60, 0.36, 85, 25),
    ('PRD-039', 'Wurkz Energy Drink', 'Beverages', 0.70, 0.42, 90, 30),
    ('PRD-040', 'Yeo''s Chrysanthemum Tea', 'Beverages', 0.80, 0.48, 50, 15),
    ('PRD-041', 'Pokka Melon Milk', 'Beverages', 1.00, 0.6, 40, 15),
    ('PRD-042', 'Nescafe Iced Coffee Can', 'Beverages', 0.80, 0.48, 60, 20),
    ('PRD-043', 'Angkor Beer Can (330ml)', 'Beverages', 0.80, 0.48, 150, 50),
    ('PRD-044', 'Hanuman Beer Can (330ml)', 'Beverages', 0.85, 0.51, 120, 40),
    ('PRD-045', 'V-Active Isotonic Drink', 'Beverages', 0.60, 0.36, 45, 15),
    ('PRD-046', 'Paseo Facial Tissue (Box)', 'Household', 1.50, 0.9, 30, 10),
    ('PRD-047', 'Vinda Tissue Paper (3-ply pack)', 'Household', 1.20, 0.72, 40, 15),
    ('PRD-048', 'Scott Toilet Paper (4 Rolls)', 'Household', 2.50, 1.5, 25, 10),
    ('PRD-049', 'Omo Laundry Detergent Powder', 'Household', 2.00, 1.2, 35, 10),
    ('PRD-050', 'Sunlight Lemon Dishwashing Liquid', 'Household', 1.50, 0.9, 40, 15),
    ('PRD-051', 'Downy Fabric Softener', 'Household', 1.80, 1.08, 45, 15),
    ('PRD-052', 'Vim Floor Cleaner', 'Household', 2.50, 1.5, 20, 5),
    ('PRD-053', 'Duck Toilet Bowl Cleaner', 'Household', 2.00, 1.2, 25, 10),
    ('PRD-054', 'Scotch-Brite Dish Sponge', 'Household', 0.80, 0.48, 50, 15),
    ('PRD-055', 'Baygon Mosquito Repellent Spray', 'Household', 3.50, 2.1, 15, 5),
    ('PRD-056', 'Medium Trash Bags (Roll)', 'Household', 1.50, 0.9, 40, 10),
    ('PRD-057', 'Mr. Muscle Glass Cleaner', 'Household', 2.50, 1.5, 20, 5),
    ('PRD-058', 'Green Cross Rubbing Alcohol', 'Household', 1.50, 0.9, 30, 10),
    ('PRD-059', 'Febreze Air Freshener', 'Household', 3.00, 1.8, 15, 5),
    ('PRD-060', 'Kitchen Paper Towel (Roll)', 'Household', 1.20, 0.72, 35, 10),
    ('PRD-061', 'Colgate Cavity Protection Toothpaste', 'Personal Care', 1.80, 1.08, 40, 15),
    ('PRD-062', 'Sensodyne Repair & Protect', 'Personal Care', 4.50, 2.7, 15, 5),
    ('PRD-063', 'Oral-B Soft Toothbrush', 'Personal Care', 1.50, 0.9, 50, 15),
    ('PRD-064', 'Sunsilk Smooth & Manageable Shampoo', 'Personal Care', 3.00, 1.8, 25, 10),
    ('PRD-065', 'Clear Men Anti-Dandruff Shampoo', 'Personal Care', 3.50, 2.1, 20, 5),
    ('PRD-066', 'Dove Beauty Moisture Body Wash', 'Personal Care', 4.00, 2.4, 20, 5),
    ('PRD-067', 'Lux Botanical Bar Soap', 'Personal Care', 1.00, 0.6, 60, 20),
    ('PRD-068', 'Protex Antibacterial Talcum Powder', 'Personal Care', 2.00, 1.2, 30, 10),
    ('PRD-069', 'Nivea Pearl & Beauty Roll-On', 'Personal Care', 2.50, 1.5, 35, 10),
    ('PRD-070', 'Vaseline Healthy Bright Lotion', 'Personal Care', 3.50, 2.1, 25, 10),
    ('PRD-071', 'Kotex Maxi Pads (Pack)', 'Personal Care', 1.80, 1.08, 40, 15),
    ('PRD-072', 'Carefree Panty Liners', 'Personal Care', 1.50, 0.9, 35, 10),
    ('PRD-073', 'Gillette Blue 3 Disposable Razors', 'Personal Care', 2.50, 1.5, 30, 10),
    ('PRD-074', 'Panadol Extra (Strip of 10)', 'Personal Care', 1.20, 0.72, 50, 15),
    ('PRD-075', 'Tiger Balm (Red, Small)', 'Personal Care', 1.50, 0.9, 40, 10),
    ('PRD-076', 'Mee Chiet Instant Noodles (Pork)', 'Pantry', 0.40, 0.24, 120, 40),
    ('PRD-077', 'Hao Hao Instant Noodles', 'Pantry', 0.40, 0.24, 120, 40),
    ('PRD-078', 'Indomie Mi Goreng', 'Pantry', 0.50, 0.3, 100, 30),
    ('PRD-079', 'Nongshim Shin Ramyun', 'Pantry', 1.20, 0.72, 60, 20),
    ('PRD-080', 'Phka Rumduol Jasmine Rice (5kg)', 'Pantry', 5.50, 3.3, 15, 5),
    ('PRD-081', 'Kampot Pepper (50g)', 'Pantry', 3.00, 1.8, 25, 10),
    ('PRD-082', 'Lee Kum Kee Soy Sauce', 'Pantry', 1.80, 1.08, 30, 10),
    ('PRD-083', 'Maggi Seasoning Sauce', 'Pantry', 1.50, 0.9, 35, 10),
    ('PRD-084', 'Heinz Tomato Ketchup', 'Pantry', 2.50, 1.5, 20, 5),
    ('PRD-085', 'Cholimex Chili Sauce', 'Pantry', 1.20, 0.72, 40, 15),
    ('PRD-086', 'Knorr Chicken Flavor Bouillon', 'Pantry', 1.50, 0.9, 45, 15),
    ('PRD-087', 'Ajinomoto MSG (Small Bag)', 'Pantry', 0.80, 0.48, 60, 20),
    ('PRD-088', 'Ayam Brand Canned Sardines', 'Pantry', 1.80, 1.08, 50, 15),
    ('PRD-089', 'Century Tuna Flakes in Oil', 'Pantry', 1.50, 0.9, 45, 15),
    ('PRD-090', 'Meizan Vegetable Cooking Oil (1L)', 'Pantry', 2.50, 1.5, 30, 10),
    ('PRD-091', 'Meiji Fresh Milk (830ml)', 'Dairy', 2.80, 1.68, 15, 5),
    ('PRD-092', 'Meiji Chocolate Milk (830ml)', 'Dairy', 2.80, 1.68, 15, 5),
    ('PRD-093', 'Yakult Probiotic Drink (5-Pack)', 'Dairy', 1.50, 0.9, 40, 15),
    ('PRD-094', 'Meiji Paigen Cultured Milk', 'Dairy', 0.80, 0.48, 40, 15),
    ('PRD-095', 'Vinamilk Drinking Yogurt', 'Dairy', 0.60, 0.36, 60, 20),
    ('PRD-096', 'Anchor Cheddar Cheese Slices', 'Dairy', 3.50, 2.1, 20, 5),
    ('PRD-097', 'La Vache Qui Rit (8 Portions)', 'Dairy', 2.50, 1.5, 25, 10),
    ('PRD-098', 'Carnation Evaporated Milk', 'Dairy', 1.20, 0.72, 35, 10),
    ('PRD-099', 'Milkmaid Condensed Milk', 'Dairy', 1.50, 0.9, 40, 10),
    ('PRD-100', 'Anchor Unsalted Butter (227g)', 'Dairy', 4.00, 2.4, 15, 5);

-- Category directory (matches the categories already used above; the
-- product form's category dropdown now pulls from this table)
INSERT INTO categories (name, description, icon) VALUES
    ('Snacks', 'Chips, cookies, candy, and other snack foods', 'fa-cookie-bite'),
    ('Beverages', 'Soft drinks, juices, water, and other drinks', 'fa-bottle-water'),
    ('Dairy', 'Milk, cheese, yogurt, and other dairy products', 'fa-cheese'),
    ('Household', 'Cleaning supplies and household essentials', 'fa-broom'),
    ('Personal Care', 'Soap, shampoo, and other personal care items', 'fa-pump-soap'),
    ('Pantry', 'Cooking oil, canned goods, sauces, and dry goods', 'fa-jar');

-- A few example suppliers so the product/purchase-order forms have real
-- options to pick from out of the box
INSERT INTO suppliers (name, contact_name, phone, email, address) VALUES
    ('Mekong Distribution Co.', 'Sok Dara', '012 345 678', 'sales@mekongdist.com', 'Phnom Penh, Cambodia'),
    ('Golden Rice Trading', 'Chan Vibol', '098 765 432', 'orders@goldenrice.com', 'Battambang, Cambodia'),
    ('Angkor Fresh Supplies', 'Ly Sophea', '077 111 222', 'contact@angkorfresh.com', 'Siem Reap, Cambodia');

-- Shift templates — same four shifts the staff-edit page already offered
-- as a hardcoded list; now a real, admin-editable table instead
INSERT INTO shift_templates (name, start_time, end_time) VALUES
    ('Morning', '06:00:00', '14:00:00'),
    ('Afternoon', '10:00:00', '18:00:00'),
    ('Evening', '14:00:00', '22:00:00'),
    ('Night', '22:00:00', '06:00:00');
