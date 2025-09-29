# amda_scout/utils/db_connector.py

from sqlalchemy import create_engine, Engine, exc
from .config import settings


def get_db_engine() -> Engine:
    """
    Cria e retorna uma instância do engine do SQLAlchemy com base nas
    configurações da aplicação.

    A função também tenta estabelecer uma conexão inicial para validar
    as credenciais e a disponibilidade do banco de dados.

    Returns:
        Engine: Uma instância do engine do SQLAlchemy configurada e pronta para uso.

    Raises:
        ValueError: Se as credenciais do banco de dados não estiverem configuradas.
        ConnectionError: Se a conexão com o banco de dados falhar.
    """
    # Valida se as configurações essenciais foram fornecidas no .env
    if not all(
        [settings.DB_USER, settings.DB_PASSWORD, settings.DB_HOST, settings.DB_NAME]
    ):
        raise ValueError(
            "Erro Crítico: As credenciais do banco de dados não estão completamente configuradas no arquivo .env"
        )

    try:
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,  # Verifica a validade das conexões antes de usá-las
            echo=False,  # Defina como True para ver o SQL gerado no console (ótimo para debug)
        )

        # Tenta conectar para validar as credenciais imediatamente
        with engine.connect() as connection:
            print("Conexão com o banco de dados estabelecida com sucesso!")

        return engine

    except exc.SQLAlchemyError as e:
        # Captura qualquer erro do SQLAlchemy (ex: senha errada, host não encontrado)
        # e lança uma exceção mais amigável.
        print(
            f"Erro Crítico: Não foi possível conectar ao banco de dados em '{settings.DB_HOST}'."
        )
        print(f"Detalhe do Erro: {e}")
        raise ConnectionError("Falha ao conectar no banco de dados.") from e
