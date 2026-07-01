from decimal import Decimal

import pytest

from fba_mcp_server.tools import analyse_product, calculate_margin, score_product, search_products


def test_server_can_be_created() -> None:
    pytest.importorskip("mcp")
    from fba_mcp_server.server import create_server

    server = create_server()

    assert server.name == "agentic-ecommerce-mcp"


def test_search_products_returns_schema_valid_simulated_data() -> None:
    response = search_products("garlic press", limit=1)

    assert response["simulated"] is False
    assert response["data"][0]["asin"] == "B0TEST0001"


def test_analyse_product_returns_schema_valid_simulated_data() -> None:
    response = analyse_product("B0TEST0001")

    assert response["data"]["risk_level"] == "controlled"


def test_calculate_margin_returns_financial_breakdown() -> None:
    response = calculate_margin(Decimal("30.00"), Decimal("9.00"), Decimal("4.50"), Decimal("5.50"))

    assert response["data"]["net_profit"] == "11.00"
    assert response["data"]["margin_percent"] == "36.67"


def test_score_product_returns_decision_score() -> None:
    response = score_product("B0TEST0001", 800, 100, Decimal("30.00"))

    assert response["data"]["recommendation"] == "investigate"
