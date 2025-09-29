from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from amda_scout.utils.config import settings


def _load_prompt_template() -> ChatPromptTemplate:
    """
    Carrega o template de prompt para o Tool Calling Agent.
    """
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Você é um assistente especialista em análise de dados chamado AMDA-Scout. Use as ferramentas disponíveis para responder às perguntas do usuário da forma mais completa e precisa possível.",
            ),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )


def create_amda_scout_agent(tools: List[BaseTool]) -> AgentExecutor:
    """
    Cria e monta o Agente AMDA-Scout usando a API do Google Gemini.
    """
    print("Montando o Agente AMDA-Scout (Gemini Tool Calling)...")

    prompt = _load_prompt_template()

    if settings.LLM_PROVIDER == "google":
        llm = ChatGoogleGenerativeAI(model=settings.LLM_MODEL_NAME, temperature=0)
    else:
        raise ValueError(f"Provedor de LLM desconhecido: {settings.LLM_PROVIDER}")

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )

    print("Agente montado com sucesso.")
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
    )
