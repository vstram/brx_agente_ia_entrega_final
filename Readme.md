  Agente de IA para Análise Gerencial de Notas Fiscais

  Este projeto implementa um agente de Inteligência Artificial conversacional, especializado em análise gerencial de notas fiscais brasileiras.
  Utilizando LangGraph para orquestração e Google Gemini para raciocínio, o agente permite que usuários interajam em linguagem natural para obter
  insights, relatórios e visualizações gráficas a partir de seus dados fiscais. A interface é uma aplicação web interativa construída com Streamlit.

  Funcionalidades

   * Carregamento Automático de Dados: Identifica e carrega arquivos CSV de notas fiscais de diretórios comuns (nf/, nfe/, etc.).
   * Limpeza e Padronização: Processa dados brutos, limpa valores monetários e datas, e padroniza nomes de colunas.
   * Análise de Dados Conversacional: Responde a perguntas complexas sobre os dados fiscais em linguagem natural.
   * Geração de Gráficos: Cria e exibe gráficos (barras, linhas, etc.) para visualização de dados.
   * Busca de Informações Externas: Utiliza pesquisa web para complementar análises com dados externos (cotações, legislação, etc.).
   * Interface Web Intuitiva: Aplicação Streamlit para uma experiência de usuário amigável.

  Pré-requisitos

  Antes de começar, certifique-se de ter o seguinte instalado:

   * Python 3.11+: Recomendamos usar pyenv para gerenciar suas versões de Python.
   * `pip`: Gerenciador de pacotes do Python.
   * Chaves de API:
       * Google Gemini API Key: Para o modelo de linguagem (LLM).
       * Tavily API Key: Para a ferramenta de busca na web.

  Passo a Passo para Rodar o Agente

  Siga as instruções abaixo para configurar e executar a aplicação.

  1. Clonar o Repositório (se aplicável)

  Se você recebeu este projeto como um repositório Git, comece clonando-o:

   1 git clone <URL_DO_SEU_REPOSITORIO>
   2 cd <nome_do_diretorio_do_projeto>

  2. Criar e Ativar o Ambiente Virtual com `pyenv`

  É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto.

   1 # Verifique as versões do Python disponíveis (opcional)
   2 pyenv versions
   3 
   4 # Crie um novo ambiente virtual (usando Python 3.11.12 como exemplo)
   5 pyenv virtualenv 3.11.12 langgraph-agent
   6 
   7 # Defina este ambiente como local para o projeto
   8 pyenv local langgraph-agent

  3. Instalar as Dependências

  Com o ambiente virtual ativado, instale todas as bibliotecas necessárias:

   1 pip install -r requirements.txt

  4. Configurar as Chaves de API

  Crie um arquivo chamado .env na raiz do diretório do projeto (o mesmo nível de app.py e requirements.txt) e adicione suas chaves de API:

   1 GOOGLE_API_KEY="sua_chave_da_api_do_google_gemini_aqui"
   2 TAVILY_API_KEY="sua_chave_da_api_da_tavily_aqui"

  Importante: Mantenha este arquivo .env seguro e NUNCA o envie para repositórios públicos.

  5. Preparar os Dados (Opcional)

  Certifique-se de que seus arquivos CSV de notas fiscais estejam em um diretório chamado nf/ (ou nfe/, notas_fiscais/, notas/) na raiz do projeto. O
  agente irá procurá-los automaticamente.

  Exemplo de estrutura de diretórios:

   1 .
   2 ├── app.py
   3 ├── requirements.txt
   4 ├── .env
   5 ├── nf/
   6 │   ├── 202401_NFs_Cabecalho.csv
   7 │   └── 202401_NFs_Itens.csv
   8 └── src/
   9     └── agent.py

  6. Rodar a Aplicação Streamlit

  Finalmente, execute a aplicação Streamlit a partir da raiz do projeto:

   1 streamlit run app.py

  Seu navegador padrão será aberto automaticamente, exibindo a interface do agente.

  Como Usar o Agente

   1. Insira as Chaves de API: Na barra lateral da aplicação Streamlit, insira suas GOOGLE_API_KEY e TAVILY_API_KEY.
   2. Interaja no Chat: Digite suas perguntas e comandos na caixa de texto do chat.

  Exemplos de Comandos:

   * carregue as notas fiscais (O agente fará isso automaticamente na primeira análise, mas você pode forçar o carregamento).
   * Qual o valor total das notas fiscais?
   * Gere um gráfico de barras com as vendas por estado.
   * Quais os 10 produtos mais vendidos?
   * Busque a cotação atual do dólar.
   * Qual a legislação mais recente sobre ICMS para serviços de TI?