"""
seed.py — Popula o banco auto_pecas com dados fictícios.
Execute após criar o schema:
    python database/seed.py
"""

import random
from datetime import datetime, timedelta

import pymysql
from faker import Faker

from app.config import settings

fake = Faker("pt_BR")
random.seed(42)
Faker.seed(42)

# ------------------------------------------------------------------
# Dados mestres realistas para auto peças
# ------------------------------------------------------------------

CATEGORIAS = [
    ("Motor e Peças Internas", "Pistões, anéis, válvulas, virabrequim e afins"),
    ("Freios", "Pastilhas, discos, tambores, fluido e componentes"),
    ("Suspensão e Direção", "Amortecedores, molas, caixas de direção, pivôs"),
    ("Elétrica e Iluminação", "Baterias, alternadores, velas, lâmpadas, fios"),
    ("Filtros", "Filtros de ar, óleo, combustível e habitáculo"),
    ("Transmissão", "Embreagens, câmbio, semi-eixos, rolamentos"),
    ("Arrefecimento", "Radiadores, bombas d'água, termostatos, mangueiras"),
    ("Escapamento", "Catalisadores, silenciosos, tubos, sensores lambda"),
    ("Carroceria e Acessórios", "Retrovisores, faróis, para-choques, borrachas"),
    ("Lubrificantes e Fluidos", "Óleos de motor, câmbio, hidráulico, aditivos"),
]

PRODUTOS_BASE = [
    # (nome, categoria_idx, unidade, custo_min, custo_max)
    ("Pastilha de Freio Dianteira",   1, "JG",  35,  90),
    ("Disco de Freio Ventilado",      1, "PC",  80, 200),
    ("Fluido de Freio DOT 4",         1, "UN",  18,  35),
    ("Amortecedor Dianteiro",         2, "PC", 120, 350),
    ("Mola Espiral Dianteira",        2, "PC",  60, 180),
    ("Pivô de Suspensão",             2, "PC",  30,  90),
    ("Bateria 60Ah",                  3, "UN", 280, 480),
    ("Alternador Remanufaturado",     3, "UN", 220, 550),
    ("Vela de Ignição (jogo 4)",      3, "JG",  40, 120),
    ("Filtro de Ar",                  4, "UN",  20,  65),
    ("Filtro de Óleo",                4, "UN",  15,  45),
    ("Filtro de Combustível",         4, "UN",  22,  60),
    ("Filtro de Habitáculo",          4, "UN",  25,  70),
    ("Embreagem Completa (kit)",      5, "KT", 280, 650),
    ("Rolamento de Roda Traseira",    5, "PC",  55, 130),
    ("Semi-Eixo Direito",             5, "PC", 180, 420),
    ("Radiador de Água",              6, "UN", 250, 600),
    ("Bomba d'Água",                  6, "UN",  80, 220),
    ("Termostato",                    6, "UN",  25,  70),
    ("Silicioso Traseiro",            7, "PC",  90, 250),
    ("Catalisador Universal",         7, "PC", 350, 900),
    ("Sensor Lambda",                 7, "UN",  80, 200),
    ("Óleo Motor 5W30 Sintético 1L",  9, "UN",  28,  55),
    ("Óleo Motor 10W40 Semi-sint. 1L",9, "UN",  18,  38),
    ("Aditivo Radiador Concentrado",  9, "UN",  22,  45),
    ("Pistão com Anel (STD)",         0, "JG", 180, 480),
    ("Junta Motor Completa",          0, "KT", 220, 550),
    ("Correia Dentada Kit",           0, "KT",  90, 280),
    ("Retrovisor Elétrico Esquerdo",  8, "PC",  95, 280),
    ("Farol Dianteiro Led",           8, "PC", 180, 550),
]

ESTADOS = ["SP", "MG", "RJ", "RS", "PR", "SC", "BA", "GO", "PE", "CE"]

FORMAS_PAG = ["dinheiro", "cartao_credito", "cartao_debito", "pix", "boleto"]
STATUSES   = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
STATUS_W   = [0.05, 0.15, 0.15, 0.55, 0.10]          # pesos de probabilidade


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def margem(custo: float) -> float:
    """Aplica margem de 30-80% sobre o custo."""
    return round(custo * random.uniform(1.30, 1.80), 2)


def random_date(start_days_ago: int = 365) -> datetime:
    delta = timedelta(days=random.randint(0, start_days_ago))
    return datetime.now() - delta


# ------------------------------------------------------------------
# Funções de inserção
# ------------------------------------------------------------------

def seed_categorias(cur) -> list[int]:
    ids = []
    for nome, desc in CATEGORIAS:
        cur.execute(
            "INSERT INTO categorias (nome, descricao) VALUES (%s, %s)",
            (nome, desc),
        )
        ids.append(cur.lastrowid)
    print(f"  ✓ {len(ids)} categorias inseridas")
    return ids


