-- =============================================================
-- Banco de dados: auto_pecas
-- Descrição: Schema para sistema de auto peças
-- =============================================================

CREATE DATABASE IF NOT EXISTS auto_pecas
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE auto_pecas;

-- -------------------------------------------------------------
-- Tabela: categorias
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categorias (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  nome        VARCHAR(100) NOT NULL,
  descricao   TEXT,
  criado_em   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------------------------------
-- Tabela: fornecedores
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fornecedores (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  nome        VARCHAR(150) NOT NULL,
  cnpj        VARCHAR(18) UNIQUE NOT NULL,
  telefone    VARCHAR(20),
  email       VARCHAR(150),
  cidade      VARCHAR(100),
  estado      CHAR(2),
  criado_em   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------------------------------
-- Tabela: produtos
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS produtos (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  codigo          VARCHAR(30) UNIQUE NOT NULL,
  nome            VARCHAR(200) NOT NULL,
  descricao       TEXT,
  categoria_id    INT NOT NULL,
  fornecedor_id   INT NOT NULL,
  preco_custo     DECIMAL(10,2) NOT NULL,
  preco_venda     DECIMAL(10,2) NOT NULL,
  estoque         INT NOT NULL DEFAULT 0,
  estoque_minimo  INT NOT NULL DEFAULT 5,
  unidade         VARCHAR(10) DEFAULT 'UN',
  ativo           TINYINT(1) DEFAULT 1,
  criado_em       DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (categoria_id)  REFERENCES categorias(id),
  FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
);

-- -------------------------------------------------------------
-- Tabela: clientes
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clientes (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  nome        VARCHAR(150) NOT NULL,
  cpf_cnpj    VARCHAR(18) UNIQUE NOT NULL,
  tipo        ENUM('PF','PJ') DEFAULT 'PF',
  telefone    VARCHAR(20),
  email       VARCHAR(150),
  cidade      VARCHAR(100),
  estado      CHAR(2),
  criado_em   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------------------------------
-- Tabela: pedidos
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pedidos (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  cliente_id      INT NOT NULL,
  status          ENUM('pendente','aprovado','enviado','entregue','cancelado') DEFAULT 'pendente',
  total           DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  desconto        DECIMAL(10,2) DEFAULT 0.00,
  forma_pagamento ENUM('dinheiro','cartao_credito','cartao_debito','pix','boleto') DEFAULT 'pix',
  observacoes     TEXT,
  criado_em       DATETIME DEFAULT CURRENT_TIMESTAMP,
  atualizado_em   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- -------------------------------------------------------------
-- Tabela: itens_pedido
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS itens_pedido (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  pedido_id   INT NOT NULL,
  produto_id  INT NOT NULL,
  quantidade  INT NOT NULL,
  preco_unit  DECIMAL(10,2) NOT NULL,
  subtotal    DECIMAL(10,2) GENERATED ALWAYS AS (quantidade * preco_unit) STORED,
  FOREIGN KEY (pedido_id)  REFERENCES pedidos(id),
  FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

-- -------------------------------------------------------------
-- Views úteis
-- -------------------------------------------------------------

-- Produtos com estoque abaixo do mínimo
CREATE OR REPLACE VIEW vw_estoque_critico AS
SELECT
  p.codigo,
  p.nome,
  c.nome          AS categoria,
  p.estoque       AS estoque_atual,
  p.estoque_minimo,
  p.estoque - p.estoque_minimo AS diferenca
FROM produtos p
JOIN categorias c ON c.id = p.categoria_id
WHERE p.estoque < p.estoque_minimo AND p.ativo = 1;

-- Resumo de vendas por produto
CREATE OR REPLACE VIEW vw_vendas_produto AS
SELECT
  p.codigo,
  p.nome                        AS produto,
  c.nome                        AS categoria,
  SUM(ip.quantidade)            AS total_vendido,
  SUM(ip.subtotal)              AS receita_total,
  COUNT(DISTINCT ip.pedido_id)  AS num_pedidos
FROM itens_pedido ip
JOIN produtos p  ON p.id  = ip.produto_id
JOIN categorias c ON c.id = p.categoria_id
JOIN pedidos pd  ON pd.id = ip.pedido_id
WHERE pd.status NOT IN ('cancelado')
GROUP BY p.id, p.codigo, p.nome, c.nome;
