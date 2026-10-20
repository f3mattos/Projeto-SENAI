"""Testes de unidade para as ferramentas e banco do servidor MCP."""
import pytest
from mcp_server.server import create_ticket, get_ticket, initialize_database


def setup_module():
    initialize_database()


def test_create_and_get_ticket():
    res = create_ticket(
        title="Erro no pagamento",
        description="Clientes relatam tela preta ao tentar pagar com cartão",
        urgency="alta"
    )
    assert res["status"] == "aberto"
    assert res["urgency"] == "alta"
    assert res["id"].startswith("TKT-")

    fetched = get_ticket(res["id"])
    assert fetched["found"] is True
    assert fetched["title"] == "Erro no pagamento"


def test_invalid_urgency_rejected():
    with pytest.raises(ValueError):
        create_ticket("Chamado de teste", "Descrição válida com mais de dez caracteres", "urgencia_invalida")


def test_short_title_rejected():
    with pytest.raises(ValueError):
        create_ticket("Oi", "Descrição válida com mais de dez caracteres", "baixa")
