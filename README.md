# Full-Stack Ecommerce Platform

A production-ready ecommerce platform built with FastAPI, featuring authentication, product catalog, shopping cart, Stripe payments, order management, admin panel, product reviews, wishlist, shipping addresses, and email notifications.

**Tech stack:** FastAPI · SQLAlchemy · Jinja2 · TailwindCSS · Stripe · SQLite (dev) / PostgreSQL (prod)
---

## ✨ Features

### 🛍️ Shopping Experience
- 100+ real products seeded from DummyJSON
- Search, filter by category, price range, sorting
- Product detail pages with image zoom on hover
- Star ratings and customer reviews (purchase-gated)
- Shopping cart with quantity management
- Wishlist for saving items

### 💳 Payments
- Stripe Checkout integration (hosted payment page)
- Real card payments in test mode
- Payment verification before order creation
- Amazon-style order numbers (`ORD-20260408-A7B2C9`)
- Automatic order confirmation on successful payment

### 📦 Order Management
- Full order lifecycle: Pending → Confirmed → Shipped → Delivered
- Order history with status tracking
- Cancellation and refund support
- Real Stripe refunds via admin panel

### 🔐 Authentication
- User registration with email verification
- JWT tokens stored in secure HTTP-only cookies
- Route protection for both API and HTML pages
- Automatic redirect to login for unauthenticated users

### 🌍 International Support
- USD pricing for global markets
- 26 country dropdown for shipping addresses
- 25+ country phone codes
- US state autocomplete for addresses

### 👤 Admin Panel
- Dashboard with live statistics
- Manage all orders (update status, issue refunds)
- Manage all products
- View all users
- Role-based access control

### 📧 Notifications
- Welcome emails on registration
- Order confirmation emails
- Status update emails
- Refund confirmation emails

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- A Stripe test account (free at stripe.com)

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/raj-store.git
cd raj-store

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Stripe test keys

# Run the app
uvicorn app.main:app --reload
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to see your store.

On first startup, 100 products are automatically seeded from DummyJSON.

### Environment Variables

Create a `.env` file in the project root:

```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SUCCESS_URL=http://127.0.0.1:8000/orders/stripe-success
STRIPE_CANCEL_URL=http://127.0.0.1:8000/cart?error=payment_cancelled

# Stripe (get keys from https://dashboard.stripe.com/test/apikeys)
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_SUCCESS_URL=http://127.0.0.1:8000/orders/stripe-success
STRIPE_CANCEL_URL=http://127.0.0.1:8000/cart?error=payment_cancelled

# Database (defaults to SQLite for local dev)
# DATABASE_URL=postgresql://user:password@host:5432/dbname

# Optional — only used in production
# REDIS_URL=redis://localhost:6379/0
# CACHE_ENABLED=true
# OTEL_ENABLED=true
# OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
# OPENSEARCH_ENABLED=true
# OPENSEARCH_URL=http://localhost:9200
```
### Testing Payments

Use Stripe test card numbers:

- `4242 4242 4242 4242` — Successful payment
- `4000 0000 0000 9995` — Declined card
- Any future expiry date, any CVC, any ZIP

---

## 🏗️ Architecture

Raj Store is a **modular monolith** — one FastAPI application organized into logical modules, sharing one database. This is a deliberate architectural choice for apps of this size, following the "start with a monolith".
```
app/
├── main.py              # App entry, router registration
├── config.py            # Environment-based settings
├── database.py          # SQLAlchemy engine, session
├── dependencies.py      # Auth dependencies (current_user)
├── constants.py         # Countries, states lookup
├── seed_data.py         # Auto-seed products on startup
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic layer
└── routers/             # HTTP endpoints
├── auth.py          # Register, login, logout
├── pages.py         # HTML page routes
├── product.py       # Product CRUD (API)
├── category.py      # Categories
├── cart.py          # Shopping cart
├── order.py         # Orders + Stripe checkout
├── wishlist.py      # Wishlist
├── address.py       # Shipping addresses
├── review.py        # Product reviews
└── admin.py         # Admin dashboard & management
templates/               # Jinja2 HTML templates
├── base.html            # Shared layout with navbar + footer
├── home.html            # Shop grid with filters
├── product_detail.html  # Single product page
├── cart.html            # Shopping cart
├── orders.html          # Order history
├── order_detail.html    # Single order view
├── wishlist.html        # Saved items
├── addresses.html       # Manage addresses
└── admin/               # Admin panel templates
```

### Data Model
```
User ──── Cart ──── CartItem ──── Product ──── Category
│                                  │
├───── Order ──── OrderItem ───────┘
│
├───── Address
├───── Wishlist ──── Product
└───── CustomerReview ──── Product
```

---

## 🛠️ Tech Stack

| Layer          | Technology                    |
|----------------|-------------------------------|
| Backend        | FastAPI + Python 3.11         |
| ORM            | SQLAlchemy 2.x                |
| Database       | SQLite (dev) / PostgreSQL (prod) |
| Templates      | Jinja2                        |
| Styling        | TailwindCSS (CDN)             |
| Auth           | JWT via python-jose           |
| Password hash  | bcrypt via passlib            |
| Payments       | Stripe Checkout               |
| Cache (planned)| Redis                         |
| Observability (planned) | OpenTelemetry + OpenSearch |

---

## 🗺️ Roadmap

### Coming soon

- [ ] PostgreSQL migration for production
- [ ] Redis caching layer for product listings
- [ ] OpenTelemetry instrumentation (traces)
- [ ] OpenSearch log aggregation
- [ ] Prometheus metrics + Grafana dashboards
- [ ] Real email delivery via Resend
- [ ] Stripe webhooks for reliable payment processing
- [ ] Deployment to AWS EKS with Terraform
- [ ] CI/CD pipeline via GitHub Actions
- [ ] Custom domain + HTTPS via cert-manager

### Future ideas

- [ ] Shopping during checkout (guest checkout)
- [ ] Product variants (size, color)
- [ ] Multi-seller marketplace
- [ ] AI-powered product recommendations
- [ ] Multi-language support

---

## 📸 Screenshots

<details>
<summary>Click to expand</summary>

### Home page with filters
![Home](./docs/home.png)

### Product detail page
![Product](./docs/product.png)

### Cart & checkout
![Cart](./docs/cart.png)

### Admin dashboard
![Admin](./docs/admin.png)

</details>

---

## 📄 License

MIT

---

## 👤 Author

**Rajasekhar Reddy**

- Senior DevOps Engineer · 7+ years experience
- Multi-cloud: AWS · Azure · GCP · Stackit · IONOS
- Certifications: CKA · Azure Administrator · AWS Fundamentals
- Website: [rajasekharcloud.com](https://rajasekharcloud.com)

Built with ☕ and curiosity.