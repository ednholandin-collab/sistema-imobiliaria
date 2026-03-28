import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests  # Necessário para a busca do CEP

# --- 1 FUNÇÕES DE APOIO E CONEXÃO ---


def conectar():
    return psycopg2.connect(st.secrets["DB_URL"])


def formata_moeda(valor):
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


st.set_page_config(
    page_title="Mayara Vieira Negócios Imobiliários", layout="wide", page_icon="🏢")

# --- 2 TRAVA DE VISUAL E SEGURANÇA (OCULTA O MENU DO STREAMLIT) ---
st.markdown("""
    <style>
    /* Oculta o cabeçalho superior e o menu de configurações */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    /* Oculta a marca d'água do Streamlit no rodapé */
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3 SISTEMA DE LOGIN ---
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.header("🔐 Acesso ao Mayara Vieira")
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Acessar"):
            try:
                conn = conectar()
                cur = conn.cursor()
                cur.execute(
                    "SELECT login FROM usuarios WHERE login = %s AND senha_hash = %s", (u, s))
                res = cur.fetchone()
                conn.close()
                if res:
                    st.session_state.logado, st.session_state.usuario = True, res[0]
                    st.session_state.pagina_atual = "Dashboard"
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos")
            except Exception as e:
                st.error(f"Erro ao acessar banco: {e}")
    st.stop()

USUARIO = st.session_state.usuario
with st.sidebar:
    st.write(f"👤 Logado como: **{USUARIO}**")
    if st.button("Sair / Logout"):
        st.session_state.logado = False
        st.session_state.pagina_atual = "Dashboard"
        st.rerun()

st.title(f"🏠 Bem-vindo, {USUARIO}")

# --- 3. MENU LATERAL EXPANSÍVEL ---
if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = "Dashboard"

with st.sidebar:
    st.markdown("### 🏢 Menu Principal")

    # ▼ Módulo 1: Gestão de Imóveis
    with st.expander("🏠 Gestão de Imóveis", expanded=False):
        with st.expander("📋 Cadastro de Imóveis", expanded=False):
            if st.button("Cadastro Imóvel", key="m1_novo", use_container_width=True):
                st.session_state.pagina_atual = "Imoveis_Novo"
            if st.button("Lista de Imóveis", key="m1_lista", use_container_width=True):
                st.session_state.pagina_atual = "Imoveis_Lista"
            if st.button("Tipos de Imóveis", key="m1_tipos", use_container_width=True):
                st.session_state.pagina_atual = "Imoveis_Tipos"
        with st.expander("✅ Disponibilidade", expanded=False):
            if st.button("Imóveis Disponíveis", key="m1_disp", use_container_width=True):
                st.session_state.pagina_atual = "Imoveis_Disponiveis"
            if st.button("Imóveis em Negociação", key="m1_negoc", use_container_width=True):
                st.session_state.pagina_atual = "Imoveis_Negociacao"
        with st.expander("🛠️ Manutenção", expanded=False):
            if st.button("Ordens de Serviço", key="m1_os", use_container_width=True):
                st.session_state.pagina_atual = "Imoveis_OS"
            if st.button("Histórico de Manutenções", key="m1_hist_os", use_container_width=True):
                st.session_state.pagina_atual = "Imoveis_Historico_OS"

    # ▼ Módulo 2: Gestão de Corretores
    with st.expander("👔 Gestão de Corretores", expanded=False):
        with st.expander("📋 Cadastro de Corretores", expanded=False):
            if st.button("Novo Corretor", key="m2_novo", use_container_width=True):
                st.session_state.pagina_atual = "Corretores_Novo"
            if st.button("Lista de Corretores", key="m2_lista", use_container_width=True):
                st.session_state.pagina_atual = "Corretores_Lista"
        with st.expander("💰 Comissões", expanded=False):
            if st.button("Comissões Pendentes", key="m2_comis_pend", use_container_width=True):
                st.session_state.pagina_atual = "Corretores_Comissoes_Pendentes"
            if st.button("Histórico de Comissões", key="m2_comis_hist", use_container_width=True):
                st.session_state.pagina_atual = "Corretores_Comissoes_Historico"
        with st.expander("📈 Desempenho", expanded=False):
            if st.button("Avaliações", key="m2_aval", use_container_width=True):
                st.session_state.pagina_atual = "Corretores_Avaliacoes"
            if st.button("Relatórios de Vendas", key="m2_rel_vendas", use_container_width=True):
                st.session_state.pagina_atual = "Corretores_Relatorios"

    # ▼ Módulo 3: Gestão de Clientes
    with st.expander("👥 Gestão de Clientes", expanded=False):
        with st.expander("📋 Cadastro de Clientes", expanded=False):
            if st.button("Novo Cliente", key="m3_novo", use_container_width=True):
                st.session_state.pagina_atual = "Clientes_Novo"
            if st.button("Lista de Clientes", key="m3_lista", use_container_width=True):
                st.session_state.pagina_atual = "Clientes_Lista"
        with st.expander("🎯 Interesses", expanded=False):
            if st.button("Registros de Interesse", key="m3_int_reg", use_container_width=True):
                st.session_state.pagina_atual = "Clientes_Interesses"
            if st.button("Histórico de Visitas", key="m3_int_vis", use_container_width=True):
                st.session_state.pagina_atual = "Clientes_Visitas"
        with st.expander("🤝 Atendimentos", expanded=False):
            if st.button("Agendar Atendimento", key="m3_atend_agend", use_container_width=True):
                st.session_state.pagina_atual = "Clientes_Agendar"
            if st.button("Histórico de Atendimentos", key="m3_atend_hist", use_container_width=True):
                st.session_state.pagina_atual = "Clientes_Historico_Atend"

    # ▼ Módulo 4: Gestão de Vendas
    with st.expander("🤝 Gestão de Vendas", expanded=False):
        with st.expander("💰 Vendas", expanded=False):
            if st.button("Nova Venda", key="m4_nova", use_container_width=True):
                st.session_state.pagina_atual = "Vendas_Nova"
            if st.button("Histórico de Vendas", key="m4_hist", use_container_width=True):
                st.session_state.pagina_atual = "Vendas_Historico"
        with st.expander("🔄 Acompanhamento de Processos", expanded=False):
            if st.button("Negociações Ativas", key="m4_negoc", use_container_width=True):
                st.session_state.pagina_atual = "Vendas_Negociacoes"
            with st.expander("⏬ Etapas do Processo", expanded=False):
                if st.button("Propostas Recebidas", key="m4_etp_prop", use_container_width=True):
                    st.session_state.pagina_atual = "Vendas_Propostas"
                if st.button("Documentação em Análise", key="m4_etp_doc", use_container_width=True):
                    st.session_state.pagina_atual = "Vendas_Docs"
                if st.button("Aprovação de Financiamento", key="m4_etp_fin", use_container_width=True):
                    st.session_state.pagina_atual = "Vendas_Financiamento"
                if st.button("Assinatura de Contrato", key="m4_etp_ass", use_container_width=True):
                    st.session_state.pagina_atual = "Vendas_Assinatura"
                if st.button("Conclusão de Venda", key="m4_etp_conc", use_container_width=True):
                    st.session_state.pagina_atual = "Vendas_Conclusao"
        with st.expander("📊 Relatórios e Desempenho", expanded=False):
            if st.button("Relatório de Vendas", key="m4_rel_ven", use_container_width=True):
                st.session_state.pagina_atual = "Vendas_Relatorios"
            if st.button("Análise de Tempo Fechamento", key="m4_rel_tempo", use_container_width=True):
                st.session_state.pagina_atual = "Vendas_Tempo_Fechamento"

    # ▼ Módulo 5: Gestão Financeira
    with st.expander("💲 Gestão Financeira", expanded=False):
        with st.expander("📉 Controle de Despesas", expanded=False):
            if st.button("Novo Lançamento", key="m5_desp_nova", use_container_width=True):
                st.session_state.pagina_atual = "Fin_Despesa_Nova"
            if st.button("Lista de Despesas", key="m5_desp_lista", use_container_width=True):
                st.session_state.pagina_atual = "Fin_Despesa_Lista"
            if st.button("Categorias de Despesas", key="m5_desp_cat", use_container_width=True):
                st.session_state.pagina_atual = "Fin_Despesa_Cat"
        with st.expander("📈 Controle de Entradas", expanded=False):
            if st.button("Novo Lançamento", key="m5_ent_nova", use_container_width=True):
                st.session_state.pagina_atual = "Fin_Entrada_Nova"
            if st.button("Lista de Entradas", key="m5_ent_lista", use_container_width=True):
                st.session_state.pagina_atual = "Fin_Entrada_Lista"
            if st.button("Categorias de Entradas", key="m5_ent_cat", use_container_width=True):
                st.session_state.pagina_atual = "Fin_Entrada_Cat"
        with st.expander("⚖️ Fluxo de Caixa", expanded=False):
            if st.button("Entradas vs. Saídas", key="m5_flux_vs", use_container_width=True):
                st.session_state.pagina_atual = "Fin_Fluxo_Comparativo"
            if st.button("Saldo Atual", key="m5_flux_saldo", use_container_width=True):
                st.session_state.pagina_atual = "Fin_Fluxo_Saldo"
        with st.expander("📊 Relatórios Financeiros", expanded=False):
            if st.button("Resumo Mensal", key="m5_rel_mensal", use_container_width=True):
                st.session_state.pagina_atual = "Fin_Rel_Mensal"
            if st.button("Análises de Custos", key="m5_rel_custos", use_container_width=True):
                st.session_state.pagina_atual = "Fin_Rel_Custos"
        with st.expander("💳 Pagamentos e Compras", expanded=False):
            if st.button("Pagamentos Pendentes", key="m5_pag_pend", use_container_width=True):
                st.session_state.pagina_atual = "Fin_Pag_Pendentes"
            if st.button("Histórico de Pagamentos", key="m5_pag_hist", use_container_width=True):
                st.session_state.pagina_atual = "Fin_Pag_Historico"
        with st.expander("📅 Orçamentos", expanded=False):
            if st.button("Planejamento de Gastos", key="m5_orc_plan", use_container_width=True):
                st.session_state.pagina_atual = "Fin_Orc_Plan"
            if st.button("Real x Planejado", key="m5_orc_real", use_container_width=True):
                st.session_state.pagina_atual = "Fin_Orc_Real"

    # ▼ Módulo 6: Gestão de Contratos
    with st.expander("📄 Gestão de Contratos", expanded=False):
        with st.expander("📋 Cadastro de Contratos", expanded=False):
            if st.button("Novo Contrato", key="m6_novo", use_container_width=True):
                st.session_state.pagina_atual = "Contratos_Novo"
            if st.button("Lista de Contratos", key="m6_lista", use_container_width=True):
                st.session_state.pagina_atual = "Contratos_Lista"
        with st.expander("⚙️ Gerenciamento", expanded=False):
            if st.button("Contratos Ativos", key="m6_ativos", use_container_width=True):
                st.session_state.pagina_atual = "Contratos_Ativos"
            if st.button("Contratos Concluídos", key="m6_conc", use_container_width=True):
                st.session_state.pagina_atual = "Contratos_Concluidos"

    # ▼ Módulo 7: Cadastros Gerais
    with st.expander("⚙️ Cadastros Gerais", expanded=False):
        with st.expander("👤 Usuários do Sistema", expanded=False):
            if st.button("Novo Usuário", key="m7_usr_novo", use_container_width=True):
                st.session_state.pagina_atual = "Users_Novo"
            if st.button(" Lista de Usuários", key="m7_usr_lista", use_container_width=True):
                st.session_state.pagina_atual = "Users_Lista"
        with st.expander("🔧 Parâmetros de Configuração", expanded=False):
            if st.button("Configurações Gerais", key="m7_cfg_geral", use_container_width=True):
                st.session_state.pagina_atual = "Config_Gerais"
            if st.button("Regras e Permissões", key="m7_cfg_regras", use_container_width=True):
                st.session_state.pagina_atual = "Config_Regras"

    st.divider()
    if st.button("📊 Dashboard Executivo", key="btn_dash_geral", use_container_width=True):
        st.session_state.pagina_atual = "Dashboard"

    st.divider()
    if st.button("Sair / Logout", type="primary", use_container_width=True):
        st.session_state.logado = False
        st.session_state.pagina_atual = "Dashboard"
        st.rerun()

# --- VARIÁVEL DE ROTEAMENTO GERAL ---
pagina = st.session_state.pagina_atual


# ==========================================
# 4. ROTEAMENTO DAS TELAS (ÁREA PRINCIPAL)
# ==========================================

# ------------------------------------------
# TELA 1: CADASTRO E EDIÇÃO DE IMÓVEIS
# ------------------------------------------
if pagina == "Imoveis_Novo":
    st.header("🏢 Cadastro de Imóveis")

    import requests

    if 'imovel_editando' not in st.session_state:
        st.session_state.imovel_editando = None
    if 'abrir_expander' not in st.session_state:
        st.session_state.abrir_expander = False
    if 'tabela_versao' not in st.session_state:
        st.session_state.tabela_versao = 0
    if 'dados_cep_imovel' not in st.session_state:
        st.session_state.dados_cep_imovel = {}

    conn = conectar()

    try:
        props = pd.read_sql(
            "SELECT id_cliente, nome_completo FROM clientes", conn)
    except:
        props = pd.DataFrame()

    edit = st.session_state.imovel_editando
    id_interno = int(edit['id_imovel']) if edit else 0

    def tratar_numero(valor):
        try:
            return float(valor) if pd.notna(valor) else 0.0
        except:
            return 0.0

    def tratar_int(valor):
        try:
            return int(valor) if pd.notna(valor) else 0
        except:
            return 0

    # --- EXPANDER DE CADASTRO / EDIÇÃO ---
    with st.expander("➕ Cadastrar / Alterar Imóvel", expanded=st.session_state.abrir_expander):

        st.markdown("#### 🔎 Busca Automática de Endereço")
        c_busca1, c_busca2 = st.columns([1, 3])
        chave_cep_imovel = f"input_cep_imovel_{st.session_state.tabela_versao}"
        cep_busca = c_busca1.text_input(
            "Digite o CEP e aperte ENTER", placeholder="Apenas números", max_chars=9, key=chave_cep_imovel)

        if cep_busca:
            cep_limpo = cep_busca.replace("-", "").replace(".", "").strip()
            if len(cep_limpo) == 8:
                try:
                    resposta = requests.get(
                        f"https://viacep.com.br/ws/{cep_limpo}/json/").json()
                    if "erro" not in resposta:
                        st.session_state.dados_cep_imovel = resposta
                        c_busca2.success(
                            f"✅ Encontrado: {resposta['logradouro']}, {resposta['bairro']} - {resposta['localidade']}/{resposta['uf']}")
                    else:
                        st.session_state.dados_cep_imovel = {}
                        c_busca2.error("❌ CEP não encontrado.")
                except:
                    c_busca2.error("❌ Erro ao consultar o ViaCEP.")
            elif len(cep_limpo) > 0:
                c_busca2.warning("⚠️ O CEP deve ter 8 números.")

        st.divider()

        chave_form = f"form_imovel_{st.session_state.tabela_versao}"

        with st.form(chave_form, clear_on_submit=False):
            st.markdown("📍 **Localização**")

            val_rua = st.session_state.dados_cep_imovel.get(
                'logradouro', edit.get('endereco_rua', '') if edit else "")
            val_bairro = st.session_state.dados_cep_imovel.get(
                'bairro', edit.get('bairro', '') if edit else "")
            val_cidade = st.session_state.dados_cep_imovel.get(
                'localidade', edit.get('cidade', '') if edit else "")
            val_cep_form = st.session_state.dados_cep_imovel.get(
                'cep', edit.get('cep', '') if edit else "")

            c_loc1, c_loc2, c_loc3, c_loc4 = st.columns([2, 2, 2, 1])
            with c_loc1:
                rua_val = st.text_input("Rua", value=val_rua)
            with c_loc2:
                bairro_val = st.text_input("Bairro", value=val_bairro)
            with c_loc3:
                cidade_val = st.text_input("Cidade", value=val_cidade)
            with c_loc4:
                cep_val = st.text_input("CEP", value=val_cep_form)

            st.divider()

            st.markdown("🏠 **Características do Imóvel**")
            c_car1, c_car2, c_car3, c_car4, c_car5, c_car6 = st.columns(
                [2, 1, 1, 1, 1, 1])

            try:
                df_tipos_db = pd.read_sql(
                    "SELECT nome FROM tipos_imoveis ORDER BY nome", conn)
                lista_tipos = df_tipos_db['nome'].tolist() if not df_tipos_db.empty else [
                    "Apartamento", "Casa"]
            except:
                lista_tipos = ["Apartamento", "Casa"]

            tipo_idx = lista_tipos.index(edit.get('tipo_imovel')) if edit and edit.get(
                'tipo_imovel') in lista_tipos else 0

            with c_car1:
                tipo_val = st.selectbox(
                    "Tipo do Imóvel", lista_tipos, index=tipo_idx)
            with c_car2:
                area_t = st.number_input("Área (m²)", value=tratar_numero(
                    edit.get('area_total_m2')) if edit else 0.0)
            with c_car3:
                qtos_val = st.number_input("Quartos", min_value=0, value=tratar_int(
                    edit.get('quartos')) if edit else 0)
            with c_car4:
                suites_val = st.number_input(
                    "Suítes", min_value=0, value=tratar_int(edit.get('suites')) if edit else 0)
            with c_car5:
                banh_val = st.number_input("Banheiros", min_value=0, value=tratar_int(
                    edit.get('banheiros')) if edit else 0)
            with c_car6:
                vagas_val = st.number_input("Vagas", min_value=0, value=tratar_int(
                    edit.get('garagens')) if edit else 0)

            st.divider()

            st.markdown("💰 **Valores e Contrato**")
            c_val1, c_val2, c_val3, c_val4 = st.columns(4)
            with c_val1:
                v_venda_val = st.number_input("Valor Venda", min_value=0.0, value=tratar_numero(
                    edit.get('valor_venda')) if edit else 0.0)
                iptu_v = st.number_input("IPTU Anual", value=tratar_numero(
                    edit.get('iptu_anual')) if edit else 0.0)

            with c_val2:
                lista_st = ["Disponível", "Reservado", "Vendido"]
                st_idx = lista_st.index(
                    edit['status']) if edit and edit['status'] in lista_st else 0
                status_i = st.selectbox("Status Venda", lista_st, index=st_idx)

                valor_agenc = tratar_numero(edit.get('perc_agenciamento')) if edit and pd.notna(
                    edit.get('perc_agenciamento')) else 6.0
                p_agenc_val = st.number_input(
                    "% Agenciamento", min_value=0.0, value=valor_agenc)

            with c_val3:
                lista_doc = ["Ok", "Em Regularização", "Falta Matrícula"]
                doc_idx = lista_doc.index(edit.get('doc_status')) if edit and edit.get(
                    'doc_status') in lista_doc else 0
                doc_sit = st.selectbox(
                    "Status Documentação", lista_doc, index=doc_idx)

                agenciador_val = st.text_input("Agenciador / Captador", value=edit.get(
                    'agenciador_nome', '') if edit else "", placeholder="Ex: João (Corretor), Seu Zé (Zelador)")

            with c_val4:
                if not props.empty:
                    nomes_props = props['nome_completo'].tolist()
                    idx_p = 0
                    if edit and pd.notna(edit.get('id_proprietario')):
                        try:
                            nome_p = props.loc[props['id_cliente'] ==
                                               edit['id_proprietario'], 'nome_completo'].values[0]
                            if nome_p in nomes_props:
                                idx_p = nomes_props.index(nome_p)
                        except:
                            idx_p = 0
                    sel_p = st.selectbox(
                        "Proprietário", nomes_props, index=idx_p)
                else:
                    sel_p = "Nenhum"
                    st.selectbox("Proprietário", [
                                 "Nenhum (Cadastre um cliente)"], disabled=True)

            st.divider()

            st.markdown("✨ **Extras e Links**")
            c_link, c_comod = st.columns([1, 2])
            with c_link:
                link_val = st.text_input("🔗 Link do Imóvel no Site", value=edit.get(
                    'link_site', "") if edit else "")

            with c_comod:
                try:
                    df_comod_db = pd.read_sql(
                        "SELECT nome FROM comodidades ORDER BY nome", conn)
                    opcoes_comodidades = df_comod_db['nome'].tolist(
                    ) if not df_comod_db.empty else []
                except:
                    opcoes_comodidades = ["Piscina", "Academia"]

                comod_default = edit.get('comodidades').split(
                    ", ") if edit and edit.get('comodidades') else []
                comod_default = [
                    c for c in comod_default if c in opcoes_comodidades]
                comod_sel = st.multiselect(
                    "Comodidades", opcoes_comodidades, default=comod_default)
                comod_string = ", ".join(comod_sel)

            btn_salvar = st.form_submit_button("💾 Salvar Registro")

            if btn_salvar:
                if props.empty or sel_p == "Nenhum":
                    st.error(
                        "⚠️ Atenção: É obrigatório vincular um Proprietário ao imóvel.")
                else:
                    cur = conn.cursor()
                    id_p_sel = int(
                        props[props['nome_completo'] == sel_p]['id_cliente'].values[0])

                    if id_interno == 0:
                        cur.execute("""
                            INSERT INTO imoveis 
                            (endereco_rua, bairro, cidade, cep, tipo_imovel, quartos, suites, banheiros, garagens, area_total_m2, valor_venda, status, id_proprietario, criado_por, doc_status, iptu_anual, comodidades, link_site, perc_agenciamento, agenciador_nome) 
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (rua_val, bairro_val, cidade_val, cep_val, tipo_val, qtos_val, suites_val, banh_val, vagas_val, area_t, v_venda_val, status_i, id_p_sel, USUARIO, doc_sit, iptu_v, comod_string, link_val, p_agenc_val, agenciador_val))
                    else:
                        cur.execute("""
                            UPDATE imoveis SET 
                            endereco_rua=%s, bairro=%s, cidade=%s, cep=%s, tipo_imovel=%s, quartos=%s, suites=%s, banheiros=%s, garagens=%s, area_total_m2=%s, valor_venda=%s, status=%s, id_proprietario=%s, doc_status=%s, iptu_anual=%s, comodidades=%s, link_site=%s, perc_agenciamento=%s, agenciador_nome=%s 
                            WHERE id_imovel=%s
                        """, (rua_val, bairro_val, cidade_val, cep_val, tipo_val, qtos_val, suites_val, banh_val, vagas_val, area_t, v_venda_val, status_i, id_p_sel, doc_sit, iptu_v, comod_string, link_val, p_agenc_val, agenciador_val, id_interno))

                    conn.commit()
                    st.session_state.imovel_editando = None
                    st.session_state.dados_cep_imovel = {}
                    st.session_state.abrir_expander = False
                    st.session_state.tabela_versao += 1
                    st.toast("✅ Imóvel salvo com sucesso!")
                    st.rerun()

        if st.button("🚫 Cancelar / Limpar"):
            st.session_state.imovel_editando = None
            st.session_state.dados_cep_imovel = {}
            st.session_state.abrir_expander = False
            st.session_state.tabela_versao += 1
            st.rerun()

    # --- LISTA RÁPIDA DE IMÓVEIS ---
    st.divider()
    st.subheader("🔍 Pesquisar para Editar")

    try:
        df_tipos_busca = pd.read_sql(
            "SELECT nome FROM tipos_imoveis ORDER BY nome", conn)
        lista_tipos_busca = df_tipos_busca['nome'].tolist(
        ) if not df_tipos_busca.empty else []
    except:
        lista_tipos_busca = []  # Segurança caso a tabela não exista ainda

    col_p1, col_p2, col_p3 = st.columns(3)
    busca_i = col_p1.text_input(
        "Filtrar por Rua ou Bairro", key="txt_busca_cad")

    status_f = col_p2.selectbox("Filtrar por Status", [
                                "Todos", "Disponível", "Reservado", "Vendido"], key="sel_status_cad")

    tipo_f = col_p3.selectbox(
        "Filtrar por Tipo", ["Todos"] + lista_tipos_busca, key="sel_tipo_cad")

    q_i = "SELECT * FROM imoveis WHERE 1=1"
    p_i = []

    if busca_i:
        q_i += " AND (endereco_rua ILIKE %s OR bairro ILIKE %s)"
        p_i.extend([f"%{busca_i}%", f"%{busca_i}%"])
    if status_f != "Todos":
        q_i += " AND status = %s"
        p_i.append(status_f)
    if tipo_f != "Todos":
        q_i += " AND tipo_imovel = %s"
        p_i.append(tipo_f)

    df_i_full = pd.read_sql(q_i + " ORDER BY id_imovel DESC", conn, params=p_i)
    conn.close()

    if not df_i_full.empty:
        df_i_edit = df_i_full[['id_imovel', 'tipo_imovel', 'endereco_rua',
                               'bairro', 'quartos', 'valor_venda', 'status']].copy()
        df_i_edit.insert(0, "Editar", False)

        df_i_edit['valor_venda'] = df_i_edit['valor_venda'].apply(
            formata_moeda)

        chave_edit = f"editor_cad_v{st.session_state.tabela_versao}"
        st.data_editor(df_i_edit, use_container_width=True, hide_index=True, key=chave_edit,
                       column_config={
                           "Editar": st.column_config.CheckboxColumn("Editar")},
                       disabled=['id_imovel', 'tipo_imovel', 'endereco_rua', 'bairro', 'quartos', 'valor_venda', 'status'])

        if chave_edit in st.session_state:
            mudancas = st.session_state[chave_edit].get("edited_rows", {})
            if mudancas:
                idx = [i for i, v in mudancas.items() if v.get("Editar")
                       is True]
                if idx:
                    st.session_state.imovel_editando = df_i_full.iloc[idx[-1]].to_dict(
                    )
                    st.session_state.abrir_expander = True
                    st.session_state.tabela_versao += 1
                    st.rerun()
    else:
        st.info("Nenhum imóvel cadastrado com esses filtros.")

