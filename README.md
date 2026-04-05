# 🔩 autopecas-sql-chat

> Chat em linguagem natural para consultar o estoque de uma auto peças — sem escrever SQL.

Faça perguntas como **"quais os 10 produtos mais vendidos?"** ou **"mostre os itens com estoque crítico"** e o sistema gera e executa o SQL automaticamente, devolvendo a resposta em português.

---

## Demonstração

```
Você: produtos com estoque crítico
Bot:  Encontrei 4 produtos abaixo do estoque mínimo:
      - Pastilha de Freio Dianteira (estoque: 2, mínimo: 5)
      - Filtro de Óleo (estoque: 1, mínimo: 5)
      ...
      ▸ SQL GERADO  [expansível]
```

---

## Stack

| Camada | Tecnologia |
|---|---|
| LLM | **Llama 3.2** via Ollama (100% local) |
| Orquestrador | **LangChain** — `create_sql_agent` |
| Banco de dados | **MySQL** via XAMPP |
| ORM | **SQLAlchemy** + `langchain-community` |
| Frontend | **Streamlit** |
| Dependências | **Poetry** |

---

## Pré-requisitos

- Python **3.11+**
- [Poetry](https://python-poetry.org/docs/#installation)
- [XAMPP](https://www.apachefriends.org/) com MySQL rodando
- [Ollama](https://ollama.com/download)

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/autopecas-sql-chat.git
cd autopecas-sql-chat
```

### 2. Instale as dependências

```bash
poetry install
poetry add pydantic-settings   # se ainda não estiver no lock
```

### 3. Configure o Ollama e baixe o modelo

```bash
# Inicie o serviço
ollama serve

# Em outro terminal, baixe o modelo (~2 GB)
ollama pull llama3.2
```

> **Windows:** abra o app Ollama pela bandeja do sistema antes de rodar `ollama pull`.

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` se necessário (por padrão funciona com XAMPP sem senha):

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=auto_pecas
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### 5. Crie o banco de dados

Abra o **XAMPP Control Panel**, inicie o MySQL e execute:

```bash
mysql -u root < database/schema.sql
```

Ou importe o arquivo manualmente no phpMyAdmin (`http://localhost/phpmyadmin`).

### 6. Popule com dados fictícios

```bash
poetry run python database/seed.py
```

Isso insere: 10 categorias · 15 fornecedores · 30 produtos · 60 clientes · 120 pedidos.

### 7. Rode a aplicação

```bash
poetry run streamlit run app/main.py
```

Acesse **http://localhost:8501** no navegador.

---

## Estrutura do projeto

```
autopecas-sql-chat/
│
├── .streamlit/
│   └── config.toml         # Tema claro (obrigatório)
│
├── app/
│   ├── main.py             # Interface Streamlit
│   ├── chain.py            # LangChain SQL agent
│   ├── database.py         # Conexão MySQL via SQLAlchemy
│   ├── config.py           # Variáveis de ambiente (Pydantic Settings)
│   └── __init__.py
│
├── database/
│   ├── schema.sql          # Tabelas + views
│   └── seed.py             # Dados fictícios (Faker pt_BR)
│
├── .env.example
├── pyproject.toml
└── README.md
```

---

## Exemplos de perguntas

```
10 produtos mais vendidos
Produtos com estoque crítico
Faturamento total do mês passado
Clientes que mais compraram
Fornecedores cadastrados
Margem média dos produtos de freios
Pedidos com status pendente
Produto com maior receita
```

---

## Como funciona

```
Usuário digita pergunta
        ↓
  Streamlit (main.py)
        ↓
  LangChain SQL Agent
        ↓
  Llama 3.2 (Ollama)     →  gera SQL
        ↓
  MySQL (XAMPP)          →  executa query
        ↓
  Llama 3.2 (Ollama)     →  interpreta resultado
        ↓
  Resposta em português  →  exibe na UI
```

O agent usa `AgentType.ZERO_SHOT_REACT_DESCRIPTION` com o toolkit `SQLDatabaseToolkit`, que expõe ferramentas de inspeção de schema e execução de queries. O histórico da conversa é passado como contexto em cada chamada.

---

## Troubleshooting

| Problema | Solução |
|---|---|
| `Connection refused` na porta 3306 | Inicie o MySQL no XAMPP Control Panel |
| `model not found` | Execute `ollama pull llama3.2` com o serviço rodando |
| `include_tables not found` | Certifique-se que rodou `schema.sql` antes de iniciar o app |
| Resposta só aparece no terminal | Verifique se está usando o `main.py` mais recente |
| Respostas lentas (~30s) | Normal sem GPU — Llama 3.2 3B em CPU leva ~10-30s por query |

---

## Licença

MIT — veja [LICENSE](LICENSE) para detalhes.
