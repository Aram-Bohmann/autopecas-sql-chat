"""
app/database.py — Cria e retorna a instância SQLDatabase do LangChain.
"""
 
from functools import lru_cache
 
from langchain_community.utilities import SQLDatabase
 
from app.config import settings
 
 
@lru_cache(maxsize=1)
def get_db() -> SQLDatabase:
    """
    Retorna uma instância cacheada do SQLDatabase do LangChain.
    view_support=True permite que o LangChain enxergue as views MySQL.
    """
    db = SQLDatabase.from_uri(
        settings.db_uri,
        include_tables=[
            "categorias",
            "fornecedores",
            "produtos",
            "clientes",
            "pedidos",
            "itens_pedido",
            "vw_estoque_critico",
            "vw_vendas_produto",
        ],
        sample_rows_in_table_info=3,
        view_support=True,             # necessário para views MySQL
    )
    return db