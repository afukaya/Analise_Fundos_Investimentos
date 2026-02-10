import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from io import StringIO

# URL base para a API SIDRA
SIDRA_BASE_URL = 'https://apisidra.ibge.gov.br/values'

# Tableas de dados API SIDRA

# Tabela 1737: IPCA - Série histórica com número-índice, variação mensal e variações acumuladas em 3 meses, 
# em 6 meses, no ano e em 12 meses (a partir de dezembro/1979)

#Tabela 7060: IPCA - Variação mensal, acumulada no ano, acumulada em 12 meses e peso mensal, para o índice 
# geral, grupos, subgrupos, itens e subitens de produtos e serviços (a partir de janeiro/2020)

SIDRA_INPC_TABLEID = 1736
SIDRA_IPCA_TABLEID = 1737

def converte_para_data(df, col):

    mes_map = {
        "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
        "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
        "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
    }

    df[col] = (
        df[col]
        .str.strip()
        .str.lower()
        .str.replace(r"(\w+)\s+(\d{4})", lambda m: f"{m.group(2)}-{mes_map[m.group(1)]}-01", regex=True)
        .pipe(pd.to_datetime, format="%Y-%m-%d")
    )
    return df

def get_sidra_data(table_id, params):
    param_str:str = "/".join([f"{key}/{value}" for key, value in params.items()])
    url: str = f"{SIDRA_BASE_URL}/t/{table_id}/{param_str}"
    try:
         response: requests.Response = requests.get(url)
         response.raise_for_status()  # Lança uma exceção para códigos de erro HTTP
         data = response.json()
         df: pd.DataFrame = pd.DataFrame(data)
         return df
    except requests.exceptions.RequestException as e:
         print(f"Erro ao fazer a requisição: {e}")
    except (ValueError, KeyError) as e:
         print(f"Erro ao processar o JSON recebido: {e}")
    except Exception as e:
         print(f"Ocorreu um erro inesperado: {e}")
    return None

#Recupera o IPCA variação mensal dos últimos N meses
def get_ipca_variacao_mensal(ultimos_meses=12):
    
    """
    Busca a variação mensal do IPCA (Índice Geral) para o Brasil na API do IBGE (SIDRA)
    utilizando o formato JSON.

    :param ultimos_meses: O número de últimos meses a serem buscados.
    :return: Um DataFrame do Pandas com os dados ou None em caso de erro.
    """
    # Tabela 1737: IPCA - Variação mensal.
    # Variável 63: IPCA - Variação mensal.
    # Classificação C315/7169: Índice geral.
    # Nível Territorial N1/1: Brasil.
    # Período: /p/last%20{ultimos_meses} -> Últimos N meses.

    # Variação IPCA 12 messes

    SIDRA_IPCA_PARAMS = {
        'n1': '1',
        'v' : '63',
        'p' : f'last {ultimos_meses}'
    }

    df = get_sidra_data(SIDRA_IPCA_TABLEID,SIDRA_IPCA_PARAMS)
    df_variacao_mes = df[['D3N','V']]
    
    # Renomeia as colunas de interesse
    df_variacao_mes.rename(columns={
        'D3N':'mes',
        'V':'variacao_mensal'
    }, inplace=True)

    df_variacao_mes = df_variacao_mes.iloc[1:]
    
    # Converte a coluna de variação para tipo numérico
    df_variacao_mes['variacao_mensal'] = pd.to_numeric(df_variacao_mes['variacao_mensal'], errors='coerce')
    converte_para_data(df_variacao_mes,'mes')
    
    return df_variacao_mes