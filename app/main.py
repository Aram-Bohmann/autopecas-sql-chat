"""
app/main.py - Interface Streamlit para o SQL Chat de Auto Pecas.
Para rodar: streamlit run app/main.py
"""
 
import re
import pandas as pd
import streamlit as st
 
from app.chain import build_agent, run_query
 
 
# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
 
def _try_parse_table(text: str):
    lines = [l.strip() for l in text.splitlines() if l.strip().startswith("|")]
    if len(lines) < 3:
        return None
    try:
        data_lines = [l for l in lines if not re.match(r"^\|[-| :]+\|$", l)]
        rows = [
            [cell.strip() for cell in line.strip("|").split("|")]
            for line in data_lines
        ]
        if len(rows) < 2:
            return None
        return pd.DataFrame(rows[1:], columns=rows[0])
    except Exception:
        return None
 
 
# ------------------------------------------------------------------
# Configuracao da pagina
# ------------------------------------------------------------------
 
st.set_page_config(
    page_title="AutoPecas Estoque",
    page_icon="🔩",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# CSS — Estética editorial industrial
# ------------------------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

:root {
    --cream:  #F0EDE6;
    --black:  #111110;
    --orange: #C8460A;
    --gray:   #8A8880;
    --border: #D0CCC4;
    --white:  #FAFAF8;
}

/* Força fundo creme em TUDO — sem exceção */
html, body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
[data-testid="stDecoration"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"],
section,
.main,
.main > div,
.css-1d391kg,
.css-18e3th9,
[class*="css"] {
    background-color: #F0EDE6 !important;
    color: #111110 !important;
}

/* Fonte e cor base */
html, body { font-family: 'IBM Plex Sans', sans-serif !important; }
p, label, div, h1, h2, h3, h4, li { color: #111110 !important; }
span { color: #111110; } /* sem !important para spans personalizados sobrescreverem */

.main-header {
    padding: 2.5rem 0 1rem 0;
    border-bottom: 2px solid var(--black);
    margin-bottom: 2rem;
    overflow: hidden;
}


[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 0 !important;
}
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] { display: none !important; }

[data-testid="stChatInput"] {
    border: 2px solid var(--black) !important;
    border-radius: 0 !important;
    background: var(--white) !important;
}
[data-testid="stChatInput"]:focus-within { border-color: var(--orange) !important; }
[data-testid="stChatInput"] textarea {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.88rem !important;
    color: var(--black) !important;
    background: transparent !important;
}

[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 0 !important;
    background: var(--white) !important;
    margin-top: 0.5rem !important;
}
[data-testid="stExpander"] summary {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--gray) !important;
}

pre, code {
    font-family: 'IBM Plex Mono', monospace !important;
    background: var(--black) !important;
    color: #E8E4DC !important;
    border-radius: 0 !important;
    font-size: 0.8rem !important;
}

[data-testid="stDataFrame"] { border: 1px solid var(--black) !important; }

[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"] {
    background: var(--cream) !important;
    border-right: 2px solid var(--black) !important;
}
[data-testid="stSidebar"] * { color: var(--black) !important; }
[data-testid="stSidebar"] button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    border-radius: 0 !important;
    color: var(--gray) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    text-align: left !important;
    padding: 0.4rem 0.75rem !important;
    transition: all 0.15s !important;
}
[data-testid="stSidebar"] button:hover {
    border-color: var(--orange) !important;
    color: var(--black) !important;
    background: var(--cream) !important;
}

.sidebar-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.63rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--gray) !important;
    display: block;
    margin-bottom: 0.75rem;
}

.status-badge {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0.18rem 0.55rem;
    border: 1px solid var(--orange);
    color: var(--orange);
    margin: 0.4rem 0;
}

.msg-user {
    background: var(--black);
    color: var(--white) !important;
    padding: 0.65rem 1rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.88rem;
    border-left: 3px solid var(--orange);
    margin-bottom: 0.25rem;
}
.msg-assistant {
    background: var(--white);
    border: 1px solid var(--border);
    border-left: 3px solid var(--black);
    padding: 0.65rem 1rem;
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}

