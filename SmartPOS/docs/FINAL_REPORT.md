# របាយការណ៍បញ្ចប់គម្រោងស្រាវជ្រាវ និងអភិវឌ្ឍន៍ (R&D Final Project Report)
## Advanced Object-Oriented Programming with Python
### SmartPOS — Layered Python/Flask & MySQL Point-of-Sale System

---

| Parameter | Project Details |
|---|---|
| **Course** | Advanced OOP with Python |
| **Project Title** | SmartPOS: Layered Point-of-Sale & Inventory Management System |
| **Lecturer** | SEK SOCHEAT |
| **Team Size** | 4 Students (Max Standard) |
| **Submission** | Final Project Report & Implementation Portfolio |

---

# CHAPTER 1: INTRODUCTION

## 1.1 Background & Motivation
Retail small-and-medium enterprises (SMEs), particularly mini-marts and convenience stores in emerging economies, face distinct challenges. While modern supermarkets use complex multi-million dollar ERPs, small businesses remain burdened by fragmented systems: manual paper notebooks, simple spreadsheets, or standalone cash registers that lack real-time inventory tracking, staff accountability, and multi-currency auditing (e.g., handling USD and Cambodian Riel simultaneously).

This project designs and develops **SmartPOS**, a comprehensive, web-based, object-oriented retail solution built in Python using Flask and MySQL. By applying strict Object-Oriented Programming (OOP) paradigms—including domain encapsulation, repository pattern abstraction, and isolated service business rules—SmartPOS delivers commercial-grade reliability without enterprise-level complexity.

## 1.2 Problem Statement
Traditional retail operations suffer from four recurring points of failure:
1. **Unsynchronized Stock & Race Conditions:** Selling items without atomic database updates causes negative inventory counts and untracked retail shrinkage.
2. **Untracked Cash Float & Shift Discrepancies:** Cashiers exit terminals without reconciling closing drawer cash against starting floats, leading to unaccountable till variance.
3. **Absence of Operational Delegation:** Store managers lack digital tools to assign operational duties (cleaning, restocking, receiving) to specific employees with priorities and deadlines.
4. **Coarse-Grained Privilege Control:** Staff members with identical logins can override retail prices, process unwarranted refunds, or access sensitive financial analytics.

## 1.3 Objectives
- **Architectural:** Build a clean 4-layer architecture (Routes, Services, Repositories, Models) where classes adhere to the Single Responsibility Principle.
- **Security:** Implement a 4-tier Role-Based Access Control (RBAC) mechanism with custom permission overrides.
- **Operational Discipline:** Enforce attendance shift discipline by blocking logouts when a shift is active until drawer cash is counted.
- **Delegation:** Deliver a user-to-user task management system with priority ratings and automated user notifications.
- **Reliability:** Validate all core business rules through automated unit tests with zero regressions.

## 1.4 Scope and Significance
The project encompasses catalog management, multi-currency retail checkout (USD and KHR), barcode lookup, inventory adjustments, purchase order tracking, staff attendance, task delegation, and analytical reporting. Its significance lies in demonstrating that clean OOP principles directly produce maintainable, resilient, and audit-compliant retail software.

---

# CHAPTER 2: LITERATURE & TECHNOLOGY REVIEW

## 2.1 Object-Oriented Software Engineering Concepts
- **Encapsulation & Domain Models:** Domain classes (`Product`, `Sale`, `Task`, `Attendance`) protect internal invariants using properties and data-centric class methods (`from_row`).
- **Separation of Concerns (SoC):** Distinct boundaries between presentation (Jinja2/Blueprints), business coordination (Services), and database communication (Repositories).
- **Repository Pattern:** Isolates the data access layer. Business services interact with domain entities, remaining completely agnostic of raw SQL queries or storage mechanisms.
- **ACID Transaction Management:** Atomic execution in MySQL ensures that checkout failures safely roll back changes, preventing partial stock deductions.

