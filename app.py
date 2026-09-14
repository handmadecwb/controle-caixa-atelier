from datetime import datetime
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Controle de Caixa - Atelier", page_icon="🧵", layout="centered"
)


# Função para conectar ao Google Sheets usando as credenciais do Secrets
@st.cache_resource
init_connection = lambda: gspread.authorize(
    Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
)


def carregar_dados():
  try:
    client = init_connection()
    # Abre a planilha pelo nome exato no Google Drive
    sheet = client.open("dados_caixa_atelier").worksheet("Página1")
    dados = sheet.get_all_records()
    if not dados:
      return pd.DataFrame(
          columns=[
              "Data",
              "Tipo",
              "Categoria",
              "Nome do Cliente",
              "Telefone / WhatsApp",
              "Largura (cm)",
              "Altura / Comprimento (cm)",
              "Quantidade de Peças",
              "Tempo de Exemplo",
              "Observação",
              "Valor (R$)",
          ]
      )
    return pd.DataFrame(dados)
  except Exception as e:
    st.error(f"Erro ao conectar com o Google Sheets: {e}")
    return pd.DataFrame()


def salvar_dados(novo_registro):
  try:
    client = init_connection()
    sheet = client.open("dados_caixa_atelier").worksheet("Página1")
    # Adiciona a nova linha no final da planilha
    sheet.append_row(list(novo_registro.values()))
    return True
  except Exception as e:
    st.error(f"Erro ao salvar no Google Sheets: {e}")
    return False


# --- TELA DO APLICATIVO ---
st.title("🧵 Controle de Caixa - Atelier")
st.write(
    "Preencha os dados do lançamento abaixo para registrar na sua planilha"
    " oficial."
)

with st.form("form_lancamento", clear_on_submit=True):
  col1, col2 = st.columns(2)
  with col1:
    data_lancamento = st.date_input(
        "Data", datetime.now()
    ).strftime("%d/%m/%Y")
    tipo = st.selectbox("Tipo", ["Entrada (Venda)", "Saída (Despesa)"])
    categoria = st.selectbox(
        "Categoria",
        [
            "Encomenda",
            "Pronta Entrega",
            "Material/Insumo",
            "Manutenção",
            "Outros",
        ],
    )
    nome_cliente = st.text_input("Nome do Cliente")
    telefone = st.text_input("Telefone / WhatsApp")

  with col2:
    largura = st.number_input("Largura (cm)", min_format="%.1f", value=0.0)
    altura = st.number_input(
        "Altura / Comprimento (cm)", min_format="%.1f", value=0.0
    )
    qtd_pecas = st.number_input(
        "Quantidade de Peças", min_value=1, value=1, step=1
    )
    tempo_exemplo = st.text_input("Tempo de Exemplo / Produção")
    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", value=0.0)

  observacao = st.text_area("Observação")

  submitted = st.form_submit_button("Salvar Lançamento")

  if submitted:
    registro = {
        "Data": data_lancamento,
        "Tipo": tipo,
        "Categoria": categoria,
        "Nome do Cliente": nome_cliente,
        "Telefone / WhatsApp": telefone,
        "Largura (cm)": largura,
        "Altura / Comprimento (cm)": altura,
        "Quantidade de Peças": qtd_pecas,
        "Tempo de Exemplo": tempo_exemplo,
        "Observação": observacao,
        "Valor (R$)": valor,
    }

    if salvar_dados(registro):
      st.success("Lançamento salvo com sucesso na planilha do Google Sheets!")
    else:
      st.error("Houve um erro ao salvar o lançamento.")

# --- SEÇÃO DE VISUALIZAÇÃO ---
st.divider()
st.subheader("📋 Registros Atuais")

df_atual = carregar_dados()
if not df_atual.empty:
  st.dataframe(df_atual, use_container_width=True)
else:
  st.info(
      "Nenhum registro encontrado na planilha ainda ou aguardando sincronia."
  )