# ------------------------------------------
# TELA 2: LISTA DE CONSULTA E MATCH
# ------------------------------------------
elif pagina == "Imoveis_Lista":
    st.header("🔍 Consulta e Match de Imóveis")
    st.write(
        "Utilize os filtros abaixo para encontrar imóveis e cruzar com os interesses dos clientes.")

    col_p1, col_p2, col_p3 = st.columns(3)
    busca_i = col_p1.text_input("Filtrar por Rua ou Bairro", key="txt_busca_i")
    status_f = col_p2.selectbox("Filtrar por Status", [
                                "Todos", "Disponível", "Reservado", "Vendido"])
    conn = conectar()

    # 👇 Busca a lista do banco de dados para o filtro de Match
    try:
        df_comod_busca = pd.read_sql(
            "SELECT nome FROM comodidades ORDER BY nome", conn)
        lista_comod_busca = df_comod_busca['nome'].tolist(
        ) if not df_comod_busca.empty else []
    except:
        lista_comod_busca = []

    comod_f = col_p3.multiselect("Filtrar por Comodidades", lista_comod_busca)

    conn = conectar()
    q_i = "SELECT * FROM imoveis WHERE 1=1"
    p_i = []

    if busca_i:
        q_i += " AND (endereco_rua ILIKE %s OR bairro ILIKE %s)"
        p_i.extend([f"%{busca_i}%", f"%{busca_i}%"])
    if status_f != "Todos":
        q_i += " AND status = %s"
        p_i.append(status_f)
    if comod_f:
        for c in comod_f:
            q_i += " AND comodidades ILIKE %s"
            p_i.append(f"%{c}%")

    df_i_full = pd.read_sql(q_i + " ORDER BY id_imovel DESC", conn, params=p_i)

    if not df_i_full.empty:
        df_i_view = df_i_full[['id_imovel', 'endereco_rua',
                               'bairro', 'valor_venda', 'status', 'comodidades']].copy()
        df_i_view.insert(0, "Selecionar", False)
        df_i_view['valor_venda'] = df_i_view['valor_venda'].apply(
            formata_moeda)

        chave_lista = f"lista_match_v{st.session_state.get('tabela_versao', 0)}"
        st.data_editor(df_i_view, use_container_width=True, hide_index=True, key=chave_lista,
                       column_config={
                           "Selecionar": st.column_config.CheckboxColumn("Ver Match")},
                       disabled=['id_imovel', 'endereco_rua', 'bairro', 'valor_venda', 'status', 'comodidades'])

        if chave_lista in st.session_state:
            mudancas = st.session_state[chave_lista].get("edited_rows", {})
            if mudancas:
                idx = [i for i, v in mudancas.items() if v.get(
                    "Selecionar") is True]
                if idx:
                    st.session_state.imovel_selecionado_match = df_i_full.iloc[idx[-1]].to_dict(
                    )
                    if 'tabela_versao' in st.session_state:
                        st.session_state.tabela_versao += 1
                    st.rerun()

        # --- SISTEMA DE MATCH E ENVIO ---
        if st.session_state.get('imovel_selecionado_match'):
            imob = st.session_state.imovel_selecionado_match
            st.divider()
            st.subheader(f"🎯 Match: Interessados em {imob['bairro']}")

            try:
                query_p = """
                    SELECT c.nome_completo, c.telefone, i.valor_maximo, i.bairro_preferencial, i.comodidades_desejadas
                    FROM interesses_clientes i
                    JOIN clientes c ON i.id_cliente = c.id_cliente
                    WHERE i.valor_maximo >= %s
                """
                df_potenciais = pd.read_sql(
                    query_p, conn, params=[imob['valor_venda']])
                df_corretores = pd.read_sql(
                    "SELECT nome_completo FROM corretores WHERE ativo = TRUE", conn)

                if not df_potenciais.empty:
                    def validar_match(row):
                        b_cli = str(row['bairro_preferencial']).lower(
                        ) if row['bairro_preferencial'] else ""
                        b_imo = str(imob['bairro']).lower()
                        match_b = True if not b_cli.strip() or b_imo in b_cli else False

                        c_cli = str(row['comodidades_desejadas']).lower(
                        ) if row['comodidades_desejadas'] else ""
                        c_imo = str(imob.get('comodidades', '')).lower()
                        afin = "100%"
                        if c_cli:
                            l_d = [x.strip() for x in c_cli.split(",")]
                            l_t = [x.strip() for x in c_imo.split(",")]
                            ac = [c for c in l_d if c in l_t]
                            afin = f"{(len(ac)/len(l_d))*100:.0f}%" if len(l_d) > 0 else "100%"
                        return pd.Series([match_b, afin])

                    df_potenciais[['Match_Bairro', 'Afinidade']
                                  ] = df_potenciais.apply(validar_match, axis=1)
                    df_final = df_potenciais[df_potenciais['Match_Bairro'] == True].copy(
                    )

                    if not df_final.empty:
                        st.success(
                            f"🔥 {len(df_final)} Match(es) encontrado(s)!")
                        st.dataframe(df_final[[
                                     'nome_completo', 'telefone', 'valor_maximo', 'Afinidade']], use_container_width=True)

                        if not df_corretores.empty:
                            st.write("---")
                            c_sel = st.selectbox(
                                "Enviar ficha para o corretor:", df_corretores['nome_completo'])

                            cliente_n = df_final.iloc[0]['nome_completo']
                            cliente_t = df_final.iloc[0]['telefone']
                            imob_id = imob['id_imovel']

                            msg_corpo = (
                                f"Olá *{c_sel}*!\n\n"
                                f"🚀 *NOVO MATCH ENCONTRADO*\n"
                                f"------------------------------\n"
                                f"👤 *Cliente:* {cliente_n}\n"
                                f"📞 *Tel:* {cliente_t}\n"
                                f"🎯 *Afinidade:* {df_final.iloc[0]['Afinidade']}\n\n"
                                f"🏠 *Dados do Imóvel:*\n"
                                f"🆔 *ID:* {imob_id}\n"
                                f"📍 Rua: {imob['endereco_rua']}\n"
                                f"🏘️ Bairro: {imob['bairro']}\n"
                                f"💰 Valor: {formata_moeda(imob['valor_venda'])}\n"
                                f"✨ Comodidades: {imob.get('comodidades', 'Nenhuma')}\n"
                                f"🔗 *Link:* {imob.get('link_site', 'Não cadastrado')}\n"
                                f"------------------------------\n"
                                f"Favor dar andamento no atendimento!"
                            )

                            import urllib.parse
                            msg_encoded = urllib.parse.quote(
                                msg_corpo.encode('utf-8'))
                            link_zap = f"https://api.whatsapp.com/send?text={msg_encoded}"

                            st.markdown(f"""
                                <a href="{link_zap}" target="_blank">
                                    <button style="width:100%;background-color:#25D366;color:white;border:none;padding:12px;border-radius:8px;cursor:pointer;font-weight:bold;font-size:16px;">
                                        📲 Enviar Ficha e Contato via WhatsApp
                                    </button>
                                </a>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning(
                                "Cadastre um corretor para poder enviar o Match via WhatsApp.")
                    else:
                        st.info(
                            "Clientes encontrados pelo valor, mas nenhum no bairro deste imóvel.")
                else:
                    st.info("Nenhum cliente com interesse neste valor no momento.")
            except Exception as e:
                # Oculta erro silenciosamente se a tabela interesses_clientes ainda nao existir
                pass
    else:
        st.info("Nenhum imóvel cadastrado no sistema.")

    conn.close()

# ------------------------------------------
# TELA 3: CADASTRO E EDIÇÃO DE CLIENTES
# ------------------------------------------
elif pagina == "Clientes_Novo":
    st.header("👥 Cadastro de Clientes")

    if 'cliente_editando' not in st.session_state:
        st.session_state.cliente_editando = None
    if 'abrir_expander_cli' not in st.session_state:
        st.session_state.abrir_expander_cli = False
    if 'tabela_versao_cli' not in st.session_state:
        st.session_state.tabela_versao_cli = 0
    if 'dados_cep' not in st.session_state:
        st.session_state.dados_cep = {}

    conn = conectar()
    edit_cli = st.session_state.cliente_editando
    id_interno_cli = int(edit_cli['id_cliente']) if edit_cli else 0

    with st.expander("➕ Cadastrar / Alterar Cliente", expanded=st.session_state.abrir_expander_cli):

        # --- BUSCADOR DE CEP MAGICO ---
        st.markdown("#### 🔎 Busca Automática de Endereço")
        c_busca1, c_busca2 = st.columns([1, 3])
# Criamos a chave dinâmica AQUI, e amarramos ela na caixinha!
        chave_cep = f"input_cep_busca_{st.session_state.tabela_versao_cli}"
        cep_busca = c_busca1.text_input(
            "Digite o CEP e aperte ENTER", placeholder="Apenas números", max_chars=9, key=chave_cep)

        if cep_busca:
            cep_limpo = cep_busca.replace("-", "").replace(".", "").strip()
            if len(cep_limpo) == 8:
                try:
                    resposta = requests.get(
                        f"https://viacep.com.br/ws/{cep_limpo}/json/").json()
                    if "erro" not in resposta:
                        st.session_state.dados_cep = resposta
                        c_busca2.success(
                            f"✅ Encontrado: {resposta['logradouro']}, {resposta['bairro']} - {resposta['localidade']}/{resposta['uf']}")
                    else:
                        st.session_state.dados_cep = {}
                        c_busca2.error("❌ CEP não encontrado.")
                except:
                    c_busca2.error("❌ Erro ao consultar o ViaCEP.")
            elif len(cep_limpo) > 0:
                c_busca2.warning("⚠️ O CEP deve ter 8 números.")

        st.divider()

        # --- FORMULÁRIO DE CLIENTE ---
        chave_form_cli = f"form_cli_{st.session_state.tabela_versao_cli}"
        with st.form(chave_form_cli, clear_on_submit=False):
            st.markdown("📝 **Dados Pessoais / Contato**")
            c1, c2 = st.columns(2)
            nome_val = c1.text_input(
                "Nome Completo *", value=edit_cli.get('nome_completo', '') if edit_cli else "")
            telefone_val = c2.text_input(
                "Telefone (WhatsApp) *", value=edit_cli.get('telefone', '') if edit_cli else "")

            c3, c4 = st.columns(2)
            email_val = c3.text_input(
                "E-mail", value=edit_cli.get('email', '') if edit_cli else "")
            cpf_val = c4.text_input(
                "CPF / CNPJ", value=edit_cli.get('cpf', '') if edit_cli else "")

            st.markdown("📍 **Endereço**")

            val_rua = st.session_state.dados_cep.get(
                'logradouro', edit_cli.get('endereco_rua', '') if edit_cli else "")
            val_bairro = st.session_state.dados_cep.get(
                'bairro', edit_cli.get('bairro', '') if edit_cli else "")
            val_cidade = st.session_state.dados_cep.get(
                'localidade', edit_cli.get('cidade', '') if edit_cli else "")
            val_estado = st.session_state.dados_cep.get(
                'uf', edit_cli.get('estado', '') if edit_cli else "")
            val_cep_form = st.session_state.dados_cep.get(
                'cep', edit_cli.get('cep', '') if edit_cli else "")

            c_end1, c_end2, c_end3 = st.columns([3, 1, 1])
            rua_val = c_end1.text_input("Rua", value=val_rua)
            numero_val = c_end2.text_input(
                "Número", value=edit_cli.get('numero', '') if edit_cli else "")
            cep_val = c_end3.text_input("CEP", value=val_cep_form)

            c_end4, c_end5, c_end6 = st.columns([2, 2, 1])
            bairro_val = c_end4.text_input("Bairro", value=val_bairro)
            cidade_val = c_end5.text_input("Cidade", value=val_cidade)
            estado_val = c_end6.text_input(
                "Estado (UF)", value=val_estado, max_chars=2)

            st.divider()
            btn_salvar_cli = st.form_submit_button("💾 Salvar Cliente")

            if btn_salvar_cli:
                if not nome_val or not telefone_val:
                    st.error("⚠️ Os campos Nome e Telefone são obrigatórios!")
                else:
                    try:
                        cur = conn.cursor()
                        if id_interno_cli == 0:
                            cur.execute("""
                                INSERT INTO clientes (nome_completo, telefone, email, cpf, endereco_rua, numero, cep, bairro, cidade, estado)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (nome_val, telefone_val, email_val, cpf_val, rua_val, numero_val, cep_val, bairro_val, cidade_val, estado_val.upper()))
                        else:
                            cur.execute("""
                                UPDATE clientes SET
                                nome_completo=%s, telefone=%s, email=%s, cpf=%s, endereco_rua=%s, numero=%s, cep=%s, bairro=%s, cidade=%s, estado=%s
                                WHERE id_cliente=%s
                            """, (nome_val, telefone_val, email_val, cpf_val, rua_val, numero_val, cep_val, bairro_val, cidade_val, estado_val.upper(), id_interno_cli))

                        conn.commit()
                        st.session_state.cliente_editando = None
                        st.session_state.dados_cep = {}
                        st.session_state.abrir_expander_cli = False
                        st.session_state.tabela_versao_cli += 1
                        st.toast("✅ Cliente salvo com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar cliente: {e}")

        if st.button("🚫 Cancelar / Limpar", key="btn_canc_cli"):
            st.session_state.cliente_editando = None
            st.session_state.dados_cep = {}
            st.session_state.abrir_expander_cli = False
            st.session_state.tabela_versao_cli += 1
            st.rerun()

    # --- LISTA RÁPIDA DE CLIENTES ---
    st.divider()
    st.subheader("🔍 Pesquisar para Editar")

    busca_c = st.text_input(
        "Filtrar por Nome ou Telefone", key="txt_busca_cli")

    q_c = "SELECT * FROM clientes WHERE 1=1"
    p_c = []
    if busca_c:
        q_c += " AND (nome_completo ILIKE %s OR telefone ILIKE %s)"
        p_c.extend([f"%{busca_c}%", f"%{busca_c}%"])

    df_c_full = pd.read_sql(
        q_c + " ORDER BY id_cliente DESC", conn, params=p_c)
    conn.close()

    if not df_c_full.empty:
        colunas_visao = ['id_cliente', 'nome_completo', 'telefone']
        if 'cidade' in df_c_full.columns:
            colunas_visao.append('cidade')

        df_c_edit = df_c_full[colunas_visao].copy()
        df_c_edit.insert(0, "Editar", False)

        chave_edit_cli = f"editor_cli_v{st.session_state.tabela_versao_cli}"
        st.data_editor(df_c_edit, use_container_width=True, hide_index=True, key=chave_edit_cli,
                       column_config={
                           "Editar": st.column_config.CheckboxColumn("Editar")},
                       disabled=colunas_visao)

        if chave_edit_cli in st.session_state:
            mudancas_cli = st.session_state[chave_edit_cli].get(
                "edited_rows", {})
            if mudancas_cli:
                idx_c = [i for i, v in mudancas_cli.items()
                         if v.get("Editar") is True]
                if idx_c:
                    st.session_state.cliente_editando = df_c_full.iloc[idx_c[-1]].to_dict(
                    )
                    st.session_state.abrir_expander_cli = True
                    st.session_state.tabela_versao_cli += 1
                    st.rerun()
    else:
        st.info(
            "Nenhum cliente cadastrado ainda. Use o formulário acima para adicionar o primeiro.")