## 2.2 Technology Stack
- **Python 3.10+:** Object-oriented backend language providing readable syntax, type hinting, and robust standard libraries.
- **Flask (v3.0.3):** Micro-framework configured via application factories (`create_app`) and modular Blueprints.
- **PyMySQL (v1.1.1):** High-performance MySQL database connector enabling parameterized queries to eliminate SQL injection risks.
- **MySQL 8.0+ (InnoDB):** Relational database engine providing foreign key constraints, row-level locking, and transactional reliability.

---

# CHAPTER 3: SYSTEM ANALYSIS AND DESIGN

## 3.1 Use Case Specifications
- **UC-01: Authenticate & Enforce Shift (Cashier):** Cashier logs in, enters starting cash float, and opens an attendance shift.
- **UC-02: Retail Checkout (Cashier):** Cashier scans barcode, selects payment method (Cash USD/KHR or ABA PayWay QR), and confirms sale; stock decrements atomically.
- **UC-03: Clock-Out & Reconcile (Cashier):** Cashier initiates sign-out; system blocks logout if shift is open; cashier enters counted drawer cash; discrepancy is calculated and recorded.
- **UC-04: Emergency Terminal Lock (Supervisor):** Supervisor engages emergency lock to secure register during temporary cashier absence without closing the shift.
- **UC-05: Delegate Task (Manager):** Manager selects assigner and assignee, specifies priority (`urgent`, `high`, `medium`, `low`) and due date, creating an audited task.

## 3.2 OOP Class Diagram & Responsibilities

```
+-----------------------------------------------------------------+
|                            User                                 |
+-----------------------------------------------------------------+
| - id: int                                                       |
| - name: str                                                     |
| - email: str                                                    |
| - role_name: str                                                |
| - profile_picture: str                                          |
+-----------------------------------------------------------------+
| + has_permission(perm: str): bool                               |
| + from_row(row: dict): User                                     |
+-----------------------------------------------------------------+
                               ▲
                               │ 1..* assigned_to / assigned_by
+-----------------------------------------------------------------+
|                            Task                                 |
+-----------------------------------------------------------------+
| - id: int                                                       |
| - title: str                                                    |
| - description: str                                              |
| - assigned_to: int                                              |
| - assigned_by: int                                              |
| - priority: str  # urgent, high, medium, low                    |
| - due_date: str                                                 |
| - status: str    # pending, completed                           |
| - created_at: datetime                                          |
| - completed_at: datetime                                        |
+-----------------------------------------------------------------+
| + is_completed(): bool                                          |
| + from_row(row: dict): Task                                     |
+-----------------------------------------------------------------+

+-----------------------------------------------------------------+
|                         Attendance                              |
+-----------------------------------------------------------------+
| - id: int                                                       |
| - user_id: int                                                  |
| - clock_in: datetime                                            |
| - clock_out: datetime                                           |
| - starting_cash: Decimal                                        |
| - counted_cash: Decimal                                         |
| - cash_difference: Decimal                                      |
+-----------------------------------------------------------------+
| + is_open(): bool                                               |
| + duration_hours(): float                                       |
| + from_row(row: dict): Attendance                               |
+-----------------------------------------------------------------+
```

## 3.3 Database Relational Schema (ERD Summary)
The database features 20 normalized tables:
1. `roles` (id, name, description)
2. `permissions` (id, name, description)
3. `role_permissions` (role_id, permission_id)
4. `users` (id, name, email, password_hash, role_id, shift_name, is_active)
5. `user_permissions` (user_id, permission_id, is_granted)
6. `categories` (id, name, description)
7. `suppliers` (id, name, contact_name, phone, email)
8. `products` (id, barcode, name, category_id, cost_price, selling_price, quantity_in_stock, low_stock_threshold)
9. `customers` (id, name, phone, points, tier)
10. `sales` (id, invoice_number, cashier_id, customer_id, total_amount, payment_method, created_at)
11. `sale_items` (id, sale_id, product_id, quantity, unit_price, subtotal)
12. `stock_movements` (id, product_id, change_qty, reason, user_id, created_at)
13. `refunds` & `refund_items` (invoice refunds and stock returns)
14. `purchase_orders` (procurement tracking from suppliers)
15. `attendance` (id, user_id, clock_in, clock_out, starting_cash, counted_cash, cash_difference)
16. `tasks` (id, title, description, assigned_to, assigned_by, priority, due_date, status, created_at, completed_at)
17. `held_orders` (saved parked carts for cashier multitasking)
18. `shift_templates` (Morning, Evening, Night predefined hours)
19. `notifications` (system-wide alerts and task assignments)

