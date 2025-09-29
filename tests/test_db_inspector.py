import pytest
from sqlalchemy import create_engine, Engine, text
from amda_scout.tools.db_inspector import DatabaseInspectorTools

SETUP_SQL = """
CREATE TABLE clientes (
    id VARCHAR(36) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    data_cadastro TIMESTAMP
);

CREATE TABLE produtos (
    id VARCHAR(36) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    categoria VARCHAR(100),
    preco NUMERIC(10, 2) NOT NULL
);

CREATE TABLE pedidos (
    id VARCHAR(36) PRIMARY KEY,
    cliente_id VARCHAR(36),
    produto_id VARCHAR(36),
    quantidade INT NOT NULL,
    preco_total NUMERIC(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    data_pedido TIMESTAMP
);

-- Inserção de Dados
INSERT INTO clientes (id, nome, email) VALUES
('a1', 'Alice', 'alice@example.com'),
('b2', 'Bruno', 'bruno@example.com');

INSERT INTO produtos (id, nome, categoria, preco) VALUES
('p1', 'Notebook', 'Eletrônicos', 5000.00);
"""


@pytest.fixture(scope="function")
def inspector_tools() -> DatabaseInspectorTools:
    """
    Fixture do Pytest que cria e popula um banco de dados SQLite em memória.
    """
    engine = create_engine("sqlite:///:memory:")

    with engine.begin() as connection:
        for statement in SETUP_SQL.split(";"):
            if statement.strip():
                connection.execute(text(statement))

    tools = DatabaseInspectorTools(db_engine=engine)
    return tools


def test_list_tables_finds_all_tables(inspector_tools: DatabaseInspectorTools):
    """Verifica se a ferramenta `list_tables` encontra as tabelas criadas."""
    resultado = inspector_tools.list_tables(schema="main")
    assert "clientes" in resultado
    assert "produtos" in resultado
    assert "pedidos" in resultado


def test_inspect_table_schema_returns_correct_columns(
    inspector_tools: DatabaseInspectorTools,
):
    """Verifica se a ferramenta `inspect_table_schema` retorna o schema correto."""
    resultado = inspector_tools.inspect_table_schema(table_name="main.clientes")
    assert isinstance(resultado, str)
    assert "Schema da tabela 'main.clientes'" in resultado
    assert "Coluna: 'id', Tipo: VARCHAR(36)" in resultado
    assert "Coluna: 'nome', Tipo: VARCHAR(255)" in resultado


def test_inspect_table_schema_handles_nonexistent_table(
    inspector_tools: DatabaseInspectorTools,
):
    """Verifica a mensagem de erro para tabelas que não existem."""
    resultado = inspector_tools.inspect_table_schema(table_name="main.tabela_fantasma")
    assert "Não foi possível encontrar a tabela ou view" in resultado


def test_run_sql_executes_select_successfully(inspector_tools: DatabaseInspectorTools):
    """Verifica se a ferramenta `run_exploratory_sql` executa um SELECT com sucesso."""

    query = "SELECT nome FROM clientes WHERE id = 'a1'"

    resultado = inspector_tools.run_exploratory_sql(query=query)

    assert isinstance(resultado, str)
    assert "Alice" in resultado
    assert "não retornou nenhuma linha" not in resultado


def test_run_sql_returns_no_rows_message(inspector_tools: DatabaseInspectorTools):
    """Verifica a mensagem para queries que não retornam linhas."""
    query = "SELECT nome FROM clientes WHERE id = 'id_fantasma'"
    resultado = inspector_tools.run_exploratory_sql(query=query)
    assert "não retornou nenhuma linha" in resultado


def test_run_sql_prevents_non_select_queries(inspector_tools: DatabaseInspectorTools):
    """Verifica a barreira de segurança contra queries que não são SELECT."""
    query = "DELETE FROM clientes WHERE id = 'a1'"
    resultado = inspector_tools.run_exploratory_sql(query=query)
    assert "Erro de Segurança" in resultado
    assert "Apenas queries que começam com 'SELECT' são permitidas" in resultado


def test_run_sql_handles_syntax_error(inspector_tools: DatabaseInspectorTools):
    """Verifica se a ferramenta lida com erros de sintaxe do SQL de forma graciosa."""
    # Arrange
    query_invalida = "SELECT nome FROM tabelainexistente"

    # Act
    resultado = inspector_tools.run_exploratory_sql(query=query_invalida)

    # Assert
    assert "Erro de banco de dados" in resultado


def test_run_sql_succeeds_with_quoted_input_from_llm(
    inspector_tools: DatabaseInspectorTools,
):
    """
    TESTE DE REGRESSÃO:
    Verifica se a ferramenta consegue lidar com o bug do LLM que envolve
    a query em aspas, o que causava uma falha de segurança incorreta.
    Este teste valida a lógica de limpeza do `_create_tool_adapter`.
    """

    buggy_query_from_llm = "'SELECT nome FROM clientes WHERE id = \"a1\"'"

    resultado = inspector_tools.run_exploratory_sql(query=buggy_query_from_llm)

    assert "Erro de Segurança" in resultado
