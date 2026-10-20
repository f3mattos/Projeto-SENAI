"""Interface Web com Streamlit para o EasySupport AI."""
import streamlit as st
from mcp_server.client import call_tool_sync
from workflow.graph import support_graph
from observability.logger import log_event
import time

st.set_page_config(
    page_title="EasySupport AI — Suporte Corporativo",
    page_icon="🤖",
    layout="wide",
)

st.title("EasySupport AI")
st.caption("Assistente Corporativo com RAG, Classificação de Urgência e Ações Governadas")

# Sidebar com status e diagnósticos
with st.sidebar:
    st.header("Painel de Controle")
    st.markdown("**Modelo**: `OpenAI gpt-4o-mini`")
    st.markdown("**Base de Conhecimento**: 4 documentos ativos")
    st.markdown("**Servidor MCP**: SQLite (`data/support.db`)")
    st.divider()
    if st.button("Limpar Histórico da Sessão"):
        st.session_state.messages = []
        st.session_state.pending_action = None
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_action" not in st.session_state:
    st.session_state.pending_action = None

# Exibição do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("urgency"):
            st.caption(f"Urgência: {message['urgency'].upper()} | Confiança: {message.get('confidence', 0):.1%}")
        if message.get("sources"):
            with st.expander("Fontes oficiais consultadas"):
                for source in message["sources"]:
                    st.write(f"- 📄 {source['source']} ({source.get('chunk_id')})")

question = st.chat_input("Descreva sua dúvida técnica ou relate um problema operacional...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        t0 = time.time()
        with st.status("Processando requisição no LangGraph...", expanded=True) as status:
            result = support_graph.invoke({"question": question})
            status.update(label="Análise e inferência concluídas", state="complete")
        latency = int((time.time() - t0) * 1000)

        answer = result["answer"]
        st.markdown(answer["answer"])

        urgency_val = answer.get("urgency", "baixa")
        conf_val = answer.get("classifier_confidence", 0.0)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Urgência Sugerida", urgency_val.upper())
        with col2:
            st.metric("Confiança do Classificador", f"{conf_val:.1%}")

        if answer.get("sources"):
            with st.expander("Fontes consultadas"):
                for s in answer["sources"]:
                    st.write(f"- 📄 {s['source']} ({s.get('chunk_id')})")

        # Registro de log de auditoria
        log_event(
            trace_id=result.get("trace_id", "trace-demo"),
            event="request_completed",
            question=question,
            urgency=urgency_val,
            confidence=conf_val,
            retrieved_sources=[s["source"] for s in answer.get("sources", [])],
            context_tokens=result.get("context_tokens", 0),
            action_proposed=result.get("proposed_action"),
            action_executed=False,
            latency_ms=latency,
        )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer["answer"],
            "urgency": urgency_val,
            "confidence": conf_val,
            "sources": answer.get("sources", []),
        })

        if result.get("requires_approval") and result.get("proposed_action"):
            st.session_state.pending_action = {
                "tool": result["proposed_action"],
                "arguments": {
                    "title": f"Incidente: {question[:50]}",
                    "description": question,
                    "urgency": urgency_val,
                },
                "trace_id": result.get("trace_id", "trace-demo"),
            }

# Caixa de Human-in-the-Loop para Ações de Escrita
if st.session_state.pending_action:
    st.warning("⚠️ **Confirmação Obrigatória**: O assistente propôs a abertura de um chamado crítico.")
    st.info(f"**Ação**: `{st.session_state.pending_action['tool']}`\n**Título**: {st.session_state.pending_action['arguments']['title']}")

    col_confirm, col_cancel = st.columns(2)

    with col_confirm:
        if st.button("✅ Confirmar Abertura do Chamado", type="primary"):
            action = st.session_state.pending_action
            tool_result = call_tool_sync(action["tool"], action["arguments"])
            st.success(f"Chamado aberto com sucesso no banco SQLite! ID: {tool_result.get('id')}")
            st.json(tool_result)

            log_event(
                trace_id=action.get("trace_id", "trace-demo"),
                event="action_confirmed",
                action_proposed=action["tool"],
                action_executed=True,
            )
            st.session_state.pending_action = None

    with col_cancel:
        if st.button("❌ Cancelar Ação"):
            action = st.session_state.pending_action
            log_event(
                trace_id=action.get("trace_id", "trace-demo"),
                event="action_cancelled",
                action_proposed=action["tool"],
                action_executed=False,
            )
            st.session_state.pending_action = None
            st.info("Ação cancelada pelo operador. Nenhum registro foi inserido no banco de dados.")
