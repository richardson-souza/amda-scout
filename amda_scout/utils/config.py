import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Classe que centraliza e gerencia as configurações da aplicação.
    Lê as variáveis de ambiente do arquivo .env ou do sistema operacional.
    """

    DB_TYPE: str = os.getenv("DB_TYPE", "postgresql")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")

    # Chaves de API
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "google")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash")

    @property
    def database_url(self) -> str:
        """
        Gera a URL de conexão completa para o SQLAlchemy a partir das
        variáveis de ambiente. A URL segue o formato:
        dialect+driver://username:password@host:port/database
        """

        driver = "psycopg2"
        return (
            f"{self.DB_TYPE}+{driver}://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
