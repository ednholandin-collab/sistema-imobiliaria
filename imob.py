import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests  # Necessário para a busca do CEP

# --- 1. FUNÇÕES DE APOIO E CONEXÃO ---


def conectar():
    # Busca a conexão segura direto do cofre (secrets)
    return psycopg2.connect(st.secrets["DB_URL"])


def formata_moeda(valor):
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


st.set_page_config(
    page_title="Mayara Vieira Negócios Imobiliários", layout="wide", page_icon="🏢")

# --- TRAVA DE VISUAL E SEGURANÇA (OCULTA O MENU DO STREAMLIT) ---
st.markdown("""
    <style>
    /* Oculta o cabeçalho superior e o menu de configurações */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    /* Oculta a marca d'água do Streamlit no rodapé */
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

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
    # Variável de memória para o CEP do imóvel
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

        # --- BUSCADOR DE CEP MÁGICO (IMÓVEIS) ---
        st.markdown("#### 🔎 Busca Automática de Endereço")
        c_busca1, c_busca2 = st.columns([1, 3])

        # Chave dinâmica para limpar perfeitamente no botão Cancelar
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

            # Puxa da memória do CEP ou do banco de dados (se estiver editando)
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
            # ... [A PARTIR DAQUI O CÓDIGO CONTINUA EXATAMENTE IGUAL] ...
            c_car1, c_car2, c_car3, c_car4, c_car5, c_car6 = st.columns(
                [2, 1, 1, 1, 1, 1])

            # Busca os tipos direto do banco de dados
            try:
                df_tipos_db = pd.read_sql(
                    "SELECT nome FROM tipos_imoveis ORDER BY nome", conn)
                lista_tipos = df_tipos_db['nome'].tolist() if not df_tipos_db.empty else [
                    "Apartamento", "Casa"]
            except:
                # Segurança caso o banco falhe
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
                # 👇 Busca a lista do banco de dados na hora
                try:
                    df_comod_db = pd.read_sql(
                        "SELECT nome FROM comodidades ORDER BY nome", conn)
                    opcoes_comodidades = df_comod_db['nome'].tolist(
                    ) if not df_comod_db.empty else []
                except:
                    # Caso de erro no banco
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

    # 👇 NOVO: Busca os tipos no banco de dados para o filtro
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

    # 👇 NOVO: Usa a lista dinâmica que acabou de buscar do banco
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
    with st.expander("🏢 Categorias de Imóveis", expanded=True):
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
# TELAS EM CONSTRUÇÃO E DASHBOARD EXECUTIVO
# ------------------------------------------
elif pagina == "Dashboard":
    st.header("📊 Visão Geral")

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
    # Dados de Status
    df_status = pd.DataFrame({
        "Status": ["Disponível", "Vendido", "Reservado"],
        "Quantidade": [98, 28, 16]
    })

    # Dados de Tipo
    df_tipos = pd.DataFrame({
        "Tipo": ["Apartamento", "Casa", "Terreno", "Sobrado", "Sítio/Chácara", "Comercial"],
        "Quantidade": [55, 42, 25, 12, 8, 5]
    })

    # Dados de Evolução Mensal
    df_evolucao = pd.DataFrame({
        "Mês": ["Outubro", "Novembro", "Dezembro", "Janeiro", "Fevereiro", "Março"],
        "Vendas (R$ Milhões)": [1.2, 1.8, 3.5, 2.1, 2.5, 4.2]
    })

    # --- 3. CONSTRUÇÃO DOS GRÁFICOS (PLOTLY) ---
    c_graf1, c_graf2 = st.columns(2)

    with c_graf1:
        st.subheader("Distribuição por Status")
        # Gráfico de Rosca (Donut)
        fig_status = px.pie(df_status, values='Quantidade', names='Status', hole=0.4,
                            color_discrete_sequence=['#2ecc71', '#3498db', '#f1c40f'])
        fig_status.update_layout(margin=dict(
            t=20, b=20, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_status, use_container_width=True)

    with c_graf2:
        st.subheader("Imóveis por Categoria")
        # Gráfico de Barras Coloridas
        fig_tipos = px.bar(df_tipos, x='Tipo', y='Quantidade', text='Quantidade',
                           color='Tipo', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_tipos.update_layout(showlegend=False, margin=dict(t=20, b=20, l=0, r=0),
                                xaxis_title="", yaxis_title="", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_tipos, use_container_width=True)

    st.divider()

    # --- 4. GRÁFICO DE LINHA (EVOLUÇÃO TENDÊNCIA) ---
    st.subheader("📈 Evolução de Vendas (Últimos 6 Meses)")
    fig_evo = px.line(df_evolucao, x='Mês', y='Vendas (R$ Milhões)', markers=True,
                      line_shape='spline', color_discrete_sequence=['#e74c3c'])
    fig_evo.update_traces(line=dict(width=4), marker=dict(size=10))
    fig_evo.update_layout(margin=dict(t=20, b=20, l=0, r=0),
                          yaxis_title="Volume de Vendas (Milhões R$)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_evo, use_container_width=True)

# ------------------------------------------
# ROTEADOR PARA AS TELAS NÃO FINALIZADAS
# ------------------------------------------
elif pagina != "Dashboard":
    st.info(
        f"🚧 A tela **{pagina}** está em desenvolvimento. O módulo será liberado em breve!")
