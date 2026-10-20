"""Execução automatizada da avaliação de recuperação e ponta a ponta."""
import json
from pathlib import Path
from rag.retriever import KnowledgeRetriever
from workflow.graph import support_graph


def evaluate_rag():
    with open("evaluation/rag_cases.json", "r", encoding="utf-8") as f:
        cases = json.load(f)

    retriever = KnowledgeRetriever()
    hit_at_3 = 0
    hit_at_5 = 0
    correct_abstentions = 0
    total_abstain_cases = 0

    print("==========================================")
    print("AVALIAÇÃO DO PIPELINE DE RECUPERAÇÃO (RAG)")
    print("==========================================")

    for case in cases:
        q = case["question"]
        expected = case["expected_source"]
        must_abstain = case["must_abstain"]

        results = retriever.search(q)
        sources = [r["source"] for r in results]

        if must_abstain:
            total_abstain_cases += 1
            if len(results) == 0:
                correct_abstentions += 1
                status = "OK (Absteve-se)"
            else:
                status = "FALHA (Deveria abster-se)"
        else:
            if expected in sources[:3]:
                hit_at_3 += 1
            if expected in sources[:5]:
                hit_at_5 += 1
                status = f"OK (Encontrado: {expected})"
            else:
                status = f"FALHA (Esperado: {expected}, Obtido: {sources})"

        print(f"[{status}] {q[:45]}...")

    non_abstain = len(cases) - total_abstain_cases
    hit_rate_3 = hit_at_3 / non_abstain if non_abstain else 1.0
    recall_5 = hit_at_5 / non_abstain if non_abstain else 1.0
    abstain_rate = correct_abstentions / total_abstain_cases if total_abstain_cases else 1.0

    print("\nMÉTRICAS FINAIS:")
    print(f"- Hit Rate @ 3: {hit_rate_3:.1%}")
    print(f"- Recall @ 5:   {recall_5:.1%}")
    print(f"- Taxa de Abstenção Correta: {abstain_rate:.1%}")

    if recall_5 < 0.8:
        print("ALERTA: O RAG não atingiu o critério mínimo de 8/10 casos.")
    else:
        print("SUCESSO: Critério mínimo de recuperação superado!")


if __name__ == "__main__":
    evaluate_rag()
