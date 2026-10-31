# ApexStore: Complete E-Commerce Management Platform

A modern, production-grade E-Commerce management platform and customer storefront built using standard **HTML5**, **CSS3**, **vanilla JavaScript**, and **Python Django**.

---

## 1. Technology Stack

- **Backend Framework:** Python 3.12+ with Django 5.1
- **Database Engine:** SQL via SQLite (development default; fully compliant with MySQL and PostgreSQL)
- **Templating Engine:** Django Template Language (DTL)
- **Frontend Architecture:** Standard HTML5, custom responsive CSS3, vanilla JavaScript (ES6+) — *No React, Vue, or external frontend framework dependencies*
- **Authentication & Security:** Django Built-in Authentication, Role-Based Access Control (RBAC), CSRF protection, PBKDF2 password hashing, and session management
- **Media & Image Processing:** Pillow (Python Imaging Library)

---

## 2. Architecture & Applications Overview

The codebase is organized into reusable Django applications:

```text
ecommerce/
├── manage.py                     # Django management CLI
├── requirements.txt              # Production and development dependencies
├── db.sqlite3                    # Relational SQLite database
├── config/                       # Project configuration and routing
│   ├── settings.py               # Core settings, context processors, RBAC
│   ├── urls.py                   # Master URL dispatching
│   ├── wsgi.py                   # WSGI deployment gateway
│   └── asgi.py                   # ASGI asynchronous gateway
├── accounts/                     # Users, Profiles, Roles, Addresses, Support Tickets, Audit Logs
├── catalog/                      # Categories, Products, Variants, Images, Reviews
├── cart/                         # Database/Session Carts, Cart Items, Wishlist
├── orders/                       # Order Processing, Coupons, Shipments, Invoices
├── payments/                     # Transactions, Gateway Simulation, Refunds
├── inventory/                    # Atomic Stock Deductions, Inventory Transactions Log
├── dashboard/                    # Administrative Control Panel (Products, Orders, Inventory, CRM)
├── reports/                      # Financial Intelligence, Monthly Charts, CSV Exports
├── templates/                    # Django HTML Templates (Storefront, Dashboard, Accounts, Orders)
├── static/                       # Custom CSS, vanilla JS, icons
│   ├── css/style.css             # Storefront design system
│   ├── css/dashboard.css         # Admin dashboard layout & charts
│   ├── js/main.js                # AJAX Cart, Wishlist, Gallery controls
│   └── js/dashboard.js           # Admin Modals, Stock adjustment forms
└── media/                        # User-uploaded product photos and category images
```

---

## 3. Pre-Seeded Development Accounts

The database comes pre-populated with ready-to-use accounts across each administrative and customer role:

| Role | Username | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin` | `admin123` | Full unrestricted access to all dashboard sections, settings, and staff roles |
| **Manager** | `manager` | `pass123` | Catalog, Order processing, Inventory warehouse, and Financial reports |
| **Inventory Staff** | `inventory_staff` | `pass123` | Product catalog editing, stock adjustments, and replenishment logs |
| **Order Staff** | `order_staff` | `pass123` | Order fulfillment, carrier assignment, tracking code entry, shipments |
| **Support Staff** | `support_staff` | `pass123` | Customer care, inquiry management, and support ticket resolution |
| **Customer 1** | `customer1` | `pass123` | Browsing, shopping cart, checkout, profile, order history, tickets |
| **Customer 2** | `customer2` | `pass123` | Sample customer with active orders in shipment transit |

> **Interactive 1-Tap Login:** On the login page (`/accounts/login/`), you can tap any of the pre-set quick credentials pills (**Admin**, **Manager**, or **Customer**) to instantly autofill both username and password, with a password reveal toggle (👁️) to view credentials.

---

## 4. Setup & Running Instructions (Windows)

### Prerequisites
- Python 3.10+ installed on your Windows machine.

### Step-by-Step Installation

1. Open PowerShell or Command Prompt and navigate to the project directory:
   ```powershell
   cd "C:\Users\Kartik\.gemini\antigravity\scratch\ecommerce"
   ```

2. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\activate
   ```

3. Ensure dependencies are installed:
   ```powershell
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Seed sample data (categories, products, variants, orders, coupons, and test users):
   ```powershell
   python manage.py seed_data
   ```

6. Start the development web server:
   ```powershell
   python manage.py runserver
   ```

7. Access the application in your web browser:
   - **Customer Storefront:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - **Admin Dashboard:** [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
   - **Django Superuser Admin:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 5. End-to-End Workflow Testing Guide

### A. Testing Customer Shopping & Checkout
1. Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) as a guest or log in as `customer1` (`pass123`).
2. Search for products or filter by category (e.g. *Electronics*, *Laptops & Tech*, *Fashion*).
3. Open a product detail page (e.g., *Apex Pro Wireless Headphones*).
4. Choose a variant (e.g., *Midnight Black* or *Silver Frost*) and click **Add to Shopping Cart**. Notice the real-time toast notification and cart badge count update without full page reloads.
5. Navigate to the Cart (`/cart/`). Apply the coupon code **`WELCOME25`** to unlock a 25% discount.
6. Proceed to Checkout (`/orders/checkout/`):
   - Choose **Cash on Delivery** or **Online Payment (Credit / Debit Card)**.
   - For simulated card payment, enter demo digits `4242 4242 4242 4242`.
7. Click **Confirm & Place Order**:
   - The backend locks inventory rows using `select_for_update()` inside an atomic transaction.
   - Stock is immediately deducted and an `InventoryTransaction` record is created.
   - An automated tracking code is generated.
8. View the confirmation screen and click **Print Invoice** to generate a clean, print-styled commercial receipt.

### B. Testing Administrative Dashboard & Inventory Automation
1. Log in as `admin` (`admin123`) and navigate to `/dashboard/`.
2. Inspect the **Executive Dashboard**:
   - Total sales, orders, products, and customer counts are calculated dynamically from SQL records.
   - The monthly revenue bar chart illustrates actual calendar year performance.
   - Low-stock and out-of-stock items are highlighted with immediate restock triggers.
3. Manage Orders (`/dashboard/orders/`):
   - Open an order's detail page.
   - Update its fulfillment status to `Shipped`, specify carrier tracking details, or cancel the order.
   - **Atomic Stock Restoration Test:** When an order is changed to `Cancelled` or `Returned`, the backend automatically restores the exact purchased quantities back to the warehouse catalog.
4. Manage Inventory (`/dashboard/inventory/`):
   - Use the **Adjust Stock** modal to restock or deduct quantities with internal audit notes.
   - Review `/dashboard/inventory/history/` to inspect every logged change with user attribution.
5. Payment Transactions & Refunds (`/dashboard/transactions/`):
   - Inspect real-time payment records across Cash on Delivery and Online simulated card transactions.
   - View payment status badges, provider transaction references, card brand / last4 indicators, and issue refunds directly from the dashboard.
6. Financial Reports & Analytics (`/dashboard/reports/`):
   - View daily, weekly, monthly, and yearly revenue breakdowns.
   - Click **Export All Orders (CSV)** or **Export Inventory (CSV)** to download operational spreadsheets.

---

## 6. Running Automated Tests

Run the full Django test suite verifying inventory locking, coupon logic, RBAC, cart updates, and cancellation workflows:

```powershell
python manage.py test
```

All tests execute inside isolated database transactions and clean up automatically.
