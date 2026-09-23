# Final Defense Presentation Slides (PPTX Outline)
## Advanced OOP with Python — Final Project Defense
### Lecturer: SEK SOCHEAT | Target Duration: 12–15 Minutes (16 Slides)

---

### Group 1: Opening & Context (Slides 1–2)
#### Slide 1: Title & Presentation Introduction
- **Project:** SmartPOS — Advanced OOP Retail Management System
- **Technologies:** Python 3, Flask, MySQL, PyMySQL
- **Course:** Advanced OOP with Python | Lecturer: SEK SOCHEAT
- **Team Roles:** Lead Analyst, Backend OOP Architect, Database Engineer, UI/Test Engineer

#### Slide 2: Project Background & Problem Addressed
- **The Problem:** Fragmented retail management leads to inventory shrinkage, cash discrepancies at shift close, untracked staff duties, and unauthorized privilege escalation.
- **The Solution:** A web-based POS developed with clean OOP architecture, repository patterns, shift-enforced attendance, and granular RBAC.

---

### Group 2: Architectural & OOP Design (Slides 3–6)
#### Slide 3: System Architecture & Data Flow
- Visual 4-layer flow:
  `Client (Jinja2/CSS) ➔ Flask Blueprints (Routes) ➔ Service Layer ➔ Repository Layer ➔ MySQL Database`
- Clear separation between presentation, transactional logic, and persistence.

#### Slide 4: Advanced OOP Patterns Implemented
- **Domain Modeling:** Self-contained domain entities protecting invariants (`is_completed`, `is_open`, `duration_hours`).
- **Repository Pattern:** Parameterized SQL queries completely isolated from business services.
- **Service Layer Pattern:** Atomic business transactions and workflow orchestration.
- **RBAC Decorator Pattern:** Custom `@permission_required` enforcing granular route security.

#### Slide 5: Core Domain Class Relationships
- Class diagram showcasing `User`, `Role`, `Permission`, `Product`, `Sale`, `Task`, `Attendance`.
- Association between `User` and `Task` (assigned_to and assigned_by).
- Association between `User` and `Attendance` (shift tracking and till float reconciliation).

#### Slide 6: Database Relational Design (ERD)
- 20 normalized InnoDB tables with foreign key constraints.
- Elimination of redundant data through relational normalization (3NF).
- Transactional safety: InnoDB row-level locking for inventory deductions.

---

### Group 3: Core Implementation & Features (Slides 7–10)
#### Slide 7: Point-of-Sale (POS) & Multi-Currency Engine
- Barcode scanning & quick-search product catalog.
- Dual-currency calculations (USD and Cambodian Riel at 4,100 KHR/USD).
- Split payment support (Cash + ABA PayWay QR) and held cart functionality.

#### Slide 8: Atomic Inventory Checkout Transaction
- Single ACID transaction: Sales receipt creation, stock validation, inventory decrement, stock movement log, and customer points update.
- Complete rollback if stock is insufficient or database connection drops.

#### Slide 9: Shift-Enforced Attendance & Logout Protection
- Cashiers must clock in with an opening cash float.
- Terminal intercepts logout if shift is active: Requires drawer cash count or Supervisor Emergency Override.
- Automated calculation of expected vs. counted cash with discrepancy logging.

#### Slide 10: Task Delegation & Management Engine
- Supervisors assign operational tasks with assigner, assignee, priority (`urgent`, `high`, `medium`, `low`), and target due date.
- Real-time in-app notification dispatch to assignee.
- Filterable task board with status tracking and completion audits.

---

### Group 4: Testing & Verification (Slides 11–12)
#### Slide 11: Testing Methodology & Test Suite
- Unit & service test coverage using Python `unittest`.
- Automated test suites:
  - `test_auth_service.py` (Login, password hashing, permissions)
  - `test_sales_service.py` (Stock deduction, transaction rollbacks)
  - `test_task_service.py` (Delegation, priority, completion rules)
  - `test_attendance_service.py` (Clock-in, float calculation, shift closure)

#### Slide 12: Test Results & Quality Metrics
- 100% test execution pass rate (18 test cases, 0 failures).
- Security audit: Elimination of SQL injection vulnerabilities via parameterized queries.
- Clean code analysis: Modular file organization and type hints.

---

### Group 5: Live Demonstration (Slides 13–14)
#### Slide 13: Live Demo Script & Workflow
1. **Admin View:** Review sales dashboard, inventory alerts, and delegate an urgent restocking task.
2. **Cashier View:** Clock in with starting float, receive task notification, process a dual-currency sale.
3. **Logout Interception:** Attempt sign out while clocked in ➔ show blocked dialog ➔ enter counted cash ➔ clock out and exit.

#### Slide 14: System Screenshots & Fallback Evidence
- Backup screenshots of the POS interface, task board, till count modal, and analytical reports.

---

### Group 6: Conclusion & Future Work (Slides 15–16)
#### Slide 15: Key Achievements & Learning Outcomes
- Successfully implemented commercial-ready software using Advanced OOP standards.
- Deepened understanding of layered architecture, repository isolation, and ACID database integrity.
- Delivered real-world operational security and staff discipline features.

#### Slide 16: Future Enhancements & Q&A
- Future Work: Hardware receipt printer drivers, offline PWA synchronization, AI-powered inventory forecasting.
- Thank you to Lecturer SEK SOCHEAT!
- Questions & Discussion.
