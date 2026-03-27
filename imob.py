import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from datetime import datetime


# --- 1. FUNÇÕES DE APOIO E CONEXÃO ---

def conectar():
    # Agora o sistema busca a conexão segura direto do cofre!
    return psycopg2.connect(st.secrets["DB_URL"])


def formata_moeda(valor):
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


st.set_page_config(
    page_title="Mayara Vieira Negócios Imobiliários", layout="wide", page_icon="🏢")

# --- 2. SISTEMA DE LOGIN ---
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
        st.rerun()

st.title(f"🏠 Bem-vindo, {USUARIO}")

# --- 3. MENU LATERAL EXPANSÍVEL (MODO HARD - ACORDEÃO COMPLETO) ---
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
        st.rerun()

# --- VARIÁVEL DE ROTEAMENTO GERAL ---
pagina = st.session_state.pagina_atual

# -----------------------------------------------------------------------------------------------------------------------------
# ==========================================
# 4. ROTEAMENTO DAS TELAS (ÁREA PRINCIPAL)
# ==========================================

# --- VARIÁVEIS DE SESSÃO GERAIS DE IMÓVEIS ---
if 'imovel_editando' not in st.session_state:
    st.session_state.imovel_editando = None
if 'imovel_selecionado_match' not in st.session_state:
    st.session_state.imovel_selecionado_match = None
if 'tabela_versao' not in st.session_state:
    st.session_state.tabela_versao = 0


def tratar_numero(valor):
    try:
        return float(valor) if valor is not None else 0.0
    except:
        return 0.0


