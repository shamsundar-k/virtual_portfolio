import pytest


class TestBuy:
    async def test_buy_returns_trade(self, client, portfolio):
        pid = portfolio["_id"]
        resp = await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "reliance.ns", "quantity": 5, "price": 2800},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["type"] == "BUY"
        assert data["symbol"] == "RELIANCE.NS"  # uppercased
        assert data["quantity"] == 5
        assert data["price"] == 2800
        assert data["portfolio_id"] == pid

    async def test_buy_deducts_cash(self, client, portfolio):
        pid = portfolio["_id"]
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "TCS.NS", "quantity": 10, "price": 3000},
        )
        resp = await client.get(f"/portfolios/{pid}")
        assert resp.json()["current_cash"] == 100000 - 30000

    async def test_buy_insufficient_cash(self, client, portfolio):
        pid = portfolio["_id"]
        resp = await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "TCS.NS", "quantity": 1000, "price": 3000},
        )
        assert resp.status_code == 400
        assert "Insufficient cash" in resp.json()["detail"]

    async def test_buy_zero_quantity(self, client, portfolio):
        pid = portfolio["_id"]
        resp = await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "TCS.NS", "quantity": 0, "price": 3000},
        )
        assert resp.status_code == 400

    async def test_buy_negative_price(self, client, portfolio):
        pid = portfolio["_id"]
        resp = await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "TCS.NS", "quantity": 1, "price": -100},
        )
        assert resp.status_code == 400

    async def test_buy_portfolio_not_found(self, client):
        resp = await client.post(
            "/portfolios/000000000000000000000001/buy",
            json={"symbol": "TCS.NS", "quantity": 1, "price": 100},
        )
        assert resp.status_code == 404

    async def test_buy_exact_available_cash(self, client, portfolio):
        pid = portfolio["_id"]
        resp = await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "TCS.NS", "quantity": 100, "price": 1000},
        )
        assert resp.status_code == 201
        detail = await client.get(f"/portfolios/{pid}")
        assert detail.json()["current_cash"] == 0.0


class TestSell:
    async def test_sell_returns_trade(self, client, portfolio):
        pid = portfolio["_id"]
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "INFY.NS", "quantity": 10, "price": 1500},
        )
        resp = await client.post(
            f"/portfolios/{pid}/sell",
            json={"symbol": "INFY.NS", "quantity": 5, "price": 1600},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["type"] == "SELL"
        assert data["quantity"] == 5
        assert data["price"] == 1600

    async def test_sell_adds_cash(self, client, portfolio):
        pid = portfolio["_id"]
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "INFY.NS", "quantity": 10, "price": 1500},
        )
        cash_after_buy = (await client.get(f"/portfolios/{pid}")).json()["current_cash"]
        await client.post(
            f"/portfolios/{pid}/sell",
            json={"symbol": "INFY.NS", "quantity": 10, "price": 1600},
        )
        cash_after_sell = (await client.get(f"/portfolios/{pid}")).json()["current_cash"]
        assert cash_after_sell == cash_after_buy + 16000

    async def test_sell_insufficient_holdings(self, client, portfolio):
        pid = portfolio["_id"]
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "WIPRO.NS", "quantity": 5, "price": 500},
        )
        resp = await client.post(
            f"/portfolios/{pid}/sell",
            json={"symbol": "WIPRO.NS", "quantity": 10, "price": 500},
        )
        assert resp.status_code == 400
        assert "Insufficient holdings" in resp.json()["detail"]

    async def test_sell_with_no_holdings(self, client, portfolio):
        pid = portfolio["_id"]
        resp = await client.post(
            f"/portfolios/{pid}/sell",
            json={"symbol": "SBIN.NS", "quantity": 1, "price": 600},
        )
        assert resp.status_code == 400

    async def test_sell_zero_quantity(self, client, portfolio):
        pid = portfolio["_id"]
        resp = await client.post(
            f"/portfolios/{pid}/sell",
            json={"symbol": "SBIN.NS", "quantity": 0, "price": 600},
        )
        assert resp.status_code == 400

    async def test_sell_portfolio_not_found(self, client):
        resp = await client.post(
            "/portfolios/000000000000000000000001/sell",
            json={"symbol": "TCS.NS", "quantity": 1, "price": 100},
        )
        assert resp.status_code == 404

    async def test_sell_symbol_uppercased(self, client, portfolio):
        pid = portfolio["_id"]
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "hdfcbank.ns", "quantity": 5, "price": 1600},
        )
        resp = await client.post(
            f"/portfolios/{pid}/sell",
            json={"symbol": "hdfcbank.ns", "quantity": 3, "price": 1700},
        )
        assert resp.status_code == 201
        assert resp.json()["symbol"] == "HDFCBANK.NS"


class TestTradeHistory:
    async def test_empty_history(self, client, portfolio):
        pid = portfolio["_id"]
        resp = await client.get(f"/portfolios/{pid}/trades")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_history_contains_buy_and_sell(self, client, portfolio):
        pid = portfolio["_id"]
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "TCS.NS", "quantity": 10, "price": 3000},
        )
        await client.post(
            f"/portfolios/{pid}/sell",
            json={"symbol": "TCS.NS", "quantity": 5, "price": 3200},
        )
        resp = await client.get(f"/portfolios/{pid}/trades")
        trades = resp.json()
        assert len(trades) == 2
        types = {t["type"] for t in trades}
        assert types == {"BUY", "SELL"}

    async def test_history_sorted_newest_first(self, client, portfolio):
        pid = portfolio["_id"]
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "RELIANCE.NS", "quantity": 5, "price": 2800},
        )
        await client.post(
            f"/portfolios/{pid}/buy",
            json={"symbol": "TCS.NS", "quantity": 3, "price": 3000},
        )
        resp = await client.get(f"/portfolios/{pid}/trades")
        trades = resp.json()
        assert trades[0]["symbol"] == "TCS.NS"

    async def test_history_isolated_per_portfolio(self, client):
        r1 = await client.post(
            "/portfolios", json={"name": "P1", "starting_amount": 100000}
        )
        r2 = await client.post(
            "/portfolios", json={"name": "P2", "starting_amount": 100000}
        )
        pid1 = r1.json()["_id"]
        pid2 = r2.json()["_id"]

        await client.post(
            f"/portfolios/{pid1}/buy",
            json={"symbol": "INFY.NS", "quantity": 5, "price": 1500},
        )
        resp = await client.get(f"/portfolios/{pid2}/trades")
        assert resp.json() == []

    async def test_history_portfolio_not_found(self, client):
        resp = await client.get("/portfolios/000000000000000000000001/trades")
        assert resp.status_code == 404
