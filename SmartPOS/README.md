# SmartPOS — Inventory & Point of Sale Management System

A web-based Point-of-Sale and Inventory Management System built with
Python, Flask, and MySQL, using a layered architecture with RBAC
(role-based access control).

## Architecture

```
Browser -> Flask Routes/Blueprints -> Services -> Repositories -> MySQL
```

- **Routes** (`app/routes/<domain>/`) — receive HTTP requests, call a service, return a template. No business logic or SQL.
- **Services** (`app/services/<domain>/`) — own every business rule: `AuthService` (RBAC decisions), `InventoryService` (products + purchase orders + stock), `SalesService` (checkout + stock deduction as one transaction), `CRMService`, `HeldOrderService`, `AttendanceService`, `TaskService`, `ReportService`, `AnalyticsService`.
- **Repositories** (`app/repositories/<domain>/`) — the only layer that touches MySQL, using parameterized queries.
- **Models** (`app/models/<domain>/`) — plain domain objects (`User`, `Role`, `Permission`, `Product`, `Sale`, `SaleItem`, `Refund`, `RefundItem`, `PurchaseOrder`, `Customer`, `HeldOrder`, `Attendance`, `Task`, `StockMovement`).

RBAC is enforced through a single reusable decorator (`@permission_required("...")` in `app/utils/decorators.py`), backed by a normalized `roles` / `permissions` / `role_permissions` schema rather than a fixed role string.

## Setup

### 1. Create the database

```bash
mysql -u root -p -e "CREATE DATABASE smartpos;"
mysql -u root -p smartpos < sql/schema.sql
```

This creates all 16 tables — including the starter product catalog and RBAC roles/permissions, which are seeded automatically as part of `schema.sql`.

### 2. Configure environment variables

```bash
cp .env.example .env
# then edit .env with your real DB credentials
```

### 3. Install dependencies

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Create demo logins

```bash
python scripts/seed_users.py
```

Creates one account per role, all with password `password123`:

| Role | Email |
|---|---|
| Admin | admin@smartpos.local |
| Admin Assistant | assistant@smartpos.local |
| Inventory Manager | inventory@smartpos.local |
| Cashier | cashier@smartpos.local |

### 5. Run the app

```bash
python main.py
```

Visit `http://localhost:5000` and log in with any of the demo accounts above to see how the sidebar and available actions change per role.

## Telegram notifications (optional)

The app can send low-stock, restock, new-transaction, and password-reset alerts to a Telegram chat — entirely optional. Until configured, everything works normally; notifications just silently skip. See `.env.example` for the setup steps and required variables (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `PUBLIC_BASE_URL`).

## What's implemented

- Role-based authentication (Admin, Admin Assistant, Inventory Manager, Cashier) with a normalized roles/permissions/role_permissions schema and per-user permission overrides
- Password reset via a Telegram-delivered link (no email server required)
- Product management (CRUD) with SKU codes, supplier info, images, barcode generation, and low-stock visibility
- Checkout: multi-item cart, percentage discount, tax, stock validation, automatic stock deduction, QR code payment display, held/resumed orders
- Refunds against a past sale, with automatic stock restoration
- Purchase orders: create, receive (restocks inventory + records cost), cancel
- Customer phone lookup with PII masking (CRM) — only a masked tag like "Sara012" is ever shown in the UI
- Staff management: CRUD, per-user permission overrides, shift assignment, attendance clock in/out + history, task assignment
- Reports: sales/business dashboard, business health, CRM dashboard, best-sellers
- Telegram alerts for new transactions, low stock, and restocks
- Category and supplier directories, managed under Products, that feed real dropdowns on the product form (previously free text / a hardcoded list)
- Shift templates (Admin-managed) that feed the shift dropdown on the staff-edit page (previously a hardcoded list)
- In-app notifications (bell icon, unread badge, mark read / mark all read) — fired automatically on low stock and on task assignment, in addition to the existing Telegram alerts
- CSRF protection (Flask-WTF) on every form and AJAX request in the app, verified against a live database
- Real WTForms validator classes for every form in the app (see app/forms/README.md for the one deliberate scope note on these)
- Downloadable plain-text receipts (thermal-printer width), alongside the existing on-screen HTML receipt
- Staff details page (view-only profile: photo, role, tasks/attendance stats, personal info) — separate from the edit page
- Product cost tracking — editable on create/edit, and automatically kept current when a purchase order is received
- Staff name and email are now editable (previously display-only)
- Category renames cascade to every product using that category, instead of silently orphaning them
- Category icons are a real, per-category database field (picked from a curated dropdown when creating/editing a category) instead of a hardcoded name → icon Python dict that only covered 6 fixed names
- Admin "Force Close" on a stuck-open attendance shift — recovers a staff member who forgot to clock out and would otherwise be permanently locked out of clocking in again

