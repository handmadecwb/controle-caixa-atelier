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
        dtf_valor_unit = st.sidebar.number_input("Valor Unitário (R$)", min_value=0.0, format="%.2f", value=0.0)
        dtf_obs = st.sidebar.text_input("Observação Adicional (opcional)")

        if st.sidebar.button("➕ Adicionar DTF ao Pedido"):
            qtd_final = dtf_qtd if dtf_qtd > 0 else 1
            valor_total_dtf = dtf_valor_unit * qtd_final
            obs_texto = f" - Obs: {dtf_obs}" if dtf_obs else ""
            descricao_completa = f"DTF [{dtf_largura}x{dtf_altura}cm] - Posição: {dtf_posicao} - {dtf_prensagem}{obs_texto}"
            
            st.session_state.carrinho_itens.append({
                "Tamanho": f"{dtf_largura}x{dtf_altura}cm",
                "Cor": f"DTF ({dtf_posicao})",
                "Qtd": qtd_final,
                "Reforma": "Não",
                "Obs": descricao_completa,
                "ValorTotal": valor_total_dtf
            })
            st.success("Lote de DTF adicionado à lista!")
            st.rerun()

    elif categoria == "Insumos / Materiais":
        st.sidebar.markdown("**🛠️ Cadastro de Insumo / Material / Peça:**")
        tipo_insumo = st.sidebar.selectbox("Tipo de Insumo", [
            "Tecido", "Linha / Insumo de Costura", "Agulha", "Peça p/ Máquina Reta", 
            "Peça p/ Máquina Overlock", "Peça p/ Bordadeira", "Insumo p/ Prensa / DTF", 
            "Ferramenta / Acessório Geral", "Outro"
        ])
        nome_item_insumo = st.sidebar.text_input("Descrição do Item")
        
        col_ins1, col_ins2 = st.sidebar.columns(2)
        with col_ins1:
            ins_qtd = st.number_input("Quantidade", min_value=1, value=1, step=1)
        with col_ins2:
            ins_unidade = st.selectbox("Unidade de Medida", ["Metros", "Unidades", "Bobinas", "Cones", "Pacotes", "Litros"])

        ins_valor_unit = st.sidebar.number_input("Valor Unitário (R$)", min_value=0.0, format="%.2f", value=0.0)
        ins_obs = st.sidebar.text_input("Observação / Marca / Especificação")

        if st.sidebar.button("➕ Adicionar Insumo à Compra"):
            valor_total_insumo = ins_valor_unit * ins_qtd
            obs_texto = f" - Obs: {ins_obs}" if ins_obs else ""
            descricao_completa = f"Insumo [{tipo_insumo}]: {nome_item_insumo} ({ins_qtd} {ins_unidade}){obs_texto}"
            st.session_state.carrinho_itens.append({
                "Tamanho": f"{ins_qtd} {ins_unidade}",
                "Cor": tipo_insumo,
                "Qtd": ins_qtd,
                "Reforma": "Não",
                "Obs": descricao_completa,
                "ValorTotal": valor_total_insumo
            })
            st.success("Insumo adicionado à lista!")
            st.rerun()

    else:
        st.sidebar.markdown("**Adicionar Itens ao Pedido:**")
        with st.sidebar.form("form_adicionar_item", clear_on_submit=True):
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                item_tam = st.selectbox("Tamanho", [
                    "Único", "RN", "P (Bebê)", "M (Bebê)", "G (Bebê)", 
                    "Tam 1", "Tam 2", "Tam 4", "Tam 6", "Tam 8", "Tam 10", "Tam 12", "Tam 14", "Tam 16", 
                    "PP", "P", "M", "G", "GG", "XG", "G1", "G2", "G3", "G4"
                ])
            with col_t2:
                item_cor_sel = st.selectbox("Cor", [
                    "Preto", "Branco", "Cinza", "Grafite", "Chumbo", "Off-White", "Creme",
                    "Azul Marinho", "Azul Royal", "Azul Claro", "Azul Petróleo", "Turquesa", "Jeans",
                    "Vermelho", "Bordô", "Vinho", "Rosa", "Rosa Chá", "Pink", "Magenta", "Lilás", "Roxo", "Lavanda",
                    "Verde", "Verde Militar", "Verde Musgo", "Verde Água", "Verde Lima", "Mint",
                    "Amarelo", "Mostarda", "Laranja", "Salmão", "Coral", "Terracota",
                    "Marrom", "Bege", "Nude", "Cáqui", "Dourado", "Prata", "Bronze", "Outra"
                ])

            item_cor_custom = st.text_input("Qual a cor? (Se 'Outra' acima)")

            col_t3, col_t4 = st.columns(2)
            with col_t3:
                item_qtd = st.number_input("Qtd", min_value=1, value=1, step=1)
            with col_t4:
                item_reforma = st.selectbox("É Reforma?", ["Não", "Sim"])

            item_obs = st.text_input("Detalhe/Observação do item (ex: barra, ajuste)")
            item_valor_unit = st.number_input("Valor Unitário (R$)", min_value=0.0, format="%.2f", value=0.0)

            btn_adicionar = st.form_submit_button("➕ Adicionar este item na lista")
            
            if btn_adicionar:
                cor_final = item_cor_custom.strip() if item_cor_sel == "Outra" and item_cor_custom.strip() else item_cor_sel
                valor_total_item = item_valor_unit * item_qtd
                st.session_state.carrinho_itens.append({
                    "Tamanho": item_tam,
                    "Cor": cor_final,
                    "Qtd": item_qtd,
                    "Reforma": item_reforma,
                    "Obs": item_obs if item_obs else "",
                    "ValorTotal": valor_total_item
                })
                st.rerun()

    if st.session_state.carrinho_itens:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"### 🛒 Carrinho ({len(st.session_state.carrinho_itens)} itens)")
        
        soma_calculada_itens = 0.0
        opcoes_itens = []
        
        for idx, it in enumerate(st.session_state.carrinho_itens):
            soma_calculada_itens += it["ValorTotal"]
            ref_texto = " [REFORMA]" if it["Reforma"] == "Sim" else ""
            label = f"[{idx+1}] {it['Qtd']}x {it['Tamanho']} ({it['Cor']}){ref_texto} - R$ {it['ValorTotal']:.2f}"
            opcoes_itens.append(label)
            st.sidebar.caption(label)
            
        st.sidebar.markdown("---")
        st.sidebar.markdown("**✏️ Editar / Remover Item:**")
        
        item_selecionado_idx = st.sidebar.selectbox(
            "Selecione o item para alterar:", 
            options=range(len(opcoes_itens)), 
            format_func=lambda x: f"Item #{x+1}"
        )
        
        item_atual = st.session_state.carrinho_itens[item_selecionado_idx]
        
        with st.sidebar.form(f"form_editar_item_{item_selecionado_idx}"):
            edit_tam = st.text_input("Descrição / Tamanho / Medida", value=item_atual["Tamanho"])
            edit_cor = st.text_input("Categoria / Cor / Tipo", value=item_atual["Cor"])
            edit_qtd = st.number_input("Qtd", min_value=1, value=int(item_atual["Qtd"]), step=1)
            
            lista_ref = ["Não", "Sim"]
            idx_ref = lista_ref.index(item_atual["Reforma"]) if item_atual["Reforma"] in lista_ref else 0
            edit_reforma = st.selectbox("É Reforma?", lista_ref, index=idx_ref)
            
            edit_obs = st.text_input("Observação", value=item_atual["Obs"])
            edit_val_unit_cart = st.number_input("Valor Unitário (R$)", min_value=0.0, format="%.2f", value=float(item_atual["ValorTotal"] / item_atual["Qtd"]) if item_atual["Qtd"] > 0 else 0.0)
            
            btn_salvar_edit = st.form_submit_button("💾 Confirmar Alteração")
            
            if btn_salvar_edit:
                novo_total_item = edit_val_unit_cart * edit_qtd
                st.session_state.carrinho_itens[item_selecionado_idx] = {
                    "Tamanho": edit_tam,
                    "Cor": edit_cor,
                    "Qtd": edit_qtd,
                    "Reforma": edit_reforma,
                    "Obs": edit_obs,
                    "ValorTotal": novo_total_item
                }
                st.success("Item atualizado!")
                st.rerun()

        col_del1, col_del2 = st.sidebar.columns(2)
        with col_del1:
            if st.button("🗑️ Excluir Selecionado"):
                st.session_state.carrinho_itens.pop(item_selecionado_idx)
                st.rerun()
        with col_del2:
            if st.button("🗑️ Limpar Tudo"):
                st.session_state.carrinho_itens = []
                st.rerun()

        st.sidebar.markdown(f"**Soma Total: R$ {soma_calculada_itens:.2f}**")
        st.sidebar.markdown("---")
    else:
        soma_calculada_itens = 0.0

    with st.sidebar.form("form_finalizacao"):
        st.markdown("**Fechamento do Pagamento:**")
        
        valor_total_pedido = st.number_input("Valor Total Final (R$)", min_value=0.0, format="%.2f", value=float(soma_calculada_itens))
        valor_pago = st.number_input("Valor Pago / Desembolsado (R$)", min_value=0.0, format="%.2f", value=0.0)
        forma_pgto = st.selectbox("Forma de Pagamento", ["PIX", "Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Fiado / Pendente"])
        
        submit_pedido = st.form_submit_button("💾 Salvar Registro no Caixa")
        
        if submit_pedido:
            if st.session_state.carrinho_itens:
                partes_detalhes = []
                for it in st.session_state.carrinho_itens:
                    ref_tag = " [REFORMA]" if it["Reforma"] == "Sim" else ""
                    obs_str = f" - {it['Obs']}" if it['Obs'].strip() else ""
                    partes_detalhes.append(f"{it['Qtd']}x {it['Tamanho']} ({it['Cor']}){ref_tag}{obs_str} [R$ {it['ValorTotal']:.2f}]")
                detalhes_final = " ;; ".join(partes_detalhes)
            else:
                detalhes_final = "Lançamento direto sem itens especificados"

            restante = valor_total_pedido - valor_pago
            
            if valor_total_pedido <= 0.0:
                status = "Em Orçamento / Em Estudo"
            elif restante > 0.001:
                status = "Pendente"
            else:
                status = "Quitado"
            
            if df.empty:
                novo_id = 1
            else:
                novo_id = int(pd.to_numeric(df["ID"]).max()) + 1
            
            novo_registro = pd.DataFrame([{
                "ID": novo_id,
                "Data": data_registro.strftime("%d/%m/%Y"),
                "Tipo": tipo,
                "Categoria": categoria,
                "Cliente": nome_cliente if nome_cliente else "Não informado",
                "Telefone": telefone_cliente if telefone_cliente else "Não informado",
                "Detalhes": detalhes_final,
                "Valor Total": valor_total_pedido,
                "Valor Pago": valor_pago,
                "Restante": restante,
                "Forma de Pagamento": forma_pgto,
                "Status": status
            }])
            
            df = pd.concat([df, novo_registro], ignore_index=True)
            salvar_dados(df)
            
            st.session_state.carrinho_itens = []
            st.success("Lançamento salvo com sucesso!")
            st.rerun()

