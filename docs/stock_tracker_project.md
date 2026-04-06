# Stock Tracker — Personal Finance Web Application
> Version 1.0 | April 2026

---

## Table of Contents
1. [Requirements Summary](#1-requirements-summary)
2. [System Architecture](#2-system-architecture)
3. [Data Model Design](#3-data-model-design)
4. [API Endpoint Design](#4-api-endpoint-design)
5. [Project Folder Structure](#5-project-folder-structure)
6. [2-Week Sprint Plan](#6-2-week-sprint-plan)

---

## 1. Requirements Summary

### 1.1 Project Goal
A personal web application for tracking Indian stock prices with multiple virtual portfolio simulation, journaling, and Telegram price alerts — all in INR.

### 1.2 Stakeholders
- Single user (personal use only)

### 1.3 Functional Requirements
1. Search and view Indian stock prices (NSE/BSE via yfinance, delayed data)
2. Create up to 10 virtual portfolios, each with a custom starting amount set at creation
3. Simulate buy/sell trades within each portfolio
4. Track portfolio value and P&L in INR per portfolio
5. Set price alerts for stocks — trigger Telegram message when target price is hit (auto-deactivate after trigger)
6. Free-text journal as a simple list of notes

### 1.4 Non-Functional Requirements
- Lightweight, personal-scale performance
- Mobile-first responsive React frontend (designed for mobile, scales up to desktop)
- Stock prices refreshed every 5 minutes via scheduled job

### 1.5 Constraints
- 2-week timeline
- Use UV package manager for python
- Use vite react+ts+tailwind for front end
- Free-tier tools only (yfinance, Telegram Bot API)
- Single user — no authentication required
- Indian stocks only (NSE/BSE)

### 1.6 Integrations
- **yfinance** — NSE/BSE stock data in INR
- **Telegram Bot API** — price alert notifications

### 1.7 Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Backend    | FastAPI (Python)        |
| Frontend   | React + TypeScript + Tailwind CSS (mobile-first) |
| Database   | MongoDB                 |
| Stock Data | yfinance (NSE/BSE)      |
| Alerts     | Telegram Bot API        |
| Scheduler  | APScheduler             |

### 1.8 Success Criteria
- Can create multiple portfolios and simulate buy/sell trades independently
- Portfolio P&L tracked correctly in INR per portfolio
- Price alerts deliver Telegram messages when target price is hit
- Journal notes saved and displayed as a simple list

---

## 2. System Architecture

### 2.1 High-Level Overview

```
  [React + TypeScript Frontend]
            |
       HTTP / REST
            |
   [FastAPI Backend (Python)]
            |
   +---------+---------+----------+
   |                   |          |
[MongoDB]         [yfinance]  [Telegram Bot API]
   |                   |
 Data store      Stock prices
                 (every 5 min)
```

### 2.2 Component Responsibilities

| Component        | Responsibility                                          |
|------------------|---------------------------------------------------------|
| React Frontend   | UI pages — Dashboard, Portfolio, Journal, Alerts        |
| FastAPI Backend  | REST API, business logic, scheduled jobs                |
| MongoDB          | Stores portfolios, trades, journal, alerts, stock cache |
| yfinance         | Fetches NSE/BSE stock prices server-side only           |
| APScheduler      | Polls yfinance every 5 min, checks alert conditions     |
| Telegram Bot API | Sends message when alert condition is met               |

### 2.3 Price Alert Flow

1. APScheduler triggers every 5 minutes
2. Fetch latest prices for all stocks with active alerts via yfinance
3. Update `stock_cache` in MongoDB
4. Check each active alert — if condition met, send Telegram message
5. Set `is_active = false` and record `triggered_at`

---

## 3. Data Model Design

### 3.1 portfolios
```json
{
  "_id":             "ObjectId",
  "name":            "string",
  "starting_amount": "number",
  "current_cash":    "number",
  "created_at":      "datetime"
}
```

### 3.2 trades
```json
{
  "_id":          "ObjectId",
  "portfolio_id": "ObjectId",
  "symbol":       "string",
  "type":         "BUY | SELL",
  "quantity":     "number",
  "price":        "number",
  "traded_at":    "datetime"
}
```

### 3.3 alerts
```json
{
  "_id":          "ObjectId",
  "symbol":       "string",
  "target_price": "number",
  "condition":    "ABOVE | BELOW",
  "is_active":    "boolean",
  "created_at":   "datetime",
  "triggered_at": "datetime | null"
}
```

### 3.4 journal
```json
{
  "_id":        "ObjectId",
  "note":       "string",
  "created_at": "datetime"
}
```

### 3.5 stock_cache
```json
{
  "_id":        "ObjectId",
  "symbol":     "string",
  "last_price": "number",
  "fetched_at": "datetime"
}
```

---

## 4. API Endpoint Design

### 4.1 Portfolio Endpoints

| Method | Endpoint            | Description          |
|--------|---------------------|----------------------|
| GET    | /portfolios         | List all portfolios  |
| POST   | /portfolios         | Create new portfolio |
| GET    | /portfolios/{id}    | Holdings + live P&L  |
| DELETE | /portfolios/{id}    | Delete portfolio     |

**`GET /portfolios/{id}` returns:**
- Each holding: symbol, quantity, avg buy price
- Current price from `stock_cache`
- Unrealized P&L per holding
- Total portfolio value and overall P&L

### 4.2 Trade Endpoints

| Method | Endpoint                    | Description       |
|--------|-----------------------------|-------------------|
| POST   | /portfolios/{id}/buy        | Simulate buy      |
| POST   | /portfolios/{id}/sell       | Simulate sell     |
| GET    | /portfolios/{id}/trades     | Trade history     |

### 4.3 Stock Endpoints

| Method | Endpoint                  | Description               |
|--------|---------------------------|---------------------------|
| GET    | /stocks/search?q=         | Search NSE/BSE stocks     |
| GET    | /stocks/{symbol}/price    | Get latest cached price   |

### 4.4 Alert Endpoints

| Method | Endpoint        | Description      |
|--------|-----------------|------------------|
| GET    | /alerts         | List all alerts  |
| POST   | /alerts         | Create alert     |
| DELETE | /alerts/{id}    | Delete alert     |

### 4.5 Journal Endpoints

| Method | Endpoint        | Description    |
|--------|-----------------|----------------|
| GET    | /journal        | List all notes |
| POST   | /journal        | Add note       |
| DELETE | /journal/{id}   | Delete note    |

---

## 5. Project Folder Structure

### 5.1 Backend (FastAPI)
```
backend/
├── main.py                  # FastAPI app entry point
├── config.py                # MongoDB, Telegram config
├── db.py                    # MongoDB connection
├── scheduler.py             # APScheduler jobs
│
├── models/                  # Pydantic models
│   ├── portfolio.py
│   ├── trade.py
│   ├── alert.py
│   ├── journal.py
│   └── stock_cache.py
│
├── routes/                  # API endpoints
│   ├── portfolio.py
│   ├── trade.py
│   ├── alert.py
│   ├── journal.py
│   └── stock.py
│
└── services/                # Business logic
    ├── portfolio_service.py
    ├── trade_service.py
    ├── alert_service.py
    ├── stock_service.py     # yfinance calls
    └── telegram_service.py
```

### 5.2 Frontend (React + TypeScript)
```
frontend/
└── src/
    ├── pages/
    │   ├── Dashboard.tsx
    │   ├── Portfolio.tsx
    │   ├── Journal.tsx
    │   └── Alerts.tsx
    │
    ├── components/
    │   ├── StockSearch.tsx
    │   ├── HoldingsTable.tsx
    │   ├── TradeForm.tsx
    │   └── AlertForm.tsx
    │
    ├── services/
    │   └── api.ts
    │
    ├── types/               # TypeScript interfaces
    │   ├── portfolio.ts
    │   ├── trade.ts
    │   ├── alert.ts
    │   └── journal.ts
    │
    └── App.tsx
```

### 5.3 Root
```
stock-tracker/
├── backend/
├── frontend/
├── .env                     # Telegram token, MongoDB URI
└── README.md
```

---

## 6. 2-Week Sprint Plan

### Week 1 — Backend

| Day   | Task                                                                 |
|-------|----------------------------------------------------------------------|
| Day 1 | Project setup — FastAPI, MongoDB connection, folder structure, .env  |
| Day 2 | Portfolio CRUD endpoints + Pydantic models                           |
| Day 3 | Trade endpoints — buy/sell logic, cash deduction, holdings calc      |
| Day 4 | Stock service — yfinance integration, stock_cache, search endpoint   |
| Day 5 | Alerts — CRUD endpoints + Telegram bot setup                         |
| Day 6 | APScheduler — price fetch job + alert check job                      |
| Day 7 | Journal endpoints + backend testing (Postman / pytest)               |

### Week 2 — Frontend

| Day    | Task                                                   |
|--------|--------------------------------------------------------|
| Day 8  | React + TypeScript setup, routing, API service layer   |
| Day 9  | Dashboard page — list portfolios, create portfolio     |
| Day 10 | Portfolio page — holdings table, P&L display           |
| Day 11 | Trade form — buy/sell simulation                       |
| Day 12 | Alerts page — create/delete alerts                     |
| Day 13 | Journal page — add/delete notes                        |
| Day 14 | End-to-end testing, bug fixes, cleanup                 |

### Daily Recommendations
- Test each backend endpoint in Postman before building the frontend for that feature
- Keep `.env` updated as each new service is added
- Commit code at end of each day
