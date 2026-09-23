# គម្រោងស្រាវជ្រាវ និងអភិវឌ្ឍន៍ (R&D Project Proposal)
## Advanced Object-Oriented Programming with Python
### Python + Flask + MySQL Architecture

---

### Project Information
| Field | Information |
|---|---|
| **Project Title** | SmartPOS — Intelligent Inventory & Point-of-Sale Management System |
| **Team Members** | 1. [Student Name 1] - Project Lead & Analyst<br>2. [Student Name 2] - Backend & OOP Architecture<br>3. [Student Name 3] - Database & Repository Design<br>4. [Student Name 4] - UI, Testing & Integration |
| **Course / Class** | Advanced OOP with Python |
| **Lecturer** | SEK SOCHEAT |
| **Semester / Year** | Semester 2 / Academic Year 2025–2026 |
| **Submission Type** | Project Proposal |

---

## ១. Abstract / Executive Summary
SmartPOS is a modular, enterprise-grade Point-of-Sale (POS) and inventory management web platform built using **Python 3**, **Flask**, and **MySQL**, adhering strictly to the principles of **Advanced Object-Oriented Programming (OOP)**, **Separation of Concerns (SoC)**, and **Layered Architecture**. The system addresses the real-world operational bottlenecks of retail mini-marts: uncoordinated stock deductions, manual attendance and cash float drift, unassigned operational task tracking, and vulnerability to role privilege escalation. 

By implementing distinct Domain Models (`Product`, `Sale`, `User`, `Task`, `Attendance`), Repository interfaces handling parameterized MySQL queries, and isolated Service classes governing atomic business transactions, SmartPOS achieves robust transactional integrity (e.g. atomic checkout with stock decrement and loyalty point calculation). The system features Role-Based Access Control (RBAC) across four operational tiers (Admin, Assistant, Inventory Manager, Cashier), shift-enforced cash float reconciliation, dual-currency ledgering (USD and KHR), and comprehensive automated unit testing.

---

## ២. Problem Statement (សេចក្តីថ្លែងអំពីបញ្ហា)
In small-to-medium retail convenience stores and mini-marts, legacy operations depend on unlinked paper logs, basic spreadsheet trackers, or brittle standalone desktop registers. This leads to four critical failure points:
1. **Stock Drift and Over-selling:** Stock levels fail to reconcile atomically with customer checkouts, leading to oversold items, unaccounted shrinkage, and stockouts of high-velocity goods.
2. **Attendance & Till Float Variance:** Cashiers frequently terminate terminal sessions without counting cash drawers or reconciling closing balances against opening floats, causing untraceable cash discrepancies.
3. **Lack of Operational Delegation:** Store supervisors lack structured accountability to assign daily operational tasks (e.g., restocking coolers, shelf audits, receiving deliveries) to specific on-shift employees with priority levels and target completion times.
4. **Security & Privilege Leakage:** Systems without granular Role-Based Access Control (RBAC) expose price modifications, refund authorizations, and database records to junior operators.

```
Current Situation: Manual logs & disconnected point solutions
        ↓
Pain Points: Stock shrinkage, unverified drawer cash, untracked operational tasks
        ↓
Solution: Layered OOP Web Architecture with Flask + MySQL + Atomic Transactions
```

---

## ៣. Objectives & Success Criteria (គោលបំណង និងលក្ខខណ្ឌវាស់វែង)
### General Objective:
To design, implement, and validate a maintainable, testable, and secure retail Point-of-Sale and Inventory Management web application using Advanced OOP patterns in Python, Flask, and MySQL.

### Specific Measurable Objectives:
1. **Domain & Layered OOP Architecture:** Implement a 4-tier layered architecture (Models, Repositories, Services, Routes) with at least 10 domain entities, 8 repositories, and 8 domain services, where each class has a Single Responsibility (SRP).
2. **Granular RBAC Security:** Construct a normalized 4-table RBAC database schema (`roles`, `permissions`, `role_permissions`, `users`) and a reusable Python decorator (`@permission_required`) to prevent unauthorized endpoint access.
3. **Atomic Transactional Processing:** Execute retail sales checkout as an ACID transaction in MySQL (order record creation, line-item insertion, inventory stock deduction, loyalty point accrual, and stock movement logging).
4. **Shift-Enforced Attendance & Till Reconciliation:** Require staff to clock in with starting cash and block terminal logouts unless the cashier performs till float counting or manager emergency override.
5. **Task Delegation Workflow:** Implement a multi-user task assignment engine allowing supervisors to assign tasks with priority levels (`urgent`, `high`, `medium`, `low`) and due dates to specific staff members.
6. **Automated Verification:** Achieve a minimum of 15 automated unit and service test cases validating core business rules.

---

## ៤. Research & Development Questions
1. How does the separation of data persistence (Repository Layer) from domain rules (Service Layer) enhance system maintainability and testability in a Python/Flask web environment?
2. How can database race conditions during peak checkout hours be mitigated using ACID transactions and row-level locking in MySQL?
3. What is the optimal object-oriented strategy for decoupling attendance shift management and terminal session authentication?

---

## ៥. Scope and Limitations (វិសាលភាព និងដែនកំណត់)
### In Scope:
- **Authentication & RBAC:** Session management, password hashing with salt, role assignment, custom permission overrides.
- **Inventory & Catalog:** Products, categories, suppliers, reorder points, low-stock notifications, batch and barcode support.
- **Point of Sale (POS):** Multi-currency calculation (USD / KHR @ 4100 KHR/USD rate), split payments (Cash + ABA PayWay QR), hold cart, receipt printing.
- **Attendance & Shift Enforcement:** Clock-in float recording, clock-out drawer cash reconciliation, logout interception.
- **Team Task Board:** Task creation by assigner to assignee, priority levels, status updates, completion audit.
- **Reporting & Analytics:** Daily sales, top-selling items, cashier performance, stock valuation.