# ------------------------------------------
# TELA 4: CADASTRO E EDIÇÃO DE CORRETORES
# ------------------------------------------
elif pagina == "Corretores_Novo":
    st.header("👔 Cadastro de Corretores")

    if 'corretor_editando' not in st.session_state:
        st.session_state.corretor_editando = None
    if 'abrir_expander_corr' not in st.session_state:
        st.session_state.abrir_expander_corr = False
    if 'tabela_versao_corr' not in st.session_state:
        st.session_state.tabela_versao_corr = 0

    conn = conectar()
    edit_corr = st.session_state.corretor_editando
    id_interno_corr = int(edit_corr['id_corretor']) if edit_corr else 0

    with st.expander("➕ Cadastrar / Alterar Corretor", expanded=st.session_state.abrir_expander_corr):
        chave_form_corr = f"form_corr_{st.session_state.tabela_versao_corr}"

        with st.form(chave_form_corr, clear_on_submit=False):
            st.markdown("📝 **Dados do Profissional**")

            c1, c2, c3 = st.columns([2, 1, 1])
            nome_val = c1.text_input(
                "Nome Completo *", value=edit_corr.get('nome_completo', '') if edit_corr else "")
            creci_val = c2.text_input("CRECI", value=edit_corr.get(
                'creci', '') if edit_corr else "")
            cpf_val = c3.text_input("CPF", value=edit_corr.get(
                'cpf', '') if edit_corr else "")

            c4, c5, c6 = st.columns([1, 1, 1])
            telefone_val = c4.text_input(
                "Telefone (WhatsApp) *", value=edit_corr.get('telefone', '') if edit_corr else "")
            email_val = c5.text_input(
                "E-mail", value=edit_corr.get('email', '') if edit_corr else "")

            perc_val = float(edit_corr.get('comissao_padrao_percentual', 0)) if edit_corr and pd.notna(
                edit_corr.get('comissao_padrao_percentual')) else 0.0
            comissao_val = c6.number_input(
                "Comissão Padrão (%)", min_value=0.0, value=perc_val)

            st.divider()

            ativo_val = st.checkbox("Corretor Ativo no Sistema", value=edit_corr.get(
                'ativo', True) if edit_corr else True)

            btn_salvar_corr = st.form_submit_button("💾 Salvar Corretor")

            if btn_salvar_corr:
                if not nome_val or not telefone_val:
                    st.error("⚠️ Os campos Nome e Telefone são obrigatórios!")
                else:
                    try:
                        cur = conn.cursor()
                        if id_interno_corr == 0:
                            cur.execute("""
                                INSERT INTO corretores (nome_completo, cpf, telefone, email, creci, comissao_padrao_percentual, ativo)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (nome_val, cpf_val, telefone_val, email_val, creci_val, comissao_val, ativo_val))
                        else:
                            cur.execute("""
                                UPDATE corretores SET
                                nome_completo=%s, cpf=%s, telefone=%s, email=%s, creci=%s, comissao_padrao_percentual=%s, ativo=%s
                                WHERE id_corretor=%s
                            """, (nome_val, cpf_val, telefone_val, email_val, creci_val, comissao_val, ativo_val, id_interno_corr))

                        conn.commit()
                        st.session_state.corretor_editando = None
                        st.session_state.abrir_expander_corr = False
                        st.session_state.tabela_versao_corr += 1
                        st.toast("✅ Corretor salvo com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar corretor: {e}")

        if st.button("🚫 Cancelar / Limpar", key="btn_canc_corr"):
            st.session_state.corretor_editando = None
            st.session_state.abrir_expander_corr = False
            st.session_state.tabela_versao_corr += 1
            st.rerun()

    # --- LISTA RÁPIDA DE CORRETORES ---
    st.divider()
    st.subheader("🔍 Pesquisar para Editar")

    busca_corr = st.text_input(
        "Filtrar por Nome ou CRECI", key="txt_busca_corr")

    q_corr = "SELECT * FROM corretores WHERE 1=1"
    p_corr = []
    if busca_corr:
        q_corr += " AND (nome_completo ILIKE %s OR creci ILIKE %s)"
        p_corr.extend([f"%{busca_corr}%", f"%{busca_corr}%"])

    df_corr_full = pd.read_sql(
        q_corr + " ORDER BY id_corretor DESC", conn, params=p_corr)
    conn.close()

    if not df_corr_full.empty:
        colunas_visao = ['id_corretor', 'nome_completo',
                         'creci', 'telefone', 'ativo']
        colunas_reais = [
            col for col in colunas_visao if col in df_corr_full.columns]

        df_corr_edit = df_corr_full[colunas_reais].copy()
        df_corr_edit.insert(0, "Editar", False)

        chave_edit_corr = f"editor_corr_v{st.session_state.tabela_versao_corr}"
        st.data_editor(df_corr_edit, use_container_width=True, hide_index=True, key=chave_edit_corr,
                       column_config={
                           "Editar": st.column_config.CheckboxColumn("Editar")},
                       disabled=colunas_reais)

        if chave_edit_corr in st.session_state:
            mudancas_corr = st.session_state[chave_edit_corr].get(
                "edited_rows", {})
            if mudancas_corr:
                idx_corr = [i for i, v in mudancas_corr.items()
                            if v.get("Editar") is True]
                if idx_corr:
                    st.session_state.corretor_editando = df_corr_full.iloc[idx_corr[-1]].to_dict(
                    )
                    st.session_state.abrir_expander_corr = True
                    st.session_state.tabela_versao_corr += 1
                    st.rerun()
    else:
        st.info(
            "Nenhum corretor cadastrado ainda. Use o formulário acima para adicionar a equipe.")

# ------------------------------------------
# TELA 1.3: CONFIGURAÇÕES DE IMÓVEIS (Tipos e Comodidades)
# ------------------------------------------
elif pagina == "Imoveis_Tipos":
    st.header("⚙️ Configurações de Imóveis")
    st.write(
        "Gerencie as categorias e características disponíveis para o cadastro de imóveis.")

    conn = conectar()

    # --- EXPANDER 1: CATEGORIAS DE IMÓVEIS ---
    with st.expander("🏢 Categorias de Imóveis", expanded=False):
        with st.form("form_novo_tipo", clear_on_submit=True):
            st.markdown("➕ **Adicionar Nova Categoria**")
            col1, col2 = st.columns([3, 1])
            novo_tipo = col1.text_input(
                "Nome da Categoria (Ex: Galpão, Fazenda)")
            btn_add_tipo = col2.form_submit_button("💾 Salvar Tipo")

            if btn_add_tipo:
                if novo_tipo.strip() == "":
                    st.error("⚠️ O nome não pode estar vazio.")
                else:
                    try:
                        cur = conn.cursor()
                        cur.execute(
                            "INSERT INTO tipos_imoveis (nome) VALUES (%s)", (novo_tipo.strip(),))
                        conn.commit()
                        st.success(
                            f"✅ Tipo '{novo_tipo}' adicionado com sucesso!")
                        st.rerun()
                    except psycopg2.errors.UniqueViolation:
                        st.error("⚠️ Esta categoria já existe no sistema.")
                    except Exception as e:
                        st.error(f"Erro ao adicionar: {e}")

        st.markdown("🔍 **Categorias Cadastradas**")
        try:
            df_tipos = pd.read_sql(
                "SELECT id_tipo AS \"ID\", nome AS \"Categoria\" FROM tipos_imoveis ORDER BY nome", conn)
            if not df_tipos.empty:
                st.dataframe(df_tipos, hide_index=True,
                             use_container_width=True)
            else:
                st.info("Nenhuma categoria cadastrada.")
        except:
            st.warning("Tabela de tipos não encontrada no banco de dados.")

    # --- EXPANDER 2: COMODIDADES (CARACTERÍSTICAS) ---
    with st.expander("✨ Características e Comodidades", expanded=False):
        with st.form("form_nova_comod", clear_on_submit=True):
            st.markdown("➕ **Adicionar Nova Comodidade**")
            col3, col4 = st.columns([3, 1])
            nova_comod = col3.text_input(
                "Nome (Ex: Quadra de Tênis, Sauna, Coworking)")
            btn_add_comod = col4.form_submit_button("💾 Salvar Comodidade")

            if btn_add_comod:
                if nova_comod.strip() == "":
                    st.error("⚠️ O nome não pode estar vazio.")
                else:
                    try:
                        cur = conn.cursor()
                        cur.execute(
                            "INSERT INTO comodidades (nome) VALUES (%s)", (nova_comod.strip(),))
                        conn.commit()
                        st.success(
                            f"✅ Comodidade '{nova_comod}' adicionada com sucesso!")
                        st.rerun()
                    except psycopg2.errors.UniqueViolation:
                        st.error("⚠️ Esta comodidade já existe no sistema.")
                    except Exception as e:
                        st.error(f"Erro ao adicionar: {e}")

        st.markdown("🔍 **Comodidades Cadastradas**")
        try:
            df_comod = pd.read_sql(
                "SELECT id_comodidade AS \"ID\", nome AS \"Comodidade\" FROM comodidades ORDER BY nome", conn)
            if not df_comod.empty:
                st.dataframe(df_comod, hide_index=True,
                             use_container_width=True)
            else:
                st.info("Nenhuma comodidade cadastrada.")
        except:
            st.warning(
                "Tabela de comodidades não encontrada no banco de dados.")

    conn.close()

# ------------------------------------------
# TELA 1.4: IMÓVEIS DISPONÍVEIS
# ------------------------------------------
elif pagina == "Imoveis_Disponiveis":
    st.header("✅ Imóveis Disponíveis")
    st.write("Visão geral de todos os imóveis prontos para venda na carteira.")

    conn = conectar()

    # Busca apenas os imóveis com status 'Disponível'
    query = """
        SELECT id_imovel, tipo_imovel, endereco_rua, bairro, valor_venda, quartos, garagens, comodidades 
        FROM imoveis 
        WHERE status = 'Disponível' 
        ORDER BY id_imovel DESC
    """
    df_disp = pd.read_sql(query, conn)
    conn.close()

    if not df_disp.empty:
        # --- MÉTRICAS RÁPIDAS ---
        total_imoveis = len(df_disp)
        valor_total = df_disp['valor_venda'].sum()

        col1, col2 = st.columns(2)
        col1.metric("Quantidade em Estoque", f"{total_imoveis} imóveis")
        col2.metric("Valor Geral em Estoque (VGV)", formata_moeda(valor_total))

        st.divider()

        # --- TABELA DE VISUALIZAÇÃO ---
        df_view = df_disp.copy()
        df_view['valor_venda'] = df_view['valor_venda'].apply(formata_moeda)

        # Renomeia as colunas para ficar bonito na tela
        df_view = df_view.rename(columns={
            'id_imovel': 'ID', 'tipo_imovel': 'Tipo', 'endereco_rua': 'Rua',
            'bairro': 'Bairro', 'valor_venda': 'Valor', 'quartos': 'Qts',
            'garagens': 'Vagas', 'comodidades': 'Comodidades'
        })

        st.dataframe(df_view, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum imóvel com status 'Disponível' encontrado no momento.")

# ------------------------------------------
# TELA 1.5: IMÓVEIS EM NEGOCIAÇÃO
# ------------------------------------------
elif pagina == "Imoveis_Negociacao":
    st.header("🤝 Imóveis em Negociação")
    st.write("Acompanhamento de imóveis que estão com status 'Reservado'.")

    conn = conectar()

    # Busca apenas os imóveis com status 'Reservado'
    query = """
        SELECT i.id_imovel, i.tipo_imovel, i.endereco_rua, i.bairro, i.valor_venda, i.agenciador_nome, c.nome_completo as proprietario
        FROM imoveis i
        LEFT JOIN clientes c ON i.id_proprietario = c.id_cliente
        WHERE i.status = 'Reservado' 
        ORDER BY i.id_imovel DESC
    """
    df_negoc = pd.read_sql(query, conn)
    conn.close()

    if not df_negoc.empty:
        # --- MÉTRICAS RÁPIDAS ---
        total_negoc = len(df_negoc)
        valor_negoc = df_negoc['valor_venda'].sum()

        col1, col2 = st.columns(2)
        col1.metric("Negociações em Andamento", f"{total_negoc} imóveis")
        col2.metric("Valor em Negociação (VGV)", formata_moeda(valor_negoc))

        st.divider()

        # --- TABELA DE VISUALIZAÇÃO ---
        df_view = df_negoc.copy()
        df_view['valor_venda'] = df_view['valor_venda'].apply(formata_moeda)

        # Renomeia as colunas para ficar bonito na tela
        df_view = df_view.rename(columns={
            'id_imovel': 'ID', 'tipo_imovel': 'Tipo', 'endereco_rua': 'Rua',
            'bairro': 'Bairro', 'valor_venda': 'Valor', 'agenciador_nome': 'Agenciador', 'proprietario': 'Proprietário'
        })

        st.dataframe(df_view, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum imóvel em negociação (Reservado) no momento.")

# ------------------------------------------
# TELA 3.2: REGISTROS DE INTERESSE (O MOTOR DO MATCH)
# ------------------------------------------
elif pagina == "Clientes_Interesses":
    st.header("🎯 Registros de Interesse")
    st.write("Cadastre ou altere o que os clientes estão procurando para que o sistema faça o cruzamento (Match) automático.")

    if 'interesse_editando' not in st.session_state:
        st.session_state.interesse_editando = None
    if 'abrir_expander_int' not in st.session_state:
        st.session_state.abrir_expander_int = False
    if 'tabela_versao_int' not in st.session_state:
        st.session_state.tabela_versao_int = 0

    conn = conectar()
    edit_int = st.session_state.interesse_editando
    id_interno_int = int(edit_int['id_interesse']) if edit_int else 0

    try:
        df_clientes = pd.read_sql(
            "SELECT id_cliente, nome_completo FROM clientes ORDER BY nome_completo", conn)
        df_tipos = pd.read_sql(
            "SELECT nome FROM tipos_imoveis ORDER BY nome", conn)
        df_comod = pd.read_sql(
            "SELECT nome FROM comodidades ORDER BY nome", conn)

        lista_clientes = df_clientes['nome_completo'].tolist(
        ) if not df_clientes.empty else []
        lista_tipos = df_tipos['nome'].tolist() if not df_tipos.empty else []
        lista_comod = df_comod['nome'].tolist() if not df_comod.empty else []
    except:
        lista_clientes, lista_tipos, lista_comod = [], [], []

    # --- 1. EXPANDER PARA CADASTRAR / EDITAR INTERESSE ---
    espacos_hack = " " * (st.session_state.tabela_versao_int % 10)
    titulo_exp = f"✏️ Editando Perfil de Busca (Aberto){espacos_hack}" if st.session_state.abrir_expander_int else f"➕ Registrar Novo Perfil de Busca{espacos_hack}"

    with st.expander(titulo_exp, expanded=st.session_state.abrir_expander_int):
        if not lista_clientes:
            st.warning(
                "⚠️ Cadastre pelo menos um cliente primeiro para poder registrar um interesse.")
        else:
            chave_form_int = f"form_int_{st.session_state.tabela_versao_int}"
            with st.form(chave_form_int, clear_on_submit=False):
                c1, c2 = st.columns([2, 1])

                opcoes_clientes = [
                    "-- Selecione um Cliente --"] + lista_clientes
                idx_cli = 0
                if edit_int and edit_int.get('cliente') in opcoes_clientes:
                    idx_cli = opcoes_clientes.index(edit_int['cliente'])

                cliente_sel = c1.selectbox(
                    "Selecione o Cliente *", opcoes_clientes, index=idx_cli)

                tipo_atual = edit_int.get(
                    'tipo_imovel_desejado', '') if edit_int else ''
                if not tipo_atual:
                    tipo_atual = "Qualquer"
                opcoes_tipo = ["Qualquer"] + lista_tipos
                idx_tipo = opcoes_tipo.index(
                    tipo_atual) if tipo_atual in opcoes_tipo else 0
                tipo_sel = c2.selectbox(
                    "Tipo de Imóvel Desejado", opcoes_tipo, index=idx_tipo)

                c3, c4 = st.columns([1, 2])

                try:
                    v_max_val = float(edit_int['valor_maximo']) if edit_int and pd.notna(
                        edit_int.get('valor_maximo')) else 0.0
                except:
                    v_max_val = 0.0

                valor_max = c3.number_input(
                    "Valor Máximo de Compra (R$)", min_value=0.0, value=v_max_val, step=10000.0)

                bairros_val = c4.text_input("Bairros de Preferência", value=edit_int.get(
                    'bairro_preferencial', '') if edit_int else "", placeholder="Ex: Centro, Jardim América (separe por vírgula)")

                str_comod = edit_int.get(
                    'comodidades_desejadas', '') if edit_int else ''
                if not str_comod:
                    str_comod = ''
                comod_atual = str_comod.split(", ") if str_comod else []
                comod_atual = [c for c in comod_atual if c in lista_comod]

                comodidades_sel = st.multiselect(
                    "Comodidades Desejadas", lista_comod, default=comod_atual)
                comodidades_str = ", ".join(comodidades_sel)

                st.divider()

                # 👇 NOVO: A chavinha de Ativo/Inativo
                ativo_val = st.checkbox("🔥 Busca Ativa (Mostrar no Radar e cruzar Match Automático)", value=edit_int.get(
                    'ativo', True) if edit_int else True)

                btn_salvar_int = st.form_submit_button(
                    "💾 Salvar Perfil de Busca")

                if btn_salvar_int:
                    if cliente_sel == "-- Selecione um Cliente --":
                        st.error(
                            "⚠️ Por favor, selecione um cliente válido na lista!")
                    elif valor_max <= 0:
                        st.error(
                            "⚠️ O valor máximo de compra deve ser maior que zero!")
                    else:
                        id_c = int(
                            df_clientes[df_clientes['nome_completo'] == cliente_sel]['id_cliente'].values[0])
                        tipo_final = tipo_sel if tipo_sel != "Qualquer" else ""

                        try:
                            cur = conn.cursor()
                            if id_interno_int == 0:
                                cur.execute("""
                                    INSERT INTO interesses_clientes 
                                    (id_cliente, tipo_imovel_desejado, valor_maximo, bairro_preferencial, comodidades_desejadas, ativo) 
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """, (id_c, tipo_final, valor_max, bairros_val, comodidades_str, ativo_val))
                            else:
                                cur.execute("""
                                    UPDATE interesses_clientes SET 
                                    id_cliente=%s, tipo_imovel_desejado=%s, valor_maximo=%s, bairro_preferencial=%s, comodidades_desejadas=%s, ativo=%s 
                                    WHERE id_interesse=%s
                                """, (id_c, tipo_final, valor_max, bairros_val, comodidades_str, ativo_val, id_interno_int))

                            conn.commit()
                            st.session_state.interesse_editando = None
                            st.session_state.abrir_expander_int = False
                            st.session_state.tabela_versao_int += 1
                            st.toast("✅ Perfil de busca salvo com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar interesse: {e}")

            if st.button("🚫 Cancelar / Limpar", key="btn_canc_int"):
                st.session_state.interesse_editando = None
                st.session_state.abrir_expander_int = False
                st.session_state.tabela_versao_int += 1
                st.rerun()

    st.divider()

    # --- 2. LISTA DOS INTERESSES ATIVOS (EDITÁVEL) ---
    st.markdown("🔍 **Painel de Buscas (Radar)** - *Selecione para editar*")

    # 👇 NOVO: Botões de Filtro Rápidos
    filtro_status_int = st.radio(
        "Mostrar:", ["🔥 Apenas Ativas", "💤 Apenas Inativas", "📋 Todas"], horizontal=True)

    query_int = """
        SELECT i.id_interesse, c.nome_completo as cliente, c.telefone as contato,
               i.tipo_imovel_desejado, i.valor_maximo,
               i.bairro_preferencial, i.comodidades_desejadas, i.ativo
        FROM interesses_clientes i
        JOIN clientes c ON i.id_cliente = c.id_cliente
        WHERE 1=1
    """

    # Aplica o filtro na busca do banco
    if filtro_status_int == "🔥 Apenas Ativas":
        query_int += " AND i.ativo = TRUE"
    elif filtro_status_int == "💤 Apenas Inativas":
        query_int += " AND i.ativo = FALSE"

    query_int += " ORDER BY i.id_interesse DESC"

    try:
        df_int = pd.read_sql(query_int, conn)

        if not df_int.empty:
            df_view = df_int.copy()
            df_view['valor_maximo_fmt'] = df_view['valor_maximo'].apply(
                formata_moeda)

            # 👇 NOVO: Coluna visual de Status para a tabela
            df_view['Status'] = df_view['ativo'].apply(
                lambda x: "🟢 Ativa" if x else "🔴 Inativa")

            df_ui = df_view[['id_interesse', 'cliente', 'contato', 'tipo_imovel_desejado',
                             'valor_maximo_fmt', 'bairro_preferencial', 'comodidades_desejadas', 'Status']].copy()
            df_ui = df_ui.rename(columns={
                'cliente': 'Cliente', 'contato': 'Contato', 'tipo_imovel_desejado': 'Tipo Desejado',
                'valor_maximo_fmt': 'Valor Máx.', 'bairro_preferencial': 'Bairros', 'comodidades_desejadas': 'Comodidades'
            })

            df_ui.insert(0, "Editar", False)

            chave_edit_int = f"editor_int_v{st.session_state.tabela_versao_int}"
            st.data_editor(df_ui, use_container_width=True, hide_index=True, key=chave_edit_int,
                           column_config={
                               "Editar": st.column_config.CheckboxColumn("Editar")},
                           disabled=['id_interesse', 'Cliente', 'Contato', 'Tipo Desejado', 'Valor Máx.', 'Bairros', 'Comodidades', 'Status'])

            if chave_edit_int in st.session_state:
                mudancas_int = st.session_state[chave_edit_int].get(
                    "edited_rows", {})
                if mudancas_int:
                    idx_i = [int(i) for i, v in mudancas_int.items()
                             if v.get("Editar") is True]
                    if idx_i:
                        st.session_state.interesse_editando = df_int.iloc[idx_i[-1]].to_dict(
                        )
                        st.session_state.abrir_expander_int = True
                        st.session_state.tabela_versao_int += 1
                        st.rerun()
        else:
            st.info("Nenhum interesse registrado com este filtro no momento.")
    except Exception as e:
        st.error(f"Erro técnico ao carregar a tabela: {e}")

    conn.close()

# ------------------------------------------
# TELA 3.4: AGENDAR ATENDIMENTO / VISITA
# ------------------------------------------
elif pagina == "Clientes_Agendar":
    st.header("📅 Agendar Atendimento / Visita")
    st.write(
        "Agende visitas, reuniões internas ou eventos avulsos, e notifique a equipe.")

    if 'atend_editando' not in st.session_state:
        st.session_state.atend_editando = None
    if 'abrir_expander_atend' not in st.session_state:
        st.session_state.abrir_expander_atend = False
    if 'tab_versao_atend' not in st.session_state:
        st.session_state.tab_versao_atend = 0

    conn = conectar()
    edit_a = st.session_state.atend_editando
    id_interno_a = int(edit_a['id_atendimento']) if edit_a else 0

    try:
        df_clientes = pd.read_sql(
            "SELECT id_cliente, nome_completo FROM clientes ORDER BY nome_completo", conn)
        df_corretores = pd.read_sql(
            "SELECT id_corretor, nome_completo, telefone FROM corretores WHERE ativo = TRUE ORDER BY nome_completo", conn)
        query_imob = "SELECT id_imovel, CONCAT('ID ', id_imovel, ' - ', tipo_imovel, ' em ', bairro) as desc_imovel FROM imoveis WHERE status = 'Disponível' ORDER BY id_imovel DESC"
        df_imoveis = pd.read_sql(query_imob, conn)

        lista_clientes = df_clientes['nome_completo'].tolist(
        ) if not df_clientes.empty else []
        lista_corretores = df_corretores['nome_completo'].tolist(
        ) if not df_corretores.empty else []
        lista_imoveis = df_imoveis['desc_imovel'].tolist(
        ) if not df_imoveis.empty else []
    except:
        lista_clientes, lista_corretores, lista_imoveis = [], [], []

    # --- 1. FORMULÁRIO DE NOVO / EDITAR AGENDAMENTO ---
    espacos_hack = " " * (st.session_state.tab_versao_atend % 10)
    titulo_exp = f"✏️ Editando Agendamento (Aberto){espacos_hack}" if st.session_state.abrir_expander_atend else f"➕ Novo Agendamento{espacos_hack}"

    with st.expander(titulo_exp, expanded=st.session_state.abrir_expander_atend):
        chave_form_atend = f"form_atend_{st.session_state.tab_versao_atend}"
        with st.form(chave_form_atend, clear_on_submit=False):

            titulo_val = st.text_input("📌 Título do Evento ou Contato Avulso",
                                       value=edit_a.get(
                                           'titulo_evento', '') if edit_a else "",
                                       placeholder="Ex: Reunião Equipe, Visita Sr. Marcos (sem cadastro)...")

            c1, c2 = st.columns(2)

            op_cli = ["-- Nenhum / Avulso --"] + lista_clientes
            idx_cli = op_cli.index(edit_a['Cliente']) if edit_a and edit_a.get(
                'Cliente') in op_cli else 0
            cliente_sel = c1.selectbox(
                "Vincular Cliente (Opcional)", op_cli, index=idx_cli)

            op_cor = ["-- Nenhum / Interno --"] + lista_corretores
            idx_cor = op_cor.index(edit_a['Corretor']) if edit_a and edit_a.get(
                'Corretor') in op_cor else 0
            corretor_sel = c2.selectbox(
                "Corretor / Responsável", op_cor, index=idx_cor)

            c3, c4 = st.columns(2)
            op_tipo = ["Visita ao Imóvel", "Reunião na Imobiliária",
                       "Contato Telefônico/Online", "Evento Interno/Outros"]
            idx_tipo = op_tipo.index(edit_a['Tipo']) if edit_a and edit_a.get(
                'Tipo') in op_tipo else 0
            tipo_sel = c3.selectbox(
                "Tipo de Atendimento", op_tipo, index=idx_tipo)

            op_imob = ["-- Nenhum --"] + lista_imoveis
            idx_imob = op_imob.index(edit_a['imovel_desc']) if edit_a and edit_a.get(
                'imovel_desc') in op_imob else 0
            imovel_sel = c4.selectbox(
                "Imóvel Relacionado (Opcional)", op_imob, index=idx_imob)

            c5, c6, c7 = st.columns([2, 2, 2])

            if edit_a and edit_a.get('data_hora_raw'):
                dt_obj = pd.to_datetime(edit_a['data_hora_raw'])
                val_d = dt_obj.date()
                val_t = dt_obj.time()
            else:
                from datetime import datetime
                val_d = datetime.today().date()
                val_t = datetime.strptime("09:00", "%H:%M").time()

            data_sel = c5.date_input("Data do Compromisso", value=val_d)
            hora_sel = c6.time_input("Horário", value=val_t)

            op_status = ["Agendado", "Realizado", "Cancelado"]
            idx_status = op_status.index(edit_a['Status']) if edit_a and edit_a.get(
                'Status') in op_status else 0
            status_sel = c7.selectbox("Status", op_status, index=idx_status)

            obs_val = st.text_area("Observações", value=edit_a.get(
                'Obs', '') if edit_a else "", placeholder="Detalhes, orientações, etc.")

            st.divider()
            btn_agendar = st.form_submit_button("💾 Salvar Agenda")

            if btn_agendar:
                if not titulo_val.strip() and cliente_sel == "-- Nenhum / Avulso --":
                    st.error(
                        "⚠️ Você deve preencher um 'Título' para o evento OU selecionar um 'Cliente' na lista!")
                else:
                    id_c = int(df_clientes[df_clientes['nome_completo'] == cliente_sel]
                               ['id_cliente'].values[0]) if cliente_sel != "-- Nenhum / Avulso --" else None
                    id_cor = int(df_corretores[df_corretores['nome_completo'] == corretor_sel]
                                 ['id_corretor'].values[0]) if corretor_sel != "-- Nenhum / Interno --" else None

                    id_imob = None
                    if imovel_sel != "-- Nenhum --":
                        id_imob = int(
                            df_imoveis[df_imoveis['desc_imovel'] == imovel_sel]['id_imovel'].values[0])

                    data_hora_agendamento = f"{data_sel} {hora_sel}"

                    try:
                        cur = conn.cursor()
                        if id_interno_a == 0:
                            cur.execute("""
                                INSERT INTO atendimentos 
                                (titulo_evento, id_cliente, id_corretor, id_imovel, data_hora, tipo_atendimento, observacoes, status) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (titulo_val, id_c, id_cor, id_imob, data_hora_agendamento, tipo_sel, obs_val, status_sel))
                        else:
                            cur.execute("""
                                UPDATE atendimentos SET 
                                titulo_evento=%s, id_cliente=%s, id_corretor=%s, id_imovel=%s, data_hora=%s, tipo_atendimento=%s, observacoes=%s, status=%s 
                                WHERE id_atendimento=%s
                            """, (titulo_val, id_c, id_cor, id_imob, data_hora_agendamento, tipo_sel, obs_val, status_sel, id_interno_a))

                        conn.commit()
                        st.session_state.atend_editando = None
                        st.session_state.abrir_expander_atend = False
                        st.session_state.tab_versao_atend += 1
                        st.toast("✅ Evento salvo na agenda com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao agendar: {e}")

        if st.button("🚫 Cancelar / Limpar", key="btn_canc_atend"):
            st.session_state.atend_editando = None
            st.session_state.abrir_expander_atend = False
            st.session_state.tab_versao_atend += 1
            st.rerun()

    st.divider()

    # --- 2. LISTA DE PRÓXIMOS AGENDAMENTOS (A AGENDA INTERATIVA) ---
    st.markdown(
        "🗓️ **Próximos Compromissos (Agenda Geral)** - *Selecione para editar*")

    query_agenda = """
        SELECT a.id_atendimento, 
               a.titulo_evento,
               a.data_hora as data_hora_raw,
               TO_CHAR(a.data_hora, 'DD/MM/YYYY HH24:MI') as "Data/Hora",
               c.nome_completo as "Cliente",
               cor.nome_completo as "Corretor",
               cor.telefone as "tel_corretor",
               a.tipo_atendimento as "Tipo",
               a.status as "Status",
               a.observacoes as "Obs",
               i.bairro as "Bairro Imóvel",
               CONCAT('ID ', i.id_imovel, ' - ', i.tipo_imovel, ' em ', i.bairro) as "imovel_desc"
        FROM atendimentos a
        LEFT JOIN clientes c ON a.id_cliente = c.id_cliente
        LEFT JOIN corretores cor ON a.id_corretor = cor.id_corretor
        LEFT JOIN imoveis i ON a.id_imovel = i.id_imovel
        ORDER BY a.data_hora DESC
    """
    try:
        df_agenda = pd.read_sql(query_agenda, conn)

        if not df_agenda.empty:
            import urllib.parse

            def formatar_evento(row):
                tit = row['titulo_evento']
                cli = row['Cliente']
                if tit and cli:
                    return f"{tit} ({cli})"
                if tit:
                    return tit
                if cli:
                    return cli
                return "Evento s/ Título"

            df_agenda['Evento / Contato'] = df_agenda.apply(
                formatar_evento, axis=1)

            def gerar_link_wpp(row):
                tel = str(row['tel_corretor']).replace(" ", "").replace(
                    "-", "").replace("(", "").replace(")", "")
                if not tel or tel == 'None' or str(row['Corretor']) == 'None':
                    return ""

                # 1. Geração do Link Inteligente do Google Calendar
                try:
                    dt_inicio = pd.to_datetime(row['data_hora_raw'])
                    dt_fim = dt_inicio + pd.Timedelta(hours=1)

                    str_inicio = dt_inicio.strftime("%Y%m%dT%H%M%S")
                    str_fim = dt_fim.strftime("%Y%m%dT%H%M%S")

                    tit_cal = urllib.parse.quote(row['Evento / Contato'])
                    detalhes = f"Cliente: {row['Cliente'] if row['Cliente'] else 'Não informado'}"
                    if row['Obs']:
                        detalhes += f" | Obs: {row['Obs']}"
                    det_cal = urllib.parse.quote(detalhes)
                    loc_cal = urllib.parse.quote(
                        row['Bairro Imóvel'] if row['Bairro Imóvel'] else "A combinar")

                    link_agenda = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={tit_cal}&dates={str_inicio}/{str_fim}&details={det_cal}&location={loc_cal}"
                except:
                    link_agenda = ""

                # 2. Montagem da Mensagem do WhatsApp
                msg = f"📅 *Novo Compromisso*\n\nOlá {row['Corretor']}!\nResumo da agenda:\n\n📌 *Evento:* {row['Evento / Contato']}\n🗓️ *Data/Hora:* {row['Data/Hora']}\n🏷️ *Tipo:* {row['Tipo']}"
                if row['Bairro Imóvel']:
                    msg += f"\n🏠 *Imóvel:* {row['Bairro Imóvel']}"
                if row['Obs']:
                    msg += f"\n📝 *Obs:* {row['Obs']}"

                # Acopla o link do Google Calendar no final da mensagem!
                if link_agenda:
                    msg += f"\n\n👇 *Adicione na sua agenda (1 clique):*\n{link_agenda}"

                msg_enc = urllib.parse.quote(msg)
                return f"https://api.whatsapp.com/send?phone=55{tel}&text={msg_enc}"

            df_agenda['Avisar Corretor'] = df_agenda.apply(
                gerar_link_wpp, axis=1)

            df_view = df_agenda[['id_atendimento', 'Data/Hora', 'Evento / Contato',
                                 'Corretor', 'Tipo', 'Status', 'Avisar Corretor']].copy()
            df_view.insert(0, "Editar", False)

            chave_edit_atend = f"editor_atend_v{st.session_state.tab_versao_atend}"

            st.data_editor(df_view, use_container_width=True, hide_index=True, key=chave_edit_atend,
                           column_config={
                               "Editar": st.column_config.CheckboxColumn("Editar"),
                               "Avisar Corretor": st.column_config.LinkColumn("Notificar via WhatsApp", display_text="📲 Enviar Zap")
                           },
                           disabled=['id_atendimento', 'Data/Hora', 'Evento / Contato', 'Corretor', 'Tipo', 'Status', 'Avisar Corretor'])

            if chave_edit_atend in st.session_state:
                mudancas_atend = st.session_state[chave_edit_atend].get(
                    "edited_rows", {})
                if mudancas_atend:
                    idx_a = [int(i) for i, v in mudancas_atend.items()
                             if v.get("Editar") is True]
                    if idx_a:
                        st.session_state.atend_editando = df_agenda.iloc[idx_a[-1]].to_dict(
                        )
                        st.session_state.abrir_expander_atend = True
                        st.session_state.tab_versao_atend += 1
                        st.rerun()
        else:
            st.info("Nenhuma agenda registrada no momento.")
    except Exception as e:
        st.error(f"Erro técnico ao carregar a agenda: {e}")

    conn.close()

