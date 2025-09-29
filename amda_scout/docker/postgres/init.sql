-- docker/postgres/init.sql

-- Criação de Schemas para simular um ambiente de dados real
CREATE SCHEMA IF NOT EXISTS ecommerce;
CREATE SCHEMA IF NOT EXISTS marketing;

-- Tabela de Clientes
CREATE TABLE ecommerce.clientes (
    id UUID PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    data_cadastro TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de Produtos
CREATE TABLE ecommerce.produtos (
    id UUID PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    categoria VARCHAR(100),
    preco NUMERIC(10, 2) NOT NULL
);

-- Tabela de Pedidos (Fatos)
CREATE TABLE ecommerce.pedidos (
    id UUID PRIMARY KEY,
    cliente_id UUID REFERENCES ecommerce.clientes(id),
    produto_id UUID REFERENCES ecommerce.produtos(id),
    quantidade INT NOT NULL,
    preco_total NUMERIC(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL, -- Ex: 'PENDENTE', 'APROVADO', 'ENVIADO', 'CANCELADO'
    data_pedido TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de Sessões do Site (para exploração cross-schema)
CREATE TABLE marketing.sessoes_site (
    id UUID PRIMARY KEY,
    cliente_id UUID, -- Pode ser nulo se o usuário não estiver logado
    pagina_visitada VARCHAR(255),
    tempo_gasto_segundos INT,
    data_sessao TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


--- INSERÇÃO DE DADOS DE EXEMPLO ---

-- Clientes
INSERT INTO ecommerce.clientes (id, nome, email, data_cadastro) VALUES
('a1b2c3d4-e5f6-7890-1234-567890abcdef', 'Alice Silva', 'alice.silva@example.com', '2025-01-15T10:00:00Z'),
('b2c3d4e5-f6a7-8901-2345-67890abcdef1', 'Bruno Costa', 'bruno.costa@example.com', '2025-02-20T14:30:00Z');

-- Produtos
INSERT INTO ecommerce.produtos (id, nome, categoria, preco) VALUES
('c3d4e5f6-a7b8-9012-3456-7890abcdef12', 'Notebook Pro', 'Eletrônicos', 7500.00),
('d4e5f6a7-b8c9-0123-4567-890abcdef123', 'Cadeira Gamer', 'Móveis', 1200.50),
('e5f6a7b8-c9d0-1234-5678-90abcdef1234', 'Livro de Ficção', 'Livros', 89.90);

-- Pedidos
INSERT INTO ecommerce.pedidos (id, cliente_id, produto_id, quantidade, preco_total, status, data_pedido) VALUES
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'c3d4e5f6-a7b8-9012-3456-7890abcdef12', 1, 7500.00, 'ENVIADO', '2025-08-01T11:00:00Z'),
(gen_random_uuid(), 'b2c3d4e5-f6a7-8901-2345-67890abcdef1', 'd4e5f6a7-b8c9-0123-4567-890abcdef123', 2, 2401.00, 'APROVADO', '2025-09-05T18:00:00Z'),
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', 'e5f6a7b8-c9d0-1234-5678-90abcdef1234', 1, 89.90, 'PENDENTE', '2025-09-10T09:45:00Z'),
(gen_random_uuid(), 'b2c3d4e5-f6a7-8901-2345-67890abcdef1', 'e5f6a7b8-c9d0-1234-5678-90abcdef1234', 5, 449.50, 'CANCELADO', '2025-09-11T12:00:00Z');

-- Sessões
INSERT INTO marketing.sessoes_site (id, cliente_id, pagina_visitada, tempo_gasto_segundos, data_sessao) VALUES
(gen_random_uuid(), 'a1b2c3d4-e5f6-7890-1234-567890abcdef', '/produtos/notebook-pro', 300, '2025-07-31T15:00:00Z'),
(gen_random_uuid(), null, '/home', 60, '2025-08-15T20:00:00Z');