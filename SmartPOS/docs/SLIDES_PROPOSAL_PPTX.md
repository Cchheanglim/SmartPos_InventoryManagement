# Proposal Defense Presentation Slides (PPTX Outline)
## Advanced OOP with Python — Project R&D Defense
### Lecturer: SEK SOCHEAT | Target Duration: 8–10 Minutes (12 Slides)

---

### Slide 1: Project Title & Team
- **Title:** SmartPOS — Intelligent Inventory & Point-of-Sale System
- **Subtitle:** Layered Architecture with Python, Flask, and MySQL
- **Course:** Advanced Object-Oriented Programming with Python
- **Lecturer:** SEK SOCHEAT
- **Team Members:**
  1. Student 1 — Project Lead & Requirements Analyst
  2. Student 2 — Backend Architecture & Domain Modeling
  3. Student 3 — Database Design & Repository Layer
  4. Student 4 — Frontend UI, Validation & Automated Testing

---

### Slide 2: Problem Statement & Motivation
- **The Context:** Convenience stores & mini-marts relying on disconnected spreadsheets or manual paper logs.
- **Critical Failure Points:**
  - Stock desynchronization leading to overselling and inventory shrinkage.
  - Cashiers closing shifts without till reconciliation, causing untracked cash drift.
  - Absence of operational task delegation (restocking, inventory counts) among staff.
  - Overly broad access permissions exposing financial records to junior staff.
- **Core Motivation:** Build an object-oriented, web-based solution enforcing operational discipline and data integrity.

---

### Slide 3: Project Objectives & Success Criteria
- **General Objective:** Design, build, and test an enterprise-grade retail POS system applying Advanced OOP paradigms in Python, Flask, and MySQL.
- **Specific Measurable Objectives:**
  - 4-layer architecture: Models, Repositories, Services, Blueprints (SRP adhered).
  - Normalized 4-table RBAC schema with a reusable `@permission_required` decorator.
  - Shift-enforced cash reconciliation blocking logout if attendance shift is open.
  - Task assignment engine with user-to-user delegation, priority tags, and due dates.
  - 100% pass rate across 15+ automated unit and service tests.

---

### Slide 4: Project Scope & Boundaries
- **What is In Scope:**
  - Authentication, password hashing, and granular Role-Based Access Control.
  - Inventory management with barcode lookup and low-stock alerts.
  - Multi-currency checkout (USD / KHR @ 4,100 KHR/USD) and split payments (Cash / ABA QR).
  - Shift attendance, till float count, and supervisor emergency override.
  - Team task management and analytical reporting.
- **What is Excluded:**
  - Physical thermal printer hardware drivers (standard browser print formatting used).
  - Multi-branch cloud replication (single-store deployment focus).

---

### Slide 5: Target Users & Use Cases
- **Store Owner / General Admin:** System configuration, sales analytics, employee role administration.
- **Assistant Manager / Supervisor:** Daily shift supervision, task delegation, stock reception, emergency register overrides.
- **Inventory Manager:** Purchase orders, supplier tracking, inventory reconciliation.
- **Cashier:** Terminal clock-in with starting cash, sales processing, cart parking, shift clock-out with drawer count.

---

### Slide 6: System Features & Module Breakdown
- **Module 1: Authentication & Access:** Password hashing with salt, session management, RBAC enforcement.
- **Module 2: Point of Sale:** Barcode scanning, dual-currency calculation, held carts, digital receipts.
- **Module 3: Inventory & Supply:** Real-time stock decrements, low-stock threshold triggers, purchase orders.
- **Module 4: Staff Operations:** Shift clock-in/out float reconciliation, logout protection, task delegation.
- **Module 5: Analytics & Reports:** Daily sales summaries, cashier turnover, stock valuation reports.

---

### Slide 7: Advanced OOP Design & Patterns
- **Domain Models:** Encapsulated domain entities (`User`, `Product`, `Sale`, `Task`, `Attendance`).
- **Repository Pattern:** Isolates MySQL queries into dedicated repository classes (`ProductRepository`, `TaskRepository`).
- **Service Layer:** Houses all business rules and atomic transactions (`SalesService`, `TaskService`, `AttendanceService`).
- **Composition & Dependency Injection:** Services receive repositories via composition, ensuring testability with mocks.

---

### Slide 8: System Architecture
```
[Browser Client: Jinja2 Templates + CSS + JS Fetch]
                      │
                      ▼ HTTP Requests
[Flask Blueprints / Routes] -> Enforces RBAC (@permission_required)
                      │
                      ▼ Service Calls
[Service Layer] -> Coordinates Business Logic & Transactions
                      │
                      ▼ Entity Manipulation
[Repository Layer] -> Executes Parameterized MySQL Queries
                      │
                      ▼ Database I/O
[MySQL Database (InnoDB Engine)] -> Tables with Foreign Keys & ACID
```

---

### Slide 9: Database Plan & ERD Overview
- **Storage Engine:** MySQL 8.0 InnoDB with strict foreign key constraints.
- **Core Entity Groups:**
  - Security: `roles`, `permissions`, `role_permissions`, `users`, `user_permissions`
  - Catalog: `categories`, `suppliers`, `products`, `stock_movements`, `purchase_orders`
  - Sales: `customers`, `sales`, `sale_items`, `refunds`, `held_orders`
  - Operations: `attendance`, `tasks`, `notifications`, `shift_templates`
- **Data Protection:** No raw string concatenation; all queries use parameterized placeholders (`%s`).

---

### Slide 10: R&D Methodology & Sprint Timeline
- **Sprint 1 (Weeks 1–4):** Domain modeling, ERD design, schema generation (`schema.sql`).
- **Sprint 2 (Weeks 5–8):** Flask factory setup, Repository Layer, Domain Models, RBAC decorator.
- **Sprint 3 (Weeks 9–12):** Service Layer, checkout transactions, shift float enforcement, task board.
- **Sprint 4 (Weeks 13–15):** Testing suite execution, UI refinement, Final Report & Defense PPTX preparation.

---

### Slide 11: Expected Outputs & Demonstration Plan
- **Primary Deliverables:**
  - Clean, functional Flask + MySQL web application codebase.
  - Complete documentation conforming to academic standards (Proposal, Report, Manual).
  - Automated test suite validating business rules.
- **Live Demo Flow:**
  - Login as Cashier ➔ Enter starting float ➔ Process multi-currency sale with barcode scan.
  - Attempt unauthorized logout ➔ Demonstrate shift blocking & drawer count reconciliation.
  - Login as Admin ➔ Assign high-priority task to Cashier ➔ Verify notification and completion.

---

### Slide 12: Q&A and Lecturer Feedback
- Open floor for technical evaluation, architecture defense, and Lecturer suggestions.
- **Key Discussion Points:**
  - Concurrency handling during peak retail checkouts.
  - Decoupling of attendance shift states from web session lifecycles.
  - Extensibility of the Repository Layer for cloud database backends.