# ------------------------------------------
# TELA 3.5: HISTÓRICO DE ATENDIMENTOS
# ------------------------------------------
elif pagina == "Clientes_Historico_Atend":
    st.header("📚 Histórico de Atendimentos")
    st.write("Consulte os compromissos passados, filtre por corretor e faça a baixa das visitas realizadas.")

    conn = conectar()

    # --- 1. PAINEL DE FILTROS ---
    st.markdown("🔍 **Filtros de Busca**")
    col1, col2, col3, col4 = st.columns(4)

    # Define o período padrão (Últimos 30 dias até hoje)
    from datetime import datetime, timedelta
    hoje = datetime.today()
    trinta_dias_atras = hoje - timedelta(days=30)

    data_inicio = col1.date_input("Data Inicial", value=trinta_dias_atras)
    data_fim = col2.date_input("Data Final", value=hoje)

    # Busca corretores para o filtro
    try:
        df_corr_filt = pd.read_sql(
            "SELECT nome_completo FROM corretores ORDER BY nome_completo", conn)
        lista_corretores_filt = ["Todos"] + \
            df_corr_filt['nome_completo'].tolist()
    except:
        lista_corretores_filt = ["Todos"]

    corretor_f = col3.selectbox("Filtrar por Corretor", lista_corretores_filt)
    status_f = col4.selectbox("Filtrar por Status", [
                              "Todos", "Agendado", "Realizado", "Cancelado"])

    st.divider()

    # --- 2. BUSCA DINÂMICA NO BANCO DE DADOS ---
    query_hist = """
        SELECT a.id_atendimento,
               TO_CHAR(a.data_hora, 'DD/MM/YYYY HH24:MI') as "Data/Hora",
               COALESCE(a.titulo_evento, 'Evento Avulso') as "Título/Evento",
               COALESCE(c.nome_completo, '-') as "Cliente",
               COALESCE(cor.nome_completo, 'Interno') as "Corretor",
               a.tipo_atendimento as "Tipo",
               a.status as "Status",
               COALESCE(a.observacoes, '') as "Observações"
        FROM atendimentos a
        LEFT JOIN clientes c ON a.id_cliente = c.id_cliente
        LEFT JOIN corretores cor ON a.id_corretor = cor.id_corretor
        WHERE DATE(a.data_hora) >= %s AND DATE(a.data_hora) <= %s
    """
    params = [data_inicio, data_fim]

    # Aplica os filtros se a gestora mudou a caixa de seleção
    if corretor_f != "Todos":
        query_hist += " AND cor.nome_completo = %s"
        params.append(corretor_f)

    if status_f != "Todos":
        query_hist += " AND a.status = %s"
        params.append(status_f)

    query_hist += " ORDER BY a.data_hora DESC"

    # --- 3. EXIBIÇÃO E EDIÇÃO RÁPIDA (MAGIC GRID) ---
    try:
        df_hist = pd.read_sql(query_hist, conn, params=params)

        if not df_hist.empty:

            # KPIs Rápidos no topo
            c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
            c_kpi1.metric("Total no Período", len(df_hist))
            c_kpi2.metric("Realizados", len(
                df_hist[df_hist['Status'] == 'Realizado']))
            c_kpi3.metric("Cancelados / Faltas",
                          len(df_hist[df_hist['Status'] == 'Cancelado']))

            st.markdown(
                "📝 **Edição Rápida:** *Dê dois cliques nas colunas 'Status' ou 'Observações' para dar baixa na visita. O sistema salva sozinho!*")

            if 'tab_hist_versao' not in st.session_state:
                st.session_state.tab_hist_versao = 0

            chave_grid = f"grid_hist_{st.session_state.tab_hist_versao}"

            # O st.data_editor permite editar a tabela como se fosse um Excel
            df_editado = st.data_editor(
                df_hist,
                use_container_width=True,
                hide_index=True,
                key=chave_grid,
                column_config={
                    "Status": st.column_config.SelectboxColumn("Status", options=["Agendado", "Realizado", "Cancelado"], required=True),
                    "Observações": st.column_config.TextColumn("Observações / Feedback do Cliente")
                },
                # Bloqueia a edição de quem, quando e o quê (só permite mudar o status e o feedback)
                disabled=['id_atendimento', 'Data/Hora',
                          'Título/Evento', 'Cliente', 'Corretor', 'Tipo']
            )

            # 👇 O MOTOR DE SALVAMENTO AUTOMÁTICO
            if chave_grid in st.session_state:
                mudancas = st.session_state[chave_grid].get("edited_rows", {})
                if mudancas:
                    cur = conn.cursor()
                    for idx_row, alteracoes in mudancas.items():
                        # Descobre qual foi a linha alterada
                        id_atend = df_hist.iloc[int(idx_row)]['id_atendimento']

                        # Pega os valores novos (se houveram) ou mantém os antigos
                        novo_status = alteracoes.get(
                            "Status", df_hist.iloc[int(idx_row)]['Status'])
                        nova_obs = alteracoes.get(
                            "Observações", df_hist.iloc[int(idx_row)]['Observações'])

                        # Atualiza silenciosamente no banco de dados
                        cur.execute("UPDATE atendimentos SET status = %s, observacoes = %s WHERE id_atendimento = %s",
                                    (novo_status, nova_obs, int(id_atend)))

                    conn.commit()
                    # Força a tela a piscar para garantir a atualização
                    st.session_state.tab_hist_versao += 1
                    st.toast("✅ Alterações salvas com sucesso!")
                    st.rerun()

        else:
            st.info("Nenhum atendimento encontrado para os filtros selecionados.")

    except Exception as e:
        st.error(f"Erro técnico ao carregar o histórico: {e}")

    conn.close()

