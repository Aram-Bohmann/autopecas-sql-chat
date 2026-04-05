"""
app/chain.py — SQL chain sem ReAct agent.

Usa SQLDatabaseChain diretamente: LLM gera o SQL, executa, e interpreta
o resultado numa única passagem — sem o loop Thought/Action que confunde
modelos menores como o Llama 3.2.
"""

from langchain.memory import ConversationBufferWindowMemory
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.agent_types import AgentType

from app.config import settings
from app.database import get_db


_SYSTEM_PROMPT = """Você é um assistente de banco de dados para a loja "Auto Peças Boa Vista".

Você tem acesso a um banco MySQL com estas tabelas:
- produtos: catálogo de peças (codigo, nome, preco_venda, estoque, categoria_id, fornecedor_id)
- categorias: categorias dos produtos
- fornecedores: fornecedores cadastrados
- clientes: clientes PF e PJ
- pedidos: pedidos de venda (status, total, forma_pagamento)
- itens_pedido: itens de cada pedido (produto_id, quantidade, preco_unit)
- vw_estoque_critico: produtos abaixo do estoque mínimo
- vw_vendas_produto: resumo de vendas por produto (total_vendido, receita_total)

Regras:
- Responda SEMPRE em português brasileiro
- Use apenas SELECT — nunca modifique dados
- Limite a 50 resultados por padrão
- Formate valores como R$ X.XXX,XX
- Após os dados, escreva um resumo curto em linguagem natural
"""


def build_agent(memory: ConversationBufferWindowMemory | None = None):
    """
    Constrói um SQL agent usando AgentType.ZERO_SHOT_REACT_DESCRIPTION
    com prompt em inglês (exigido pelo parser ReAct do LangChain).
    """
    llm = ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=0,
        num_ctx=8192,
    )

    db = get_db()

    # create_sql_agent já monta o prompt ReAct internamente em inglês
    # e é mais tolerante com modelos locais
    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=15,
        max_execution_time=120,
        prefix=_SYSTEM_PROMPT,
        extra_tools=[],
    )

    return agent


def run_query(agent, question: str, history: list[dict]) -> dict:
    """
    Executa a pergunta no agent e retorna dict com:
      - answer: resposta em texto
      - sql: último SQL executado (ou None)
    """
    # Adiciona contexto do histórico à pergunta
    if history:
        context = "\n".join(
            f"{'Usuário' if m['role'] == 'user' else 'Assistente'}: {m['content']}"
            for m in history[-4:]  # últimas 4 mensagens
        )
        full_question = f"Histórico recente:\n{context}\n\nPergunta atual: {question}"
    else:
        full_question = question

    try:
        result = agent.invoke({"input": full_question})
        output = result.get("output", "")

        # Recupera SQL dos steps intermediários
        sql = None
        for action, _ in reversed(result.get("intermediate_steps", [])):
            tool = getattr(action, "tool", "")
            if tool == "sql_db_query":
                inp = getattr(action, "tool_input", None)
                sql = inp if isinstance(inp, str) else (inp or {}).get("query")
                break

        # Se output for erro de parsing, tenta pegar da última observação
        if not output.strip() or "Invalid Format" in output or "Agent stopped" in output:
            for _, obs in reversed(result.get("intermediate_steps", [])):
                if isinstance(obs, str) and len(obs) > 30:
                    output = obs
                    break
            if not output.strip():
                output = "Não consegui processar. Tente reformular a pergunta."

        return {"answer": output, "sql": sql}

    except Exception as exc:
        return {"answer": f"Erro: {exc}", "sql": None}


def extract_sql_from_steps(intermediate_steps: list) -> str | None:
    """Mantido por compatibilidade — use run_query() de preferência."""
    for action, _ in reversed(intermediate_steps):
        if getattr(action, "tool", "") == "sql_db_query":
            inp = getattr(action, "tool_input", None)
            return inp if isinstance(inp, str) else (inp or {}).get("query")
    return None