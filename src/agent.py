import os
import pandas as pd
import matplotlib
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain.tools import tool
from typing import TypedDict, Annotated, Sequence
import operator
from tavily import TavilyClient

# --- Configuração do Matplotlib ---
# Deve ser feito antes de qualquer importação de pyplot
matplotlib.use('Agg')

# --- Carregamento de Variáveis de Ambiente ---
load_dotenv()

# --- Variável Global para o DataFrame ---
df_notas_fiscais = None

# --- Definição das Ferramentas ---

@tool
def load_fiscal_notes():
    """
    Encontra e carrega automaticamente arquivos CSV de notas fiscais de diretórios comuns (como 'nf/', 'nfe/').
    Consolida, padroniza as colunas e prepara os dados para análise.
    Esta ferramenta deve ser chamada antes de qualquer análise de dados.
    """
    global df_notas_fiscais
    
    # Se os dados já estiverem carregados, não faz nada.
    if df_notas_fiscais is not None:
        return "Os dados das notas fiscais já foram carregados."

    possible_dirs = ['nf', 'nfe', 'notas_fiscais', 'notas']
    target_dir = None

    for directory in possible_dirs:
        if os.path.isdir(directory):
            target_dir = directory
            break
    
    if not target_dir:
        return "Nenhum diretório de notas fiscais ('nf', 'nfe', etc.) foi encontrado no projeto."

    all_files = [os.path.join(target_dir, f) for f in os.listdir(target_dir) if f.endswith('.csv')]
    if not all_files:
        return f"Nenhum arquivo CSV encontrado no diretório '{target_dir}'."

    df_list = []
    for file in all_files:
        df = None
        try:
            df = pd.read_csv(file, encoding='utf-8', delimiter=';')
        except Exception:
            try:
                df = pd.read_csv(file, encoding='latin1', delimiter=';')
            except Exception:
                try:
                    df = pd.read_csv(file, encoding='latin1', delimiter=',')
                except Exception as e:
                    return f"Erro ao ler o arquivo {file}: {e}"
        if df is not None:
            df_list.append(df)
    
    if not df_list:
        return "Nenhum dado foi carregado dos arquivos CSV."

    full_df = pd.concat(df_list, ignore_index=True)

    standard_columns_map = {
        'valor_total': ['Valor da Nota', 'Valor Total', 'vlr_total', 'vProd', 'Total', 'valor'],
        'data_emissao': ['Data Emissao', 'dt_emissao', 'dEmi', 'Data'],
        'cliente': ['Nome Cliente', 'xNome', 'Cliente'],
        'produto': ['Descricao', 'xProd', 'Produto'],
        'quantidade': ['Quantidade', 'qCom', 'Qtd']
    }

    rename_map = {}
    original_cols_lower = {col.lower(): col for col in full_df.columns}
    for original_col_lower, original_col in original_cols_lower.items():
        if original_col in rename_map:
            continue
        for standard_name, possible_names in standard_columns_map.items():
            for p_name in possible_names:
                if p_name.lower() in original_col_lower:
                    if standard_name not in rename_map.values():
                        if p_name.lower() == 'data' and 'emiss' not in original_col_lower:
                            continue
                        rename_map[original_col] = standard_name
                        break
            if original_col in rename_map:
                break
    
    full_df.rename(columns=rename_map, inplace=True)

    if 'data_emissao' in full_df.columns:
        full_df['data_emissao'] = pd.to_datetime(full_df['data_emissao'], errors='coerce')
    
    if 'valor_total' in full_df.columns:
        # Limpeza robusta da coluna de valor
        full_df['valor_total'] = full_df['valor_total'].astype(str).str.replace(r'[^\d,]', '', regex=True).str.replace(',', '.', regex=True)
        full_df['valor_total'] = pd.to_numeric(full_df['valor_total'], errors='coerce')

    df_notas_fiscais = full_df
    
    return f"Dados carregados com sucesso! {len(full_df)} registros de {len(all_files)} arquivos. As colunas padronizadas disponíveis são: {list(df_notas_fiscais.columns)}"

@tool
def python_data_analyst(query: str):
    """
    Executa uma análise de dados em Python usando o dataframe de notas fiscais já carregado.
    Pode responder a perguntas, calcular métricas e gerar gráficos.
    Para gerar um gráfico, use matplotlib ou seaborn e salve a figura em 'plot.png'.
    Exemplo de query: 'Qual o faturamento total por mês? Gere um gráfico de barras.'
    O dataframe está disponível na variável 'df'.
    """
    global df_notas_fiscais
    if df_notas_fiscais is None:
        return "Os dados das notas fiscais ainda não foram carregados. Por favor, peça para carregar os dados primeiro."

    prompt = f"""
    Você é um assistente de ciência de dados.
    O usuário fez a seguinte pergunta sobre um dataframe de notas fiscais: '{query}'
    O dataframe pandas está disponível na variável `df`.
    As colunas disponíveis são: {df_notas_fiscais.columns.tolist()}

    Gere um script Python para responder à pergunta.
    - Use a variável `df`. Não a carregue novamente.
    - Se a pergunta pedir um gráfico, use matplotlib.pyplot ou seaborn para criar o gráfico e salve-o como 'plot.png'.
    - O resultado final da sua análise deve ser impresso (usando `print()`).
    - Não inclua ```python no início ou ``` no final. Apenas o código.
    """
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    response = llm.invoke(prompt)
    python_code = response.content.strip()

    if 'plot' in python_code and "savefig" not in python_code:
        python_code += "\nplt.savefig('plot.png')"

    import io
    from contextlib import redirect_stdout

    local_vars = {"df": df_notas_fiscais, "pd": pd, "matplotlib": matplotlib}
    output_buffer = io.StringIO()

    try:
        with redirect_stdout(output_buffer):
            exec(python_code, {"__builtins__": __builtins__}, local_vars)
        
        output = output_buffer.getvalue()
        if not output and os.path.exists("plot.png"):
            output = "Gráfico gerado e salvo como 'plot.png'."
        elif not output:
            output = "Código executado com sucesso, sem saída de texto."
        return f"Resultado da Análise:\n{output}"

    except Exception as e:
        return f"Erro ao executar o código de análise: {e}"

@tool
def web_search(query: str):
    """
    Realiza uma pesquisa na web para buscar informações externas, como notícias,
    cotações, legislação tributária ou dados econômicos.
    """
    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    try:
        response = client.search(query, search_depth="advanced")
        return "\n\n".join([f"Fonte: {r['url']}\nResposta: {r['content']}" for r in response['results'][:2]])
    except Exception as e:
        return f"Erro ao realizar a pesquisa na web: {e}"

# --- Lógica do Agente e Grafo ---

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

def get_agent_executor():
    """
    Cria e compila o grafo do agente LangGraph.
    """
    if not os.getenv("GOOGLE_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        raise ValueError("As chaves GOOGLE_API_KEY e TAVILY_API_KEY devem ser definidas.")

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    tools = [load_fiscal_notes, python_data_analyst, web_search]
    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state):
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    def should_continue(state):
        last_message = state["messages"][-1]
        return "end" if not last_message.tool_calls else "continue"

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("action", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"continue": "action", "end": END},
    )
    graph.add_edge("action", "agent")

    return graph.compile()

# A função load_fiscal_notes_tool é apenas uma referência direta à ferramenta
# para que a app Streamlit possa chamá-la diretamente se necessário.
load_fiscal_notes_tool = load_fiscal_notes