# =========================================================================
# ABA 2: CONSULTA & EDIÇÃO DE PEDIDOS (CORREÇÃO DE LEITURA INDIVIDUAL)
# =========================================================================
with aba_consulta:
    st.markdown("### ✏️ Edição de Pedidos & Itens Individuais")
    
    if df.empty:
        st.warning("Nenhum registro encontrado no sistema.")
    else:
        df_sorted = df.sort_values(by="ID", ascending=False)
        opcoes_pedidos = []
        for idx, row in df_sorted.iterrows():
            opcoes_pedidos.append(f"ID #{row['ID']} - {row['Data']} - {row['Cliente']} (Total: R$ {row['Valor Total']})")
            
        pedido_selecionado_str = st.selectbox("Selecione o Lançamento / Pedido para Editar:", opcoes_pedidos)
        
        pedido_id = int(pedido_selecionado_str.split(" - ")[0].replace("ID #", ""))
        idx_pedido = df[df["ID"] == pedido_id].index[0]
        row_pedido = df.loc[idx_pedido]
        
        detalhes_brutos = str(row_pedido["Detalhes"])
        
        # Garante o recarregamento correto e isolado ao trocar de pedido
        if st.session_state.current_edit_id != pedido_id:
            st.session_state.current_edit_id = pedido_id
            
            parsed_items = []
            if detalhes_brutos and detalhes_brutos != "Lançamento direto sem itens especificados":
                itens_split = detalhes_brutos.split(" ;; ")
                for item_str in itens_split:
                    try:
                        # Identifica a quantidade exata antes do "x " isolado
                        if "x " in item_str and " [R$ " in item_str:
                            partes_item = item_str.split("x ", 1)
                            qtd = int(partes_item[0].strip())
                            resto = partes_item[1]
                            desc, val_str = resto.rsplit(" [R$ ", 1)
                            val_total = float(val_str.replace("]", "").strip())
                            parsed_items.append({
                                "desc": desc.strip(),
                                "qtd": qtd,
                                "val_total": val_total
                            })
                        else:
                            parsed_items.append({"desc": item_str, "qtd": 1, "val_total": 0.0})
                    except Exception:
                        parsed_items.append({"desc": item_str, "qtd": 1, "val_total": 0.0})
                        
            st.session_state.edit_order_items = parsed_items
        
        st.markdown("---")
        st.markdown("#### 📋 Itens Individuais do Pedido (Edição & Exclusão)")
        
        novos_itens_editados = []
        valor_total_itens_edit = 0.0
        
        for i, item in enumerate(st.session_state.edit_order_items):
            st.caption(f"**Item #{i+1}**")
            
            novo_desc = st.text_input(f"Descrição #{i+1}", value=item["desc"], key=f"edit_desc_{i}")
            
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                nova_qtd = st.number_input(f"Qtd #{i+1}", min_value=1, value=int(item["qtd"]), step=1, key=f"edit_qtd_{i}")
            with col_e2:
                val_unit_atual = item["val_total"] / item["qtd"] if item["qtd"] > 0 else 0.0
                novo_val_unit = st.number_input(f"Val. Unit #{i+1} (R$)", min_value=0.0, format="%.2f", value=float(val_unit_atual), key=f"edit_val_unit_{i}")
            
            if st.button(f"🗑️ Excluir Item #{i+1}", key=f"del_item_{i}"):
                st.session_state.edit_order_items.pop(i)
                st.rerun()
            
            novo_val_total = nova_qtd * novo_val_unit
            novos_itens_editados.append({
                "desc": novo_desc,
                "qtd": nova_qtd,
                "val_total": novo_val_total
            })
            valor_total_itens_edit += novo_val_total
            st.markdown("---")
            
        st.session_state.edit_order_items = novos_itens_editados
        
        with st.expander("➕ Adicionar NOVO item a este pedido"):
            add_desc = st.text_input("Descrição do novo item")
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                add_qtd = st.number_input("Quantidade", min_value=1, value=1, step=1, key="add_qtd")
            with col_a2:
                add_val_unit = st.number_input("Valor Unitário (R$)", min_value=0.0, format="%.2f", value=0.0, key="add_val_unit")
            
            if st.button("Adicionar Item ao Pedido"):
                if add_desc.strip():
                    st.session_state.edit_order_items.append({
                        "desc": add_desc,
                        "qtd": add_qtd,
                        "val_total": add_qtd * add_val_unit
                    })
                    st.success("Item adicionado ao pedido!")
                    st.rerun()
                else:
                    st.warning("Preencha a descrição do item.")

        st.markdown("---")
        
        with st.form("form_salvar_edicao_pedido"):
            st.markdown("#### 👤 Dados do Pedido / Pagamento")
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                edit_cliente = st.text_input("Cliente / Fornecedor", value=str(row_pedido["Cliente"]))
            with col_d2:
                edit_telefone = st.text_input("Telefone", value=str(row_pedido["Telefone"]))
            
            sugestao_total = valor_total_itens_edit if st.session_state.edit_order_items else row_pedido["Valor Total"]
            
            col_d3, col_d4 = st.columns(2)
            with col_d3:
                edit_valor_total = st.number_input("Valor Total Final (R$)", min_value=0.0, format="%.2f", value=float(sugestao_total))
            with col_d4:
                edit_valor_pago = st.number_input("Valor Pago (R$)", min_value=0.0, format="%.2f", value=float(row_pedido["Valor Pago"]))
            
            formas_pgto = ["PIX", "Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Fiado / Pendente"]
            idx_pgto = formas_pgto.index(row_pedido["Forma de Pagamento"]) if row_pedido["Forma de Pagamento"] in formas_pgto else 0
            edit_forma_pgto = st.selectbox("Forma de Pagamento", formas_pgto, index=idx_pgto)
            
            btn_salvar_alteracoes = st.form_submit_button("💾 Salvar Alterações na Planilha")
            
            if btn_salvar_alteracoes:
                if st.session_state.edit_order_items:
                    partes = []
                    for it in st.session_state.edit_order_items:
                        partes.append(f"{it['qtd']}x {it['desc']} [R$ {it['val_total']:.2f}]")
                    nova_string_detalhes = " ;; ".join(partes)
                else:
                    nova_string_detalhes = "Lançamento sem itens especificados"
                
                novo_restante = edit_valor_total - edit_valor_pago
                if edit_valor_total <= 0.0:
                    novo_status = "Em Orçamento / Em Estudo"
                elif novo_restante > 0.001:
                    novo_status = "Pendente"
                else:
                    novo_status = "Quitado"
                
                df.at[idx_pedido, "Cliente"] = edit_cliente
                df.at[idx_pedido, "Telefone"] = edit_telefone
                df.at[idx_pedido, "Detalhes"] = nova_string_detalhes
                df.at[idx_pedido, "Valor Total"] = edit_valor_total
                df.at[idx_pedido, "Valor Pago"] = edit_valor_pago
                df.at[idx_pedido, "Restante"] = novo_restante
                df.at[idx_pedido, "Forma de Pagamento"] = edit_forma_pgto
                df.at[idx_pedido, "Status"] = novo_status
                
                salvar_dados(df)
                st.session_state.current_edit_id = None
                st.success("Pedido atualizado com sucesso!")
                st.rerun()

        st.markdown("---")
        if st.button("🚨 Excluir Pedido Inteiro", type="primary"):
            df = df.drop(idx_pedido)
            salvar_dados(df)
            st.session_state.current_edit_id = None
            st.success("Pedido excluído do sistema!")
            st.rerun()

