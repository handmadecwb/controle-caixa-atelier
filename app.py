with st.sidebar.form("form_finalizacao"):
        st.markdown("**Fechamento do Pagamento:**")
        
        valor_total_pedido = st.number_input("Valor Total Final (R$)", min_value=0.0, format="%.2f", value=float(soma_calculada_itens))
        valor_pago = st.number_input("Valor Pago / Desembolsado (R$)", min_value=0.0, format="%.2f", value=float(soma_calculada_itens))
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
            
            # Lógica corrigida para definir o status de forma estrita
            if valor_total_pedido <= 0.0:
                status = "Em Orçamento / Em Estudo"
            elif restante > 0.001:
                status = "Pendente"
            else:
                status = "Quitado"
            
            novo_id = 1 if df.empty else int(df["ID"].max()) + 1
            
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
