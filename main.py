from amda_scout.utils.db_connector import get_db_engine
from amda_scout.tools.db_inspector import get_tools
from amda_scout.core.agent_creator import create_amda_scout_agent


def main():
    """
    Função principal que orquestra a inicialização e execução do agente AMDA-Scout.
    """
    print("--- Iniciando o Agente de Modelagem de Dados Analíticos (AMDA-Scout) ---")

    try:
        db_engine = get_db_engine()

        tools = get_tools(db_engine)

        agent_executor = create_amda_scout_agent(tools)

        print(
            "\n--- Agente pronto para uso. Digite 'sair' ou 'exit' para terminar. ---"
        )

        while True:
            query = input("Pergunte ao AMDA-Scout > ")

            if query.lower() in ["exit", "sair"]:
                print("--- Encerrando o agente. Até mais! ---")
                break

            if not query.strip():
                continue

            result = agent_executor.invoke({"input": query})

            print("\nResposta do Agente:")
            print(result.get("output", "Nenhuma resposta gerada."))
            print("-" * 50)

    except (ConnectionError, ValueError) as e:
        print(f"\nErro fatal durante a inicialização: {e}")
        print(
            "Verifique suas configurações no arquivo .env e a disponibilidade do banco de dados."
        )
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")


if __name__ == "__main__":
    main()