### Limitations / Out of Scope:
- Hardware driver integration for physical receipt cutting (standard browser print formatting used).
- Cloud SMS gateway (Telegram Bot notification used for password recovery and shift alerts).
- External accounting ERP synchronization (data exported via CSV / JSON).

---

## ៦. Target Users and Stakeholders
1. **Store Owner / General Admin:** Full visibility over store revenue, user administration, avatar moderation, stock audits, and business configurations.
2. **Assistant Manager / Supervisor:** Oversees daily floor operations, creates and assigns operational tasks to staff, handles emergency terminal overrides, and approves inventory stock-ins.
3. **Inventory Manager:** Manages purchase orders, tracks vendor receipts, logs stock adjustments, and monitors expiry dates.
4. **Cashier:** Clocks in, counts starting cash, executes customer checkout, holds/resumes orders, and completes assigned shift tasks.

---

## ៧. System Architecture & Layered Design
SmartPOS enforces clean architectural separation:

```
+-------------------------------------------------------------+
|                     Client Browser / UI                     |
|           (Jinja2 Templates, Responsive CSS, Fetch API)      |
+-------------------------------------------------------------+
                              │ HTTP Requests
                              ▼
+-------------------------------------------------------------+
|                  Route / Controller Layer                   |
|  (Flask Blueprints: auth, pos, inventory, staff, reports)   |
|   - Validates incoming parameters / WTForms                 |
|   - Enforces RBAC via @permission_required decorator        |
+-------------------------------------------------------------+
                              │ Method Calls
                              ▼
+-------------------------------------------------------------+
|                       Service Layer                         |
|   (AuthService, SalesService, InventoryService, TaskService)|
|   - Coordinates business rules, policies, and workflows    |
|   - Manages atomic transactions and validation              |
+-------------------------------------------------------------+
                              │ Domain Objects
                              ▼
+-------------------------------------------------------------+
|                     Repository Layer                        |
| (UserRepository, ProductRepository, SaleRepository, etc.)  |
|   - Executes parameterized SQL queries                      |
|   - Converts MySQL row dictionaries into Domain Objects     |
+-------------------------------------------------------------+
                              │ PyMySQL Connection
                              ▼
+-------------------------------------------------------------+
|                       MySQL Database                        |
|  (InnoDB tables, Foreign Keys, Unique Constraints, Triggers)|
+-------------------------------------------------------------+
```

---

## ៨. OOP Design Plan (Core Domain Classes & Roles)

| Class Name | Layer | Primary Responsibility |
|---|---|---|
| `User` | Model | Represents user credentials, assigned role, avatar, and active state. |
| `Product` | Model | Represents catalog items, stock quantity, cost, retail price, and low stock threshold. |
| `Sale` & `SaleItem` | Model | Represents completed retail transactions and line-item details. |
| `Attendance` | Model | Represents shift clock-in, clock-out, float counts, and discrepancy properties. |
| `Task` | Model | Encapsulates delegated operational duties, priority, due date, assigner, and assignee. |
| `AuthService` | Service | Validates logins, checks permissions, and handles secure password recovery. |
| `SalesService` | Service | Executes atomic checkout, validates stock sufficiency, decrements inventory. |
| `TaskService` | Service | Enforces task assignment rules, status transitions, and notification dispatch. |
| `ProductRepository` | Repository | Direct SQL queries for product CRUD, barcode lookups, and stock updates. |
| `AttendanceRepository`| Repository | Direct SQL queries for active shifts, float tracking, and historical hours. |

---

## ៩. Database Plan (Key Tables & Schema)
The MySQL schema consists of 20 normalized InnoDB tables:
- `roles`, `permissions`, `role_permissions`, `users`, `user_permissions` (Security & RBAC)
- `categories`, `suppliers`, `products`, `stock_movements`, `purchase_orders` (Inventory)
- `customers`, `sales`, `sale_items`, `refunds`, `refund_items`, `held_orders` (POS & Sales)
- `attendance`, `tasks`, `shift_templates`, `notifications` (Operations & Staff)

---

## ១០. Methodology, Sprint Timeline & Deliverables

| Week / Sprint | Objectives & Milestones | Deliverables |
|---|---|---|
| **Sprint 1 (Week 1–4)** | Requirements gathering, OOP domain modeling, ERD design, schema creation | Proposal Document, ERD Diagram, Database Script (`schema.sql`) |
| **Sprint 2 (Week 5–8)** | Flask factory setup, Repository Layer, Domain Models, RBAC decorators | Authentication Blueprint, Repository Unit Tests |
| **Sprint 3 (Week 9–12)** | Service Layer, Sales transaction logic, Inventory deduction, POS UI | Working POS Checkout, Shift Attendance, Task Delegation |
| **Sprint 4 (Week 13–15)**| Multi-currency (KHR/USD), Reports, Test Suite, User Guide, Defense PPTX | Final Report, Codebase, Automated Tests, Demo |

---

## ១១. Expected Results & Acceptance Criteria
1. Fully functional web-based POS running on Python Flask + MySQL.
2. Verified multi-user login with four operational roles and distinct dashboards.
3. Shift-enforced logout blocking: Staff cannot log out without clocking out or manager emergency override.
4. Interactive Task Delegation: Assign tasks by user to user with priority and notifications.
5. 100% pass rate on automated test suite covering authentication, stock deduction, and task workflows.
