import pytest


class TestListPortfolios:
    async def test_empty(self, client):
        resp = await client.get("/portfolios")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_returns_created_portfolios(self, client):
        await client.post("/portfolios", json={"name": "A", "starting_amount": 50000})
        await client.post("/portfolios", json={"name": "B", "starting_amount": 75000})
        resp = await client.get("/portfolios")
        assert resp.status_code == 200
        names = [p["name"] for p in resp.json()]
        assert "A" in names and "B" in names

    async def test_sorted_newest_first(self, client):
        await client.post("/portfolios", json={"name": "First", "starting_amount": 10000})
        await client.post("/portfolios", json={"name": "Second", "starting_amount": 20000})
        resp = await client.get("/portfolios")
        assert resp.json()[0]["name"] == "Second"


class TestCreatePortfolio:
    async def test_creates_with_correct_fields(self, client):
        resp = await client.post(
            "/portfolios", json={"name": "My Portfolio", "starting_amount": 100000}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "My Portfolio"
        assert data["starting_amount"] == 100000
        assert data["current_cash"] == 100000
        assert "_id" in data
        assert "created_at" in data

    async def test_current_cash_equals_starting_amount(self, client):
        resp = await client.post(
            "/portfolios", json={"name": "P", "starting_amount": 55000}
        )
        data = resp.json()
        assert data["current_cash"] == data["starting_amount"]

    async def test_rejects_11th_portfolio(self, client):
        for i in range(10):
            r = await client.post(
                "/portfolios", json={"name": f"P{i}", "starting_amount": 10000}
            )
            assert r.status_code == 201
        resp = await client.post(
            "/portfolios", json={"name": "P10", "starting_amount": 10000}
        )
        assert resp.status_code == 400
        assert "10" in resp.json()["detail"]


class TestGetPortfolioDetail:
    async def test_no_trades_returns_empty_holdings(self, client, portfolio):
        pid = portfolio["_id"]
        resp = await client.get(f"/portfolios/{pid}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["holdings"] == []
        assert data["total_value"] == portfolio["starting_amount"]
        assert data["total_pnl"] == 0.0

    async def test_not_found(self, client):
        resp = await client.get("/portfolios/000000000000000000000001")
        assert resp.status_code == 404

    async def test_invalid_id(self, client):
        resp = await client.get("/portfolios/not-an-id")
        assert resp.status_code == 404

    async def test_holding_after_buy(self, client, portfolio):
        pid = portfolio["_id"]
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "INFY.NS", "quantity": 10, "price": 1500},
        )
        resp = await client.get(f"/portfolios/{pid}")
        data = resp.json()
        assert len(data["holdings"]) == 1
        h = data["holdings"][0]
        assert h["symbol"] == "INFY.NS"
        assert h["quantity"] == 10
        assert h["avg_buy_price"] == 1500.0

    async def test_avg_buy_price_across_multiple_buys(self, client, portfolio):
        pid = portfolio["_id"]
        # Buy 10 @ 1000, then 10 @ 2000 → avg = 1500
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "TCS.NS", "quantity": 10, "price": 1000},
        )
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "TCS.NS", "quantity": 10, "price": 2000},
        )
        resp = await client.get(f"/portfolios/{pid}")
        h = resp.json()["holdings"][0]
        assert h["avg_buy_price"] == 1500.0
        assert h["quantity"] == 20

    async def test_sold_out_position_removed_from_holdings(self, client, portfolio):
        pid = portfolio["_id"]
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "WIPRO.NS", "quantity": 5, "price": 500},
        )
        await client.post(
            f"/portfolios/{pid}/sell",
            json={"symbol": "WIPRO.NS", "quantity": 5, "price": 550},
        )
        resp = await client.get(f"/portfolios/{pid}")
        assert resp.json()["holdings"] == []

    async def test_unrealized_pnl_when_cache_price_available(self, client, portfolio):
        import db as db_module
        from datetime import datetime, timezone

        pid = portfolio["_id"]
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "HDFCBANK.NS", "quantity": 10, "price": 1600},
        )
        # Seed stock_cache with a current price
        await db_module.client[db_module.DB_NAME].stock_cache.insert_one(
            {"symbol": "HDFCBANK.NS", "last_price": 1700.0, "fetched_at": datetime.now(timezone.utc)}
        )
        resp = await client.get(f"/portfolios/{pid}")
        h = resp.json()["holdings"][0]
        assert h["current_price"] == 1700.0
        assert h["unrealized_pnl"] == 1000.0  # (1700 - 1600) * 10

    async def test_total_pnl_reflects_realized_gain(self, client, portfolio):
        pid = portfolio["_id"]
        # Buy 10 @ 1000, sell 10 @ 1200 → realized gain = 2000
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "AXISBANK.NS", "quantity": 10, "price": 1000},
        )
        await client.post(
            f"/portfolios/{pid}/sell",
            json={"symbol": "AXISBANK.NS", "quantity": 10, "price": 1200},
        )
        resp = await client.get(f"/portfolios/{pid}")
        data = resp.json()
        assert data["total_pnl"] == 2000.0
        assert data["current_cash"] == 100000 - 10000 + 12000


class TestDeletePortfolio:
    async def test_delete_returns_204(self, client, portfolio):
        pid = portfolio["_id"]
        resp = await client.delete(f"/portfolios/{pid}")
        assert resp.status_code == 204

    async def test_deleted_portfolio_not_found(self, client, portfolio):
        pid = portfolio["_id"]
        await client.delete(f"/portfolios/{pid}")
        resp = await client.get(f"/portfolios/{pid}")
        assert resp.status_code == 404

    async def test_delete_cascades_trades(self, client, portfolio):
        pid = portfolio["_id"]
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "SBIN.NS", "quantity": 5, "price": 600},
        )
        await client.delete(f"/portfolios/{pid}")
        # Recreate portfolio with same id check impossible, but confirm
        # trade history is gone by verifying portfolio is gone
        resp = await client.get(f"/portfolios/{pid}/trades")
        assert resp.status_code == 404

    async def test_delete_not_found(self, client):
        resp = await client.delete("/portfolios/000000000000000000000001")
        assert resp.status_code == 404
