import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

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

# Arquivo de dados local
ARQUIVO_DADOS = "dados_caixa_atelier.csv"

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    else:
        return pd.DataFrame(columns=[
            "ID", "Data", "Tipo", "Categoria", "Cliente", "Telefone", "Detalhes", 
            "Valor Total", "Valor Pago", "Restante", "Forma de Pagamento", "Status"
        ])

def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

df = carregar_dados()

# Inicializa as variáveis de sessão
if "carrinho_itens" not in st.session_state:
    st.session_state.carrinho_itens = []

if "edit_order_items" not in st.session_state:
    st.session_state.edit_order_items = []

if "current_edit_id" not in st.session_state:
    st.session_state.current_edit_id = None

# Botão de Logout na barra lateral
st.sidebar.markdown("### 🔒 Sessão")
if st.sidebar.button("Bloquear / Sair"):
    st.session_state.autenticado = False
    st.rerun()
st.sidebar.markdown("---")

# Cabeçalho Principal
st.markdown("## 🧵 handmadecwb: Gestão Integrada de Caixa & Pedidos")
st.markdown("Controle de fluxo de caixa, bordados, costura, impressões DTF e histórico de fornecedores/clientes.")
st.markdown("---")

# Abas de Navegação Principal
aba_principal, aba_consulta = st.tabs(["📊 Caixa & Lançamentos", "🔍 Consulta & Edição de Pedidos"])

