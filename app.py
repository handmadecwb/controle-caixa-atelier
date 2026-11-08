import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
import gspread
from google.oauth2.service_account import Credentials

# =========================================================================
# CONFIGURAÇÃO DA SENHA DE ACESSO
# =========================================================================
SENHA_MESTRE = "Santana1989"

# Configuração da página
st.set_page_config(
    page_title="Controle de Caixa - handmadecwb",
    page_icon="🧵",
    layout="wide"
)

# Tela de Login / Verificação de Senha
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("## 🧵 handmadecwb: Acesso Restrito")
    st.markdown("Por favor, digite a senha para acessar o sistema de gestão.")
    
    senha_digitada = st.text_input("Senha de Acesso", type="password")
    
    if st.button("Entrar"):
        if senha_digitada == SENHA_MESTRE:
            st.session_state.autenticado = True
            st.success("Acesso autorizado!")
            st.rerun()
        else:
            st.error("Senha incorreta. Tente novamente.")
    
    st.stop()

# Função para aplicar a foto de capa como plano de fundo
def definir_fundo(imagem_file):
    if os.path.exists(imagem_file):
        with open(imagem_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(255, 255, 255, 0.75), rgba(255, 255, 255, 0.75)), url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            .main {{
                background-color: transparent !important;
            }}
            .block-container {{
                background-color: rgba(255, 255, 255, 0.88);
                padding: 2rem;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

definir_fundo("fundo.png")

# =========================================================================
# INTEGRAÇÃO COM GOOGLE SHEETS
# =========================================================================
NOME_PLANILHA = "dados_caixa_atelier"

def get_google_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    secrets_dict = dict(st.secrets["gcp_service_account"])
    
    if "private_key" in secrets_dict:
        pk = secrets_dict["private_key"].strip()
        pk = pk.replace("\\n", "\n")
        secrets_dict["private_key"] = pk

    credentials = Credentials.from_service_account_info(
        secrets_dict, scopes=scopes
    )
    gc = gspread.authorize(credentials)
    sh = gc.open(NOME_PLANILHA)
    return sh.sheet1

def carregar_dados():
    colunas_padrao = [
        "ID", "Data", "Tipo", "Categoria", "Cliente", "Telefone", "Detalhes", 
        "Valor Total", "Valor Pago", "Restante", "Forma de Pagamento", "Status"
    ]
    try:
        worksheet = get_google_sheet()
        data = worksheet.get_all_records()
        if data:
            df_temp = pd.DataFrame(data)
            df_temp["ID"] = pd.to_numeric(df_temp["ID"], errors="coerce")
            df_temp = df_temp.dropna(subset=["ID"])
            df_temp["ID"] = df_temp["ID"].astype(int)
            
            df_temp["Valor Total"] = pd.to_numeric(df_temp["Valor Total"], errors="coerce").fillna(0.0)
            df_temp["Valor Pago"] = pd.to_numeric(df_temp["Valor Pago"], errors="coerce").fillna(0.0)
            
            df_temp["Restante"] = df_temp["Valor Total"] - df_temp["Valor Pago"]
            
            df_temp["Status"] = df_temp.apply(
                lambda r: "Em Orçamento / Em Estudo" if r["Valor Total"] <= 0 
                else ("Pendente" if r["Restante"] > 0.001 else "Quitado"), axis=1
            )
            return df_temp
        else:
            df_vazio = pd.DataFrame(columns=colunas_padrao)
            worksheet.update(values=[colunas_padrao], range_name="A1")
            return df_vazio
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        return pd.DataFrame(columns=colunas_padrao)

def salvar_dados(df):
    try:
        worksheet = get_google_sheet()
        worksheet.clear()
        df_para_salvar = df.fillna("")
        dados_lista = [df_para_salvar.columns.values.tolist()] + df_para_salvar.values.tolist()
        worksheet.update(values=dados_lista, range_name="A1")
    except Exception as e:
        st.error(f"Erro ao salvar na planilha: {e}")

df = carregar_dados()

if "carrinho_itens" not in st.session_state:
    st.session_state.carrinho_itens = []

if "edit_order_items" not in st.session_state:
    st.session_state.edit_order_items = []

if "current_edit_id" not in st.session_state:
    st.session_state.current_edit_id = None

if "manual_valor_total" not in st.session_state:
    st.session_state.manual_valor_total = None

st.sidebar.markdown("### 🔒 Sessão")
if st.sidebar.button("Bloquear / Sair"):
    st.session_state.autenticado = False
    st.rerun()
st.sidebar.markdown("---")

st.markdown("## 🧵 handmadecwb: Gestão Integrada de Caixa & Pedidos")
st.markdown("Controle de fluxo de caixa, bordados, costura, impressões DTF e histórico de fornecedores/clientes.")
st.markdown("---")

aba_principal, aba_consulta, aba_clientes, aba_fornecedores = st.tabs([
    "📊 Caixa & Lançamentos", 
    "🔍 Consulta & Edição", 
    "👥 Clientes", 
    "🚚 Fornecedores"
])

# =========================================================================
# ABA 1: CAIXA & LANÇAMENTOS
# =========================================================================
with aba_principal:
    st.markdown("### 📊 Visão Geral do Caixa")
    if df.empty:
        st.info("Nenhum lançamento registrado ainda.")
    else:
        total_geral = df["Valor Total"].sum()
        total_pago = df["Valor Pago"].sum()
        total_restante = df["Restante"].sum()
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("💰 Valor Total Geral", f"R$ {total_geral:.2f}")
        col_m2.metric("✅ Total Pago", f"R$ {total_pago:.2f}")
        col_m3.metric("⏳ Total Restante (Pendente)", f"R$ {total_restante:.2f}")
        
        st.markdown("---")
        st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("---")

    st.sidebar.markdown("### ➕ Novo Lançamento / Pedido")

    data_registro = st.sidebar.date_input("Data do Registro", datetime.today(), format="DD/MM/YYYY")
    tipo = st.sidebar.selectbox("Tipo de Movimentação", ["Entrada (Venda/Serviço)", "Saída (Despesa/Insumo)"])
    categoria = st.sidebar.selectbox("Categoria", ["Impressão DTF", "Matriz de Bordado", "Peça Costurada / Confeccionada", "Insumos / Materiais", "Outros"])

    if tipo.startswith("Saída"):
        label_titulo = "Dados do Fornecedor"
        label_campo = "Nome do Fornecedor"
    else:
        label_titulo = "Dados do Cliente"
        label_campo = "Nome do Cliente"

    st.sidebar.markdown(f"**{label_titulo}:**")
    nome_cliente = st.sidebar.text_input(label_campo, key="form_nome_cliente")
    telefone_cliente = st.sidebar.text_input("Telefone / WhatsApp", key="form_telefone_cliente")

    st.sidebar.markdown("---")

    if categoria == "Matriz de Bordado":
        st.sidebar.markdown("**📐 Parâmetros da Matriz de Bordado:**")
        col_mb1, col_mb2 = st.sidebar.columns(2)
        with col_mb1:
            mb_largura = st.number_input("Largura (cm)", min_value=0.0, format="%.1f", value=10.0)
        with col_mb2:
            mb_altura = st.number_input("Altura (cm)", min_value=0.0, format="%.1f", value=10.0)
            
        col_mb3, col_mb4 = st.sidebar.columns(2)
        with col_mb3:
            mb_pontos = st.number_input("Qtd de Pontos", min_value=0, value=10000, step=500)
        with col_mb4:
            mb_cores = st.number_input("Cores Usadas", min_value=1, value=4, step=1)
            
        col_mb5, col_mb6 = st.sidebar.columns(2)
        with col_mb5:
            mb_tempo = st.text_input("Tempo Gasto (ex: 1h30)", value="1h")
        with col_mb6:
            mb_tecido = st.selectbox("Tecido / Aplicação", ["Camiseta", "Moletom", "Toalha", "Boneca / Pelúcia", "Jeans", "Boné", "Outro"])

        mb_obs_tecnica = st.sidebar.text_input("Detalhe / Observação da Matriz")
        mb_valor_preco = st.sidebar.number_input("Valor da Matriz (R$)", min_value=0.0, format="%.2f", value=0.0)

        if st.sidebar.button("➕ Adicionar Matriz ao Pedido"):
            obs_texto = f" - Obs: {mb_obs_tecnica}" if mb_obs_tecnica else ""
            descricao_completa = f"Matriz [{mb_largura}x{mb_altura}cm, {mb_pontos} pts, {mb_cores} cores, Tecido: {mb_tecido}, Tempo: {mb_tempo}]{obs_texto}"
            st.session_state.carrinho_itens.append({
                "Tamanho": f"{mb_largura}x{mb_altura}cm",
                "Cor": f"{mb_cores} cores",
                "Qtd": 1,
                "Reforma": "Não",
                "Obs": descricao_completa,
                "ValorTotal": mb_valor_preco
            })
            st.success("Matriz adicionada à lista!")
            st.rerun()

    elif categoria == "Impressão DTF":
        st.sidebar.markdown("**🖨️ Parâmetros da Impressão DTF:**")
        col_dtf1, col_dtf2 = st.sidebar.columns(2)
        with col_dtf1:
            dtf_largura = st.number_input("Largura (cm)", min_value=0.0, format="%.1f", value=20.0)
        with col_dtf2:
            dtf_altura = st.number_input("Altura / Comprimento (cm)", min_value=0.0, format="%.1f", value=30.0)
            
        col_dtf3, col_dtf4 = st.sidebar.columns(2)
        with col_dtf3:
            dtf_qtd = st.number_input("Quantidade de Peças", min_value=1, value=1, step=1)
        with col_dtf4:
            dtf_posicao = st.selectbox("Posição da Estampa", ["Frente", "Costas", "Frente e Costas", "Manga / Localizada"])

        dtf_prensagem = st.selectbox("Inclui Prensagem?", ["Apenas Filme (Sem Prensagem)", "Sim (Com Prensagem na Peça)"])
        dtf_valor_unit = st.sidebar.number_
