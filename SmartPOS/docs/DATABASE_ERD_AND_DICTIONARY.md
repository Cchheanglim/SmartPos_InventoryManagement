# Database Relational Architecture & Data Dictionary
## SmartPOS — MySQL Schema (InnoDB Engine)

---

### Entity Relationship Diagram (ERD) Text Specification

```
[roles] 1 ────< [role_permissions] >──── 1 [permissions]
   │
   1
   │
   └──< [users] 1 ────< [attendance] (shifts & float counts)
          │     1 ────< [tasks] (assigned_to & assigned_by)
          │     1 ────< [stock_movements]
          │     1 ────< [sales] 1 ────< [sale_items] >──── 1 [products]
          │     1 ────< [held_orders]
          │
[customers] 1 ────────< [sales]
                           │
[products] 1 ────────< [sale_items]
[products] 1 ────────< [stock_movements]
[categories] 1 ──────< [products]
[suppliers] 1 ───────< [products]
[suppliers] 1 ───────< [purchase_orders]
```

---

### Core Data Dictionary

#### 1. `users`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| `name` | VARCHAR(100) | NOT NULL | Staff member full name |
| `email` | VARCHAR(120) | NOT NULL, UNIQUE | User login email |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt / pbkdf2 hashed password |
| `role_id` | INT | NOT NULL, FK -> roles(id) | Associated security role |
| `profile_picture` | VARCHAR(255) | NULL | Avatar image identifier or URL |
| `shift_name` | VARCHAR(50) | NULL | Assigned work shift (Morning, Evening) |
| `is_active` | BOOLEAN | NOT NULL DEFAULT TRUE | Status flag (soft deletion) |

#### 2. `attendance`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique attendance record ID |
| `user_id` | INT | NOT NULL, FK -> users(id) | Clocked-in staff member |
| `clock_in` | DATETIME | NOT NULL | Timestamp when shift began |
| `clock_out` | DATETIME | NULL | Timestamp when shift ended (NULL = open) |
| `starting_cash` | DECIMAL(10,2) | NULL | Initial cash drawer float ($) |
| `counted_cash` | DECIMAL(10,2) | NULL | Closing cash drawer count ($) |
| `expected_cash` | DECIMAL(10,2) | NULL | Calculated expected drawer cash ($) |
| `cash_difference` | DECIMAL(10,2) | NULL | Over/Short discrepancy ($) |

#### 3. `tasks`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique task ID |
| `title` | VARCHAR(200) | NOT NULL | Task summary |
| `description` | TEXT | NULL | Detailed instructions |
| `assigned_to` | INT | NOT NULL, FK -> users(id) | Assignee executing the task |
| `assigned_by` | INT | NOT NULL, FK -> users(id) | Assigner/Manager delegating task |
| `priority` | VARCHAR(20) | NOT NULL DEFAULT 'medium' | Priority: urgent, high, medium, low |
| `due_date` | VARCHAR(100) | NULL | Target deadline or shift |
| `status` | VARCHAR(20) | NOT NULL DEFAULT 'pending' | Status: pending or completed |
| `created_at` | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `completed_at` | DATETIME | NULL | Timestamp of completion |

#### 4. `products`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique product ID |
| `barcode` | VARCHAR(50) | NOT NULL, UNIQUE | Barcode/SKU string |
| `name` | VARCHAR(150) | NOT NULL | Product title |
| `category_id` | INT | NOT NULL, FK -> categories(id) | Merchandise category |
| `cost_price` | DECIMAL(10,2) | NOT NULL | Acquisition unit cost ($) |
| `selling_price` | DECIMAL(10,2) | NOT NULL | Retail unit price ($) |
| `quantity_in_stock` | INT | NOT NULL DEFAULT 0 | Available inventory units |
| `low_stock_threshold` | INT | NOT NULL DEFAULT 5 | Minimum threshold triggering reorder alert |