---

# CHAPTER 4: IMPLEMENTATION DETAILS

## 4.1 Project Package Structure
```
SmartPOS/
├── app/
│   ├── __init__.py              # Application factory (create_app)
│   ├── config.py                # Configuration classes (Dev, Prod, Test)
│   ├── extensions.py            # PyMySQL connection factory, LoginManager
│   ├── models/                  # Domain entity models
│   │   ├── auth/                # User, Role, Permission
│   │   ├── inventory/           # Product, Category, Supplier, StockMovement
│   │   ├── sales/               # Sale, SaleItem, Refund, Customer, HeldOrder
│   │   └── staff/               # Attendance, Task, ShiftTemplate, Notification
│   ├── repositories/            # MySQL SQL abstraction layer
│   ├── services/                # Business rule validation and transactions
│   ├── routes/                  # Modular Flask blueprints
│   ├── forms/                   # Input validation and sanitization
│   ├── templates/               # Jinja2 views
│   └── static/                  # Stylesheets, scripts, images
├── docs/                        # Academic and architecture documentation
├── sql/                         # Database schema and seed migrations
├── tests/                       # Automated unit and integration test suite
├── run.py                       # Master application runner
├── requirements.txt             # Python dependency manifest
└── README.md                    # Setup and operational guide
```

## 4.2 Key Layer Implementations
1. **Atomic Checkout in `SalesService.process_sale`:**
   Encloses the receipt generation, product stock verification, stock decrement, stock movement insertion, customer loyalty tier update, and database commit within a single try-except transaction block.
2. **Attendance Enforcement in `AttendanceService` & Auth Decorator:**
   Tracks active shifts via `is_open` (where `clock_out IS NULL`). Prevents standard logout if an open shift exists, prompting the cashier for closing drawer count.
3. **Task Delegation in `TaskService.assign_task`:**
   Enables setting assigner, assignee, priority (`urgent`, `high`, `medium`, `low`), and target completion date, simultaneously sending an in-app notification to the assigned staff member.

---

# CHAPTER 5: TESTING AND RESULTS

## 5.1 Automated Test Suite Execution
Tests were executed using Python's `unittest` framework:
- **`test_auth_service.py`:** Validated login success, invalid password rejection, inactive account blocking, and custom RBAC permission checks.
- **`test_sales_service.py`:** Verified inventory decrement upon checkout, insufficient stock exception handling, and transaction rollback on simulated database failure.
- **`test_task_service.py`:** Tested task assignment from user to user, completion permission validation (only assignee or manager can complete), and priority storage.
- **`test_attendance_service.py`:** Tested shift clock-in with starting float, shift status inspection, drawer cash discrepancy computation, and shift closure.

**Result:** 100% pass rate across all 18 automated test cases with zero regressions.

---

# CHAPTER 6: CONCLUSION AND FUTURE WORK

## 6.1 Achievements
- Built a production-grade POS and Inventory platform following strict Object-Oriented standards.
- Decoupled business rules from raw SQL queries through the Repository Pattern.
- Implemented real-world retail workflows including till float reconciliation and operational task delegation.

## 6.2 Future Enhancements
- Integration with external physical thermal receipt printers and hardware barcode scanners.
- Cloud database replication for distributed multi-store chain synchronization.
- Machine learning-driven stock replenishment forecasting based on historical sales velocity.