# =========================================================================
# ABA 1: CAIXA & LANÇAMENTOS
# =========================================================================
with aba_principal:
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

    # 1. SEÇÃO: MATRIZ DE BORDADO
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

    # 2. SEÇÃO: IMPRESSÃO DTF
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

    # 3. SEÇÃO: INSUMOS / MATERIAIS
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

    # 4. SEÇÃO PADRÃO (Peça Costurada / Outros)
    else:
        st.sidebar.markdown("**Adicionar Itens ao Pedido:**")
        
        with st.sidebar.form("form_adicionar_item", clear_on_submit=True):
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                item_tam = st.selectbox("Tamanho", [
                    "Único", 
                    "RN", "P (Bebê)", "M (Bebê)", "G (Bebê)", 
                    "Tam 1", "Tam 2", "Tam 4", "Tam 6", "Tam 8", "Tam 10", "Tam 12", "Tam 14", "Tam 16", 
                    "PP", "P", "M", "G", "GG", "XG", 
                    "G1", "G2", "G3", "G4"
                ])
            with col_t2:
                item_cor_sel = st.selectbox("Cor", [
                    "Preto", "Branco", "Cinza", "Grafite", "Chumbo", "Off-White", "Creme",
                    "Azul Marinho", "Azul Royal", "Azul Claro", "Azul Petróleo", "Turquesa", "Jeans",
                    "Vermelho", "Bordô", "Vinho", "Rosa", "Rosa Chá", "Pink", "Magenta", "Lilás", "Roxo", "Lavanda",
                    "Verde", "Verde Militar", "Verde Musgo", "Verde Água", "Verde Lima", "Mint",
                    "Amarelo", "Mostarda", "Laranja", "Salmão", "Coral", "Terracota",
                    "Marrom", "Bege", "Nude", "Cáqui", "Dourado", "Prata", "Bronze",
                    "Outra"
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

    # Exibição e Edição do Carrinho
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
            st.session_state.pop("form_nome_cliente", None)
            st.session_state.pop("form_telefone_cliente", None)
            st.success("Registro salvo com sucesso no caixa!")
            st.rerun()

    if not df.empty:
        df["Valor Pago"] = pd.to_numeric(df["Valor Pago"], errors="coerce").fillna(0)
        df["Restante"] = pd.to_numeric(df["Restante"], errors="coerce").fillna(0)
        df["Valor Total"] = pd.to_numeric(df["Valor Total"], errors="coerce").fillna(0)

        entradas = df[df["Tipo"].astype(str).str.contains("Entrada")]
        saidas = df[df["Tipo"].astype(str).str.contains("Saída")]
        
        total_recebido = entradas["Valor Pago"].sum()
        total_a_receber = entradas["Restante"].sum()
        total_despesas = saidas["Valor Total"].sum()
        saldo_caixa = total_recebido - total_despesas
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💰 Total em Caixa (Entradas)", f"R$ {total_recebido:.2f}")
        m2.metric("⏳ A Chegar (Fiado/Sinais)", f"R$ {total_a_receber:.2f}", delta_color="inverse")
        m3.metric("💸 Despesas / Insumos", f"R$ {total_despesas:.2f}", delta_color="inverse")
        m4.metric("📊 Saldo Líquido", f"R$ {saldo_caixa:.2f}")
        
        st.markdown("---")
        st.markdown("### 📋 Histórico Geral de Lançamentos")
        
        filtro_status = st.multiselect("Filtrar por Status", options=df["Status"].unique(), default=list(df["Status"].unique()), key="filtro_status_geral")
        df_filtrado = df[df["Status"].isin(filtro_status)]
        
        st.dataframe(df_filtrado, use_container_width=True)
        
        col_exc1, col_exc2 = st.columns([2, 1])
        
        with col_exc1:
            opcoes_exclusao = [f"ID #{row['ID']} - {row['Data']} - {row['Cliente']} (R$ {row['Valor Total']:.2f})" for _, row in df.iterrows()]
            id_para_excluir_str = st.selectbox("Selecione um lançamento específico para excluir:", options=["Selecione..."] + opcoes_exclusao, key="select_excluir_individual")
            if id_para_excluir_str != "Selecione...":
                if st.button("🗑️ Excluir Lançamento Selecionado"):
                    id_alvo = int(id_para_excluir_str.split(" - ")[0].replace("ID #", ""))
                    df = df[pd.to_numeric(df["ID"]) != id_alvo]
                    salvar_dados(df)
                    if st.session_state.current_edit_id == id_alvo:
                        st.session_state.current_edit_id = None
                        st.session_state.edit_order_items = []
                    st.success(f"Lançamento ID #{id_alvo} excluído com sucesso!")
                    st.rerun()
                    
        with col_exc2:
            st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Limpar Todos os Dados"):
                if os.path.exists(ARQUIVO_DADOS):
                    os.remove(ARQUIVO_DADOS)
                st.session_state.current_edit_id = None
                st.session_state.edit_order_items = []
                st.rerun()
    else:
        st.info("Nenhum lançamento cadastrado ainda.")

# =========================================================================
# ABA 2: CONSULTA & EDIÇÃO DE PEDIDOS
# =========================================================================
with aba_consulta:
    st.markdown("### 🔍 Consulta, Rastreio & Edição de Pedidos e Clientes")
    st.markdown("Selecione um pedido existente para gerenciar, editar, excluir ou acrescentar novos itens.")
    
    if not df.empty:
        st.markdown("---")
        st.markdown("#### ✏️ Edição de Pedidos & Itens Individuais")
        
        opcoes_pedidos = [f"ID #{row['ID']} - {row['Data']} - {row['Cliente']} (Total: R$ {row['Valor Total']:.2f})" for _, row in df.iterrows()]
        pedido_selecionado_str = st.selectbox("Selecione o Lançamento / Pedido para Editar:", options=["Selecione..."] + opcoes_pedidos)
        
        if pedido_selecionado_str != "Selecione...":
            id_escolhido = int(pedido_selecionado_str.split(" - ")[0].replace("ID #", ""))
            
            if st.session_state.current_edit_id != id_escolhido:
                st.session_state.current_edit_id = id_escolhido
                row_atual = df[pd.to_numeric(df["ID"]) == id_escolhido].iloc[0]
                
                detalhes_str = str(row_atual["Detalhes"])
                items_parsed = []
                total_val = float(row_atual["Valor Total"])
                
                if ";;" in detalhes_str:
                    raw_partes = [p.strip() for p in detalhes_str.split(";;") if p.strip()]
                else:
                    raw_partes = [p.strip() for p in detalhes_str.split(" | ") if p.strip()]
                
                partes_consolidadas = []
                for p in raw_partes:
                    if p.lower().startswith("obs:") and partes_consolidadas:
                        partes_consolidadas[-1] += " - " + p
                    else:
                        partes_consolidadas.append(p)
                
                per_item = total_val / len(partes_consolidadas) if len(partes_consolidadas) > 0 else total_val
                
                for p in partes_consolidadas:
                    if "[R$" in p:
                        try:
                            desc_part, val_part = p.split("[R$")
                            val = float(val_part.replace("]", "").strip())
                            desc_clean = desc_part.strip()
                            qtd = 1
                            if "x " in desc_clean:
                                parts_q = desc_clean.split("x ", 1)
                                if parts_q[0].strip().isdigit():
                                    qtd = int(parts_q[0].strip())
                                    desc_clean = parts_q[1].strip()
                            unit = val / qtd if qtd > 0 else val
                            items_parsed.append({"desc": desc_clean, "qtd": qtd, "valor_unit": unit})
                        except:
                            items_parsed.append({"desc": p, "qtd": 1, "valor_unit": per_item})
                    else:
                        items_parsed.append({"desc": p, "qtd": 1, "valor_unit": per_item})
                
                st.session_state.edit_order_items = items_parsed

            row_atual = df[pd.to_numeric(df["ID"]) == id_escolhido].iloc[0]
            
            st.markdown("**📋 Itens Individuais do Pedido (Edição & Exclusão):**")
            
            itens_atuais = st.session_state.edit_order_items
            novos_itens = []
            
            for idx, it in enumerate(list(itens_atuais)):
                cols = st.columns([3, 1, 1, 0.7])
                with cols[0]:
                    new_desc = st.text_input(f"Descrição #{idx+1}", value=it["desc"], key=f"item_desc_{id_escolhido}_{idx}")
                with cols[1]:
                    new_qtd = st.number_input(f"Qtd #{idx+1}", min_value=1, value=int(it["qtd"]), step=1, key=f"item_qtd_{id_escolhido}_{idx}")
                with cols[2]:
                    new_unit = st.number_input(f"Val. Unit #{idx+1} (R$)", min_value=0.0, format="%.2f", value=float(it["valor_unit"]), key=f"item_unit_{id_escolhido}_{idx}")
                with cols[3]:
                    st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
                    if st.button("🗑️ Excluir", key=f"btn_del_{id_escolhido}_{idx}", help="Excluir este item"):
                        itens_atuais.pop(idx)
                        st.session_state.edit_order_items = itens_atuais
                        
                        if len(itens_atuais) == 0:
                            df = df[pd.to_numeric(df["ID"]) != id_escolhido]
                            salvar_dados(df)
                            st.session_state.current_edit_id = None
                            st.session_state.edit_order_items = []
                            st.success("Último item excluído. O pedido foi removido completamente do sistema!")
                            st.rerun()
                        else:
                            val_tot_calculado = sum(i["qtd"] * i["valor_unit"] for i in itens_atuais)
                            novo_restante = val_tot_calculado - float(row_atual["Valor Pago"])
                            
                            if val_tot_calculado <= 0.0:
                                novo_status = "Em Orçamento / Em Estudo"
                            elif novo_restante > 0.001:
                                novo_status = "Pendente"
                            else:
                                novo_status = "Quitado"
                            
                            partes_novas = []
                            for i in itens_atuais:
                                sub = i["qtd"] * i["valor_unit"]
                                partes_novas.append(f"{i['qtd']}x {i['desc']} [R$ {sub:.2f}]")
                            detalhes_finais = " ;; ".join(partes_novas)
                            
                            df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Valor Total"] = val_tot_calculado
                            df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Restante"] = novo_restante
                            df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Status"] = novo_status
                            df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Detalhes"] = detalhes_finais
                            salvar_dados(df)
                            
                            st.success("Item removido com sucesso!")
                            st.rerun()

                novos_itens.append({"desc": new_desc, "qtd": new_qtd, "valor_unit": new_unit})
            
            st.session_state.edit_order_items = novos_itens

            st.markdown("---")

            with st.form(f"form_salvar_geral_{id_escolhido}"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    edit_cli = st.text_input("Cliente / Fornecedor", value=str(row_atual["Cliente"]))
                with col_e2:
                    edit_tel = st.text_input("Telefone", value=str(row_atual["Telefone"]))
                
                edit_val_pago = st.number_input("Valor Pago / Desembolsado (R$)", min_value=0.0, format="%.2f", value=float(row_atual["Valor Pago"]))
                
                formas_pagamento_lista = ["PIX", "Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Fiado / Pendente"]
                idx_forma = formas_pagamento_lista.index(row_atual["Forma de Pagamento"]) if row_atual["Forma de Pagamento"] in formas_pagamento_lista else 0
                edit_forma = st.selectbox("Forma de Pagamento", formas_pagamento_lista, index=idx_forma)
                
                btn_salvar_edicao = st.form_submit_button("💾 Salvar Alterações Principais")
                
                if btn_salvar_edicao:
                    if len(st.session_state.edit_order_items) == 0:
                        df = df[pd.to_numeric(df["ID"]) != id_escolhido]
                        salvar_dados(df)
                        st.session_state.current_edit_id = None
                        st.session_state.edit_order_items = []
                        st.success("Pedido removido por não conter nenhum item.")
                        st.rerun()
                    else:
                        val_tot_calculado = sum(i["qtd"] * i["valor_unit"] for i in st.session_state.edit_order_items)
                        novo_restante = val_tot_calculado - edit_val_pago
                        
                        if val_tot_calculado <= 0.0:
                            novo_status = "Em Orçamento / Em Estudo"
                        elif novo_restante > 0.001:
                            novo_status = "Pendente"
                        else:
                            novo_status = "Quitado"
                        
                        partes_novas = []
                        for i in st.session_state.edit_order_items:
                            sub = i["qtd"] * i["valor_unit"]
                            partes_novas.append(f"{i['qtd']}x {i['desc']} [R$ {sub:.2f}]")
                        detalhes_finais = " ;; ".join(partes_novas)
                        
                        df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Cliente"] = edit_cli
                        df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Telefone"] = edit_tel
                        df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Valor Pago"] = edit_val_pago
                        df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Forma de Pagamento"] = edit_forma
                        df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Valor Total"] = val_tot_calculado
                        df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Restante"] = novo_restante
                        df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Status"] = novo_status
                        df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Detalhes"] = detalhes_finais
                        
                        salvar_dados(df)
                        st.success("Pedido atualizado com sucesso!")
                        st.session_state.current_edit_id = None
                        st.session_state.edit_order_items = []
                        st.rerun()

            st.markdown("---")
            st.markdown("#### ➕ Acrescentar Novo Item a Este Pedido")
            with st.form(f"form_acrescentar_item_{id_escolhido}", clear_on_submit=True):
                col_ax1, col_ax2, col_ax3 = st.columns([2, 1, 1])
                with col_ax1:
                    extra_desc = st.text_input("Descrição do Novo Item", placeholder="Ex: Camiseta extra, bordado...")
                with col_ax2:
                    extra_qtd = st.number_input("Quantidade", min_value=1, value=1, step=1)
                with col_ax3:
                    extra_val_unit = st.number_input("Valor Unitário (R$)", min_value=0.0, format="%.2f", value=0.0)

                btn_incluir_extra = st.form_submit_button("➕ Salvar e Acrescentar Novo Item")
                
                if btn_incluir_extra:
                    if extra_desc.strip():
                        st.session_state.edit_order_items.append({
                            "desc": extra_desc.strip(),
                            "qtd": int(extra_qtd),
                            "valor_unit": float(extra_val_unit)
                        })
                        
                        val_tot_calculado = sum(i["qtd"] * i["valor_unit"] for i in st.session_state.edit_order_items)
                        val_pago_atual = float(row_atual["Valor Pago"])
                        novo_restante = val_tot_calculado - val_pago_atual
                        
                        if val_tot_calculado <= 0.0:
                            novo_status = "Em Orçamento / Em Estudo"
                        elif novo_restante > 0.001:
                            novo_status = "Pendente"
                        else:
                            novo_status = "Quitado"
                        
                        partes_novas = []
                        for i in st.session_state.edit_order_items:
                            sub = i["qtd"] * i["valor_unit"]
                            partes_novas.append(f"{i['qtd']}x {i['desc']} [R$ {sub:.2f}]")
                        detalhes_finais = " ;; ".join(partes_novas)
                        
                        df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Valor Total"] = val_tot_calculado
                        df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Restante"] = novo_restante
                        df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Status"] = novo_status
                        df.loc[pd.to_numeric(df["ID"]) == id_escolhido, "Detalhes"] = detalhes_finais
                        
                        salvar_dados(df)
                        st.success("Novo item acrescentado com sucesso!")
                        st.rerun()