## Project structure

Domain-split layered architecture — see `docs/` for the ERD, class diagram, and architecture diagram.

```
smartpos/
├── app/
│   ├── models/<domain>/         # domain classes
│   ├── repositories/<domain>/   # MySQL access only
│   ├── services/<domain>/       # business logic
│   ├── routes/<domain>/         # Flask blueprints
│   ├── utils/                   # decorators, telegram client
│   ├── templates/
│   └── static/
├── tests/
├── sql/                # schema.sql, seed.sql
├── scripts/            # one-off setup scripts (seed_users.py, import_image_urls.py)
├── main.py
└── requirements.txt
```

## Architecture notes

**Service layer.** Business logic is split into small, single-responsibility
services that compose each other rather than one large class per domain:

- `InventoryService` is a thin orchestrator composing `ProductService`
  (product CRUD + stock), `PurchaseService` (purchase orders), and
  `StockAlertService` (low-stock alerting)
- `SalesService` composes `RefundService` (refund business rules) and
  `RefundRepository`
- `AuthService` composes `PermissionService` (RBAC resolution) and
  `PasswordResetService` (the reset-token lifecycle)
- `DashboardService` assembles the home dashboard's per-permission data
- `services/staff/staff_service.py` exists as a real, tested, standalone
  orchestration class over staff CRUD/role/shift management, but is
  **not** wired into `routes/staff/staff_routes.py` — that route already
  spans staff CRUD, roles, shifts, and the permissions matrix across
  several already-tested methods, and rewiring all of it was a
  meaningfully bigger, riskier change than every other extraction in
  this codebase (each of which moved one self-contained method/section).
  It's ready to be adopted a method at a time.

**Forms / CSRF.** `app/forms/` contains real WTForms validator classes for
every form in the app, matching each route's actual fields and rules —
but they are **not** the primary validation path; each route still uses
its own existing, tested manual validation. CSRF protection (Flask-WTF's
`CSRFProtect`) **is** fully enabled globally and verified end-to-end
against a live database, on every form and every `fetch()` call in the
app, including the checkout page's AJAX flow. See `app/forms/README.md`
for the full reasoning.

**Genuinely no fit.** Five files intentionally have no class — not because
they're unfinished, but because the concept they'd represent doesn't
exist in this schema (`held_order_item.py`, `purchase_item.py` — no
line-items tables for those; `role_permission.py`, `user_permission.py`
— plain junction tables; `password_reset_token.py` — just two columns on
`users`). Each file explains why in its own docstring.

A few old-draft route/repository files also intentionally were **not**
split further during migration, to avoid breaking working `url_for()`
references throughout templates and JS: `routes/inventory/product_routes.py`
still contains the purchase-order routes under the `products` blueprint;
`routes/sales/sales_routes.py` contains checkout, refund, history, and
customer-lookup together under one `sales` blueprint; `routes/staff/staff_routes.py`
contains staff CRUD and the permissions matrix together; `RoleRepository`
and `PermissionRepository` live in one file. None of this affects
functionality — they're organizational choices worth being able to
explain in the defense.

## Consciously out of scope

- Full per-user profile customization beyond photo/name/password (bio, etc.) — role-level RBAC plus per-user permission overrides covers the access-control requirement without it.
- A payment gateway integration — the "QR to pay" flow generates a real scannable QR code but does not verify or confirm payment was actually received.
