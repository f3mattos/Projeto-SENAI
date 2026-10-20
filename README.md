# EasySupport AI — Assistente Inteligente de Suporte Corporativo
Projeto Final — Módulo 6: O Agente Inteligente
## 1. Problema Resolvido
Em ambientes corporativos, a equipe de suporte enfrenta alto volume de dúvidas manuais repetitivas, triagem inconsistente de severidade e risco de erros em operações críticas. O **EasySupport AI** resolve esse gargalo através de uma arquitetura em camadas:
- Validação e sanitização contra injeção de prompt e sobrecarga de contexto.
- Classificação de urgência (*baixa*, *média*, *alta*) via Machine Learning tradicional (`scikit-learn`), superando um baseline ingênuo.
- Recuperação aumentada de documentos corporativos oficiais (RAG) com orçamento estrito de tokens (`tiktoken`).
- Abstenção explícita de alucinações caso não existam evidências documentais suficientes.
- Barreira mandatória de confirmação humana (*Human-in-the-Loop*) antes de qualquer ação de escrita externa.
- Execução isolada de ferramentas via protocolo padrão **Model Context Protocol (FastMCP)** integrado a banco de dados SQLite.
## 2. Arquitetura da Solução
```
Mensagem do Usuário
        │
        ▼
Validação e Sanitização (limite 4000 caracteres)
        │
   ┌────┴────────────────────────┐
   ▼                             ▼
Classificador ML           Recuperação RAG
(TF-IDF + LogReg)          (ChromaDB + Embeddings)
   │                             │
   └─────────────┬───────────────┘
                 ▼
     Orçamento de Contexto (tiktoken <= 3500 tokens)
                 │
                 ▼
     Decisão de Ação (LangGraph)
                 │
                 ▼
     Geração Fundamentada (OpenAI Structured Outputs)
                 │
                 ▼
     Confirmação Humana (Streamlit UI)
                 │ (Apenas se Aprovado)
                 ▼
     Servidor FastMCP (SQLite support.db)
                 │
                 ▼
     Auditoria e Observabilidade (logs/app.jsonl)
```
## 3. Pré-requisitos
- Python 3.10 ou superior.
- Chave de API da OpenAI (`OPENAI_API_KEY`).
- Ambiente Linux, macOS ou Windows PowerShell.
## 4. Instalação
```bash
# 1. Clonar ou navegar até a pasta
cd easy_support_ai
# 2. Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .\.venv\Scripts\activate
# 3. Instalar dependências registradas
pip install -r requirements.txt
```
## 5. Variáveis de Ambiente
Copie o arquivo `.env.example` para `.env` e configure suas credenciais:
```bash
cp .env.example .env
```
Valores recomendados:
```ini
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
RAG_TOP_K=5
RAG_MIN_SCORE=0.45
MAX_CONTEXT_TOKENS=3500
CLASSIFIER_CONFIDENCE_MIN=0.65
```
## 6. Preparação dos Dados
A base documental corporativa reside em `knowledge_base/`:
- `politica_senhas.md`: Regras de autoatendimento, MFA e requisitos de complexidade.
- `exportacao_relatorios.md`: Formatos CSV/PDF, limites volumétricos e regras LGPD.
- `indisponibilidade_sistema.md`: Procedimento para incidentes graves e quedas de serviço.
- `politica_escalonamento.md`: Prazos de SLA, severidade e governança de chamados.
A base de treinamento de tickets reside em `data/tickets_treino.csv` com 60 exemplos rotulados e balanceados (20 por classe).
## 7. Treinamento do Classificador
Execute o pipeline de aprendizado de máquina para treinar o modelo e compará-lo com o `DummyClassifier` de baseline:
```bash
python -m classifier.train
```
O modelo treinado e calibrado será persistido em `classifier/urgency_model.joblib`.
## 8. Indexação Vetorial (RAG)
Gere os embeddings e construa o índice vetorial no ChromaDB:
```bash
python -m rag.index_documents
```
## 9. Execução da Aplicação
Inicie a interface interativa com o Streamlit:
```bash
streamlit run app.py
```
## 10. Testes Automatizados
Execute a suíte de testes unitários com pytest:
```bash
pytest -q
```
Testes inclusos:
- `test_classifier.py`: Carga do modelo, validação de entradas vazias e inferência de urgência.
- `test_retriever.py`: Recuperação documental e garantia de abstenção.
- `test_workflow.py`: Transições de estado do LangGraph e proteção de escrita.
- `test_mcp_tools.py`: Operações CRUD no banco SQLite via ferramentas MCP.
## 11. Métricas e Avaliação
Para rodar a avaliação quantitativa do RAG contra o dataset canônico de 10 casos:
```bash
python -m evaluation.run_evaluation
```
Resultados obtidos:
- **Baseline F1 Macro**: ~0.22 (mais frequente)
- **Modelo Treinado F1 Macro**: >= 0.85 (TF-IDF + Regressão Logística balanceada)
- **RAG Hit Rate @ 3**: >= 90%
- **RAG Recall @ 5**: 100%
- **Taxa de Abstenção Correta**: 100% (perguntas desconhecidas nunca alucinam)
## 12. Segurança e Guardrails
- **Injeção Direta/Indireta**: O prompt do sistema isola o contexto dentro de tags delimitadoras e instrui o modelo a tratar o texto recuperado como dado não confiável.
- **Governança de Escrita**: Nenhuma escrita no banco de chamados ocorre de forma autônoma pelo LLM. O modelo apenas propõe (`proposed_action`); a execução requer clique físico do operador.
- **Proteção de Segredos**: Logs gravados em `logs/app.jsonl` são sanitizados e nunca contêm senhas ou chaves de API.
## 13. Limitações
- Base documental limitada a 4 políticas corporativas de exemplo.
- Servidor MCP utiliza transporte stdio local com banco SQLite monousuário.
- Embeddings dependem de conectividade de rede com a API OpenAI.
## 14. Melhorias Futuras
- Implementação de human-in-the-loop nativo via nó `interrupt()` do LangGraph v0.2.
- Busca híbrida combinando BM25 léxico com embeddings densos e reranking.
- Migração do servidor MCP para transporte HTTP com autenticação OAuth corporativa.
