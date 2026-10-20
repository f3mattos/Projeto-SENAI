"""Testes de unidade para o recuperador RAG."""
from rag.retriever import KnowledgeRetriever


def test_retriever_finds_password_policy():
    retriever = KnowledgeRetriever()
    results = retriever.search("Como redefinir minha senha de acesso?")
    assert len(results) > 0
    sources = [r["source"] for r in results]
    assert "politica_senhas.md" in sources


def test_retriever_abstains_on_unknown_topic():
    retriever = KnowledgeRetriever()
    results = retriever.search("Qual é a cotação do bitcoin em marte hoje?")
    assert len(results) == 0
