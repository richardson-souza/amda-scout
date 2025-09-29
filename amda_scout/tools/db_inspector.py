# amda_scout/tools/db_inspector.py

from langchain.tools import Tool
from sqlalchemy import text, inspect, Engine, exc
from typing import List


class DatabaseInspectorTools:
    db_engine: Engine

    def __init__(self, db_engine: Engine):
        self.db_engine = db_engine

    def list_schemas(self) -> str:
        """Retorna uma lista de todos os schemas (datasets) não-padrão disponíveis no banco de dados."""
        try:
            inspector = inspect(self.db_engine)
            schemas = inspector.get_schema_names()
            filtered_schemas = [
                s
                for s in schemas
                if s
                not in (
                    "information_schema",
                    "pg_catalog",
                    "pg_toast",
                    "sys",
                    "performance_schema",
                    "mysql",
                )
            ]
            if not filtered_schemas:
                return "Nenhum schema de usuário encontrado. Apenas schemas de sistema estão disponíveis."
            return f"Os schemas disponíveis são: {', '.join(filtered_schemas)}"
        except exc.SQLAlchemyError as e:
            return f"Erro de banco de dados ao tentar listar schemas: {e}"

    def list_tables(self, schema: str) -> str:
        """
        Retorna uma lista de todas as tabelas e views para um determinado schema.
        """
        try:
            inspector = inspect(self.db_engine)

            all_schemas = inspector.get_schema_names()
            if schema not in all_schemas:
                return f"Nenhuma tabela ou view encontrada no schema '{schema}'. Verifique se o nome do schema está correto."

            tables = inspector.get_table_names(schema=schema)
            views = inspector.get_view_names(schema=schema)

            all_items = tables + views
            if not all_items:
                return f"Nenhuma tabela ou view encontrada no schema '{schema}'."

            return (
                f"As tabelas e views no schema '{schema}' são: {', '.join(all_items)}"
            )
        except exc.SQLAlchemyError as e:
            return f"Erro de banco de dados ao tentar listar tabelas para o schema '{schema}': {e}"

    def inspect_table_schema(self, table_name: str) -> str:
        if "." not in table_name:
            return "Erro de formato: O nome da tabela deve ser qualificado com o schema (ex: 'public.clientes')."

        try:
            schema, table = table_name.split(".", 1)
            inspector = inspect(self.db_engine)

            if not inspector.has_table(table, schema=schema):
                return f"Erro: Não foi possível encontrar a tabela ou view '{table_name}'. Verifique os nomes e tente novamente."

            columns = inspector.get_columns(table, schema=schema)

            ddl_parts = [f"Schema da tabela '{table_name}':"]
            for col in columns:
                ddl_parts.append(f"  - Coluna: '{col['name']}', Tipo: {col['type']}")
            return "\n".join(ddl_parts)

        except exc.SQLAlchemyError as e:
            return f"Erro de banco de dados ao inspecionar a tabela '{table_name}': {e}"

    def run_exploratory_sql(self, query: str) -> str:
        normalized_query = query.strip().lower()
        if not normalized_query.startswith("select"):
            return "Erro de Segurança: Apenas queries que começam com 'SELECT' são permitidas."

        safe_query = normalized_query

        if "limit" not in normalized_query:
            safe_query = normalized_query.strip().rstrip(";") + " limit 10;"

        if not normalized_query.endswith(";"):
            safe_query = normalized_query.strip() + ";"

        try:
            with self.db_engine.connect() as connection:
                cursor = connection.execute(text(safe_query))

                if cursor.returns_rows is False:
                    return "A query foi executada com sucesso, mas não é uma consulta que retorna dados (ex: um DDL)."

                rows = cursor.fetchall()
                if not rows:
                    return "A query foi executada com sucesso, mas não retornou nenhuma linha."

                header = cursor.keys()
                formatted_result = (
                    f"Resultado da query (limitado a {len(rows)} linhas):\n"
                )
                formatted_result += " | ".join(map(str, header)) + "\n"
                formatted_result += "-" * (len(" | ".join(header))) + "\n"
                for row in rows:
                    formatted_row = [str(item) for item in row]
                    formatted_result += " | ".join(formatted_row) + "\n"

                return formatted_result
        except exc.SQLAlchemyError as e:
            return f"Erro de banco de dados ao executar a query: {e}"


def _create_tool_adapter(func, arg_name: str):
    """
    Cria um wrapper para a função da ferramenta que aceita input flexível
    e limpa o input de aspas desnecessárias.
    """

    def adapter(tool_input: any) -> str:
        input_value = tool_input

        if isinstance(tool_input, str):
            if tool_input.startswith(("'", '"')) and tool_input.endswith(("'", '"')):
                input_value = tool_input[1:-1]

        if isinstance(input_value, dict):
            kwargs = input_value
        else:
            kwargs = {arg_name: input_value}

        try:
            return func(**kwargs)
        except Exception as e:
            return f"Erro ao executar a ferramenta {func.__name__}: {e}"

    return adapter


def get_tools(db_engine: Engine) -> List[Tool]:
    """
    Função fábrica que inicializa e retorna a lista de ferramentas.
    Usa o adaptador robusto para os inputs.
    """
    inspector = DatabaseInspectorTools(db_engine)

    return [
        Tool(
            name="list_schemas",
            func=lambda _: inspector.list_schemas(),
            description="Útil para obter uma lista de todos os schemas (ou datasets) de usuário disponíveis. Não requer nenhum input.",
        ),
        Tool(
            name="list_tables",
            func=_create_tool_adapter(inspector.list_tables, "schema"),
            description="Útil para listar todas as tabelas e views dentro de um schema específico. O input para esta ferramenta deve ser UMA ÚNICA STRING contendo o nome exato do schema. Exemplo de input: 'ecommerce'",
        ),
        Tool(
            name="inspect_table_schema",
            func=_create_tool_adapter(inspector.inspect_table_schema, "table_name"),
            description="Útil para ver as colunas e tipos de dados de uma tabela específica. O input para esta ferramenta deve ser UMA ÚNICA STRING no formato 'schema.nome_da_tabela'. Exemplo de input: 'ecommerce.pedidos'",
        ),
        Tool(
            name="run_exploratory_sql",
            func=_create_tool_adapter(inspector.run_exploratory_sql, "query"),
            description="Útil para executar uma query SQL de LEITURA (SELECT) para explorar dados. O input para esta ferramenta deve ser UMA ÚNICA STRING contendo a query SQL completa a ser executada. Exemplo de input: 'SELECT * FROM ecommerce.clientes LIMIT 3'",
        ),
    ]