# =========================================================================
# ABA 3: CLIENTES
# =========================================================================
with aba_clientes:
    st.markdown("### 👥 Cadastro & Histórico de Clientes")
    st.markdown("Lista consolidada de clientes extraída automaticamente dos registros de entrada.")
    
    if df.empty:
        st.info("Nenhum dado cadastrado.")
    else:
        df_clientes = df[df["Tipo"].str.contains("Entrada", case=False, na=False)].copy()
        
        if df_clientes.empty:
            st.info("Nenhum cliente cadastrado em vendas ainda.")
        else:
            df_agrupado = df_clientes.groupby(["Cliente", "Telefone"]).agg(
                Total_Gasto=("Valor Total", "sum"),
                Qtd_Pedidos=("ID", "count"),
                Ultima_Compra=("Data", "max")
            ).reset_index()
            
            busca_cliente = st.text_input("🔍 Pesquisar Cliente por Nome:")
            if busca_cliente:
                df_agrupado = df_agrupado[df_agrupado["Cliente"].str.contains(busca_cliente, case=False, na=False)]
            
            df_agrupado.columns = ["Nome do Cliente", "Telefone / WhatsApp", "Total Gasto (R$)", "Qtd de Pedidos", "Última Compra"]
            df_agrupado = df_agrupado.sort_values(by="Total Gasto (R$)", ascending=False)
            
            st.dataframe(df_agrupado, use_container_width=True, hide_index=True)