# ------------------------------------------
# TELA 4.2: NEGOCIAÇÕES ATIVAS (FUNIL KANBAN)
# ------------------------------------------
elif pagina == "Vendas_Negociacoes":
    st.header("🔄 Funil de Vendas (Kanban)")
    st.write("Acompanhe e mova os clientes pelas etapas da negociação.")

    conn = conectar()

    if st.button("🔎 Rodar Match Automático (Gerar Oportunidades)", type="primary"):
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO funil_vendas (id_imovel, id_cliente, etapa)
                SELECT im.id_imovel, ic.id_cliente, '1. Contato Inicial'
                FROM imoveis im
                JOIN interesses_clientes ic 
                  ON im.tipo_imovel = ic.tipo_imovel_desejado 
                  AND im.valor_venda <= ic.valor_maximo
                WHERE im.status = 'Disponível'
                  AND NOT EXISTS (
                      SELECT 1 FROM funil_vendas fv 
                      WHERE fv.id_imovel = im.id_imovel AND fv.id_cliente = ic.id_cliente AND ic.ativo = TRUE
                  )
            """)
            linhas_afetadas = cur.rowcount
            conn.commit()
            if linhas_afetadas > 0:
                st.success(
                    f"🔥 SUCESSO! O robô encontrou {linhas_afetadas} novos cruzamentos perfeitos e já colocou no Funil de Vendas!")
            else:
                st.info("Nenhum novo Match exato encontrado no momento.")
        except Exception as e:
            st.error(f"Erro ao processar Match: {e}")

    st.divider()

    # --- OPÇÃO 3: O QUADRO KANBAN VISUAL ---
    query_funil = """
        SELECT f.id_negociacao, f.etapa, c.nome_completo as cliente, c.telefone, 
               i.tipo_imovel, i.bairro, i.valor_venda
        FROM funil_vendas f
        JOIN clientes c ON f.id_cliente = c.id_cliente
        JOIN imoveis i ON f.id_imovel = i.id_imovel
        WHERE f.etapa != '5. Vendido (Ganho)' AND f.etapa != '6. Perdido'
    """
    try:
        df_funil = pd.read_sql(query_funil, conn)
    except:
        df_funil = pd.DataFrame()

    etapas = ["1. Contato Inicial", "2. Visita Agendada", "3. Proposta na Mesa",
              "4. Análise de Docs", "5. Vendido (Ganho)", "6. Perdido"]

    col1, col2, col3, col4 = st.columns(4)
    colunas_ui = [col1, col2, col3, col4]
    etapas_ativas = etapas[0:4]

    if not df_funil.empty:
        for idx, etapa_nome in enumerate(etapas_ativas):
            with colunas_ui[idx]:
                st.markdown(f"**{etapa_nome}**")
                df_etapa = df_funil[df_funil['etapa'] == etapa_nome]

                for _, row in df_etapa.iterrows():
                    with st.container(border=True):
                        st.markdown(f"👤 **{row['cliente']}**")
                        st.caption(
                            f"🏠 {row['tipo_imovel']} em {row['bairro']}")
                        st.caption(f"💰 {formata_moeda(row['valor_venda'])}")

                        nova_etapa = st.selectbox(
                            "Mover para:",
                            etapas,
                            index=etapas.index(row['etapa']),
                            key=f"sel_{row['id_negociacao']}",
                            label_visibility="collapsed"
                        )

                        if nova_etapa != row['etapa']:
                            cur = conn.cursor()
                            cur.execute("UPDATE funil_vendas SET etapa = %s WHERE id_negociacao = %s", (
                                nova_etapa, row['id_negociacao']))
                            if nova_etapa == '5. Vendido (Ganho)':
                                cur.execute(
                                    "UPDATE imoveis SET status = 'Vendido' WHERE id_imovel = %s", (row['id_imovel'],))
                            conn.commit()
                            st.rerun()
    else:
        st.info("O Funil de Vendas está vazio. Clique no botão azul acima para buscar Matches Automáticos ou cadastre novos interesses!")

    conn.close()

# ------------------------------------------
# TELAS EM CONSTRUÇÃO E DASHBOARD EXECUTIVO
# ------------------------------------------
elif pagina == "Dashboard":
    st.header("📊 Dashboard Executivo (Visão Geral)")

    # --- 1. CARDS DE INDICADORES RÁPIDOS (KPIs) ---
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total de Imóveis (Carteira)",
                  value="142", delta="+12 neste mês")
    with col2:
        st.metric(label="VGV (Valor Geral de Vendas)",
                  value="R$ 45.3 Milhões", delta="R$ 2.1M em captações recentes")
    with col3:
        st.metric(label="Vendas Concluídas (Ano)", value="28",
                  delta="+3 em relação ao mês anterior")
    with col4:
        st.metric(label="Comissões Projetadas",
                  value="R$ 184.500,00", delta="Alta temporada")

    st.divider()

    # --- 2. DADOS FICTÍCIOS PARA OS GRÁFICOS ---
    df_status = pd.DataFrame(
        {"Status": ["Disponível", "Vendido", "Reservado"], "Quantidade": [98, 28, 16]})
    df_tipos = pd.DataFrame({"Tipo": ["Apartamento", "Casa", "Terreno", "Sobrado",
                            "Sítio/Chácara", "Comercial"], "Quantidade": [55, 42, 25, 12, 8, 5]})
    df_evolucao = pd.DataFrame({"Mês": ["Outubro", "Novembro", "Dezembro", "Janeiro",
                               "Fevereiro", "Março"], "Vendas (R$ Milhões)": [1.2, 1.8, 3.5, 2.1, 2.5, 4.2]})

    # --- 3. CONSTRUÇÃO DOS GRÁFICOS (PLOTLY) ---
    c_graf1, c_graf2 = st.columns(2)

    with c_graf1:
        st.subheader("Distribuição por Status")
        fig_status = px.pie(df_status, values='Quantidade', names='Status',
                            hole=0.4, color_discrete_sequence=['#2ecc71', '#3498db', '#f1c40f'])
        fig_status.update_layout(margin=dict(
            t=20, b=20, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_status, use_container_width=True)

    with c_graf2:
        st.subheader("Imóveis por Categoria")
        fig_tipos = px.bar(df_tipos, x='Tipo', y='Quantidade', text='Quantidade',
                           color='Tipo', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_tipos.update_layout(showlegend=False, margin=dict(
            t=20, b=20, l=0, r=0), xaxis_title="", yaxis_title="", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_tipos, use_container_width=True)

    st.divider()

    # --- 4. GRÁFICO DE LINHA E RADAR DE DEMANDA ---
    st.subheader("📈 Evolução de Vendas (Últimos 6 Meses)")
    fig_evo = px.line(df_evolucao, x='Mês', y='Vendas (R$ Milhões)',
                      markers=True, line_shape='spline', color_discrete_sequence=['#e74c3c'])
    fig_evo.update_traces(line=dict(width=4), marker=dict(size=10))
    fig_evo.update_layout(margin=dict(t=20, b=20, l=0, r=0),
                          yaxis_title="Volume de Vendas (Milhões R$)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_evo, use_container_width=True)

    # --- OPÇÃO 2: RADAR DE DEMANDA REPRIMIDA ---
    st.divider()
    st.subheader("🚨 Radar de Captação (Demanda Reprimida)")
    st.write("O que seus clientes querem comprar hoje, mas **NÃO TEMOS** no estoque:")

    query_demanda = """
        SELECT i.tipo_imovel_desejado as "Tipo Buscado", i.bairro_preferencial as "Bairro(s)", 
               count(i.id_interesse) as "Qtd de Clientes Esperando", 
               MAX(i.valor_maximo) as "Disposição a Pagar (Até)"
        FROM interesses_clientes i
        WHERE i.ativo = TRUE
        AND NOT EXISTS (
            SELECT 1 FROM imoveis im 
            WHERE im.status = 'Disponível' 
            AND im.tipo_imovel = i.tipo_imovel_desejado 
            AND im.valor_venda <= i.valor_maximo
        )
        GROUP BY i.tipo_imovel_desejado, i.bairro_preferencial
        ORDER BY "Qtd de Clientes Esperando" DESC
    """
    try:
        conn = conectar()
        df_demanda = pd.read_sql(query_demanda, conn)
        conn.close()

        if not df_demanda.empty:
            df_demanda["Disposição a Pagar (Até)"] = df_demanda["Disposição a Pagar (Até)"].apply(
                formata_moeda)
            st.warning(
                "⚠️ Atenção: Direcione seus corretores para captar estes perfis de imóveis!")
            st.dataframe(df_demanda, use_container_width=True, hide_index=True)
        else:
            st.success(
                "✅ Nosso estoque atual atende a todos os perfis de busca registrados!")
    except Exception as e:
        st.info("Cadastre os primeiros interesses para ativar o radar de captação.")

# ------------------------------------------
# ROTEADOR PARA AS TELAS NÃO FINALIZADAS
# ------------------------------------------
elif pagina != "Dashboard":
    st.info(
        f"🚧 A tela **{pagina}** está em desenvolvimento. O módulo será liberado em breve!")
