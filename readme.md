# AMDA-Scout: Uma Jornada de Estudo na Construção de Agentes de IA

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-informational)
![Google Gemini](https://img.shields.io/badge/Google-Gemini_API-4285F4)
![Docker](https://img.shields.io/badge/Docker-blue)
![License](https://img.shields.io/badge/License-MIT-green)

Este repositório documenta a jornada de desenvolvimento do **AMDA-Scout**, um agente de IA conversacional criado para auxiliar na exploração de bancos de dados. Mais do que uma ferramenta, este projeto é um **recurso de estudo prático** que demonstra os conceitos, desafios e evoluções na construção de um agente autônomo do zero.

O agente, em seu estado atual, conecta-se a um banco de dados PostgreSQL e utiliza a **API do Google Gemini** para entender e responder a perguntas em linguagem natural sobre os metadados e os dados contidos nele.

## Funcionalidades Atuais

-   **Exploração de Metadados:** O agente pode listar schemas e tabelas, além de descrever a estrutura (colunas e tipos de dados) de uma tabela específica.
-   **Consulta de Dados:** Executa queries `SELECT` de forma segura para buscar informações diretamente das tabelas.
-   **Raciocínio Baseado em Ferramentas:** Utiliza a arquitetura moderna de "Tool Calling" do LangChain para decidir de forma autônoma qual ferramenta usar para responder à pergunta do usuário.
-   **Ambiente Contido:** O banco de dados PostgreSQL de exemplo é totalmente gerenciado via Docker, garantindo uma configuração rápida e reprodutível.
-   **Foco Educacional:** O código é comentado e a estrutura evoluiu para refletir as melhores práticas de desenvolvimento, incluindo testes unitários e separação de configurações.

## Arquitetura e Tecnologias

-   **Framework do Agente:** [LangChain](https://www.langchain.com/)
-   **Provedor de LLM:** [Google Gemini API](https://ai.google.dev/) (atualmente, o único provedor suportado)
-   **Banco de Dados:** PostgreSQL via [Docker](https://www.docker.com/)
-   **Testes:** Pytest

## Como Executar

Siga os passos abaixo para ter o AMDA-Scout rodando em seu ambiente local.

### 1. Pré-requisitos

-   Python 3.10+
-   Docker e Docker Compose
-   Conta Google e uma Chave de API do Gemini (obtida no [Google AI Studio](https://aistudio.google.com/app/apikey))

### 2. Configuração do Ambiente

a. **Clone o repositório** e entre no diretório.

b. **Crie e preencha seu arquivo de ambiente:**
Copie o arquivo de exemplo e adicione suas credenciais.
```bash
cp .env.example .env
```
Abra o `.env` e preencha as variáveis:
```env
# Credenciais do Banco de Dados (correspondem ao docker-compose.yml)
DB_TYPE="postgresql"
DB_USER="amda_user"
DB_PASSWORD="amda_password"
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="amda_db"

# Chave de API do Google Gemini
GOOGLE_API_KEY="sua_chave_de_api_do_gemini_aqui"

# Modelo Gemini a ser usado
LLM_MODEL_NAME="gemini-2.5-flash"
```

c. **Instale as dependências Python:**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# .\venv\Scripts\activate # Windows
pip install -r requirements.txt
```

### 3. Inicie o Banco de Dados

Com o Docker em execução, inicie o container:
```bash
docker-compose up -d
```

### 4. Execute o Agente
```bash
python main.py
```

## Nossa Jornada de Desenvolvimento (Resumo para Estudo)

Este projeto não nasceu pronto. Ele passou por um ciclo de desenvolvimento iterativo, enfrentando desafios comuns na criação de agentes de IA.

#### 1. Fundação e Ferramentas (Commits Iniciais)
-   **Conceitos:** Ambientes Virtuais (`venv`), Gerenciamento de Dependências (`pip`), conteinerização com `Docker Compose`, conexão com banco de dados via `SQLAlchemy`.
-   **Resumo:** A fase inicial focou em criar uma base sólida: um ambiente de desenvolvimento reprodutível e as primeiras "ferramentas" Python que permitiam ao agente interagir com o banco de dados (listar schemas, tabelas, etc.).

#### 2. O Primeiro Agente e Seus Desafios (Arquitetura ReAct)
-   **Conceitos:** Agentes `ReAct` (Reason and Act), Engenharia de Prompt, Modelos Locais (`Ollama`).
-   **Resumo:** A primeira versão do agente usava a arquitetura ReAct. Rapidamente, encontramos os desafios clássicos de agentes baseados em texto:
    -   **"Amnésia":** O agente esquecia o resultado de ações anteriores.
    -   **"Alucinações":** Concluía fatos incorretos com base em erros.
    -   **Loops e Erros de Formatação:** Ficava preso em ciclos de repetição e gerava inputs mal formatados para suas próprias ferramentas.

#### 3. Testes Unitários como Rede de Segurança
-   **Conceitos:** Testes de Unidade, `Pytest`, Fixtures, TDD (Test-Driven Development).
-   **Resumo:** Para combater a imprevisibilidade, pausamos o desenvolvimento do agente para construir uma suíte de testes unitários. Isso nos permitiu validar a lógica das nossas ferramentas de forma isolada, garantindo que o "corpo" do agente era confiável antes de consertar o "cérebro".

#### 4. A Evolução para uma Arquitetura Robusta (Tool Calling)
-   **Conceitos:** Agentes de `Tool Calling`, APIs de Modelos (Gemini), `NotImplementedError`.
-   **Resumo:** Percebendo os limites do ReAct, o projeto pivotou para a arquitetura moderna de **Tool Calling**. Essa abordagem, onde o LLM gera saídas estruturadas em vez de texto livre, provou ser muito mais confiável. A migração nos ensinou sobre as interfaces das bibliotecas (`LLM` vs. `ChatModel`) e como lidar com funcionalidades ainda não implementadas em wrappers de modelos locais.

#### 5. Refinamento Final
-   **Conceitos:** Padrão de Adaptador (`lambda`), Depuração de Interface.
-   **Resumo:** O último passo foi resolver bugs sutis de interface entre o LangChain e nossas funções, garantindo que mesmo ferramentas sem argumentos fossem chamadas corretamente pelo agente.

## Histórico de Alterações (Changelog)

Um resumo da evolução do projeto com base no histórico de commits.

-   **`f61588e`**: Migração final para a API do Google Gemini, simplificando a configuração e o código do agente. A robustez do `Tool Calling` nativo do Gemini resolveu os problemas de raciocínio do agente.
-   **`d28bd0a`**: Externalização do template de prompt para um arquivo separado, melhorando a manutenibilidade. Robustez do adaptador de ferramentas aprimorada.
-   **`6b3ce14`**: Adição de barreiras de segurança e tratamento de inputs com aspas nas ferramentas SQL, tornando o agente mais resiliente a erros de formatação do LLM.
-   **`28c986c`**: Refatoração das ferramentas e expansão da cobertura de testes unitários com `pytest`, criando uma base mais confiável para o desenvolvimento.
-   **`d977585`**: Conteinerização do banco de dados com Docker e criação de um script `init.sql` com dados de exemplo, tornando o projeto autocontido.
-   **`9feb774`**: Estrutura inicial do projeto, configuração do ambiente e implementação da primeira versão das ferramentas de inspeção de banco de dados.

## Licença

Este projeto é distribuído sob a licença MIT.