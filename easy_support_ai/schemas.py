"""Esquemas Pydantic para validação e saída estruturada."""
from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    """Referência a um trecho e documento da base de conhecimento."""
    source: str = Field(description="Nome do documento fonte, ex: politica_senhas.md")
    chunk_id: str | None = Field(default=None, description="Identificador do chunk recuperado")


class AssistantAnswer(BaseModel):
    """Resposta estruturada gerada pelo assistente de suporte."""
    answer: str = Field(description="Resposta em português brasileiro fundamentada exclusivamente nas fontes.")
    sources: list[SourceReference] = Field(default_factory=list, description="Lista de fontes oficiais utilizadas.")
    urgency: str = Field(description="Urgência classificada: baixa, media ou alta.")
    classifier_confidence: float = Field(description="Grau de certeza do classificador de 0.0 a 1.0.")
    needs_human_review: bool = Field(description="Indica se o caso requer revisão humana.")
    proposed_action: str | None = Field(default=None, description="Ação proposta: create_ticket ou None.")
