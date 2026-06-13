# Smart CRM SaaS

A web-based operating system for small shops and small industries. Phase 1 includes authentication, product management, and inventory management.

## Phase 1 Features

- JWT authentication with role-aware users
- Product categories and products
- Cost price, selling price, SKU, and active status
- Inventory stock records
- Low stock alerts
- Stock movement history
- AI guidance endpoint that stays inside CRM data and returns the required business format
- React dashboard with protected screens

## Tech Stack

- Backend: FastAPI, PostgreSQL, SQLAlchemy, JWT
- Frontend: React, Vite, React Router

## Project Structure

```text
backend/
  app/
    core/          # config, db, security
    modules/
      auth/        # auth schemas/routes/service
      products/    # product models/routes/service
      inventory/   # stock models/routes/service
      ai/          # CRM-safe guidance service
    main.py
frontend/
  src/
    api/           # HTTP client and API wrappers
    auth/          # auth context and route guard
    pages/         # dashboard screens
    components/    # shared layout
```

## Backend Setup

1. Create a PostgreSQL database:

```bash
createdb smart_crm
```

2. Configure environment:

```bash
cp backend/.env.example backend/.env
```

Update `DATABASE_URL` if your PostgreSQL credentials differ.

3. Install dependencies and run:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

## First Use

Register an owner account from the frontend, then sign in. The owner role can manage products and inventory.

## API Endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/products/categories`
- `GET /api/v1/products/categories`
- `POST /api/v1/products`
- `GET /api/v1/products`
- `GET /api/v1/products/{product_id}`
- `PUT /api/v1/products/{product_id}`
- `DELETE /api/v1/products/{product_id}`
- `POST /api/v1/inventory/stock`
- `GET /api/v1/inventory/stock`
- `GET /api/v1/inventory/alerts/low-stock`
- `POST /api/v1/inventory/movements`
- `GET /api/v1/inventory/movements`
- `GET /api/v1/ai/inventory-insight`

## Docker PostgreSQL

```bash
docker compose up -d db
```

