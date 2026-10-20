"""Testes de unidade para o grafo de orquestração LangGraph."""
from workflow.graph import support_graph


def test_empty_question_is_rejected():
    result = support_graph.invoke({"question": "   "})
    assert "vazia" in result["answer"]["answer"].lower()


def test_unknown_question_abstains():
    result = support_graph.invoke({
        "question": "Qual é a cotação do dólar em outra galáxia?"
    })
    assert result["answer"]["needs_human_review"] is True
    assert result["answer"]["sources"] == []


def test_write_action_is_only_proposed():
    result = support_graph.invoke({
        "question": "O servidor caiu e ninguém consegue trabalhar no sistema."
    })
    if result.get("proposed_action"):
        assert result["requires_approval"] is True
        assert result["proposed_action"] == "create_ticket"