# =========================================================================
# ABA 4: FORNECEDORES
# =========================================================================
with aba_fornecedores:
    st.markdown("### 🚚 Cadastro & Histórico de Fornecedores")
    st.markdown("Lista consolidada de fornecedores e insumos extraída automaticamente dos registros de saída.")
    
    if df.empty:
        st.info("Nenhum dado cadastrado.")
    else:
        df_forn = df[df["Tipo"].str.contains("Saída", case=False, na=False)].copy()
        
        if df_forn.empty:
            st.info("Nenhum fornecedor cadastrado em despesas/saídas ainda.")
        else:
            df_agrupado_forn = df_forn.groupby(["Cliente", "Telefone"]).agg(
                Total_Gasto=("Valor Total", "sum"),
                Qtd_Compras=("ID", "count"),
                Ultima_Compra=("Data", "max")
            ).reset_index()
            
            busca_forn = st.text_input("🔍 Pesquisar Fornecedor por Nome:")
            if busca_forn:
                df_agrupado_forn = df_agrupado_forn[df_agrupado_forn["Cliente"].str.contains(busca_forn, case=False, na=False)]
            
            df_agrupado_forn.columns = ["Nome do Fornecedor", "Telefone / Contato", "Total Investido (R$)", "Qtd de Compras", "Última Compra"]
            df_agrupado_forn = df_agrupado_forn.sort_values(by="Total Investido (R$)", ascending=False)
            
            st.dataframe(df_agrupado_forn, use_container_width=True, hide_index=True)
