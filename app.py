import pandas as pd
import streamlit as st

# Carregar a planilha base uma vez e cachear os dados
@st.cache_data
def carregar_planilha(file_path):
    return pd.read_excel(file_path)

# Função de busca por Código
def buscar_por_codigo(codigos, df):
    df_codigos = df[df['Código'].isin(codigos)]
    resultados = []
    for gauss, grupo in df_codigos.groupby('Gauss'):
        codigos_encontrados = ", ".join(grupo['Código'].tolist())
        resultado = {
            'Gauss': gauss,
            'Marca': grupo['Marca'].iloc[0],
            'Código': codigos_encontrados,
            'Produto': grupo['Produto'].iloc[0],
            'Status': grupo['Status'].iloc[0]
        }
        resultados.append(resultado)

    for codigo in codigos:
        if not any(d['Código'] == codigo or codigo in d['Código'].split(", ") for d in resultados):
            resultados.append({
                'Gauss': 'Não encontrado',
                'Marca': 'Não encontrado',
                'Código': codigo,
                'Produto': 'Não encontrado',
                'Status': 'Não encontrado'
            })
    return resultados

# Função para gerar a planilha com os resultados da pesquisa
def gerar_planilha_pesquisa(resultados, output_file, apenas_ativos=False, formato="virgula"):
    df_resultados = pd.DataFrame(resultados)
    if apenas_ativos:
        df_resultados = df_resultados[df_resultados['Status'] == 'Ativo']

    if formato == "abaixo":
        # Expanda os códigos para uma lista com cada código em uma linha separada
        df_expanded = pd.DataFrame(
            [
                {**row, 'Código': codigo}
                for _, row in df_resultados.iterrows()
                for codigo in row['Código'].split(', ')
            ]
        )
        df_resultados = df_expanded

    df_resultados.to_excel(output_file, index=False)
    st.success(f"Planilha gerada: {output_file}")

# Configurar o layout do Streamlit
st.set_page_config(page_title="Gauss", page_icon="🔍", layout="wide")

# Estilizar o fundo, o título, e os resultados
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(to bottom, #f0f4f5, #dfefff);
        padding: 20px;
        border-radius: 10px;
    }
    .center-title {
        display: flex;
        justify-content: center;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        color: #1f78b4;
    }
    .left-search {
        position: absolute;
        top: 20px;
        left: 20px;
        width: 300px;
    }
    .result-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
    }
    .result {
        flex: 0 0 48%;
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        background-color: #ffffff;
    }
    .result b {
        color: #1f78b4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título
st.markdown('<h1 class="center-title">Gauss</h1>', unsafe_allow_html=True)

# Campo de entrada para os códigos
st.markdown('<div class="left-search">', unsafe_allow_html=True)
codigos_input = st.text_area("Insira um ou mais códigos:", "")
st.markdown('</div>', unsafe_allow_html=True)

# Carregar a planilha base
file_path = 'Cross000-BRA-referencia-cruzada-00.xlsx'
df = carregar_planilha(file_path)

# Função para processar a entrada de códigos
def processar_entrada(entrada):
    codigos = entrada.replace(',', '\n').split('\n')
    codigos = [codigo.strip() for codigo in codigos if codigo.strip()]
    return codigos

# Botão para executar a pesquisa
if st.button("Pesquisar"):
    if codigos_input:
        codigos = processar_entrada(codigos_input)
        resultados = buscar_por_codigo(codigos, df)
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        for resultado in resultados:
            st.markdown(
                f"""
                <div class="result">
                    <b>Código Gauss:</b> {resultado['Gauss']}<br>
                    <b>Marca:</b> {resultado['Marca']}<br>
                    <b>Código:</b> {resultado['Código']}<br>
                    <b>Produto:</b> {resultado['Produto']}<br>
                    <b>Status:</b> {resultado['Status']}
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("Por favor, insira um ou mais códigos.")

# Opção de formato para extração
formato_opcao = st.radio(
    "Escolha o formato de extração dos códigos:",
    ('Separado por vírgula', 'Um abaixo do outro')
)
formato = "virgula" if formato_opcao == 'Separado por vírgula' else "abaixo"

# Botão para extrair a planilha com status ativo
if st.button("Extrair Planilha Ativa"):
    if codigos_input:
        codigos = processar_entrada(codigos_input)
        resultados = buscar_por_codigo(codigos, df)
        output_file = 'resultados_pesquisa_ativa.xlsx'
        gerar_planilha_pesquisa(resultados, output_file, apenas_ativos=True, formato=formato)
    else:
        st.error("Por favor, insira um ou mais códigos para gerar a planilha.")

# Botão para extrair a planilha geral
if st.button("Extrair Planilha Geral"):
    if codigos_input:
        codigos = processar_entrada(codigos_input)
        resultados = buscar_por_codigo(codigos, df)
        output_file = 'resultados_pesquisa_geral.xlsx'
        gerar_planilha_pesquisa(resultados, output_file, apenas_ativos=False, formato=formato)
    else:
        st.error("Por favor, insira um ou mais códigos para gerar a planilha.")