hr { border-color: var(--border) !important; }

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1100px !important;
}
*:focus { outline: none !important; box-shadow: none !important; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------

st.markdown("""
<div class="main-header">
    <p style="font-family:'Syne',sans-serif; font-weight:800; font-size:1.8rem;
              line-height:0.92; letter-spacing:-3px; color:#1a1a1a;
              margin:0 0 0.8rem 0; white-space:nowrap;">
        AUTO<span style="color:#C1440E;">PEÇAS</span><br>ESTOQUE
    </p>
    <p style="font-family:'IBM Plex Mono',monospace; font-size:.9rem;
              letter-spacing:0.18em; text-transform:uppercase; color:#8A8880;
              margin:0 0 1.2rem 0; white-space:nowrap;">
        Busca inteligente &nbsp;·&nbsp; SQL em linguagem natural &nbsp;·&nbsp; Llama 3.2
    </p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Estado da sessao
# ------------------------------------------------------------------
 
if "messages" not in st.session_state:
    st.session_state.messages = []
 
if "agent" not in st.session_state:
    with st.spinner("Inicializando modelo..."):
        st.session_state.agent = build_agent()
 
# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
 
with st.sidebar:
    st.markdown(
        '<span style="font-family:IBM Plex Mono,monospace;font-size:0.63rem;'
        'letter-spacing:0.22em;text-transform:uppercase;color:#8A8880;display:block;'
        'margin-bottom:0.75rem;">Exemplos de consulta</span>',
        unsafe_allow_html=True,
    )
 
    exemplos = [
        "10 produtos mais vendidos",
        "Produtos com estoque critico",
        "Faturamento total do mes passado",
        "Clientes que mais compraram",
        "Fornecedores cadastrados",
        "Margem media dos produtos de freios",
        "Pedidos com status pendente",
        "Produto com maior receita",
    ]
    for ex in exemplos:
        if st.button(f"->  {ex}", use_container_width=True, key=f"ex_{ex}"):
            st.session_state._quick_input = ex
 
    st.divider()
 
    if st.button("X  Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = build_agent()
        st.rerun()
 
    st.divider()
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.63rem;
                letter-spacing:0.1em;color:#8A8880;line-height:2.2">
        MODELO &nbsp;&nbsp; llama3.2<br>
        BANCO &nbsp;&nbsp;&nbsp; auto_pecas<br>
        ORM &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; SQLAlchemy<br>
        AGENT &nbsp;&nbsp;&nbsp; LangChain
    </div>
    """, unsafe_allow_html=True)
 
# ------------------------------------------------------------------
# Historico de mensagens
# ------------------------------------------------------------------
 
for msg in st.session_state.messages:
    role = msg["role"]
    if role == "user":
        st.markdown(
            f'<div class="msg-user">> {msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="msg-assistant">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
        if msg.get("sql"):
            with st.expander("SQL GERADO"):
                st.code(msg["sql"], language="sql")
        if msg.get("dataframe") is not None:
            n = len(msg["dataframe"])
            st.markdown(
                f'<span class="status-badge">o {n} resultado(s)</span>',
                unsafe_allow_html=True,
            )
            st.dataframe(msg["dataframe"], use_container_width=True)
 
# ------------------------------------------------------------------
# Input
# ------------------------------------------------------------------
 
quick = st.session_state.pop("_quick_input", None)
user_input = st.chat_input("Digite sua consulta em portugues...") or quick
 
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(
        f'<div class="msg-user">> {user_input}</div>',
        unsafe_allow_html=True,
    )
 
    with st.spinner("Consultando banco de dados..."):
        result = run_query(
            st.session_state.agent,
            user_input,
            st.session_state.messages[:-1],   # historio sem a msg atual
        )
 
    answer = result["answer"]
    sql    = result["sql"]
    df     = _try_parse_table(answer)
 
    st.markdown(
        f'<div class="msg-assistant">{answer}</div>',
        unsafe_allow_html=True,
    )
 
    if sql:
        with st.expander("SQL GERADO"):
            st.code(sql, language="sql")
 
    if df is not None:
        n = len(df)
        st.markdown(
            f'<span class="status-badge">o {n} resultado(s)</span>',
            unsafe_allow_html=True,
        )
        st.dataframe(df, use_container_width=True)
 
    st.session_state.messages.append({
        "role":      "assistant",
        "content":   answer,
        "sql":       sql,
        "dataframe": df,
    })