def seed_fornecedores(cur, n: int = 15) -> list[int]:
    ids = []
    for _ in range(n):
        cur.execute(
            """INSERT INTO fornecedores
               (nome, cnpj, telefone, email, cidade, estado)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (
                fake.company(),
                fake.cnpj(),
                fake.phone_number()[:20],
                fake.company_email(),
                fake.city(),
                random.choice(ESTADOS),
            ),
        )
        ids.append(cur.lastrowid)
    print(f"  ✓ {n} fornecedores inseridos")
    return ids


def seed_produtos(cur, cat_ids: list[int], forn_ids: list[int]) -> list[dict]:
    produtos = []
    for i, (nome, cat_idx, unidade, custo_min, custo_max) in enumerate(PRODUTOS_BASE):
        custo  = round(random.uniform(custo_min, custo_max), 2)
        venda  = margem(custo)
        codigo = f"AP{str(i+1).zfill(4)}"
        cat_id = cat_ids[cat_idx]
        forn_id = random.choice(forn_ids)
        estoque = random.randint(0, 100)
        est_min = random.randint(3, 10)

        cur.execute(
            """INSERT INTO produtos
               (codigo, nome, categoria_id, fornecedor_id,
                preco_custo, preco_venda, estoque, estoque_minimo, unidade)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (codigo, nome, cat_id, forn_id, custo, venda, estoque, est_min, unidade),
        )
        produtos.append({"id": cur.lastrowid, "preco_venda": venda})

    print(f"  ✓ {len(PRODUTOS_BASE)} produtos inseridos")
    return produtos


def seed_clientes(cur, n: int = 60) -> list[int]:
    ids = []
    for _ in range(n):
        tipo = random.choice(["PF", "PJ"])
        cur.execute(
            """INSERT INTO clientes
               (nome, cpf_cnpj, tipo, telefone, email, cidade, estado)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (
                fake.company() if tipo == "PJ" else fake.name(),
                fake.cnpj()    if tipo == "PJ" else fake.cpf(),
                tipo,
                fake.phone_number()[:20],
                fake.email(),
                fake.city(),
                random.choice(ESTADOS),
            ),
        )
        ids.append(cur.lastrowid)
    print(f"  ✓ {n} clientes inseridos")
    return ids


def seed_pedidos(cur, cli_ids: list[int], produtos: list[dict], n: int = 120):
    for _ in range(n):
        cli_id  = random.choice(cli_ids)
        status  = random.choices(STATUSES, weights=STATUS_W)[0]
        desconto= round(random.uniform(0, 50), 2) if random.random() < 0.3 else 0.0
        forma   = random.choice(FORMAS_PAG)
        created = random_date(500)

        cur.execute(
            """INSERT INTO pedidos
               (cliente_id, status, desconto, forma_pagamento, criado_em)
               VALUES (%s,%s,%s,%s,%s)""",
            (cli_id, status, desconto, forma, created),
        )
        pedido_id = cur.lastrowid

        # 1-5 itens por pedido
        itens    = random.sample(produtos, k=random.randint(1, 5))
        total    = 0.0
        for prod in itens:
            qty      = random.randint(1, 6)
            preco    = prod["preco_venda"]
            cur.execute(
                """INSERT INTO itens_pedido
                   (pedido_id, produto_id, quantidade, preco_unit)
                   VALUES (%s,%s,%s,%s)""",
                (pedido_id, prod["id"], qty, preco),
            )
            total += qty * preco

        total_final = max(0, round(total - desconto, 2))
        cur.execute(
            "UPDATE pedidos SET total = %s WHERE id = %s",
            (total_final, pedido_id),
        )

    print(f"  ✓ {n} pedidos inseridos")


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

def main():
    print("🔌 Conectando ao MySQL...")
    conn = pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        charset="utf8mb4",
    )

    try:
        with conn.cursor() as cur:
            print("🌱 Iniciando seed...\n")

            # Limpa na ordem correta (FKs)
            for t in ("itens_pedido", "pedidos", "produtos",
                      "clientes", "fornecedores", "categorias"):
                cur.execute(f"DELETE FROM {t}")
            cur.execute("SET FOREIGN_KEY_CHECKS = 0")
            for t in ("itens_pedido", "pedidos", "produtos",
                      "clientes", "fornecedores", "categorias"):
                cur.execute(f"ALTER TABLE {t} AUTO_INCREMENT = 1")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1")

            cat_ids  = seed_categorias(cur)
            forn_ids = seed_fornecedores(cur)
            produtos = seed_produtos(cur, cat_ids, forn_ids)
            cli_ids  = seed_clientes(cur)
            seed_pedidos(cur, cli_ids, produtos)

            conn.commit()
            print("\n✅ Seed concluído com sucesso!")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