# ------------------------------------------
# TELA 1: CADASTRO E EDIÇÃO DE IMÓVEIS
# ------------------------------------------
if pagina == "Imoveis_Novo":
    st.header("🏢 Cadastro de Imóveis")

    if 'imovel_editando' not in st.session_state:
        st.session_state.imovel_editando = None
    if 'abrir_expander' not in st.session_state:
        st.session_state.abrir_expander = False
    if 'tabela_versao' not in st.session_state:
        st.session_state.tabela_versao = 0

    conn = conectar()
    props = pd.read_sql("SELECT id_cliente, nome_completo FROM clientes", conn)
    edit = st.session_state.imovel_editando
    id_interno = int(edit['id_imovel']) if edit else 0

    # Funções seguras para lidar com números vazios do banco
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

    # --- 1. EXPANDER DE CADASTRO / EDIÇÃO ---
    with st.expander("➕ Cadastrar / Alterar Imóvel", expanded=st.session_state.abrir_expander):
        chave_form = f"form_imovel_{st.session_state.tabela_versao}"

        with st.form(chave_form, clear_on_submit=False):
            # --- SEÇÃO 1: LOCALIZAÇÃO ---
            st.markdown("📍 **Localização**")
            c_loc1, c_loc2, c_loc3, c_loc4 = st.columns([2, 2, 2, 1])
            with c_loc1:
                rua_val = st.text_input(
                    "Rua", value=edit['endereco_rua'] if edit else "")
            with c_loc2:
                bairro_val = st.text_input(
                    "Bairro", value=edit['bairro'] if edit else "")
            with c_loc3:
                cidade_val = st.text_input(
                    "Cidade", value=edit.get('cidade', "") if edit else "")
            with c_loc4:
                cep_val = st.text_input(
                    "CEP", value=edit.get('cep', "") if edit else "")

            st.divider()

            # --- SEÇÃO 2: CARACTERÍSTICAS ---
            st.markdown("🏠 **Características do Imóvel**")
            c_car1, c_car2, c_car3, c_car4, c_car5, c_car6 = st.columns(
                [2, 1, 1, 1, 1, 1])

            lista_tipos = ["Apartamento", "Casa", "Casa em Condominio", "Casa Comercial", "Chácara", "Cobertura", "Empreendimento",
                           "Pavilhão", "Prédio comercial", "Sala comercial", "Sitio", "Sobrado", "Terreno", "Terreno comercial"]
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

            # --- SEÇÃO 3: VALORES E STATUS ---
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
                p_agenc_val = st.number_input(
                    "% Agenciamento", min_value=0.0, value=6.0)
            with c_val3:
                lista_doc = ["Ok", "Em Regularização", "Falta Matrícula"]
                doc_idx = lista_doc.index(edit.get('doc_status')) if edit and edit.get(
                    'doc_status') in lista_doc else 0
                doc_sit = st.selectbox(
                    "Status Documentação", lista_doc, index=doc_idx)
            with c_val4:
                if not props.empty:
                    nomes_props = props['nome_completo'].tolist()
                    idx_p = 0
                    if edit:
                        cur_p = conn.cursor()
                        cur_p.execute(
                            "SELECT nome_completo FROM clientes WHERE id_cliente = %s", (edit['id_proprietario'],))
                        res_p = cur_p.fetchone()
                        if res_p and res_p[0] in nomes_props:
                            idx_p = nomes_props.index(res_p[0])
                    sel_p = st.selectbox(
                        "Proprietário", nomes_props, index=idx_p)
                else:
                    sel_p = "Nenhum"

            st.divider()

            # --- SEÇÃO 4: EXTRAS ---
            st.markdown("✨ **Extras e Links**")
            c_link, c_comod = st.columns([1, 2])
            with c_link:
                link_val = st.text_input("🔗 Link do Imóvel no Site", value=edit.get(
                    'link_site', "") if edit else "")

            with c_comod:
                opcoes_comodidades = ["Piscina", "Academia", "Churrasqueira",
                                      "Salão de Festas", "Portaria 24h", "Playground", "Elevador"]
                comod_default = edit.get('comodidades').split(
                    ", ") if edit and edit.get('comodidades') else []
                comod_sel = st.multiselect(
                    "Comodidades", opcoes_comodidades, default=comod_default)
                comod_string = ", ".join(comod_sel)

            btn_salvar = st.form_submit_button("💾 Salvar Registro")

            if btn_salvar:
                cur = conn.cursor()
                id_p_sel = props[props['nome_completo'] ==
                                 sel_p]['id_cliente'].values[0] if not props.empty else 0

                if id_interno == 0:
                    cur.execute("""
                        INSERT INTO imoveis 
                        (endereco_rua, bairro, cidade, cep, tipo_imovel, quartos, suites, banheiros, garagens, area_total_m2, valor_venda, status, id_proprietario, criado_por, doc_status, iptu_anual, comodidades, link_site) 
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (rua_val, bairro_val, cidade_val, cep_val, tipo_val, qtos_val, suites_val, banh_val, vagas_val, area_t, v_venda_val, status_i, int(id_p_sel), USUARIO, doc_sit, iptu_v, comod_string, link_val))
                else:
                    cur.execute("""
                        UPDATE imoveis SET 
                        endereco_rua=%s, bairro=%s, cidade=%s, cep=%s, tipo_imovel=%s, quartos=%s, suites=%s, banheiros=%s, garagens=%s, area_total_m2=%s, valor_venda=%s, status=%s, id_proprietario=%s, doc_status=%s, iptu_anual=%s, comodidades=%s, link_site=%s 
                        WHERE id_imovel=%s
                    """, (rua_val, bairro_val, cidade_val, cep_val, tipo_val, qtos_val, suites_val, banh_val, vagas_val, area_t, v_venda_val, status_i, int(id_p_sel), doc_sit, iptu_v, comod_string, link_val, id_interno))

                conn.commit()
                st.session_state.imovel_editando = None
                st.session_state.abrir_expander = False
                st.session_state.tabela_versao += 1
                st.toast("✅ Imóvel salvo com sucesso!")
                st.rerun()

        if st.button("🚫 Cancelar / Limpar"):
            st.session_state.imovel_editando = None
            st.session_state.abrir_expander = False
            st.session_state.tabela_versao += 1
            st.rerun()

    # --- 2. LISTA RÁPIDA PARA PESQUISA E EDIÇÃO ---
    st.divider()
    st.subheader("🔍 Pesquisar para Editar")

    col_p1, col_p2, col_p3 = st.columns(3)
    busca_i = col_p1.text_input(
        "Filtrar por Rua ou Bairro", key="txt_busca_cad")
    status_f = col_p2.selectbox("Filtrar por Status", [
                                "Todos", "Disponível", "Reservado", "Vendido"], key="sel_status_cad")
    tipo_f = col_p3.selectbox(
        "Filtrar por Tipo", ["Todos"] + lista_tipos, key="sel_tipo_cad")

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

    # Adicionamos "Tipo" e "Quartos" na visualização rápida da tabela
    df_i_edit = df_i_full[['id_imovel', 'tipo_imovel', 'endereco_rua',
                           'bairro', 'quartos', 'valor_venda', 'status']].copy()
    df_i_edit.insert(0, "Editar", False)
    df_i_edit['valor_venda'] = df_i_edit['valor_venda'].apply(formata_moeda)

    chave_edit = f"editor_cad_v{st.session_state.tabela_versao}"
    st.data_editor(df_i_edit, use_container_width=True, hide_index=True, key=chave_edit,
                   column_config={
                       "Editar": st.column_config.CheckboxColumn("Editar")},
                   disabled=['id_imovel', 'tipo_imovel', 'endereco_rua', 'bairro', 'quartos', 'valor_venda', 'status'])

    if chave_edit in st.session_state:
        mudancas = st.session_state[chave_edit].get("edited_rows", {})
        if mudancas:
            idx = [i for i, v in mudancas.items() if v.get("Editar") is True]
            if idx:
                st.session_state.imovel_editando = df_i_full.iloc[idx[-1]].to_dict(
                )
                st.session_state.abrir_expander = True
                st.session_state.tabela_versao += 1
                st.rerun()

# ------------------------------------------
# TELA 2: LISTA DE CONSULTA E MATCH
# ------------------------------------------
elif pagina == "Imoveis_Lista":
    st.header("🔍 Consulta e Match de Imóveis")
    st.write(
        "Utilize os filtros abaixo para encontrar imóveis e cruzar com os interesses dos clientes.")

    # --- FILTROS DE BUSCA ---
    col_p1, col_p2, col_p3 = st.columns(3)
    busca_i = col_p1.text_input("Filtrar por Rua ou Bairro", key="txt_busca_i")
    status_f = col_p2.selectbox("Filtrar por Status", [
                                "Todos", "Disponível", "Reservado", "Vendido"])
    comod_f = col_p3.multiselect("Filtrar por Comodidades", [
                                 "Piscina", "Academia", "Churrasqueira", "Salão de Festas", "Portaria 24h", "Playground", "Elevador"])

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

    df_i_view = df_i_full[['id_imovel', 'endereco_rua',
                           'bairro', 'valor_venda', 'status', 'comodidades']].copy()
    # Trocamos "Editar" por "Selecionar"
    df_i_view.insert(0, "Selecionar", False)
    df_i_view['valor_venda'] = df_i_view['valor_venda'].apply(formata_moeda)

    chave_lista = f"lista_match_v{st.session_state.tabela_versao}"
    st.data_editor(df_i_view, use_container_width=True, hide_index=True, key=chave_lista,
                   column_config={
                       "Selecionar": st.column_config.CheckboxColumn("Ver Match")},
                   disabled=['id_imovel', 'endereco_rua', 'bairro', 'valor_venda', 'status', 'comodidades'])

    if chave_lista in st.session_state:
        mudancas = st.session_state[chave_lista].get("edited_rows", {})
        if mudancas:
            idx = [i for i, v in mudancas.items() if v.get("Selecionar") is True]
            if idx:
                st.session_state.imovel_selecionado_match = df_i_full.iloc[idx[-1]].to_dict(
                )
                st.session_state.tabela_versao += 1
                st.rerun()

    # --- SISTEMA DE MATCH E ENVIO ---
    if st.session_state.imovel_selecionado_match:
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
                    st.success(f"🔥 {len(df_final)} Match(es) encontrado(s)!")
                    st.dataframe(df_final[[
                                 'nome_completo', 'telefone', 'valor_maximo', 'Afinidade']], use_container_width=True)

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
                    msg_encoded = urllib.parse.quote(msg_corpo.encode('utf-8'))
                    link_zap = f"https://api.whatsapp.com/send?text={msg_encoded}"

                    st.markdown(f"""
                        <a href="{link_zap}" target="_blank">
                            <button style="width:100%;background-color:#25D366;color:white;border:none;padding:12px;border-radius:8px;cursor:pointer;font-weight:bold;font-size:16px;">
                                📲 Enviar Ficha e Contato via WhatsApp
                            </button>
                        </a>
                    """, unsafe_allow_html=True)
                else:
                    st.info(
                        "Clientes encontrados pelo valor, mas nenhum no bairro deste imóvel.")
            else:
                st.info("Nenhum cliente cadastrado com este orçamento.")

        except Exception as e:
            st.error(f"Erro no Match: {e}")

    conn.close()

# ------------------------------------------
# TELAS EM CONSTRUÇÃO
# ------------------------------------------
elif pagina != "Dashboard":
    st.info(f"🚧 A tela **{pagina}** está em desenvolvimento. Módulo em breve!")
