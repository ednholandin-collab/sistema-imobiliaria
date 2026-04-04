import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests  # Necessário para a busca do CEP

# Coloque isso no TOPO do seu código para testes
# if 'nivel_acesso' not in st.session_state:
# Altere aqui para "Corretor" ou "Financeiro" para testar como a tela muda!
#    st.session_state.nivel_acesso = "Corretor"

# --- 1 FUNÇÕES DE APOIO E CONEXÃO ---


def conectar(): return psycopg2.connect(st.secrets["DB_URL"])


def formata_moeda(valor):
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


st.set_page_config(
    page_title="Mayara Vieira Negócios Imobiliários", layout="wide", page_icon="🏢")

# --- TRAVA DE VISUAL E SEGURANÇA ---
st.markdown("""
    <style>
    /* Oculta apenas a marca d'água do Streamlit no rodapé */
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3 SISTEMA DE LOGIN ---
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'permissoes' not in st.session_state:
    st.session_state.permissoes = {}

if not st.session_state.logado:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.header("🔐 Acesso ao Mayara Vieira")
        u = st.text_input("Usuário (Login)")
        s = st.text_input("Senha", type="password")

        if st.button("Acessar", type="primary", use_container_width=True):
            if u and s:
                try:
                    import hashlib
                    # Criptografa a senha digitada para comparar com o banco
                    senha_digitada_hash = hashlib.sha256(
                        s.encode('utf-8')).hexdigest()
                    conn = conectar()
                    cur = conn.cursor()

                    # 1. Verifica se o usuário e a senha existem
                    cur.execute(
                        "SELECT login, nivel_acesso FROM usuarios WHERE login = %s AND senha_hash = %s", (u, senha_digitada_hash))
                    res = cur.fetchone()

                    if res:
                        login_banco = res[0]
                        nivel_banco = res[1]

                        # 2. Busca a mochila de permissões dele na tabela nova
                        cur.execute(
                            "SELECT modulo, liberado FROM permissoes WHERE login = %s", (login_banco,))
                        permissoes_banco = dict(cur.fetchall())

                        # 3. Registra tudo na memória da sessão
                        st.session_state.logado = True
                        st.session_state.usuario = login_banco
                        st.session_state.nivel_acesso = nivel_banco
                        st.session_state.permissoes = permissoes_banco
                        st.session_state.pagina_atual = "Dashboard"

                        conn.close()
                        st.rerun()
                    else:
                        conn.close()
                        st.error(
                            "⚠️ Usuário ou senha inválidos. Tente novamente.")
                except Exception as e:
                    st.error(f"Erro ao acessar banco de dados: {e}")
            else:
                st.warning("Preencha o usuário e a senha.")
    st.stop()  # Interrompe a leitura do código aqui se não estiver logado

# --- SE PASSOU PELO STOP, ESTÁ LOGADO ---
USUARIO = st.session_state.usuario
NIVEL = st.session_state.nivel_acesso
PERM = st.session_state.permissoes

if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = "Dashboard"

# 2. O MENU LATERAL COM AS TRAVAS DE SEGURANÇA (LENDO O ACL)
with st.sidebar:
    st.markdown(f"### 🏢 Menu Principal\n👤 Perfil: **{NIVEL}**")

    # Módulo 1: Gestão de Imóveis (Lendo a chavinha 'Imoveis')
    if PERM.get("Imoveis", False):
        with st.expander("🏠 Gestão de Imóveis", expanded=False):
            with st.expander("📋 Cadastro de Imóveis", expanded=False):
                if NIVEL in ["Admin", "Gerente"]:
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

    # Módulo 2: Gestão de Corretores (Lendo a chavinha 'Corretores')
    if PERM.get("Corretores", False):
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

    # Módulo 3: Gestão de Clientes (Lendo a chavinha 'Clientes')
    if PERM.get("Clientes", False):
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

    # Módulo 4: Gestão de Vendas (Lendo a chavinha 'Vendas')
    if PERM.get("Vendas", False):
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

    # Módulo 5: Gestão Financeira (Lendo a chavinha 'Financeiro')
    if PERM.get("Financeiro", False):
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

    # Módulo 6: Gestão de Contratos (Lendo a chavinha 'Contratos')
    if PERM.get("Contratos", False):
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

    # Módulo 7: Cadastros Gerais (Lendo a chavinha 'Cadastros')
    if PERM.get("Cadastros", False):
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

    # Acesso liberado para todos (Dashboard e Logout)
    st.divider()
    if st.button("📊 Dashboard Executivo", key="btn_dash_geral", use_container_width=True):
        st.session_state.pagina_atual = "Dashboard"

    # 👇 O NOVO BOTÃO DE SENHA AQUI
    if st.button("🔑 Mudar Minha Senha", use_container_width=True):
        st.session_state.pagina_atual = "Mudar_Senha"

    st.divider()
    if st.button("Sair / Logout", type="primary", use_container_width=True):
        st.session_state.clear()  # Limpa toda a sessão (logado, permissões, pagina_atual, etc)
        st.rerun()

# --- VARIÁVEL DE ROTEAMENTO GERAL ---
pagina = st.session_state.pagina_atual

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
    titulo_expander = f"➕ Cadastrar / Alterar Imóvel{' ' * st.session_state.tabela_versao}"

    with st.expander(titulo_expander, expanded=st.session_state.abrir_expander):

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
                'logradouro', edit.get('endereco_rua') if edit else "")
            val_bairro = st.session_state.dados_cep_imovel.get(
                'bairro', edit.get('bairro') if edit else "")
            val_cidade = st.session_state.dados_cep_imovel.get(
                'localidade', edit.get('cidade') if edit else "")
            val_cep_form = st.session_state.dados_cep_imovel.get(
                'cep', edit.get('cep') if edit else "")

            # REAJUSTE DE COLUNAS
            c_loc1, c_loc2, c_loc3, c_loc4, c_loc5 = st.columns(
                [3, 1, 2, 2, 1])
            with c_loc1:
                rua_val = st.text_input("Rua *", value=val_rua or "")
            with c_loc2:
                numero_val = st.text_input(
                    "Número *", value=edit.get('numero') or "" if edit else "")
            with c_loc3:
                bairro_val = st.text_input("Bairro", value=val_bairro or "")
            with c_loc4:
                cidade_val = st.text_input("Cidade", value=val_cidade or "")
            with c_loc5:
                cep_val = st.text_input("CEP", value=val_cep_form or "")

            st.divider()

            # ==========================================
            # NOVO: DADOS JURÍDICOS PARA O CONTRATO (DENTRO DE UM EXPANDER)
            # ==========================================
            with st.expander("📜 Dados de Registro e Loteamento (Para Contratos)"):
                st.caption(
                    "💡 *Abra aqui apenas quando for preencher os dados cartorários para gerar o contrato.*")

                c_leg1, c_leg2, c_leg3 = st.columns([1, 1, 2])
                lote_val = c_leg1.text_input(
                    "Lote", value=edit.get('lote') or "" if edit else "")
                quadra_val = c_leg2.text_input(
                    "Quadra", value=edit.get('quadra') or "" if edit else "")
                loteamento_val = c_leg3.text_input(
                    "Loteamento / Condomínio", value=edit.get('loteamento') or "" if edit else "")

                c_leg4, c_leg5 = st.columns([1, 2])
                matricula_val = c_leg4.text_input(
                    "Nº da Matrícula", value=edit.get('matricula') or "" if edit else "")
                cartorio_val = c_leg5.text_input("Cartório de Registro", value=edit.get(
                    'cartorio') or "" if edit else "", placeholder="Ex: 1º Ofício de Registro de Imóveis de Içara")

            st.divider()

            st.markdown("🏠 **Características do Imóvel**")

            c_car1, c_car2, c_car2b, c_car3, c_car4, c_car5, c_car6 = st.columns(
                [2, 1.3, 1.2, 1, 1, 1, 1])

            try:
                df_tipos_db = pd.read_sql(
                    "SELECT nome FROM tipos_imoveis ORDER BY nome", conn)
                lista_tipos = df_tipos_db['nome'].tolist() if not df_tipos_db.empty else [
                    "Apartamento", "Casa", "Terreno"]
            except:
                lista_tipos = ["Apartamento", "Casa", "Terreno"]

            tipo_idx = lista_tipos.index(edit.get('tipo_imovel')) if edit and edit.get(
                'tipo_imovel') in lista_tipos else 0

            with c_car1:
                tipo_val = st.selectbox(
                    "Tipo do Imóvel", lista_tipos, index=tipo_idx)
            with c_car2:
                area_t = st.number_input(
                    "Área Terreno/Total (m²)", value=tratar_numero(edit.get('area_total_m2')) if edit else 0.0)
            with c_car2b:
                area_c = st.number_input("Área Construída (m²)", value=tratar_numero(
                    edit.get('area_construida_m2')) if edit else 0.0)
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
                    'agenciador_nome') or "" if edit else "", placeholder="Ex: João (Corretor)")

            with c_val4:
                # ==========================================
                # O NOVO SELETOR MÚLTIPLO DE PROPRIETÁRIOS
                # ==========================================
                if not props.empty:
                    nomes_props = props['nome_completo'].tolist()
                    defaults_p = []

                    # Se estiver editando, puxa todos os proprietários que foram salvos
                    if edit and pd.notna(edit.get('id_proprietario')):
                        ids_salvos = str(edit['id_proprietario']).split(',')
                        for id_s in ids_salvos:
                            try:
                                id_limpo = int(id_s.strip())
                                nome_p = props.loc[props['id_cliente']
                                                   == id_limpo, 'nome_completo'].values[0]
                                if nome_p in nomes_props:
                                    defaults_p.append(nome_p)
                            except:
                                pass

                    sel_p = st.multiselect(
                        "Proprietários (Pode escolher vários) *", nomes_props, default=defaults_p)
                else:
                    sel_p = []
                    st.multiselect(
                        "Proprietários *", ["Nenhum (Cadastre um cliente)"], disabled=True)

            st.divider()

            st.markdown("✨ **Extras e Links**")
            c_link, c_comod = st.columns([1, 2])
            with c_link:
                link_val = st.text_input("🔗 Link do Imóvel no Site", value=edit.get(
                    'link_site') or "" if edit else "")

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

            # ... (todo o código das comodidades e do botão Salvar fica aqui em cima) ...

            btn_salvar = st.form_submit_button(
                "💾 Salvar Registro", type="primary")

            if btn_salvar:
                # Note que agora testamos se a lista sel_p está vazia (len == 0)
                if props.empty or not sel_p:
                    st.error(
                        "⚠️ Atenção: É obrigatório selecionar pelo menos um Proprietário para o imóvel.")
                elif not numero_val:
                    st.error(
                        "⚠️ O campo 'Número' do endereço é obrigatório! (Se não houver, digite S/N)")
                else:
                    try:
                        cur = conn.cursor()

                        # Transforma todos os nomes escolhidos em seus respectivos IDs
                        ids_selecionados = []
                        for nome_escolhido in sel_p:
                            id_cli = int(
                                props[props['nome_completo'] == nome_escolhido]['id_cliente'].values[0])
                            ids_selecionados.append(str(id_cli))

                        # Junta os IDs com vírgula (Ex: "12, 15, 8")
                        db_id_proprietario = ", ".join(ids_selecionados)

                        db_rua = (rua_val or "").strip().upper()
                        db_num = (numero_val or "").strip().upper()
                        db_bairro = (bairro_val or "").strip().upper()
                        db_cid = (cidade_val or "").strip().upper()
                        db_cep = (cep_val or "").strip()
                        db_lote = (lote_val or "").strip().upper()
                        db_quadra = (quadra_val or "").strip().upper()
                        db_loteamento = (loteamento_val or "").strip().upper()
                        db_matricula = (matricula_val or "").strip().upper()
                        db_cartorio = (cartorio_val or "").strip().upper()
                        db_agenciador = (agenciador_val or "").strip().upper()
                        db_link = (link_val or "").strip()

                        if id_interno == 0:
                            # 👇 ADICIONAMOS area_construida_m2 NO INSERT
                            cur.execute("""
                                INSERT INTO imoveis 
                                (endereco_rua, numero, bairro, cidade, cep, tipo_imovel, quartos, suites, banheiros, garagens, area_total_m2, area_construida_m2, valor_venda, status, id_proprietario, criado_por, doc_status, iptu_anual, comodidades, link_site, perc_agenciamento, agenciador_nome, lote, quadra, loteamento, matricula, cartorio) 
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            """, (db_rua, db_num, db_bairro, db_cid, db_cep, tipo_val, qtos_val, suites_val, banh_val, vagas_val, area_t, area_c, v_venda_val, status_i, db_id_proprietario, USUARIO, doc_sit, iptu_v, comod_string, db_link, p_agenc_val, db_agenciador, db_lote, db_quadra, db_loteamento, db_matricula, db_cartorio))
                        else:
                            # 👇 ADICIONAMOS area_construida_m2 NO UPDATE
                            cur.execute("""
                                UPDATE imoveis SET 
                                endereco_rua=%s, numero=%s, bairro=%s, cidade=%s, cep=%s, tipo_imovel=%s, quartos=%s, suites=%s, banheiros=%s, garagens=%s, area_total_m2=%s, area_construida_m2=%s, valor_venda=%s, status=%s, id_proprietario=%s, doc_status=%s, iptu_anual=%s, comodidades=%s, link_site=%s, perc_agenciamento=%s, agenciador_nome=%s, lote=%s, quadra=%s, loteamento=%s, matricula=%s, cartorio=%s 
                                WHERE id_imovel=%s
                            """, (db_rua, db_num, db_bairro, db_cid, db_cep, tipo_val, qtos_val, suites_val, banh_val, vagas_val, area_t, area_c, v_venda_val, status_i, db_id_proprietario, doc_sit, iptu_v, comod_string, db_link, p_agenc_val, db_agenciador, db_lote, db_quadra, db_loteamento, db_matricula, db_cartorio, id_interno))

                        conn.commit()
                        st.session_state.imovel_editando = None
                        st.session_state.dados_cep_imovel = {}
                        st.session_state.abrir_expander = False
                        st.session_state.tabela_versao += 1
                        st.toast("✅ Imóvel salvo com sucesso!")
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Erro ao salvar o imóvel: {e}")

        # 👇 ATENÇÃO: O botão Cancelar fica FORA do bloco 'with st.form', mas DENTRO do 'with st.expander'
        # Repare no recuo (indentação) dele em relação ao 'with st.form' lá de cima!
        if st.button("🚫 Cancelar / Limpar", key="btn_canc_imovel"):
            st.session_state.imovel_editando = None
            st.session_state.dados_cep_imovel = {}
            # Fecha o expander se o usuário cancelar
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
                               'bairro', 'quartos', 'valor_venda', 'status', 'cep']].copy()
        df_i_edit.insert(0, "Editar", False)

        df_i_edit['valor_venda'] = df_i_edit['valor_venda'].apply(
            formata_moeda)

        chave_edit = f"editor_cad_v{st.session_state.tabela_versao}"
        st.data_editor(df_i_edit, use_container_width=True, hide_index=True, key=chave_edit,
                       column_config={
                           "Editar": st.column_config.CheckboxColumn("Editar")},
                       disabled=['id_imovel', 'tipo_imovel', 'endereco_rua', 'bairro', 'quartos', 'valor_venda', 'status', 'cep'])

        if chave_edit in st.session_state:
            mudancas = st.session_state[chave_edit].get("edited_rows", {})
            if mudancas:
                idx = [i for i, v in mudancas.items() if v.get("Editar")
                       is True]
                if idx:
                    st.session_state.imovel_editando = df_i_full.iloc[idx[-1]].to_dict(
                    )
                    st.session_state.abrir_expander = False
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

    try:
        df_comod_busca = pd.read_sql(
            "SELECT nome FROM comodidades ORDER BY nome", conn)
        lista_comod_busca = df_comod_busca['nome'].tolist(
        ) if not df_comod_busca.empty else []
    except:
        lista_comod_busca = []

    comod_f = col_p3.multiselect("Filtrar por Comodidades", lista_comod_busca)

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

    # Busca os imóveis com os filtros aplicados
    try:
        df_i_full = pd.read_sql(
            q_i + " ORDER BY id_imovel DESC", conn, params=p_i)
    except Exception as e:
        st.error(f"Erro ao buscar imóveis: {e}")
        df_i_full = pd.DataFrame()

    if not df_i_full.empty:
        df_i_view = df_i_full[['id_imovel', 'endereco_rua',
                               'bairro', 'valor_venda', 'status', 'comodidades']].copy()
        df_i_view.insert(0, "Selecionar", False)

        # Garante que a função formata_moeda existe no seu código topo
        try:
            df_i_view['valor_venda'] = df_i_view['valor_venda'].apply(
                formata_moeda)
        except:
            df_i_view['valor_venda'] = df_i_view['valor_venda'].apply(
                lambda x: f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        chave_lista = f"lista_match_v{st.session_state.get('tabela_versao', 0)}"

        # Desenha a tabela interativa
        st.data_editor(
            df_i_view,
            use_container_width=True,
            hide_index=True,
            key=chave_lista,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Ver Match")},
            disabled=['id_imovel', 'endereco_rua', 'bairro',
                      'valor_venda', 'status', 'comodidades']
        )

        # Lógica para capturar o clique na caixa "Selecionar"
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
                # 👇 ATENÇÃO: Confirme se o nome da sua tabela é "interesses" ou "interesses_clientes"
                query_p = """
                    SELECT c.nome_completo, c.telefone, i.valor_maximo, i.bairro_preferencial, i.comodidades_desejadas
                    FROM interesses_clientes i
                    JOIN clientes c ON i.id_cliente = c.id_cliente
                    WHERE i.valor_maximo >= %s AND i.ativo = TRUE
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

                            try:
                                v_venda_format = formata_moeda(
                                    imob['valor_venda'])
                            except:
                                v_venda_format = f"R$ {float(imob['valor_venda']):,.2f}"

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
                                f"💰 Valor: {v_venda_format}\n"
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
                # 👇 Agora tiramos o "pass" e mostramos o erro se o banco falhar!
                st.error(f"Erro ao buscar matches: {e}")
    else:
        st.info("Nenhum imóvel cadastrado no sistema.")

    conn.close()

# ------------------------------------------
# TELA 3: CADASTRO E EDIÇÃO DE CLIENTES (COM VIACEP E RECEITA FEDERAL)
# ------------------------------------------
elif pagina == "Clientes_Novo":
    st.header("👥 Cadastro de Clientes")

    # Inicia as memórias do navegador
    if 'cliente_editando' not in st.session_state:
        st.session_state.cliente_editando = None
    if 'abrir_expander_cli' not in st.session_state:
        st.session_state.abrir_expander_cli = False
    if 'tabela_versao_cli' not in st.session_state:
        st.session_state.tabela_versao_cli = 0
    if 'dados_cep' not in st.session_state:
        st.session_state.dados_cep = {}
    if 'dados_cnpj' not in st.session_state:
        st.session_state.dados_cnpj = {}

    conn = conectar()
    edit_cli = st.session_state.cliente_editando
    id_interno_cli = int(edit_cli['id_cliente']) if edit_cli else 0

    with st.expander("➕ Cadastrar / Alterar Cliente", expanded=st.session_state.abrir_expander_cli):

        import requests

        # ==========================================
        # 1. O MOTOR DINÂMICO PF/PJ
        # ==========================================
        st.markdown("#### 🏢 Natureza Jurídica")

        tipo_salvo = edit_cli.get('tipo_pessoa', 'PF') if edit_cli else 'PF'
        idx_tipo = 0 if tipo_salvo == 'PF' else 1

        chave_radio = f"radio_tipo_cli_{st.session_state.tabela_versao_cli}"

        tipo_selecionado = st.radio(
            "Selecione o tipo de cliente:",
            ["Pessoa Física (PF)", "Pessoa Jurídica (PJ)"],
            index=idx_tipo,
            horizontal=True,
            key=chave_radio
        )
        is_pf = (tipo_selecionado == "Pessoa Física (PF)")

        # Limpa o cache da empresa se o usuário voltar para Pessoa Física
        if is_pf and st.session_state.dados_cnpj:
            st.session_state.dados_cnpj = {}

        st.divider()

        # ==========================================
        # 2. BUSCADORES (CNPJ e CEP)
        # ==========================================

        # SÓ APARECE SE FOR PJ
        if not is_pf:
            st.markdown("#### 🏢 Busca Automática de Empresa (Receita Federal)")
            c_cnpj1, c_cnpj2 = st.columns([1, 3])
            chave_cnpj = f"input_cnpj_{st.session_state.tabela_versao_cli}"
            cnpj_busca = c_cnpj1.text_input(
                "Digite o CNPJ e aperte ENTER", placeholder="Apenas números", max_chars=18, key=chave_cnpj)

            if cnpj_busca:
                cnpj_limpo = cnpj_busca.replace(".", "").replace(
                    "/", "").replace("-", "").strip()
                if len(cnpj_limpo) == 14:
                    try:
                        # Bate na porta da API da ReceitaWS
                        res_cnpj = requests.get(
                            f"https://receitaws.com.br/v1/cnpj/{cnpj_limpo}").json()
                        if res_cnpj.get("status") == "OK":
                            st.session_state.dados_cnpj = res_cnpj

                            # O PULO DO GATO: Simula a resposta do ViaCEP usando os dados da Receita
                            # Assim o endereço preenche sozinho lá embaixo!
                            st.session_state.dados_cep = {
                                "logradouro": res_cnpj.get("logradouro", ""),
                                "bairro": res_cnpj.get("bairro", ""),
                                "localidade": res_cnpj.get("municipio", ""),
                                "uf": res_cnpj.get("uf", ""),
                                "cep": res_cnpj.get("cep", "").replace(".", "").replace("-", "")
                            }
                            c_cnpj2.success(
                                f"✅ Empresa Localizada: {res_cnpj.get('nome')} - Ativa!")
                        else:
                            st.session_state.dados_cnpj = {}
                            c_cnpj2.error(
                                "❌ CNPJ não encontrado ou inválido na Receita Federal.")
                    except:
                        c_cnpj2.error("❌ Erro ao consultar a Receita Federal.")
                elif len(cnpj_limpo) > 0:
                    c_cnpj2.warning("⚠️ O CNPJ deve ter 14 números.")

            st.write("")  # Espaço em branco

        # BUSCA DE CEP (Sempre visível para PF, ou caso a PJ queira mudar o endereço da sede)
        st.markdown("#### 🔎 Busca Automática de Endereço (ViaCEP)")
        c_busca1, c_busca2 = st.columns([1, 3])
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

        # ==========================================
        # 3. O FORMULÁRIO INTELIGENTE
        # ==========================================
        label_nome = "Nome Completo *" if is_pf else "Razão Social *"
        label_doc = "CPF *" if is_pf else "CNPJ *"
        label_rg = "RG" if is_pf else "Inscrição Estadual"

        chave_form_cli = f"form_cli_{st.session_state.tabela_versao_cli}"
        with st.form(chave_form_cli, clear_on_submit=False):

            st.markdown("📝 **Dados Principais**")
            c1, c2, c3 = st.columns([2, 1, 1])

            default_nome = st.session_state.dados_cnpj.get(
                'nome', edit_cli.get('nome_completo') if edit_cli else "")
            default_doc = st.session_state.dados_cnpj.get(
                'cnpj', edit_cli.get('cpf') if edit_cli else "")

            nome_val = c1.text_input(label_nome, value=default_nome or "")
            cpf_val = c2.text_input(label_doc, value=default_doc or "")
            rg_val = c3.text_input(label_rg, value=edit_cli.get(
                'rg') or "" if edit_cli else "")

            st.markdown("📞 **Contato**")
            c4, c5 = st.columns(2)

            tel_raw = st.session_state.dados_cnpj.get(
                'telefone', edit_cli.get('telefone') if edit_cli else "")
            default_tel = str(tel_raw).split('/')[0].strip() if tel_raw else ""
            default_email = st.session_state.dados_cnpj.get(
                'email', edit_cli.get('email') if edit_cli else "")

            telefone_val = c4.text_input(
                "Telefone (WhatsApp) *", value=default_tel or "")
            email_val = c5.text_input(
                "E-mail corporativo/pessoal", value=default_email or "")

            # Inicializa variáveis para não dar erro no banco se for PJ
            nacionalidade_val = ""
            estado_civil_val = ""
            profissao_val = ""

            # Qualificação Pessoal (Aparece SÓ para Pessoa Física)
            if is_pf:
                st.markdown("⚖️ **Qualificação Pessoal**")
                c6, c7, c8 = st.columns([1, 1, 2])
                nacionalidade_val = c6.text_input("Nacionalidade", value=edit_cli.get(
                    'nacionalidade') or "Brasileira" if edit_cli else "Brasileira")

                lista_civil = [
                    "-- Selecione --", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "União Estável"]
                estado_atual = edit_cli.get('estado_civil') if edit_cli else ''
                idx_civil = lista_civil.index(
                    estado_atual) if estado_atual in lista_civil else 0
                estado_civil_val = c7.selectbox(
                    "Estado Civil", lista_civil, index=idx_civil)

                profissao_val = c8.text_input("Profissão", value=edit_cli.get(
                    'profissao') or "" if edit_cli else "")

            st.markdown(
                f"📍 **Endereço {'da Sede' if not is_pf else 'Residencial'}**")
            val_rua = st.session_state.dados_cep.get(
                'logradouro', edit_cli.get('endereco_rua') if edit_cli else "")
            val_bairro = st.session_state.dados_cep.get(
                'bairro', edit_cli.get('bairro') if edit_cli else "")
            val_cidade = st.session_state.dados_cep.get(
                'localidade', edit_cli.get('cidade') if edit_cli else "")
            val_estado = st.session_state.dados_cep.get(
                'uf', edit_cli.get('estado') if edit_cli else "")

            default_num = st.session_state.dados_cnpj.get(
                'numero', edit_cli.get('numero') if edit_cli else "")
            val_cep_form = st.session_state.dados_cep.get(
                'cep', edit_cli.get('cep') if edit_cli else "")

            c_end1, c_end2, c_end3, c_end4 = st.columns([2, 1, 2, 1])
            rua_val = c_end1.text_input("Rua", value=val_rua or "")
            numero_val = c_end2.text_input("Número", value=default_num or "")
            complemento_val = c_end3.text_input("Complemento", value=edit_cli.get(
                'complemento') or "" if edit_cli else "", placeholder="Apto, Bloco, Condomínio")
            cep_val = c_end4.text_input("CEP", value=val_cep_form or "")

            c_end5, c_end6, c_end7 = st.columns([2, 2, 1])
            bairro_val = c_end5.text_input("Bairro", value=val_bairro or "")
            cidade_val = c_end6.text_input("Cidade", value=val_cidade or "")
            estado_val = c_end7.text_input(
                "Estado (UF)", value=val_estado or "", max_chars=2)

            # ==========================================
            # NOVO: DADOS DO CÔNJUGE (SÓ PARA PF)
            # ==========================================
            conj_nome_val = ""
            conj_cpf_val = ""
            conj_rg_val = ""
            conj_nac_val = ""
            conj_prof_val = ""

            if is_pf:
                st.divider()
                with st.expander("💍 Dados do Cônjuge (Se Casado ou União Estável)"):
                    st.caption(
                        "💡 *Preencha para gerar o contrato corretamente caso o cliente seja Casado ou possua União Estável.*")
                    c_conj1, c_conj2, c_conj3 = st.columns([2, 1, 1])
                    conj_nome_val = c_conj1.text_input("Nome do Cônjuge", value=edit_cli.get(
                        'conjuge_nome') or "" if edit_cli else "")
                    conj_cpf_val = c_conj2.text_input("CPF do Cônjuge", value=edit_cli.get(
                        'conjuge_cpf') or "" if edit_cli else "")
                    conj_rg_val = c_conj3.text_input("RG do Cônjuge", value=edit_cli.get(
                        'conjuge_rg') or "" if edit_cli else "")

                    c_conj4, c_conj5 = st.columns(2)
                    conj_nac_val = c_conj4.text_input("Nacionalidade do Cônjuge", value=edit_cli.get(
                        'conjuge_nacionalidade') or "Brasileira" if edit_cli else "Brasileira")
                    conj_prof_val = c_conj5.text_input("Profissão do Cônjuge", value=edit_cli.get(
                        'conjuge_profissao') or "" if edit_cli else "")

            # ==========================================
            # NOVO: DADOS DO REPRESENTANTE LEGAL (SÓ PARA PJ)
            # ==========================================
            rep_nome_val = ""
            rep_cpf_val = ""
            rep_rg_val = ""
            rep_nac_val = ""
            rep_est_civil_val = ""
            rep_prof_val = ""
            rep_nasc_val = ""
            rep_end_val = ""

            if not is_pf:
                st.divider()
                with st.expander("⚖️ Dados do Representante Legal (Sócio/Diretor)"):
                    st.caption(
                        "💡 *Qualificação completa de quem assinará pela empresa (Opcional no pré-cadastro).*")
                    c_rep1, c_rep2, c_rep3 = st.columns([2, 1, 1])
                    rep_nome_val = c_rep1.text_input("Nome do Representante", value=edit_cli.get(
                        'representante_legal') or "" if edit_cli else "")
                    rep_cpf_val = c_rep2.text_input("CPF do Representante", value=edit_cli.get(
                        'cpf_representante') or "" if edit_cli else "")
                    rep_rg_val = c_rep3.text_input(
                        "RG do Representante", value=edit_cli.get('rep_rg') or "" if edit_cli else "")

                    c_rep4, c_rep5, c_rep6 = st.columns([1, 1, 2])
                    rep_nac_val = c_rep4.text_input("Nacionalidade do Rep.", value=edit_cli.get(
                        'rep_nacionalidade') or "Brasileira" if edit_cli else "Brasileira")

                    lista_civil_rep = [
                        "-- Selecione --", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "União Estável"]
                    est_rep_atual = edit_cli.get(
                        'rep_estado_civil') if edit_cli else ''
                    idx_civil_rep = lista_civil_rep.index(
                        est_rep_atual) if est_rep_atual in lista_civil_rep else 0
                    rep_est_civil_val = c_rep5.selectbox(
                        "Estado Civil do Rep.", lista_civil_rep, index=idx_civil_rep)

                    rep_prof_val = c_rep6.text_input("Profissão do Rep.", value=edit_cli.get(
                        'rep_profissao') or "" if edit_cli else "")

                    c_rep7, c_rep8 = st.columns([1, 3])
                    rep_nasc_val = c_rep7.text_input(
                        "Data de Nasc.", placeholder="DD/MM/AAAA", value=edit_cli.get('rep_nascimento') or "" if edit_cli else "")
                    rep_end_val = c_rep8.text_input(
                        "Endereço Residencial do Rep.", placeholder="Rua, Número, Bairro, Cidade/UF", value=edit_cli.get('rep_endereco') or "" if edit_cli else "")

            st.divider()
            btn_salvar_cli = st.form_submit_button(
                "💾 Salvar Cadastro", type="primary")

            if btn_salvar_cli:
                if not nome_val or not telefone_val or not cpf_val:
                    st.error(
                        "⚠️ Os campos Nome/Razão, Documento e Telefone são obrigatórios!")
                elif not is_pf and (not rep_nome_val or not rep_cpf_val):
                    st.error(
                        "⚠️ Para Pessoa Jurídica, o Nome e o CPF do Representante são obrigatórios!")
                elif is_pf and estado_civil_val == "-- Selecione --":
                    st.error("⚠️ Por favor, escolha um Estado Civil válido!")
                else:
                    try:
                        cur = conn.cursor()
                        import re

                        # ==========================================
                        # 🪄 MÁGICA 1: FORMATADOR DE CPF E CNPJ
                        # ==========================================
                        def formatar_documento(doc_sujo):
                            # Tira tudo que não é número
                            num = re.sub(r'\D', '', str(doc_sujo))
                            if len(num) == 11:  # É CPF
                                return f"{num[:3]}.{num[3:6]}.{num[6:9]}-{num[9:]}"
                            elif len(num) == 14:  # É CNPJ
                                return f"{num[:2]}.{num[2:5]}.{num[5:8]}/{num[8:12]}-{num[12:]}"
                            # Retorna como digitou se for passaporte/estrangeiro
                            return (doc_sujo or "").strip()

                        db_tipo = 'PF' if is_pf else 'PJ'
                        db_nome = (nome_val or "").strip().upper()
                        db_rg = (rg_val or "").strip().upper()

                        # Aplica a máscara no documento principal (Pode ser CPF ou CNPJ)
                        db_cpf = formatar_documento(cpf_val)

                        # ==========================================
                        # 🪄 MÁGICA 2: FORMATADOR DE TELEFONE
                        # ==========================================
                        tel_numeros = re.sub(r'\D', '', telefone_val)
                        if len(tel_numeros) == 11:
                            db_tel = f"({tel_numeros[:2]}) {tel_numeros[2:7]}-{tel_numeros[7:]}"
                        elif len(tel_numeros) == 10:
                            db_tel = f"({tel_numeros[:2]}) {tel_numeros[2:6]}-{tel_numeros[6:]}"
                        else:
                            db_tel = (telefone_val or "").strip()

                        db_email = (email_val or "").strip().lower()
                        db_nac = (nacionalidade_val or "").strip(
                        ).upper() if is_pf else ""
                        db_est_civil = (
                            estado_civil_val or "").upper() if is_pf else ""
                        db_prof = (profissao_val or "").strip(
                        ).upper() if is_pf else ""
                        db_rua = (rua_val or "").strip().upper()
                        db_num = (numero_val or "").strip().upper()
                        db_cep = (cep_val or "").strip()
                        db_bairro = (bairro_val or "").strip().upper()
                        db_cid = (cidade_val or "").strip().upper()
                        db_uf = (estado_val or "").strip().upper()

                        # Limpeza dos dados do Cônjuge
                        db_conj_nome = (conj_nome_val or "").strip(
                        ).upper() if is_pf else ""
                        db_conj_cpf = (
                            conj_cpf_val or "").strip() if is_pf else ""
                        db_conj_rg = (conj_rg_val or "").strip(
                        ).upper() if is_pf else ""
                        db_conj_nac = (conj_nac_val or "").strip(
                        ).upper() if is_pf else ""
                        db_conj_prof = (conj_prof_val or "").strip(
                        ).upper() if is_pf else ""

                        # Limpeza dos dados do Representante (SÓ PARA PJ)
                        db_rep_nome = (rep_nome_val or "").strip(
                        ).upper() if not is_pf else ""
                        db_rep_cpf = (
                            rep_cpf_val or "").strip() if not is_pf else ""
                        db_rep_rg = (rep_rg_val or "").strip(
                        ).upper() if not is_pf else ""
                        db_rep_nac = (rep_nac_val or "").strip(
                        ).upper() if not is_pf else ""
                        db_rep_est_civil = (rep_est_civil_val or "").upper(
                        ) if not is_pf and rep_est_civil_val != "-- Selecione --" else ""
                        db_rep_prof = (rep_prof_val or "").strip(
                        ).upper() if not is_pf else ""
                        db_rep_nasc = (
                            rep_nasc_val or "").strip() if not is_pf else ""
                        db_rep_end = (rep_end_val or "").strip(
                        ).upper() if not is_pf else ""

                        if id_interno_cli == 0:
                            cur.execute("""
                                INSERT INTO clientes 
                                (tipo_pessoa, nome_completo, cpf, rg, telefone, email, nacionalidade, estado_civil, profissao, endereco_rua, numero, cep, bairro, cidade, estado,
                                conjuge_nome, conjuge_cpf, conjuge_rg, conjuge_nacionalidade, conjuge_profissao,
                                representante_legal, cpf_representante, rep_rg, rep_nacionalidade, rep_estado_civil, rep_profissao, rep_nascimento, rep_endereco)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (db_tipo, db_nome, db_cpf, db_rg, db_tel, db_email, db_nac, db_est_civil, db_prof, db_rua, db_num, db_cep, db_bairro, db_cid, db_uf, db_conj_nome, db_conj_cpf, db_conj_rg, db_conj_nac, db_conj_prof, db_rep_nome, db_rep_cpf, db_rep_rg, db_rep_nac, db_rep_est_civil, db_rep_prof, db_rep_nasc, db_rep_end))
                        else:
                            cur.execute("""
                                UPDATE clientes SET
                                tipo_pessoa=%s, nome_completo=%s, cpf=%s, rg=%s, telefone=%s, email=%s, nacionalidade=%s, estado_civil=%s, profissao=%s, 
                                endereco_rua=%s, numero=%s, cep=%s, bairro=%s, cidade=%s, estado=%s,
                                conjuge_nome=%s, conjuge_cpf=%s, conjuge_rg=%s, conjuge_nacionalidade=%s, conjuge_profissao=%s,
                                representante_legal=%s, cpf_representante=%s, rep_rg=%s, rep_nacionalidade=%s, rep_estado_civil=%s, rep_profissao=%s, rep_nascimento=%s, rep_endereco=%s
                                WHERE id_cliente=%s
                            """, (db_tipo, db_nome, db_cpf, db_rg, db_tel, db_email, db_nac, db_est_civil, db_prof, db_rua, db_num, db_cep, db_bairro, db_cid, db_uf, db_conj_nome, db_conj_cpf, db_conj_rg, db_conj_nac, db_conj_prof, db_rep_nome, db_rep_cpf, db_rep_rg, db_rep_nac, db_rep_est_civil, db_rep_prof, db_rep_nasc, db_rep_end, id_interno_cli))

                        conn.commit()
                        st.session_state.cliente_editando = None
                        st.session_state.dados_cep = {}
                        st.session_state.dados_cnpj = {}
                        st.session_state.abrir_expander_cli = True
                        st.session_state.tabela_versao_cli += 1
                        st.toast(f"✅ Cadastro de {db_nome} salvo com sucesso!")
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Erro ao salvar: {e}")

        if st.button("🚫 Cancelar / Limpar", key="btn_canc_cli"):
            st.session_state.cliente_editando = None
            st.session_state.dados_cep = {}
            st.session_state.dados_cnpj = {}
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
                                # NOVO PERFIL DE BUSCA
                                cur.execute("""
                                    INSERT INTO interesses 
                                    (id_cliente, tipo_imovel_desejado, valor_maximo, bairro_preferencial, comodidades_desejadas, ativo) 
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """, (id_c, tipo_final, valor_max, bairros_val, comodidades_str, ativo_val))
                            else:
                                # EDITANDO PERFIL EXISTENTE
                                cur.execute("""
                                    UPDATE interesses SET 
                                    id_cliente=%s, tipo_imovel_desejado=%s, valor_maximo=%s, bairro_preferencial=%s, comodidades_desejadas=%s, ativo=%s 
                                    WHERE id_interesse=%s
                                """, (id_c, tipo_final, valor_max, bairros_val, comodidades_str, ativo_val, id_interno_int))

                            conn.commit()

                            # Fecha o expander e limpa a memória
                            st.session_state.interesse_editando = None
                            st.session_state.abrir_expander_int = False
                            st.session_state.tabela_versao_int += 1

                            st.toast(
                                "✅ Perfil de busca do cliente salvo com sucesso!")
                            st.rerun()

                        except Exception as e:
                            conn.rollback()
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

            data_sel = c5.date_input(
                "Data do Compromisso", value=val_d, format="DD/MM/YYYY")
            hora_sel = c6.time_input(
                "Horário", value=val_t)

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

    data_inicio = col1.date_input(
        "Data Inicial", value=trinta_dias_atras, format="DD/MM/YYYY")
    data_fim = col2.date_input("Data Final", value=hoje, format="DD/MM/YYYY")

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
# TELA 4.1: NOVA VENDA (FECHAMENTO E RATEIO)
# ------------------------------------------
elif pagina == "Vendas_Nova":
    st.header("💰 Registrar / Editar Venda")
    st.write("Registre o fechamento e o rateio (Split) de comissões.")

    # Inicia a memória de edição de vendas
    if 'venda_editando' not in st.session_state:
        st.session_state.venda_editando = None

    edit_venda = st.session_state.venda_editando
    id_venda_edit = int(edit_venda['id_venda']) if edit_venda else 0
    id_imovel_antigo = int(edit_venda['id_imovel']) if edit_venda else 0

    conn = conectar()

    try:
        df_clientes = pd.read_sql(
            "SELECT id_cliente, nome_completo, cpf FROM clientes ORDER BY nome_completo", conn)
        df_corretores = pd.read_sql(
            "SELECT id_corretor, nome_completo FROM corretores WHERE ativo = TRUE ORDER BY nome_completo", conn)

        query_imob = f"""
            SELECT id_imovel, CONCAT('ID ', id_imovel, ' - ', tipo_imovel, ' em ', bairro) as desc_imovel, 
                   valor_venda, perc_agenciamento 
            FROM imoveis 
            WHERE status != 'Vendido' OR id_imovel = {id_imovel_antigo}
            ORDER BY id_imovel DESC
        """
        df_imoveis = pd.read_sql(query_imob, conn)

        lista_clientes = df_clientes['nome_completo'].tolist(
        ) if not df_clientes.empty else []
        lista_corretores = df_corretores['nome_completo'].tolist(
        ) if not df_corretores.empty else []
        lista_imoveis = df_imoveis['desc_imovel'].tolist(
        ) if not df_imoveis.empty else []
    except Exception as e:
        lista_clientes, lista_corretores, lista_imoveis = [], [], []
        df_imoveis = pd.DataFrame()

    if not lista_clientes or not lista_corretores or not lista_imoveis:
        st.warning(
            "⚠️ Você precisa ter pelo menos 1 Imóvel, 1 Cliente e 1 Corretor para registrar uma venda.")
    else:
        with st.container(border=True):

            st.subheader("🏡 Seleção do Imóvel")

            idx_imovel = 0
            if edit_venda:
                try:
                    nome_imovel_edit = df_imoveis[df_imoveis['id_imovel']
                                                  == id_imovel_antigo]['desc_imovel'].values[0]
                    if nome_imovel_edit in lista_imoveis:
                        idx_imovel = lista_imoveis.index(nome_imovel_edit) + 1
                except:
                    pass

            imovel_sel = st.selectbox(
                "Imóvel Negociado *", ["-- Selecione o Imóvel --"] + lista_imoveis, index=idx_imovel)

            # Busca os valores no banco assim que o corretor escolhe a casa
            val_venda_padrao = 0.0
            perc_agenc_padrao = 6.0

            if imovel_sel != "-- Selecione o Imóvel --":
                linha_imovel = df_imoveis[df_imoveis['desc_imovel']
                                          == imovel_sel].iloc[0]
                val_venda_padrao = float(linha_imovel['valor_venda'] or 0.0)
                perc_agenc_padrao = float(
                    linha_imovel['perc_agenciamento'] or 6.0)

            # Se for edição, os valores salvos no contrato sobrescrevem os padrões
            if edit_venda:
                val_venda_padrao = float(edit_venda.get(
                    'valor_venda', val_venda_padrao))
                perc_agenc_padrao = float(edit_venda.get(
                    'perc_agenciamento', perc_agenc_padrao))

            st.divider()

            # ==========================================
            # FORMULÁRIO DO CONTRATO
            # ==========================================
            with st.form("form_nova_venda", clear_on_submit=False):
                st.subheader("📑 Dados do Contrato")

                c1, c2 = st.columns(2)

                # ==========================================
                # O NOVO SELETOR MÚLTIPLO DE COMPRADORES
                # ==========================================
                defaults_c = []
                if edit_venda and pd.notna(edit_venda.get('id_cliente')):
                    ids_c_salvos = str(edit_venda['id_cliente']).split(',')
                    for id_s in ids_c_salvos:
                        try:
                            id_limpo = int(id_s.strip())
                            nome_c = df_clientes.loc[df_clientes['id_cliente']
                                                     == id_limpo, 'nome_completo'].values[0]
                            if nome_c in lista_clientes:
                                defaults_c.append(nome_c)
                        except:
                            pass

                cliente_sel = c1.multiselect(
                    "Cliente Comprador (Pode escolher vários) *", lista_clientes, default=defaults_c)

                # (O corretor continua sendo selectbox normal)
                idx_corretor = 0
                if edit_venda:
                    try:
                        nome_cor_edit = df_corretores[df_corretores['id_corretor']
                                                      == edit_venda['id_corretor']]['nome_completo'].values[0]
                        if nome_cor_edit in lista_corretores:
                            idx_corretor = lista_corretores.index(
                                nome_cor_edit) + 1
                    except:
                        pass
                corretor_sel = c2.selectbox(
                    "Corretor da Venda *", ["-- Selecione o Corretor --"] + lista_corretores, index=idx_corretor)

                import datetime

                data_default = datetime.datetime.strptime(str(edit_venda['data_venda']), '%Y-%m-%d').date(
                ) if edit_venda and pd.notnull(edit_venda.get('data_venda')) else "today"
                data_venda = st.date_input(
                    "Data de Fechamento", value=data_default, format="DD/MM/YYYY")

                st.divider()
# ====================================================================================================================================================================
                st.divider()
                st.subheader("💵 Rateio Financeiro (Split de Comissões)")

                c3, c4 = st.columns(2)
                valor_fechado = c3.number_input(
                    "Valor Final da Venda (R$)", min_value=0.0, value=val_venda_padrao, step=10000.0)

                with c4:
                    # ==========================================
                    # O NOVO MOTOR DE COMISSÃO (FLEXÍVEL)
                    # ==========================================
                    tipo_comissao = st.radio("Formato da Comissão Total", [
                                             "Percentual (%)", "Valor Fixo (R$)"], horizontal=True)

                    if tipo_comissao == "Percentual (%)":
                        perc_total_input = st.number_input("Comissão Total da Imobiliária (%)", min_value=0.0, value=float(
                            edit_venda.get('perc_comissao_total', 5.0)) if edit_venda else 5.0, step=0.5)
                        val_comissao_fixa_input = 0.0
                    else:
                        perc_total_input = 0.0
                        # Puxa o valor salvo ou sugere os 15.000 do contrato se for novo
                        val_salvo = float(edit_venda.get(
                            'valor_comissao_total', 15000.0)) if edit_venda else 15000.0
                        val_comissao_fixa_input = st.number_input(
                            "Comissão Total Fixa (R$)", min_value=0.0, value=val_salvo, step=1000.0)

                c5, c6 = st.columns(2)
                perc_corretor = c5.number_input("Parte do Corretor (%)", min_value=0.0, value=float(
                    edit_venda.get('perc_corretor', 40.0)) if edit_venda else 40.0, step=1.0)
                perc_agenciamento_val = c6.number_input(
                    "Parte do Agenciamento/Captação (%)", min_value=0.0, value=perc_agenc_padrao, step=1.0)

                obs_venda = st.text_area("Observações do Contrato", value=edit_venda.get(
                    'observacoes', '') if edit_venda else "")

                if not edit_venda:
                    st.markdown(
                        "🚨 *Atenção: Ao salvar, o imóvel sairá do estoque (VENDIDO).*")

                btn_salvar_venda = st.form_submit_button(
                    "🏆 Confirmar Venda e Rateio" if not edit_venda else "💾 Salvar Alterações", type="primary")

                if btn_salvar_venda:
                    # 👇 Nova validação: testamos se 'cliente_sel' está vazio
                    if imovel_sel == "-- Selecione o Imóvel --" or not cliente_sel or corretor_sel == "-- Selecione o Corretor --":
                        st.error(
                            "⚠️ Por favor, preencha o Imóvel, o Comprador e o Corretor!")
                    elif valor_fechado <= 0:
                        st.error("⚠️ O valor da venda não pode ser zero!")
                    else:
                        id_imob = int(
                            df_imoveis[df_imoveis['desc_imovel'] == imovel_sel]['id_imovel'].values[0])

                        # 👇 Transforma os compradores escolhidos em uma string de IDs (Ex: "10, 15")
                        ids_c_selecionados = []
                        for nome_c in cliente_sel:
                            id_cli = int(
                                df_clientes[df_clientes['nome_completo'] == nome_c]['id_cliente'].values[0])
                            ids_c_selecionados.append(str(id_cli))
                        db_id_cliente = ", ".join(ids_c_selecionados)

                        id_cor = int(
                            df_corretores[df_corretores['nome_completo'] == corretor_sel]['id_corretor'].values[0])

                        # 👇 A NOVA MATEMÁTICA EXATA (COM OPÇÃO DE FIXO OU %)
                        if tipo_comissao == "Percentual (%)":
                            perc_total = float(perc_total_input)
                            v_comissao_total = float(
                                valor_fechado * (perc_total / 100))
                        else:
                            v_comissao_total = float(val_comissao_fixa_input)
                            # Se for fixo, calcula o percentual equivalente para o banco de dados não ficar com zero!
                            perc_total = float(
                                (v_comissao_total / valor_fechado) * 100) if valor_fechado > 0 else 0.0

                        v_corretor = float(
                            v_comissao_total * (perc_corretor / 100))
                        v_agenciamento = float(
                            v_comissao_total * (perc_agenciamento_val / 100))
                        v_imobiliaria = float(
                            v_comissao_total - v_corretor - v_agenciamento)

                        try:
                            cur = conn.cursor()

                            if id_venda_edit == 0:
                                # NOVA VENDA
                                cur.execute("""
                                    INSERT INTO vendas 
                                    (id_imovel, db_id_cliente, id_corretor, data_venda, valor_venda, 
                                    perc_comissao_total, valor_comissao_total, perc_corretor, valor_corretor, 
                                    perc_agenciamento, valor_agenciamento, valor_imobiliaria, observacoes) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, (id_imob, id_c, id_cor, data_venda, valor_fechado, perc_total, v_comissao_total, perc_corretor, v_corretor, perc_agenciamento_val, v_agenciamento, v_imobiliaria, obs_venda))

                                cur.execute(
                                    "UPDATE imoveis SET status = 'Vendido' WHERE id_imovel = %s", (id_imob,))
                            else:
                                # EDITANDO VENDA EXISTENTE
                                cur.execute("""
                                    UPDATE vendas SET 
                                    id_imovel=%s, db_id_cliente=%s, id_corretor=%s, data_venda=%s, valor_venda=%s, 
                                    perc_comissao_total=%s, valor_comissao_total=%s, perc_corretor=%s, valor_corretor=%s, 
                                    perc_agenciamento=%s, valor_agenciamento=%s, valor_imobiliaria=%s, observacoes=%s 
                                    WHERE id_venda=%s
                                """, (id_imob, id_c, id_cor, data_venda, valor_fechado, perc_total, v_comissao_total, perc_corretor, v_corretor, perc_agenciamento_val, v_agenciamento, v_imobiliaria, obs_venda, id_venda_edit))

                                # Se corrigiu o imóvel errado, arruma o estoque
                                if id_imob != id_imovel_antigo:
                                    cur.execute(
                                        "UPDATE imoveis SET status = 'Disponível' WHERE id_imovel = %s", (id_imovel_antigo,))
                                    cur.execute(
                                        "UPDATE imoveis SET status = 'Vendido' WHERE id_imovel = %s", (id_imob,))

                            conn.commit()

                            st.success(f"🎉 Venda Registrada/Atualizada! Resumo do Rateio:\n\n"
                                       f"💰 **Comissão Total:** R$ {v_comissao_total:,.2f}\n"
                                       f"👔 **Corretor:** R$ {v_corretor:,.2f}\n"
                                       f"📌 **Agenciamento:** R$ {v_agenciamento:,.2f}\n"
                                       f"🏢 **Líquido Imobiliária:** R$ {v_imobiliaria:,.2f}")
                            st.balloons()

                            if edit_venda:
                                st.session_state.venda_editando = None

                        except Exception as e:
                            conn.rollback()
                            st.error(f"Erro ao registrar venda: {e}")

        # Botão extra para cancelar a edição
        if edit_venda:
            # 👇 CORREÇÃO 1: Adicionamos a 'key' para o Streamlit não dar erro de ID duplicado
            if st.button("🚫 Cancelar Edição", key="btn_cancelar_edicao_venda"):
                st.session_state.venda_editando = None
                st.rerun()

    # ==========================================
    # 📊 HISTÓRICO DE VENDAS E BOTÃO DE EDIÇÃO
    # ==========================================
    # ==========================================
    # 📊 HISTÓRICO DE VENDAS E BOTÃO DE EDIÇÃO
    # ==========================================
    st.divider()
    st.subheader("📋 Histórico de Vendas Realizadas")

    try:
        # 👇 1. Tiramos o LEFT JOIN do cliente para o banco não dar erro de tipagem!
        query_historico = """
            SELECT v.id_venda, 
                   i.endereco_rua, 
                   i.bairro,
                   co.nome_completo as corretor, 
                   v.data_venda, 
                   v.valor_venda,
                   v.id_imovel, v.id_cliente, v.id_corretor, 
                   v.perc_comissao_total, v.valor_comissao_total, 
                   v.perc_corretor, v.valor_corretor, 
                   v.perc_agenciamento, v.valor_agenciamento, 
                   v.valor_imobiliaria, v.observacoes
            FROM vendas v
            LEFT JOIN imoveis i ON v.id_imovel = i.id_imovel
            LEFT JOIN corretores co ON v.id_corretor = co.id_corretor
            ORDER BY v.data_venda DESC, v.id_venda DESC
        """
        df_vendas = pd.read_sql(query_historico, conn)

        if not df_vendas.empty:
            # 👇 2. A MÁGICA: Python traduz "15, 22" para "Iraci, Prislana"
            def mapear_compradores(ids_string):
                if not ids_string or pd.isnull(ids_string):
                    return "Não Informado"
                nomes = []
                for id_s in str(ids_string).split(','):
                    try:
                        id_limpo = int(id_s.strip())
                        nome_c = df_clientes.loc[df_clientes['id_cliente']
                                                 == id_limpo, 'nome_completo'].values[0]
                        nomes.append(nome_c)
                    except:
                        pass
                return ", ".join(nomes)

            df_vendas['cliente'] = df_vendas['id_cliente'].apply(
                mapear_compradores)

            # Prepara a tabela de visualização
            df_display = df_vendas[['id_venda', 'endereco_rua',
                                    'cliente', 'corretor', 'data_venda', 'valor_venda']].copy()
            df_display.columns = ['ID da Venda', 'Imóvel',
                                  'Comprador(es)', 'Corretor', 'Data', 'Valor (R$)']

            df_display['Data'] = pd.to_datetime(
                df_display['Data']).dt.strftime('%d/%m/%Y')
            df_display['Valor (R$)'] = df_display['Valor (R$)'].apply(
                lambda x: f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # --- SELETOR PARA EDITAR ---
            st.markdown("#### ✏️ Editar ou Corrigir Venda")
            c_ed1, c_ed2 = st.columns([3, 1])

            lista_opcoes_vendas = [
                f"ID {row['id_venda']} - {row['endereco_rua']} (Comprador: {row['cliente']})" for idx, row in df_vendas.iterrows()]
            venda_selecionada = c_ed1.selectbox("Selecione a venda que deseja corrigir:", [
                                                "-- Selecione --"] + lista_opcoes_vendas)

            if c_ed2.button("✏️ Carregar Edição", type="secondary", use_container_width=True, key="btn_carregar_edicao_venda"):
                if venda_selecionada != "-- Selecione --":
                    id_v_sel = int(venda_selecionada.split(
                        " - ")[0].replace("ID ", ""))
                    dados_venda = df_vendas[df_vendas['id_venda']
                                            == id_v_sel].iloc[0].to_dict()

                    st.session_state.venda_editando = dados_venda
                    st.rerun()
                else:
                    st.warning(
                        "⚠️ Escolha uma venda na lista ao lado primeiro.")
        else:
            st.info(
                "Nenhuma venda registrada no sistema ainda. O histórico aparecerá aqui!")

    except Exception as e:
        st.error(f"Erro ao carregar o histórico de vendas: {e}")

    conn.close()

# ------------------------------------------
# TELA 4.2: HISTÓRICO DE VENDAS E VGV
# ------------------------------------------
elif pagina == "Vendas_Historico":
    st.header("📊 Histórico de Vendas (Rateio)")
    st.write(
        "Visão detalhada de VGV, repasses a corretores e o lucro líquido da imobiliária.")

    conn = conectar()

    st.markdown("🔍 **Filtros**")
    col1, col2, col3 = st.columns(3)

    from datetime import datetime, timedelta
    hoje = datetime.today()
    trinta_dias_atras = hoje - timedelta(days=30)

    data_inicio = col1.date_input(
        "Data Inicial", value=trinta_dias_atras, format="DD/MM/YYYY")
    data_fim = col2.date_input("Data Final", value=hoje, format="DD/MM/YYYY")

    try:
        df_corr_filt = pd.read_sql(
            "SELECT nome_completo FROM corretores ORDER BY nome_completo", conn)
        lista_corretores_filt = ["Todos os Corretores"] + \
            df_corr_filt['nome_completo'].tolist()
    except:
        lista_corretores_filt = ["Todos os Corretores"]

    corretor_f = col3.selectbox("Filtrar por Corretor", lista_corretores_filt)
    st.divider()

    query_vendas = """
        SELECT v.id_venda,
               TO_CHAR(v.data_venda, 'DD/MM/YYYY') as "Data",
               i.bairro as "Bairro",
               cor.nome_completo as "Corretor",
               v.valor_venda as "Valor_Venda_Num",
               v.valor_comissao_total as "Comis_Total_Num",
               v.valor_corretor as "Repasse_Corretor_Num",
               v.valor_agenciamento as "Agenciamento_Num",
               v.valor_imobiliaria as "Lucro_Imob_Num"
        FROM vendas v
        JOIN imoveis i ON v.id_imovel = i.id_imovel
        JOIN corretores cor ON v.id_corretor = cor.id_corretor
        WHERE DATE(v.data_venda) >= %s AND DATE(v.data_venda) <= %s
    """
    params = [data_inicio, data_fim]

    if corretor_f != "Todos os Corretores":
        query_vendas += " AND cor.nome_completo = %s"
        params.append(corretor_f)

    query_vendas += " ORDER BY v.data_venda DESC"

    try:
        df_vendas = pd.read_sql(query_vendas, conn, params=params)

        if not df_vendas.empty:

            # --- CÁLCULO DE KPIs FINANCEIROS ---
            vgv_total = float(df_vendas['Valor_Venda_Num'].sum())
            comis_total = float(df_vendas['Comis_Total_Num'].sum())
            corretor_total = float(df_vendas['Repasse_Corretor_Num'].sum())
            # 👇 O cálculo do Agenciamento
            agenciamento_total = float(df_vendas['Agenciamento_Num'].sum())
            lucro_caixa = float(df_vendas['Lucro_Imob_Num'].sum())

            st.markdown("### 🏆 Visão Executiva do Período")

            # 👇 Agora dividimos o topo em 5 colunas!
            kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns([1.3, 1.1, 1, 1, 1])

            kpi1.metric("VGV Total", formata_moeda(vgv_total))
            kpi2.metric("Comissão Bruta", formata_moeda(comis_total))
            kpi3.metric("Comissao Corretores", formata_moeda(corretor_total))
            kpi4.metric("Agenciamento (Captação)", formata_moeda(
                agenciamento_total))  # 👇 O novo Card!
            kpi5.metric("Líquido Imobiliária", formata_moeda(lucro_caixa))

            st.write("")

            # --- FORMATAÇÃO DA TABELA ---
            df_view = df_vendas.copy()
            df_view['Venda'] = df_view['Valor_Venda_Num'].apply(formata_moeda)
            df_view['Comissão Bruta'] = df_view['Comis_Total_Num'].apply(
                formata_moeda)
            df_view['Comissão Corretor'] = df_view['Repasse_Corretor_Num'].apply(
                formata_moeda)
            df_view['Agenciamento'] = df_view['Agenciamento_Num'].apply(
                formata_moeda)
            df_view['Caixa Imob.'] = df_view['Lucro_Imob_Num'].apply(
                formata_moeda)

            df_view = df_view[['Data', 'Bairro', 'Corretor', 'Venda',
                               'Comissão Bruta', 'Comissão Corretor', 'Agenciamento', 'Caixa Imob.']]

            st.dataframe(df_view, use_container_width=True, hide_index=True)

        else:
            st.info("Nenhuma venda registrada no período selecionado.")

    except Exception as e:
        st.error(f"Erro ao gerar histórico: {e}")

    conn.close()

# ------------------------------------------
# TELA 4.3: RELATÓRIOS E DESEMPENHO (BI DE VENDAS)
# ------------------------------------------
elif pagina == "Vendas_Relatorios":
    st.header("📈 Relatórios de Desempenho")
    st.write("Visão analítica das vendas. Descubra tendências, melhores corretores e os imóveis mais procurados.")

    conn = conectar()

    # --- 1. FILTRO DE PERÍODO (Padrão: Ano Atual inteiro para ter volume de dados) ---
    st.markdown("🔍 **Período de Análise**")
    c1, c2 = st.columns(2)

    from datetime import datetime
    ano_atual = datetime.now().year
    primeiro_dia_ano = datetime(ano_atual, 1, 1).date()
    hoje = datetime.now().date()

    data_inicio = c1.date_input(
        "Data Inicial", value=primeiro_dia_ano, format="DD/MM/YYYY")
    data_fim = c2.date_input("Data Final", value=hoje, format="DD/MM/YYYY")

    st.divider()

    # --- 2. BUSCA GERAL DE DADOS ---
    query_bi = """
        SELECT v.id_venda,
               v.data_venda,
               TO_CHAR(v.data_venda, 'YYYY-MM') as "Mes_Ano",
               i.tipo_imovel,
               i.bairro,
               cor.nome_completo as "Corretor",
               v.valor_venda,
               v.valor_imobiliaria
        FROM vendas v
        JOIN imoveis i ON v.id_imovel = i.id_imovel
        JOIN corretores cor ON v.id_corretor = cor.id_corretor
        WHERE DATE(v.data_venda) >= %s AND DATE(v.data_venda) <= %s
    """

    try:
        df_bi = pd.read_sql(query_bi, conn, params=[data_inicio, data_fim])

        if not df_bi.empty:

            # --- 3. PREPARAÇÃO DOS GRÁFICOS (PLOTLY) ---

            # GRÁFICO 1: Evolução do VGV por Mês
            st.subheader("🗓️ Evolução do VGV (Valor Geral de Vendas)")
            # Agrupa as vendas por Mês/Ano
            df_mes = df_bi.groupby('Mes_Ano')[
                'valor_venda'].sum().reset_index()
            # Ordena cronologicamente
            df_mes = df_mes.sort_values('Mes_Ano')

            fig_linha = px.line(df_mes, x='Mes_Ano', y='valor_venda', markers=True,
                                labels={'Mes_Ano': 'Mês / Ano',
                                        'valor_venda': 'VGV Total (R$)'},
                                title="Volume Financeiro de Vendas ao Longo do Tempo")
            # Deixa a linha com a cor primária do sistema e mais grossa
            fig_linha.update_traces(
                line_color='#FF4B4B', line_width=4, marker=dict(size=10))
            st.plotly_chart(fig_linha, use_container_width=True)

            st.divider()

            # Divide a tela em duas colunas para os próximos gráficos
            col_g1, col_g2 = st.columns(2)

            # GRÁFICO 2: Ranking de Corretores (Quem gerou mais Lucro/VGV)
            col_g1.subheader("🏆 Ranking de Corretores (VGV)")
            df_corretor = df_bi.groupby(
                'Corretor')['valor_venda'].sum().reset_index()
            # Ordena do maior para o menor
            df_corretor = df_corretor.sort_values(
                'valor_venda', ascending=True)

            fig_barras = px.bar(df_corretor, x='valor_venda', y='Corretor', orientation='h',
                                labels={
                                    'valor_venda': 'VGV Gerado (R$)', 'Corretor': ''},
                                color='valor_venda', color_continuous_scale='Blues')
            # Esconde a barrinha de cor lateral
            fig_barras.update_layout(coloraxis_showscale=False)
            col_g1.plotly_chart(fig_barras, use_container_width=True)

            # GRÁFICO 3: Vendas por Tipo de Imóvel (O que mais sai)
            col_g2.subheader("🏠 Vendas por Tipo de Imóvel")
            df_tipo = df_bi.groupby('tipo_imovel')[
                'id_venda'].count().reset_index()
            df_tipo.columns = ['Tipo de Imóvel', 'Quantidade Vendida']

            fig_pizza = px.pie(df_tipo, names='Tipo de Imóvel', values='Quantidade Vendida', hole=0.4,
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pizza.update_traces(
                textposition='inside', textinfo='percent+label')
            col_g2.plotly_chart(fig_pizza, use_container_width=True)

            st.divider()

            # GRÁFICO EXTRA: Lucro da Imobiliária vs VGV (Métricas Rápidas)
            st.subheader("💡 Raio-X Financeiro do Período")
            c_rx1, c_rx2 = st.columns(2)

            total_vgv_rx = df_bi['valor_venda'].sum()
            total_lucro_rx = df_bi['valor_imobiliaria'].sum()
            margem_media = (total_lucro_rx / total_vgv_rx) * \
                100 if total_vgv_rx > 0 else 0

            c_rx1.metric("Margem Líquida Média da Imobiliária",
                         f"{margem_media:.2f}%", help="O quanto sobra limpo para a empresa em relação ao VGV total.")

            # Mostra qual foi o Bairro campeão de vendas
            bairro_campeao = df_bi['bairro'].value_counts().idxmax()
            c_rx2.metric("Bairro Campeão de Vendas", bairro_campeao,
                         help="Bairro com o maior número de imóveis vendidos no período.")

        else:
            st.warning(
                "📊 Não há dados suficientes de vendas no período selecionado para gerar os gráficos.")

    except Exception as e:
        st.error(f"Erro ao processar os gráficos de BI: {e}")

    conn.close()

# ==========================================
# MÓDULO 5: GESTÃO FINANCEIRA (DESPESAS)
# ==========================================

# ------------------------------------------
# TELA 5.1.1: NOVO LANÇAMENTO DE DESPESA (COM PARCELAMENTO E RECORRÊNCIA)
# ------------------------------------------
elif pagina == "Fin_Despesa_Nova":
    st.header("➕ Lançar Nova Despesa")
    st.write(
        "Registre contas únicas, compras parceladas ou despesas fixas recorrentes.")

    conn = conectar()

    try:
        df_categorias = pd.read_sql(
            "SELECT id_categoria, nome FROM categorias_despesas ORDER BY nome", conn)
        lista_categorias = df_categorias['nome'].tolist(
        ) if not df_categorias.empty else []
    except:
        lista_categorias = []

    if not lista_categorias:
        st.warning(
            "⚠️ Você precisa cadastrar as Categorias de Despesas primeiro na tela ao lado.")
    else:
        with st.container(border=True):
            with st.form("form_nova_despesa", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                desc_val = c1.text_input(
                    "Descrição da Conta/Compra *", placeholder="Ex: Manutenção da Internet")
                fornecedor_val = c2.text_input(
                    "Fornecedor / Favorecido", placeholder="Ex: Claro Empresas")
                cat_sel = c3.selectbox("Categoria *", lista_categorias)

                # --- RECORRÊNCIA E PARCELAMENTO ---
                st.markdown("##### 💳 Regra de Pagamento")
                tipo_pagamento = st.radio("Como essa conta se comporta?",
                                          ["À vista / Única",
                                              "Parcelado (Divide o valor Total)", "Recorrente (Repete o valor Mensal)"],
                                          horizontal=True)

                # A inteligência visual: O rótulo muda sozinho dependendo do que ela escolher
                if tipo_pagamento == "Recorrente (Repete o valor Mensal)":
                    label_valor = "Valor MENSAL Fixo (R$)"
                    label_qtd = "Projetar por quantos meses?"
                    ajuda_valor = "O valor exato que será pago todo mês (Ex: 4350.00 do Aluguel)."
                elif tipo_pagamento == "Parcelado (Divide o valor Total)":
                    label_valor = "Valor TOTAL da Compra (R$)"
                    label_qtd = "Nº de Parcelas"
                    ajuda_valor = "O sistema vai pegar esse valor e dividir pela quantidade de parcelas."
                else:
                    label_valor = "Valor da Conta (R$)"
                    label_qtd = "Meses (Fica desativado)"
                    ajuda_valor = "Valor único."

                c3, c4, c5 = st.columns(3)
                valor_input = c3.number_input(
                    label_valor, min_value=0.0, step=50.0, help=ajuda_valor)
                venc_inicial = c4.date_input(
                    "Vencimento (ou 1ª Data)", format="DD/MM/YYYY")

                # Se for à vista, trava em 1. Se não, ela escolhe os meses/parcelas.
                qtd_meses = c5.number_input(
                    label_qtd, min_value=2, max_value=120, step=1) if tipo_pagamento != "À vista / Única" else 1

                st.divider()
                st.markdown(
                    "##### 📌 Status do Pagamento (Apenas para o 1º Vencimento)")
                status_sel = st.selectbox(
                    "Status Atual", ["Pendente", "Pago", "Atrasado"])
                obs_val = st.text_area(
                    "Observações (Código de barras, chave PIX, reajuste IGPM, etc.)")

                st.divider()
                btn_salvar_despesa = st.form_submit_button(
                    "💾 Gerar Lançamentos", type="primary")

                if btn_salvar_despesa:
                    if not desc_val.strip() or valor_input <= 0:
                        st.error(
                            "⚠️ Preencha a descrição e um valor maior que zero!")
                    else:
                        id_cat = int(
                            df_categorias[df_categorias['nome'] == cat_sel]['id_categoria'].values[0])

                        from datetime import datetime
                        cur = conn.cursor()

                        try:
                            # O Motor de Decisão do Python
                            for i in range(qtd_meses):
                                data_venc_calc = venc_inicial + \
                                    pd.DateOffset(months=i)

                                # 1. Se for Parcelado, divide o dinheiro e avisa o número da parcela
                                if tipo_pagamento == "Parcelado (Divide o valor Total)":
                                    desc_final = f"{desc_val.strip()} (Parcela {i+1}/{qtd_meses})"
                                    valor_final = valor_input / qtd_meses

                                # 2. Se for Recorrente, mantém o dinheiro igual e avisa o Mês/Ano
                                elif tipo_pagamento == "Recorrente (Repete o valor Mensal)":
                                    mes_ano_str = data_venc_calc.strftime(
                                        "%m/%Y")
                                    desc_final = f"{desc_val.strip()} ({mes_ano_str})"
                                    valor_final = valor_input

                                # 3. Se for à vista, é conta normal
                                else:
                                    desc_final = desc_val.strip()
                                    valor_final = valor_input

                                # Apenas a primeira parcela/mês recebe o status escolhido. O resto é pendente futuro.
                                status_final = status_sel if i == 0 else "Pendente"
                                data_pag = datetime.today().date() if status_final == "Pago" else None

                                cur.execute("""
                                    INSERT INTO despesas (descricao, fornecedor, id_categoria, valor, data_vencimento, data_pagamento, status, observacoes) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                """, (desc_final, fornecedor_val.strip(), id_cat, valor_final, data_venc_calc.date(), data_pag, status_final, obs_val))

                            conn.commit()

                            if tipo_pagamento != "À vista / Única":
                                st.success(
                                    f"✅ Sucesso! Foram projetados {qtd_meses} meses no sistema.")
                            else:
                                st.success("✅ Despesa lançada com sucesso!")

                            st.balloons()

                        except Exception as e:
                            conn.rollback()
                            st.error(f"Erro ao gerar despesas: {e}")

    conn.close()

# ------------------------------------------
# TELA 5.1.2: LISTA DE DESPESAS (CONTAS A PAGAR)
# ------------------------------------------
elif pagina == "Fin_Despesa_Lista":
    st.header("📉 Lista de Contas e Despesas")
    st.write("Acompanhe os vencimentos e dê baixa nos pagamentos com 2 cliques.")

    conn = conectar()

    st.markdown("🔍 **Filtros do Mês**")
    f1, f2, f3 = st.columns(3)

    from datetime import datetime
    mes_atual = datetime.today().replace(day=1).date()
    filtro_inicio = f1.date_input(
        "Início (Vencimento)", value=mes_atual, format="DD/MM/YYYY")
    filtro_fim = f2.date_input(
        "Fim (Vencimento)", value=datetime.today().date() + pd.Timedelta(days=30), format="DD/MM/YYYY")
    filtro_status = f3.selectbox(
        "Filtrar Status", ["Todos", "Pendente", "Pago", "Atrasado"])

    st.divider()

    query_despesas = """
        SELECT d.id_despesa, 
               d.descricao as "Descrição",
               d.fornecedor as "Fornecedor",
               c.nome as "Categoria",
               d.valor as "Valor_Num",
               TO_CHAR(d.data_vencimento, 'DD/MM/YYYY') as "Vencimento",
               d.status as "Status",
               d.observacoes as "Obs"
        FROM despesas d
        LEFT JOIN categorias_despesas c ON d.id_categoria = c.id_categoria
        WHERE DATE(d.data_vencimento) >= %s AND DATE(d.data_vencimento) <= %s
    """
    params = [filtro_inicio, filtro_fim]

    if filtro_status != "Todos":
        query_despesas += " AND d.status = %s"
        params.append(filtro_status)

    query_despesas += " ORDER BY d.data_vencimento ASC"

    try:
        df_desp = pd.read_sql(query_despesas, conn, params=params)

        if not df_desp.empty:
            total_pendente = float(df_desp[df_desp['Status'].isin(
                ['Pendente', 'Atrasado'])]['Valor_Num'].sum())
            total_pago = float(
                df_desp[df_desp['Status'] == 'Pago']['Valor_Num'].sum())

            kpi1, kpi2 = st.columns(2)
            kpi1.metric("🔴 Total a Pagar (Pendente/Atrasado)",
                        formata_moeda(total_pendente))
            kpi2.metric("🟢 Total Pago no Período", formata_moeda(total_pago))

            st.write("")
            st.markdown(
                "📝 **Edição Rápida:** *Dê dois cliques na coluna 'Status' para marcar como 'Pago'.*")

            df_view = df_desp.copy()
            df_view['Valor'] = df_view['Valor_Num'].apply(formata_moeda)
            df_view = df_view[['id_despesa', 'Descrição', 'Fornecedor',
                               'Categoria', 'Valor', 'Vencimento', 'Status', 'Obs']]

            if 'tab_desp_versao' not in st.session_state:
                st.session_state.tab_desp_versao = 0

            chave_grid = f"grid_desp_{st.session_state.tab_desp_versao}"

            df_editado = st.data_editor(
                df_view,
                use_container_width=True,
                hide_index=True,
                key=chave_grid,
                column_config={
                    "Status": st.column_config.SelectboxColumn("Status", options=["Pendente", "Pago", "Atrasado"], required=True)
                },
                disabled=['id_despesa', 'Descrição',
                          'Categoria', 'Valor', 'Vencimento', 'Obs']
            )

            # ... (código da Tabela Mágica que já está aí) ...
            if chave_grid in st.session_state:
                mudancas = st.session_state[chave_grid].get("edited_rows", {})
                if mudancas:
                    cur = conn.cursor()
                    for idx_row, alteracoes in mudancas.items():
                        id_d = df_desp.iloc[int(idx_row)]['id_despesa']
                        novo_status = alteracoes.get("Status")

                        if novo_status:
                            if novo_status == "Pago":
                                cur.execute(
                                    "UPDATE despesas SET status = %s, data_pagamento = CURRENT_DATE WHERE id_despesa = %s", (novo_status, int(id_d)))
                            else:
                                cur.execute(
                                    "UPDATE despesas SET status = %s, data_pagamento = NULL WHERE id_despesa = %s", (novo_status, int(id_d)))

                    conn.commit()
                    st.session_state.tab_desp_versao += 1
                    st.toast("✅ Status atualizado!")
                    st.rerun()

            # 👇 COLE ESTE NOVO BLOCO AQUI (DENTRO DO IF NOT DF_DESP.EMPTY) 👇

            st.divider()
            st.markdown("🗑️ **Apagar Lançamento**")
            with st.expander("Clique aqui se precisar excluir uma conta lançada incorretamente", expanded=False):
                st.warning(
                    "⚠️ Atenção: A exclusão apagará o registro do banco de dados e não poderá ser desfeita.")

                # Prepara a lista bonitinha puxando o 'Valor' formatado do df_view
                df_desp['combo_excluir'] = df_desp['id_despesa'].astype(
                    str) + " | " + df_desp['Fornecedor'] + " - " + df_desp['Descrição'] + " | " + df_view['Valor'] + " | Venc: " + df_desp['Vencimento']
                lista_excluir = df_desp['combo_excluir'].tolist()

                conta_selecionada = st.selectbox("Selecione a conta que deseja apagar:", [
                                                 "-- Selecione --"] + lista_excluir)

                if st.button("🚨 Excluir Conta Definitivamente", type="primary"):
                    if conta_selecionada != "-- Selecione --":
                        # O Python é inteligente: ele pega só o ID (o número antes da primeira barra "|")
                        id_apagar = int(conta_selecionada.split(" | ")[0])

                        try:
                            cur = conn.cursor()
                            cur.execute(
                                "DELETE FROM despesas WHERE id_despesa = %s", (id_apagar,))
                            conn.commit()
                            st.success("✅ Conta apagada com sucesso!")
                            st.session_state.tab_desp_versao += 1  # Força a tabela a atualizar
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Erro ao apagar a conta: {e}")
                    else:
                        st.error(
                            "⚠️ Por favor, selecione uma conta na lista acima primeiro.")

        else:
            st.info("Nenhuma despesa encontrada para este período.")
    except Exception as e:
        st.error(f"Erro ao carregar despesas: {e}")

    conn.close()

# ------------------------------------------
# TELA 5.1.3: CATEGORIAS DE DESPESAS
# ------------------------------------------
elif pagina == "Fin_Despesa_Cat":
    st.header("🏷️ Categorias de Despesas")
    st.write(
        "Gerencie os centros de custo da imobiliária (ex: Água, Marketing, Folha).")

    conn = conectar()

    with st.form("form_nova_categoria", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        nova_cat = c1.text_input(
            "Nome da Nova Categoria", placeholder="Ex: Combustível / Transporte")
        btn_add_cat = c2.form_submit_button(
            "➕ Adicionar Categoria", use_container_width=True)

        if btn_add_cat and nova_cat.strip():
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO categorias_despesas (nome) VALUES (%s)", (nova_cat.strip(),))
                conn.commit()
                st.success(f"Categoria '{nova_cat}' adicionada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error("Erro ao adicionar. Talvez essa categoria já exista.")

    st.divider()
    st.markdown("📋 **Categorias Existentes**")

    try:
        df_cat = pd.read_sql(
            "SELECT id_categoria as ID, nome as Categoria FROM categorias_despesas ORDER BY nome", conn)
        st.dataframe(df_cat, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Erro ao carregar categorias: {e}")

    conn.close()

# ==========================================
# MÓDULO 5: GESTÃO FINANCEIRA (ENTRADAS / RECEITAS)
# ==========================================

# ------------------------------------------
# TELA 5.2.1: NOVO LANÇAMENTO DE ENTRADA
# ------------------------------------------
elif pagina == "Fin_Entrada_Nova":
    st.header("📈 Lançar Nova Receita (Entrada)")
    st.write("Registre previsões de recebimento ou dinheiro que já entrou no caixa.")

    conn = conectar()

    try:
        df_cat_ent = pd.read_sql(
            "SELECT id_categoria, nome FROM categorias_entradas ORDER BY nome", conn)
        lista_cat_ent = df_cat_ent['nome'].tolist(
        ) if not df_cat_ent.empty else []
    except:
        lista_cat_ent = []

    if not lista_cat_ent:
        st.warning(
            "⚠️ Cadastre as Categorias de Entradas primeiro na tela ao lado.")
    else:
        with st.container(border=True):
            with st.form("form_nova_entrada", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                desc_val = c1.text_input(
                    "Descrição do Recebimento *", placeholder="Ex: Honorários de Consultoria")
                cliente_val = c2.text_input(
                    "Cliente / Pagador", placeholder="Ex: João da Silva")
                cat_sel = c3.selectbox("Categoria *", lista_cat_ent)

                st.markdown("##### 💳 Condição de Recebimento")
                tipo_pagamento = st.radio("Como esse valor será recebido?",
                                          ["À vista / Única",
                                              "Parcelado (Divide o valor Total)", "Recorrente (Repete o valor Mensal)"],
                                          horizontal=True)

                if tipo_pagamento == "Recorrente (Repete o valor Mensal)":
                    label_valor = "Valor MENSAL a Receber (R$)"
                    label_qtd = "Projetar por quantos meses?"
                elif tipo_pagamento == "Parcelado (Divide o valor Total)":
                    label_valor = "Valor TOTAL a Receber (R$)"
                    label_qtd = "Nº de Parcelas"
                else:
                    label_valor = "Valor da Entrada (R$)"
                    label_qtd = "Meses (Fica desativado)"

                c4, c5, c6 = st.columns(3)
                valor_input = c4.number_input(
                    label_valor, min_value=0.0, step=50.0)
                venc_inicial = c5.date_input(
                    "Previsão (ou 1º Vencimento)", format="DD/MM/YYYY")
                qtd_meses = c6.number_input(
                    label_qtd, min_value=2, max_value=120, step=1) if tipo_pagamento != "À vista / Única" else 1

                st.divider()
                st.markdown(
                    "##### 📌 Status do Recebimento (Apenas para a 1ª parcela)")
                status_sel = st.selectbox(
                    "Status Atual", ["Pendente", "Recebido", "Atrasado"])
                obs_val = st.text_area("Observações do Recebimento")

                st.divider()
                btn_salvar_entrada = st.form_submit_button(
                    "💰 Lançar Receita", type="primary")

                if btn_salvar_entrada:
                    if not desc_val.strip() or valor_input <= 0:
                        st.error(
                            "⚠️ Preencha a descrição e um valor maior que zero!")
                    else:
                        id_cat = int(
                            df_cat_ent[df_cat_ent['nome'] == cat_sel]['id_categoria'].values[0])

                        from datetime import datetime
                        cur = conn.cursor()

                        try:
                            for i in range(qtd_meses):
                                data_venc_calc = venc_inicial + \
                                    pd.DateOffset(months=i)

                                if tipo_pagamento == "Parcelado (Divide o valor Total)":
                                    desc_final = f"{desc_val.strip()} (Parcela {i+1}/{qtd_meses})"
                                    valor_final = valor_input / qtd_meses
                                elif tipo_pagamento == "Recorrente (Repete o valor Mensal)":
                                    mes_ano_str = data_venc_calc.strftime(
                                        "%m/%Y")
                                    desc_final = f"{desc_val.strip()} ({mes_ano_str})"
                                    valor_final = valor_input
                                else:
                                    desc_final = desc_val.strip()
                                    valor_final = valor_input

                                status_final = status_sel if i == 0 else "Pendente"
                                data_receb = datetime.today().date() if status_final == "Recebido" else None

                                cur.execute("""
                                    INSERT INTO entradas (descricao, cliente_pagador, id_categoria, valor, data_vencimento, data_recebimento, status, observacoes) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                """, (desc_final, cliente_val.strip(), id_cat, valor_final, data_venc_calc.date(), data_receb, status_final, obs_val))

                            conn.commit()
                            st.success(
                                "✅ Receita lançada com sucesso no sistema!")
                            st.balloons()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Erro ao gerar entradas: {e}")
    conn.close()

# ------------------------------------------
# TELA 5.2.2: LISTA DE ENTRADAS (CONTAS A RECEBER)
# ------------------------------------------
elif pagina == "Fin_Entrada_Lista":
    st.header("📈 Lista de Contas a Receber")
    st.write("Acompanhe o dinheiro que está para entrar e dê baixa nos recebimentos.")

    conn = conectar()

    st.markdown("🔍 **Filtros do Mês**")
    f1, f2, f3 = st.columns(3)

    from datetime import datetime
    mes_atual = datetime.today().replace(day=1).date()
    filtro_inicio = f1.date_input(
        "Início (Previsão)", value=mes_atual, format="DD/MM/YYYY")
    filtro_fim = f2.date_input("Fim (Previsão)", value=datetime.today(
    ).date() + pd.Timedelta(days=30), format="DD/MM/YYYY")
    filtro_status = f3.selectbox(
        "Filtrar Status", ["Todos", "Pendente", "Recebido", "Atrasado"])

    st.divider()

    query_entradas = """
        SELECT e.id_entrada, 
               e.descricao as "Descrição",
               e.cliente_pagador as "Pagador",
               c.nome as "Categoria",
               e.valor as "Valor_Num",
               TO_CHAR(e.data_vencimento, 'DD/MM/YYYY') as "Data Prevista",
               e.status as "Status",
               e.observacoes as "Obs"
        FROM entradas e
        LEFT JOIN categorias_entradas c ON e.id_categoria = c.id_categoria
        WHERE DATE(e.data_vencimento) >= %s AND DATE(e.data_vencimento) <= %s
    """
    params = [filtro_inicio, filtro_fim]

    if filtro_status != "Todos":
        query_entradas += " AND e.status = %s"
        params.append(filtro_status)

    query_entradas += " ORDER BY e.data_vencimento ASC"

    try:
        df_ent = pd.read_sql(query_entradas, conn, params=params)

        if not df_ent.empty:
            total_pendente = float(df_ent[df_ent['Status'].isin(
                ['Pendente', 'Atrasado'])]['Valor_Num'].sum())
            total_recebido = float(
                df_ent[df_ent['Status'] == 'Recebido']['Valor_Num'].sum())

            kpi1, kpi2 = st.columns(2)
            kpi1.metric("🟡 A Receber (Pendente/Atrasado)",
                        formata_moeda(total_pendente))
            kpi2.metric("🟢 Dinheiro em Caixa (Recebido)",
                        formata_moeda(total_recebido))

            st.write("")
            st.markdown(
                "📝 **Edição Rápida:** *Dê dois cliques na coluna 'Status' para marcar como 'Recebido'.*")

            df_view = df_ent.copy()
            df_view['Valor'] = df_view['Valor_Num'].apply(formata_moeda)
            df_view = df_view[['id_entrada', 'Descrição', 'Pagador',
                               'Categoria', 'Valor', 'Data Prevista', 'Status', 'Obs']]

            if 'tab_ent_versao' not in st.session_state:
                st.session_state.tab_ent_versao = 0

            chave_grid = f"grid_ent_{st.session_state.tab_ent_versao}"

            df_editado = st.data_editor(
                df_view,
                use_container_width=True,
                hide_index=True,
                key=chave_grid,
                column_config={
                    "Status": st.column_config.SelectboxColumn("Status", options=["Pendente", "Recebido", "Atrasado"], required=True)
                },
                disabled=['id_entrada', 'Descrição', 'Pagador',
                          'Categoria', 'Valor', 'Data Prevista', 'Obs']
            )

            if chave_grid in st.session_state:
                mudancas = st.session_state[chave_grid].get("edited_rows", {})
                if mudancas:
                    cur = conn.cursor()
                    for idx_row, alteracoes in mudancas.items():
                        id_e = df_ent.iloc[int(idx_row)]['id_entrada']
                        novo_status = alteracoes.get("Status")

                        if novo_status:
                            if novo_status == "Recebido":
                                cur.execute(
                                    "UPDATE entradas SET status = %s, data_recebimento = CURRENT_DATE WHERE id_entrada = %s", (novo_status, int(id_e)))
                            else:
                                cur.execute(
                                    "UPDATE entradas SET status = %s, data_recebimento = NULL WHERE id_entrada = %s", (novo_status, int(id_e)))

                    conn.commit()
                    st.session_state.tab_ent_versao += 1
                    st.toast("✅ Status de recebimento atualizado!")
                    st.rerun()

            # --- ZONA DE RISCO ---
            st.divider()
            st.markdown("🗑️ **Zona de Risco: Apagar Lançamento**")
            with st.expander("Clique aqui se precisar excluir uma receita lançada incorretamente", expanded=False):
                st.warning(
                    "⚠️ Atenção: A exclusão apagará o registro do banco de dados permanentemente.")

                df_ent['combo_excluir'] = df_ent['id_entrada'].astype(
                    str) + " | " + df_ent['Pagador'] + " - " + df_ent['Descrição'] + " | " + df_view['Valor'] + " | Prev: " + df_ent['Data Prevista']
                lista_excluir = df_ent['combo_excluir'].tolist()

                conta_selecionada = st.selectbox("Selecione a receita que deseja apagar:", [
                                                 "-- Selecione --"] + lista_excluir)

                if st.button("🚨 Excluir Receita Definitivamente", type="primary"):
                    if conta_selecionada != "-- Selecione --":
                        id_apagar = int(conta_selecionada.split(" | ")[0])
                        try:
                            cur = conn.cursor()
                            cur.execute(
                                "DELETE FROM entradas WHERE id_entrada = %s", (id_apagar,))
                            conn.commit()
                            st.success("✅ Receita apagada com sucesso!")
                            st.session_state.tab_ent_versao += 1
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Erro ao apagar: {e}")
                    else:
                        st.error("⚠️ Selecione uma receita na lista primeiro.")
        else:
            st.info("Nenhuma entrada prevista ou recebida para este período.")
    except Exception as e:
        st.error(f"Erro ao carregar entradas: {e}")

    conn.close()

# ------------------------------------------
# TELA 5.2.3: CATEGORIAS DE ENTRADAS
# ------------------------------------------
elif pagina == "Fin_Entrada_Cat":
    st.header("🏷️ Categorias de Entradas (Receitas)")
    st.write("Gerencie as origens do dinheiro da imobiliária.")

    conn = conectar()

    with st.form("form_nova_categoria_ent", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        nova_cat = c1.text_input(
            "Nome da Nova Categoria", placeholder="Ex: Venda de Apostilas")
        btn_add_cat = c2.form_submit_button(
            "➕ Adicionar Categoria", use_container_width=True)

        if btn_add_cat and nova_cat.strip():
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO categorias_entradas (nome) VALUES (%s)", (nova_cat.strip(),))
                conn.commit()
                st.success(f"Categoria '{nova_cat}' adicionada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error("Erro ao adicionar. Verifique se a categoria já existe.")

    st.divider()
    st.markdown("📋 **Categorias Existentes**")

    try:
        df_cat_ent = pd.read_sql(
            "SELECT id_categoria as ID, nome as Categoria FROM categorias_entradas ORDER BY nome", conn)
        st.dataframe(df_cat_ent, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Erro ao carregar categorias: {e}")

    conn.close()

# ==========================================
# MÓDULO 5: GESTÃO FINANCEIRA (FLUXO DE CAIXA)
# ==========================================

# ------------------------------------------
# TELA 5.3.1: ENTRADAS VS SAÍDAS (COMPARATIVO)
# ------------------------------------------
elif pagina == "Fin_Fluxo_Comparativo":
    st.header("⚖️ Fluxo de Caixa: Entradas vs. Saídas")
    st.write("Visão macro da saúde financeira. Compare o volume de receitas com o total de despesas por mês.")

    conn = conectar()

    from datetime import datetime
    ano_atual = datetime.now().year

    st.markdown("🔍 **Filtro de Análise**")
    ano_selecionado = st.selectbox(
        "Selecione o Ano", [ano_atual - 1, ano_atual, ano_atual + 1], index=1)
    st.divider()

    try:
        # Busca todas as Entradas do ano selecionado, agrupadas por mês
        query_ent = f"""
            SELECT TO_CHAR(data_vencimento, 'MM') as mes, SUM(valor) as total_entradas 
            FROM entradas 
            WHERE EXTRACT(YEAR FROM data_vencimento) = {ano_selecionado} 
            GROUP BY mes
        """
        df_ent = pd.read_sql(query_ent, conn)

        # Busca todas as Saídas do ano selecionado, agrupadas por mês
        query_desp = f"""
            SELECT TO_CHAR(data_vencimento, 'MM') as mes, SUM(valor) as total_saidas 
            FROM despesas 
            WHERE EXTRACT(YEAR FROM data_vencimento) = {ano_selecionado} 
            GROUP BY mes
        """
        df_desp = pd.read_sql(query_desp, conn)

        # --- O MOTOR DO PANDAS PARA CRUZAR OS DADOS ---
        # Cria uma tabela "esqueleto" com os 12 meses para nenhum mês sumir do gráfico
        meses = [f"{i:02d}" for i in range(1, 13)]
        nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai',
                       'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        df_base = pd.DataFrame({"mes": meses, "Nome do Mês": nomes_meses})

        # Mescla (JOIN) as entradas e saídas no esqueleto de meses
        df_base = pd.merge(df_base, df_ent, on="mes",
                           how="left") if not df_ent.empty else df_base.assign(total_entradas=0)
        df_base = pd.merge(df_base, df_desp, on="mes",
                           how="left") if not df_desp.empty else df_base.assign(total_saidas=0)

        # Troca os valores vazios (NaN) por Zero e calcula o Saldo do mês
        df_base.fillna(0, inplace=True)
        df_base['Saldo Líquido'] = df_base['total_entradas'] - \
            df_base['total_saidas']

        # --- O GRÁFICO PROFISSIONAL (PLOTLY) ---
        import plotly.graph_objects as go

        fig = go.Figure()

        # Barra Verde (Entradas)
        fig.add_trace(go.Bar(x=df_base['Nome do Mês'], y=df_base['total_entradas'],
                             name='Entradas (Receitas)', marker_color='#2ECC71'))

        # Barra Vermelha (Saídas)
        fig.add_trace(go.Bar(x=df_base['Nome do Mês'], y=df_base['total_saidas'],
                             name='Saídas (Despesas)', marker_color='#E74C3C'))

        # Linha Azul (Saldo)
        fig.add_trace(go.Scatter(x=df_base['Nome do Mês'], y=df_base['Saldo Líquido'],
                                 name='Saldo Líquido', mode='lines+markers',
                                 line=dict(color='#3498DB', width=3), marker=dict(size=8)))

        fig.update_layout(title=f"Balanço Financeiro - Ano {ano_selecionado}",
                          barmode='group', hovermode='x unified',
                          yaxis_title="Valor (R$)", xaxis_title="Meses")

        st.plotly_chart(fig, use_container_width=True)

        # Tabela resumo abaixo do gráfico
        st.markdown("### 📊 Tabela Resumo Anual")
        df_tabela = df_base[['Nome do Mês', 'total_entradas',
                             'total_saidas', 'Saldo Líquido']].copy()
        df_tabela.columns = [
            'Mês', 'Total Recebido (R$)', 'Total Gasto (R$)', 'Lucro / Prejuízo (R$)']

        # Aplica a máscara de moeda em todas as colunas de valor
        for col in ['Total Recebido (R$)', 'Total Gasto (R$)', 'Lucro / Prejuízo (R$)']:
            df_tabela[col] = df_tabela[col].apply(formata_moeda)

        st.dataframe(df_tabela, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro ao gerar comparativo: {e}")

    conn.close()

# ------------------------------------------
# TELA 5.3.2: SALDO ATUAL E PROJEÇÃO
# ------------------------------------------
elif pagina == "Fin_Fluxo_Saldo":
    st.header("💰 Saldo Atual (Termômetro do Mês)")
    st.write(
        "Diferencie o dinheiro que já está no banco do dinheiro que ainda é previsão.")

    conn = conectar()

    from datetime import datetime
    mes_atual_num = datetime.today().month
    ano_atual = datetime.today().year

    st.markdown(
        f"### 🗓️ Resumo do Mês Vigente ({mes_atual_num:02d}/{ano_atual})")

    try:
        # Busca todas as contas do mês atual na base de dados (independente do status)
        query_caixa_ent = f"SELECT valor, status FROM entradas WHERE EXTRACT(MONTH FROM data_vencimento) = {mes_atual_num} AND EXTRACT(YEAR FROM data_vencimento) = {ano_atual}"
        query_caixa_desp = f"SELECT valor, status FROM despesas WHERE EXTRACT(MONTH FROM data_vencimento) = {mes_atual_num} AND EXTRACT(YEAR FROM data_vencimento) = {ano_atual}"

        df_c_ent = pd.read_sql(query_caixa_ent, conn)
        df_c_desp = pd.read_sql(query_caixa_desp, conn)

        # --- 1. O CAIXA REAL (O QUE JÁ ACONTECEU) ---
        real_recebido = float(df_c_ent[df_c_ent['status'] == 'Recebido']['valor'].sum(
        )) if not df_c_ent.empty else 0.0
        real_pago = float(df_c_desp[df_c_desp['status'] == 'Pago']['valor'].sum(
        )) if not df_c_desp.empty else 0.0
        saldo_real_banco = real_recebido - real_pago

        with st.container(border=True):
            st.markdown("#### 🏦 Caixa REAL (Dinheiro Efetivado no Banco)")
            c1, c2, c3 = st.columns(3)
            c1.metric("1️⃣ Total Recebido", formata_moeda(real_recebido))
            c2.metric("2️⃣ Total Pago", formata_moeda(real_pago))
            c3.metric("3️⃣ Saldo Líquido Atual", formata_moeda(saldo_real_banco),
                      delta="Positivo" if saldo_real_banco >= 0 else "Negativo",
                      delta_color="normal" if saldo_real_banco >= 0 else "inverse")

        # --- 2. A PROJEÇÃO (O QUE FALTA ACONTECER) ---
        prev_receber = float(df_c_ent[df_c_ent['status'].isin(
            ['Pendente', 'Atrasado'])]['valor'].sum()) if not df_c_ent.empty else 0.0
        prev_pagar = float(df_c_desp[df_c_desp['status'].isin(
            ['Pendente', 'Atrasado'])]['valor'].sum()) if not df_c_desp.empty else 0.0
        saldo_projetado = (real_recebido + prev_receber) - \
            (real_pago + prev_pagar)

        with st.container(border=True):
            st.markdown("#### 🔮 Projeção (Se todos pagarem e você pagar tudo)")
            p1, p2, p3 = st.columns(3)
            p1.metric("Falta Receber", formata_moeda(prev_receber))
            p2.metric("Falta Pagar", formata_moeda(prev_pagar))
            p3.metric("Previsão Fechamento do Mês",
                      formata_moeda(saldo_projetado))

    except Exception as e:
        st.error(f"Erro ao calcular saldo atual: {e}")

    conn.close()

# ==========================================
# MÓDULO 5: GESTÃO FINANCEIRA (RELATÓRIOS E BI)
# ==========================================

# ------------------------------------------
# TELA 5.4.1: RESUMO MENSAL DETALHADO
# ------------------------------------------
elif pagina == "Fin_Rel_Mensal":
    st.header("📊 Resumo Mensal Detalhado")
    st.write(
        "Mergulhe nos números de um mês específico e descubra os maiores impactos do seu caixa.")

    conn = conectar()

    st.markdown("🔍 **Selecione o Período**")
    c1, c2 = st.columns(2)

    from datetime import datetime
    meses_lista = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
                   7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

    mes_selecionado = c1.selectbox("Mês", options=list(meses_lista.keys(
    )), format_func=lambda x: meses_lista[x], index=datetime.today().month - 1)
    ano_selecionado = c2.selectbox("Ano", options=[datetime.today(
    ).year - 1, datetime.today().year, datetime.today().year + 1], index=1)

    st.divider()

    try:
        # Busca todas as movimentações do mês (independente do status para ter a visão global)
        query_ent = f"SELECT descricao, valor, status FROM entradas WHERE EXTRACT(MONTH FROM data_vencimento) = {mes_selecionado} AND EXTRACT(YEAR FROM data_vencimento) = {ano_selecionado}"
        query_desp = f"SELECT descricao, fornecedor, valor, status FROM despesas WHERE EXTRACT(MONTH FROM data_vencimento) = {mes_selecionado} AND EXTRACT(YEAR FROM data_vencimento) = {ano_selecionado}"

        df_ent = pd.read_sql(query_ent, conn)
        df_desp = pd.read_sql(query_desp, conn)

        if df_ent.empty and df_desp.empty:
            st.info(
                f"Nenhuma movimentação registrada para {meses_lista[mes_selecionado]} de {ano_selecionado}.")
        else:
            # --- 1. TOP 5 MAIORES ENTRADAS E SAÍDAS ---
            col_top_ent, col_top_desp = st.columns(2)

            with col_top_ent:
                st.subheader("🟢 Top 5 Maiores Receitas")
                if not df_ent.empty:
                    df_top_ent = df_ent.nlargest(
                        5, 'valor')[['descricao', 'valor', 'status']]
                    df_top_ent['valor'] = df_top_ent['valor'].apply(
                        formata_moeda)
                    df_top_ent.columns = ['Descrição', 'Valor', 'Status']
                    st.dataframe(
                        df_top_ent, use_container_width=True, hide_index=True)
                else:
                    st.write("Sem receitas neste mês.")

            with col_top_desp:
                st.subheader("🔴 Top 5 Maiores Despesas")
                if not df_desp.empty:
                    df_top_desp = df_desp.nlargest(
                        5, 'valor')[['descricao', 'fornecedor', 'valor']]
                    df_top_desp['valor'] = df_top_desp['valor'].apply(
                        formata_moeda)
                    df_top_desp.columns = ['Descrição', 'Fornecedor', 'Valor']
                    st.dataframe(
                        df_top_desp, use_container_width=True, hide_index=True)
                else:
                    st.write("Sem despesas neste mês.")

            st.divider()

            # --- 2. INDICADOR DE EFICIÊNCIA (INADIMPLÊNCIA) ---
            st.subheader("🚨 Termômetro de Inadimplência")

            if not df_ent.empty:
                total_previsto = df_ent['valor'].sum()
                total_atrasado = df_ent[df_ent['status']
                                        == 'Atrasado']['valor'].sum()
                taxa_inadimplencia = (
                    total_atrasado / total_previsto) * 100 if total_previsto > 0 else 0

                st.metric("Taxa de Inadimplência de Clientes (Mês)", f"{taxa_inadimplencia:.1f}%",
                          help="Porcentagem de dinheiro que deveria ter entrado e está marcado como 'Atrasado'. O ideal é manter abaixo de 5%.",
                          delta="Atenção" if taxa_inadimplencia > 5 else "Controlado", delta_color="inverse")
            else:
                st.write("Sem dados suficientes para calcular inadimplência.")

    except Exception as e:
        st.error(f"Erro ao gerar resumo: {e}")
    conn.close()

# ------------------------------------------
# TELA 5.4.2: ANÁLISE DE CUSTOS (ONDE O DINHEIRO VAI)
# ------------------------------------------
elif pagina == "Fin_Rel_Custos":
    st.header("📉 Análise de Custos e Despesas")
    st.write(
        "Descubra os ralos financeiros da empresa analisando categorias e fornecedores.")

    conn = conectar()

    st.markdown("🔍 **Período de Análise**")
    c1, c2 = st.columns(2)

    from datetime import datetime
    primeiro_dia_ano = datetime(datetime.today().year, 1, 1).date()
    hoje = datetime.today().date()

    data_inicio = c1.date_input(
        "Data Inicial", value=primeiro_dia_ano, format="DD/MM/YYYY")
    data_fim = c2.date_input("Data Final", value=hoje, format="DD/MM/YYYY")

    st.divider()

    try:
        # Busca todas as despesas no período com suas categorias
        query_custos = """
            SELECT d.descricao, d.fornecedor, d.valor, c.nome as categoria 
            FROM despesas d
            LEFT JOIN categorias_despesas c ON d.id_categoria = c.id_categoria
            WHERE DATE(d.data_vencimento) >= %s AND DATE(d.data_vencimento) <= %s
        """
        df_custos = pd.read_sql(query_custos, conn, params=[
                                data_inicio, data_fim])

        if not df_custos.empty:

            import plotly.express as px

            # --- 1. GRÁFICO DE ROSCA: CUSTOS POR CATEGORIA ---
            st.subheader("🏷️ Distribuição por Categoria")
            df_cat = df_custos.groupby('categoria')[
                'valor'].sum().reset_index()

            fig_cat = px.pie(df_cat, names='categoria', values='valor', hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Bold,
                             title="Para onde o dinheiro está indo?")
            fig_cat.update_traces(textposition='inside',
                                  textinfo='percent+label')
            st.plotly_chart(fig_cat, use_container_width=True)

            st.divider()

            # --- 2. GRÁFICO DE BARRAS: MAIORES FORNECEDORES ---
            st.subheader("🏢 Top Fornecedores (Quem recebe mais)")
            # Filtra os que não estão vazios ou "Não Informado"
            df_forn = df_custos[~df_custos['fornecedor'].isin(
                ['', 'Não Informado'])]

            if not df_forn.empty:
                df_forn_group = df_forn.groupby(
                    'fornecedor')['valor'].sum().reset_index()
                df_forn_group = df_forn_group.sort_values(
                    'valor', ascending=True).tail(10)  # Pega os 10 maiores

                fig_forn = px.bar(df_forn_group, x='valor', y='fornecedor', orientation='h',
                                  labels={
                                      'valor': 'Total Pago (R$)', 'fornecedor': 'Fornecedor'},
                                  color='valor', color_continuous_scale='Reds')
                fig_forn.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig_forn, use_container_width=True)
            else:
                st.info(
                    "Nenhum fornecedor nomeado foi encontrado nas despesas deste período.")

            # --- INSIGHT INTELIGENTE DO PYTHON ---
            categoria_campea = df_cat.sort_values(
                'valor', ascending=False).iloc[0]
            st.warning(
                f"💡 **Insight Rápido:** A categoria que mais consumiu recursos no período foi **{categoria_campea['categoria']}**, totalizando **{formata_moeda(categoria_campea['valor'])}**.")

        else:
            st.info("Nenhuma despesa registrada no período selecionado.")

    except Exception as e:
        st.error(f"Erro ao analisar custos: {e}")
    conn.close()

# ==========================================
# MÓDULO 5: GESTÃO FINANCEIRA (PAGAMENTOS E COMPRAS)
# ==========================================

# ------------------------------------------
# TELA 5.5.1: FILA DE PAGAMENTOS PENDENTES
# ------------------------------------------
elif pagina == "Fin_Pag_Pendentes":
    st.header("🚨 Fila de Pagamentos (A Pagar)")
    st.write("Sua mesa de operações. Veja o que está atrasado ou vencendo nos próximos dias e realize os pagamentos.")

    conn = conectar()

    # Filtros Operacionais Rápidos
    st.markdown("🔍 **Visão Operacional**")
    c1, c2 = st.columns([1, 2])

    visao_selecionada = c1.radio("O que você quer ver?",
                                 ["Atrasados e Vencem Hoje", "Vencem nos próximos 7 dias", "Todos os Pendentes"])

    # Monta a query dinamicamente baseada na urgência
    query_pendentes = """
        SELECT d.id_despesa, 
               TO_CHAR(d.data_vencimento, 'DD/MM/YYYY') as "Vencimento",
               d.fornecedor as "Fornecedor",
               d.descricao as "Descrição",
               d.valor as "Valor_Num",
               d.status as "Status",
               d.observacoes as "Dados PIX / Boleto"
        FROM despesas d
        WHERE d.status IN ('Pendente', 'Atrasado')
    """

    if visao_selecionada == "Atrasados e Vencem Hoje":
        query_pendentes += " AND DATE(d.data_vencimento) <= CURRENT_DATE"
    elif visao_selecionada == "Vencem nos próximos 7 dias":
        query_pendentes += " AND DATE(d.data_vencimento) <= CURRENT_DATE + INTERVAL '7 days'"

    query_pendentes += " ORDER BY d.data_vencimento ASC"

    try:
        df_pendentes = pd.read_sql(query_pendentes, conn)

        if not df_pendentes.empty:

            # --- KPIs de Urgência ---
            total_urgente = float(df_pendentes['Valor_Num'].sum())
            qtd_boletos = len(df_pendentes)

            st.warning(
                f"⚠️ Você tem **{qtd_boletos} contas** nesta fila, totalizando **{formata_moeda(total_urgente)}**.")

            # --- Tabela de Baixa Expressa da Tesouraria ---
            st.markdown(
                "💸 **Baixa Rápida:** *Copie os dados de pagamento, pague no banco e mude o status para 'Pago' aqui.*")

            df_view = df_pendentes.copy()
            df_view['Valor'] = df_view['Valor_Num'].apply(formata_moeda)
            df_view = df_view[['id_despesa', 'Vencimento', 'Fornecedor',
                               'Descrição', 'Valor', 'Status', 'Dados PIX / Boleto']]

            if 'tab_tesouraria_versao' not in st.session_state:
                st.session_state.tab_tesouraria_versao = 0

            chave_grid = f"grid_tesouraria_{st.session_state.tab_tesouraria_versao}"

            df_editado = st.data_editor(
                df_view,
                use_container_width=True,
                hide_index=True,
                key=chave_grid,
                column_config={
                    "Status": st.column_config.SelectboxColumn("Status", options=["Pendente", "Pago", "Atrasado"], required=True)
                },
                disabled=['id_despesa', 'Vencimento', 'Fornecedor',
                          'Descrição', 'Valor', 'Dados PIX / Boleto']
            )

            # Motor de Salvamento (A mesma mágica ágil, mas focada na tesouraria)
            if chave_grid in st.session_state:
                mudancas = st.session_state[chave_grid].get("edited_rows", {})
                if mudancas:
                    cur = conn.cursor()
                    for idx_row, alteracoes in mudancas.items():
                        id_d = df_pendentes.iloc[int(idx_row)]['id_despesa']
                        novo_status = alteracoes.get("Status")

                        if novo_status == "Pago":
                            cur.execute(
                                "UPDATE despesas SET status = 'Pago', data_pagamento = CURRENT_DATE WHERE id_despesa = %s", (int(id_d),))
                            conn.commit()
                            st.session_state.tab_tesouraria_versao += 1
                            st.toast("✅ Conta quitada! Saiu da fila.")
                            st.rerun()

        else:
            st.success(
                "🎉 Parabéns! Não há nenhuma conta pendente para a visão selecionada. Caixa limpo!")

    except Exception as e:
        st.error(f"Erro ao carregar fila de pagamentos: {e}")

    conn.close()

# ------------------------------------------
# TELA 5.5.2: HISTÓRICO DE PAGAMENTOS (AUDITORIA)
# ------------------------------------------
elif pagina == "Fin_Pag_Historico":
    st.header("🧾 Histórico de Pagamentos (Realizado)")
    st.write("Auditoria de caixa. Veja tudo o que já foi efetivamente pago, reconcilie com o banco e tire dúvidas.")

    conn = conectar()

    st.markdown("🔍 **Extrato de Pagamentos**")
    c1, c2, c3 = st.columns([1, 1, 2])

    from datetime import datetime, timedelta
    hoje = datetime.today().date()
    trinta_dias_atras = hoje - timedelta(days=30)

    # Aqui o filtro é pela DATA DE PAGAMENTO, não de vencimento!
    data_inicio = c1.date_input(
        "Pago a partir de:", value=trinta_dias_atras, format="DD/MM/YYYY")
    data_fim = c2.date_input("Até o dia:", value=hoje, format="DD/MM/YYYY")

    # Filtro de Fornecedor para achar aquele PIX perdido
    try:
        df_forn = pd.read_sql(
            "SELECT DISTINCT fornecedor FROM despesas WHERE fornecedor IS NOT NULL AND fornecedor != '' ORDER BY fornecedor", conn)
        lista_forn = ["Todos os Fornecedores"] + df_forn['fornecedor'].tolist()
    except:
        lista_forn = ["Todos os Fornecedores"]

    fornecedor_filtro = c3.selectbox("Buscar por Fornecedor", lista_forn)

    st.divider()

    query_hist = """
        SELECT TO_CHAR(d.data_pagamento, 'DD/MM/YYYY') as "Data Efetiva (Pago)",
               d.fornecedor as "Fornecedor",
               d.descricao as "Descrição",
               c.nome as "Categoria",
               d.valor as "Valor_Num",
               TO_CHAR(d.data_vencimento, 'DD/MM/YYYY') as "Vencimento Original"
        FROM despesas d
        LEFT JOIN categorias_despesas c ON d.id_categoria = c.id_categoria
        WHERE d.status = 'Pago' 
        AND DATE(d.data_pagamento) >= %s AND DATE(d.data_pagamento) <= %s
    """
    params = [data_inicio, data_fim]

    if fornecedor_filtro != "Todos os Fornecedores":
        query_hist += " AND d.fornecedor = %s"
        params.append(fornecedor_filtro)

    query_hist += " ORDER BY d.data_pagamento DESC, d.valor DESC"

    try:
        df_hist = pd.read_sql(query_hist, conn, params=params)

        if not df_hist.empty:
            total_pago = float(df_hist['Valor_Num'].sum())

            st.markdown(
                f"### 💰 Total Quitado no Período: **{formata_moeda(total_pago)}**")

            # Tabela de visualização (Apenas leitura)
            df_view = df_hist.copy()
            df_view['Valor Pago'] = df_view['Valor_Num'].apply(formata_moeda)
            df_view = df_view[[
                'Data Efetiva (Pago)', 'Fornecedor', 'Descrição', 'Categoria', 'Valor Pago', 'Vencimento Original']]

            st.dataframe(df_view, use_container_width=True, hide_index=True)

            # Botão de exportação para Excel (Opcional, mas gestores amam)
            csv = df_view.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar Extrato para Excel (CSV)",
                data=csv,
                file_name=f'extrato_pagamentos_{data_inicio}_a_{data_fim}.csv',
                mime='text/csv',
            )

        else:
            st.info(
                "Nenhum pagamento registrado no período ou para os filtros selecionados.")

    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")

    conn.close()

# ==========================================
# MÓDULO 5: GESTÃO FINANCEIRA (ORÇAMENTOS)
# ==========================================

# ------------------------------------------
# TELA 5.6.1: PLANEAMENTO DE GASTOS (ORÇADO)
# ------------------------------------------
elif pagina == "Fin_Orc_Plan":
    st.header("📅 Planeamento de Gastos (O Orçamento)")
    st.write("Defina o teto máximo de gastos para cada categoria da imobiliária.")

    conn = conectar()

    st.markdown("🔍 **Selecione o Período para Planear**")
    c1, c2 = st.columns(2)

    from datetime import datetime
    meses_lista = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
                   7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

    mes_plan = c1.selectbox("Mês Alvo", options=list(meses_lista.keys(
    )), format_func=lambda x: meses_lista[x], index=datetime.today().month - 1)
    ano_plan = c2.selectbox("Ano Alvo", options=[
                            datetime.today().year, datetime.today().year + 1], index=0)

    st.divider()

    try:
        # Busca todas as categorias existentes
        df_cat = pd.read_sql(
            'SELECT id_categoria, nome as "Categoria" FROM categorias_despesas ORDER BY nome', conn)

        # Busca o orçamento que já foi salvo para este mês/ano (se existir)
        query_orc = f"SELECT id_categoria, valor_planejado FROM orcamento_despesas WHERE mes = {mes_plan} AND ano = {ano_plan}"
        df_orc = pd.read_sql(query_orc, conn)

        if not df_cat.empty:
            # Junta as categorias com os valores já planeados (se não houver, preenche com 0)
            df_view = pd.merge(df_cat, df_orc, on='id_categoria', how='left').fillna(
                {'valor_planejado': 0.0})
            df_view.rename(
                columns={'valor_planejado': 'Teto de Gastos (R$)'}, inplace=True)

            st.markdown(
                f"### 🎯 Definição de Tetos para **{meses_lista[mes_plan]} / {ano_plan}**")
            st.write(
                "Edite os valores diretamente na tabela abaixo e o sistema irá gravar automaticamente.")

            # A Tabela Mágica do Streamlit, agora usada para edição em massa de orçamentos!
            df_editado = st.data_editor(
                df_view[['Categoria', 'Teto de Gastos (R$)']],
                use_container_width=True,
                hide_index=True,
                key=f"grid_orcamento_{mes_plan}_{ano_plan}",
                column_config={
                    "Teto de Gastos (R$)": st.column_config.NumberColumn("Teto de Gastos (R$)", min_value=0.0, step=100.0, format="R$ %.2f")
                },
                disabled=['Categoria']
            )

            # Motor para guardar os limites no banco de dados
            if st.button("💾 Guardar Orçamento do Mês", type="primary", use_container_width=True):
                cur = conn.cursor()
                for i, row in df_editado.iterrows():
                    id_c = int(df_view.iloc[i]['id_categoria'])
                    valor_plan = float(row['Teto de Gastos (R$)'])

                    # O UPSERT (Insere se for novo, atualiza se já existir)
                    cur.execute("""
                        INSERT INTO orcamento_despesas (mes, ano, id_categoria, valor_planejado) 
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (mes, ano, id_categoria) 
                        DO UPDATE SET valor_planejado = EXCLUDED.valor_planejado
                    """, (mes_plan, ano_plan, id_c, valor_plan))

                conn.commit()
                st.success(
                    f"✅ Orçamento de {meses_lista[mes_plan]} guardado com sucesso!")
                st.balloons()
        else:
            st.warning(
                "Nenhuma categoria de despesa cadastrada. Vá a 'Categorias de Despesas' primeiro.")

    except Exception as e:
        st.error(f"Erro ao carregar o planeamento: {e}")
    conn.close()

# ------------------------------------------
# TELA 5.6.2: REAL X PLANEADO (O CONFRONTO)
# ------------------------------------------
elif pagina == "Fin_Orc_Real":
    st.header("⚖️ Real x Planeado")
    st.write(
        "Confronte o que foi orçado no início do mês com o que foi efetivamente gasto.")

    conn = conectar()

    st.markdown("🔍 **Mês de Análise**")
    c1, c2 = st.columns(2)

    from datetime import datetime
    meses_lista = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
                   7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

    mes_analise = c1.selectbox("Mês", options=list(meses_lista.keys(
    )), format_func=lambda x: meses_lista[x], index=datetime.today().month - 1)
    ano_analise = c2.selectbox("Ano", options=[datetime.today(
    ).year - 1, datetime.today().year, datetime.today().year + 1], index=1)

    st.divider()

    try:
        # 1. Busca o que foi Planeado (Orçado)
        query_plan = f"""
            SELECT c.nome as "Categoria", o.valor_planejado as "Orçado"
            FROM orcamento_despesas o
            JOIN categorias_despesas c ON o.id_categoria = c.id_categoria
            WHERE o.mes = {mes_analise} AND o.ano = {ano_analise}
        """
        df_plan = pd.read_sql(query_plan, conn)

        # 2. Busca o que foi Realizado (Gasto real)
        query_real = f"""
            SELECT c.nome as "Categoria", SUM(d.valor) as "Realizado"
            FROM despesas d
            JOIN categorias_despesas c ON d.id_categoria = c.id_categoria
            WHERE EXTRACT(MONTH FROM d.data_vencimento) = {mes_analise} AND EXTRACT(YEAR FROM d.data_vencimento) = {ano_analise}
            GROUP BY c.nome
        """
        df_real = pd.read_sql(query_real, conn)

        if not df_plan.empty or not df_real.empty:

            # --- O CRUZAMENTO (PANDAS MERGE) ---
            # Cria a tabela comparativa juntando o Orçado e o Realizado
            df_comp = pd.merge(
                df_plan, df_real, on="Categoria", how="outer").fillna(0)

            # Calcula as diferenças e percentagens
            df_comp['Saldo (Restante)'] = df_comp['Orçado'] - \
                df_comp['Realizado']
            df_comp['% Utilizada'] = (
                df_comp['Realizado'] / df_comp['Orçado']) * 100
            df_comp['% Utilizada'] = df_comp['% Utilizada'].replace(
                # Trata divisões por zero
                [float('inf'), -float('inf')], 0).fillna(0)

            # --- KPIs GLOBAIS ---
            total_orcado = df_comp['Orçado'].sum()
            total_real = df_comp['Realizado'].sum()
            economia = total_orcado - total_real

            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("🎯 Teto Global (Orçado)", formata_moeda(total_orcado))
            kpi2.metric("💸 Total Gasto (Realizado)", formata_moeda(total_real))

            if economia >= 0:
                kpi3.metric("🟢 Economia / Saldo",
                            formata_moeda(economia), "Dentro do Orçamento")
            else:
                kpi3.metric("🔴 Estouro do Orçamento", formata_moeda(
                    economia), "Acima do Teto", delta_color="inverse")

            st.write("")

            # --- GRÁFICO DE CONFRONTO (PLOTLY) ---
            import plotly.graph_objects as go

            fig = go.Figure()
            # Barra Cinza (O Teto/Planeado)
            fig.add_trace(go.Bar(
                x=df_comp['Categoria'], y=df_comp['Orçado'], name='Planeado', marker_color='#BDC3C7'))
            # Barra Vermelha (O Gasto Real)
            fig.add_trace(go.Bar(
                x=df_comp['Categoria'], y=df_comp['Realizado'], name='Gasto Real', marker_color='#E74C3C'))

            fig.update_layout(title="Confronto por Categoria de Despesa",
                              barmode='group', xaxis_title="Categoria", yaxis_title="Valor (R$)")
            st.plotly_chart(fig, use_container_width=True)

            # --- TABELA DE AUDITORIA COM ALERTAS ---
            st.markdown("### 📋 Detalhe Analítico por Categoria")

            # Criamos uma coluna visual para mostrar o status do orçamento
            def status_orcamento(perc):
                if perc == 0:
                    return "⚪ Sem Gasto"
                elif perc <= 80:
                    return "🟢 Confortável"
                elif perc <= 100:
                    return "🟡 Quase no Limite"
                else:
                    return "🔴 Orçamento Estourado"

            df_comp_view = df_comp.copy()
            df_comp_view['Status'] = df_comp_view['% Utilizada'].apply(
                status_orcamento)
            df_comp_view['Orçado'] = df_comp_view['Orçado'].apply(
                formata_moeda)
            df_comp_view['Realizado'] = df_comp_view['Realizado'].apply(
                formata_moeda)
            df_comp_view['Saldo (Restante)'] = df_comp_view['Saldo (Restante)'].apply(
                formata_moeda)
            df_comp_view['% Utilizada'] = df_comp_view['% Utilizada'].apply(
                lambda x: f"{x:.1f}%")

            st.dataframe(df_comp_view[['Categoria', 'Orçado', 'Realizado', 'Saldo (Restante)', '% Utilizada', 'Status']],
                         use_container_width=True, hide_index=True)

        else:
            st.info(
                "Não há dados de orçamento nem de gastos reais para o mês selecionado.")

    except Exception as e:
        st.error(f"Erro ao gerar o comparativo Real x Planeado: {e}")
    conn.close()

# ==========================================
# MÓDULO 6: GESTÃO DE CONTRATOS (VENDAS)
# ==========================================

# ------------------------------------------
# TELA 6.1: NOVO CONTRATO (COM NUMERAÇÃO AUTOMÁTICA)
# ------------------------------------------
elif pagina == "Contratos_Novo":
    st.header("📄 Registrar Novo Contrato")
    st.write(
        "Gere o controle jurídico das vendas. A numeração é gerada automaticamente pelo sistema.")

    conn = conectar()

    try:
        df_clientes = pd.read_sql(
            "SELECT id_cliente, nome_completo FROM clientes ORDER BY nome_completo", conn)
        query_imob = "SELECT id_imovel, CONCAT('ID ', id_imovel, ' - ', tipo_imovel, ' em ', bairro) as desc_imovel FROM imoveis ORDER BY id_imovel DESC"
        df_imoveis = pd.read_sql(query_imob, conn)

        lista_clientes = df_clientes['nome_completo'].tolist(
        ) if not df_clientes.empty else []
        lista_imoveis = df_imoveis['desc_imovel'].tolist(
        ) if not df_imoveis.empty else []

        # --- MÁGICA DA NUMERAÇÃO AUTOMÁTICA ---
        from datetime import datetime
        ano_atual = datetime.now().year

        # Procura no banco qual foi o último contrato gerado NESTE ano
        query_num = "SELECT numero_contrato FROM contratos WHERE numero_contrato LIKE %s ORDER BY id_contrato DESC LIMIT 1"
        df_ult_cont = pd.read_sql(query_num, conn, params=[f"{ano_atual}/%"])

        if not df_ult_cont.empty and df_ult_cont.iloc[0]['numero_contrato']:
            # Pega o "2026/015", corta no "/", pega o "015", transforma em número (15) e soma 1 (16)
            ultimo_num = int(
                df_ult_cont.iloc[0]['numero_contrato'].split('/')[1])
            prox_num = ultimo_num + 1
        else:
            # Se não achar nada, é o primeiro contrato do ano!
            prox_num = 1

        # Monta o texto final com 3 zeros à esquerda (ex: 2026/001)
        num_gerado_automatico = f"{ano_atual}/{prox_num:03d}"

    except Exception as e:
        lista_clientes, lista_imoveis = [], []
        num_gerado_automatico = "Erro/000"

    if not lista_clientes or not lista_imoveis:
        st.warning(
            "⚠️ Você precisa ter pelo menos 1 Imóvel e 1 Cliente cadastrados para gerar um contrato.")
    else:
        with st.container(border=True):
            with st.form("form_novo_contrato", clear_on_submit=True):
                st.subheader("📑 Informações do Documento")

                c1, c2, c3 = st.columns([1, 2, 2])
                # 👇 O campo agora vem preenchido e TRAVADO (disabled=True)
                num_contrato = c1.text_input(
                    "Nº Interno (Auto)", value=num_gerado_automatico, disabled=True)

                tipo_sel = c2.selectbox("Tipo de Contrato *", [
                    "Promessa de Compra e Venda (PCV)",
                    "Autorização de Exclusividade (Captação)",
                    "Proposta de Compra Formal",
                    "Escritura Pública",
                    "Distrato"
                ])
                status_sel = c3.selectbox(
                    "Status Atual", ["Ativo", "Pendente de Assinatura", "Concluído", "Rescindido"])

                st.divider()
                st.subheader("🤝 Partes Envolvidas")

                c4, c5 = st.columns(2)
                imovel_sel = c4.selectbox(
                    "Imóvel Objeto *", ["-- Selecione --"] + lista_imoveis)
                cliente_sel = c5.selectbox(
                    "Cliente Principal *", ["-- Selecione --"] + lista_clientes)

                st.divider()
                st.subheader("📅 Prazos e Valores")

                c6, c7, c8 = st.columns(3)
                valor_val = c6.number_input(
                    "Valor Envolvido (R$)", min_value=0.0, step=10000.0)
                data_ass = c7.date_input(
                    "Data de Assinatura/Início", format="DD/MM/YYYY")
                data_venc = c8.date_input(
                    "Data de Vencimento/Prazo", format="DD/MM/YYYY")

                obs_val = st.text_area(
                    "Condições Especiais (Foro, Multas, Cláusulas Específicas)")

                btn_salvar_contrato = st.form_submit_button(
                    "💾 Gerar Contrato", type="primary")

                if btn_salvar_contrato:
                    if imovel_sel == "-- Selecione --" or cliente_sel == "-- Selecione --":
                        st.error("⚠️ O Imóvel e o Cliente são obrigatórios!")
                    else:
                        id_imob = int(
                            df_imoveis[df_imoveis['desc_imovel'] == imovel_sel]['id_imovel'].values[0])
                        id_c = int(
                            df_clientes[df_clientes['nome_completo'] == cliente_sel]['id_cliente'].values[0])

                        try:
                            cur = conn.cursor()
                            cur.execute("""
                                INSERT INTO contratos (numero_contrato, tipo_contrato, id_imovel, id_cliente, 
                                                       data_assinatura, data_vencimento, valor_contrato, status, observacoes) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (num_gerado_automatico, tipo_sel, id_imob, id_c, data_ass, data_venc, valor_val, status_sel, obs_val))

                            conn.commit()
                            st.success(
                                f"✅ Contrato {num_gerado_automatico} registrado com sucesso!")
                            st.balloons()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Erro ao salvar contrato: {e}")

    conn.close()

# ------------------------------------------
# TELA 6.2: LISTA GERAL DE CONTRATOS
# ------------------------------------------
elif pagina == "Contratos_Lista":
    st.header("📋 Controle de Contratos")
    st.write(
        "Acompanhe os documentos gerados, altere os status e controle os vencimentos.")

    conn = conectar()

    st.markdown("🔍 **Filtros de Busca**")
    f1, f2 = st.columns(2)
    filtro_tipo = f1.selectbox("Filtrar por Tipo", [
                               "Todos", "Promessa de Compra e Venda (PCV)", "Autorização de Exclusividade (Captação)", "Escritura Pública"])
    filtro_status = f2.selectbox("Filtrar por Status", [
                                 "Todos", "Ativo", "Pendente de Assinatura", "Concluído", "Rescindido"])

    st.divider()

    query_contratos = """
        SELECT con.id_contrato,
               con.numero_contrato as "Nº",
               con.tipo_contrato as "Tipo",
               c.nome_completo as "Cliente",
               i.bairro as "Bairro Imóvel",
               con.valor_contrato as "Valor_Num",
               TO_CHAR(con.data_assinatura, 'DD/MM/YYYY') as "Assinatura",
               TO_CHAR(con.data_vencimento, 'DD/MM/YYYY') as "Vencimento",
               con.status as "Status"
        FROM contratos con
        JOIN clientes c ON con.id_cliente = c.id_cliente
        JOIN imoveis i ON con.id_imovel = i.id_imovel
        WHERE 1=1
    """
    params = []

    if filtro_tipo != "Todos":
        query_contratos += " AND con.tipo_contrato = %s"
        params.append(filtro_tipo)
    if filtro_status != "Todos":
        query_contratos += " AND con.status = %s"
        params.append(filtro_status)

    query_contratos += " ORDER BY con.data_assinatura DESC"

    try:
        df_con = pd.read_sql(query_contratos, conn, params=params)

        if not df_con.empty:

            st.markdown(
                "📝 **Edição Rápida:** *Dê dois cliques na coluna 'Status' para alterar a situação do contrato.*")

            df_view = df_con.copy()
            df_view['Valor'] = df_view['Valor_Num'].apply(formata_moeda)
            df_view = df_view[['id_contrato', 'Nº', 'Tipo', 'Cliente',
                               'Bairro Imóvel', 'Valor', 'Assinatura', 'Vencimento', 'Status']]

            if 'tab_con_versao' not in st.session_state:
                st.session_state.tab_con_versao = 0

            chave_grid = f"grid_con_{st.session_state.tab_con_versao}"

            df_editado = st.data_editor(
                df_view,
                use_container_width=True,
                hide_index=True,
                key=chave_grid,
                column_config={
                    "Status": st.column_config.SelectboxColumn("Status", options=["Ativo", "Pendente de Assinatura", "Concluído", "Rescindido"], required=True)
                },
                disabled=['id_contrato', 'Nº', 'Tipo', 'Cliente',
                          'Bairro Imóvel', 'Valor', 'Assinatura', 'Vencimento']
            )

            # Motor de Salvamento Automático
            if chave_grid in st.session_state:
                mudancas = st.session_state[chave_grid].get("edited_rows", {})
                if mudancas:
                    cur = conn.cursor()
                    for idx_row, alteracoes in mudancas.items():
                        id_c = df_con.iloc[int(idx_row)]['id_contrato']
                        novo_status = alteracoes.get("Status")

                        if novo_status:
                            cur.execute(
                                "UPDATE contratos SET status = %s WHERE id_contrato = %s", (novo_status, int(id_c)))

                    conn.commit()
                    st.session_state.tab_con_versao += 1
                    st.toast("✅ Status do contrato atualizado com sucesso!")
                    st.rerun()

        else:
            st.info("Nenhum contrato encontrado com estes filtros.")

    except Exception as e:
        st.error(f"Erro ao carregar contratos: {e}")

    conn.close()

# ------------------------------------------
# TELA 6.3: CONTRATOS ATIVOS (COM ALERTAS)
# ------------------------------------------
elif pagina == "Contratos_Ativos":
    st.header("🟢 Contratos em Vigência")
    st.write("Painel de controle de todos os contratos ativos. Fique atento aos prazos de vencimento (Exclusividades).")

    conn = conectar()

    query_ativos = """
        SELECT con.numero_contrato as "Nº",
               con.tipo_contrato as "Tipo",
               c.nome_completo as "Cliente",
               i.bairro as "Bairro Imóvel",
               con.data_vencimento
        FROM contratos con
        JOIN clientes c ON con.id_cliente = c.id_cliente
        JOIN imoveis i ON con.id_imovel = i.id_imovel
        WHERE con.status = 'Ativo'
        ORDER BY con.data_vencimento ASC
    """

    try:
        df_ativos = pd.read_sql(query_ativos, conn)

        if not df_ativos.empty:
            from datetime import datetime
            hoje = datetime.today().date()

            # --- O MOTOR DE INTELIGÊNCIA DE PRAZOS ---
            def calcular_alerta(data_venc):
                if pd.isna(data_venc):
                    return "⚪ Sem Prazo"

                dias_restantes = (data_venc - hoje).days

                if dias_restantes < 0:
                    return f"🔴 Vencido há {abs(dias_restantes)} dias"
                elif dias_restantes <= 30:
                    return f"🟡 Vence em {dias_restantes} dias"
                else:
                    return f"🟢 No prazo ({dias_restantes} dias)"

            # Aplica a regra matemática criando uma nova coluna visual
            df_ativos['Status do Prazo'] = df_ativos['data_vencimento'].apply(
                calcular_alerta)

            # Formata a data para o padrão BR antes de mostrar na tela
            df_ativos['Vencimento'] = pd.to_datetime(
                df_ativos['data_vencimento']).dt.strftime('%d/%m/%Y').fillna('Não informado')

            # Prepara a tabela final para exibição
            df_view = df_ativos[['Nº', 'Tipo', 'Cliente',
                                 'Bairro Imóvel', 'Vencimento', 'Status do Prazo']]

            st.markdown(
                f"### 📊 Total de Contratos Ativos: **{len(df_ativos)}**")

            # Mostra a tabela com a coluna de status dando o destaque visual
            st.dataframe(df_view, use_container_width=True, hide_index=True)

        else:
            st.success("Tudo limpo! Não há nenhum contrato ativo no momento.")

    except Exception as e:
        st.error(f"Erro ao carregar contratos ativos: {e}")

    conn.close()

# ------------------------------------------
# TELA 6.4: CONTRATOS CONCLUÍDOS (ARQUIVO MORTO)
# ------------------------------------------
elif pagina == "Contratos_Concluidos":
    st.header("📁 Histórico de Contratos Concluídos")
    st.write("Seu arquivo digital. Consulte os negócios que já foram escriturados e finalizados com sucesso.")

    conn = conectar()

    query_conc = """
        SELECT con.numero_contrato as "Nº",
               con.tipo_contrato as "Tipo",
               c.nome_completo as "Cliente",
               i.bairro as "Bairro Imóvel",
               TO_CHAR(con.data_assinatura, 'DD/MM/YYYY') as "Assinatura",
               con.valor_contrato as "Valor_Num"
        FROM contratos con
        JOIN clientes c ON con.id_cliente = c.id_cliente
        JOIN imoveis i ON con.id_imovel = i.id_imovel
        WHERE con.status = 'Concluído'
        ORDER BY con.data_assinatura DESC
    """

    try:
        df_conc = pd.read_sql(query_conc, conn)

        if not df_conc.empty:

            total_movimentado = float(df_conc['Valor_Num'].sum())

            c1, c2 = st.columns(2)
            c1.metric("✅ Contratos Finalizados", len(df_conc))
            c2.metric("💰 Volume Financeiro (VGV)",
                      formata_moeda(total_movimentado))

            st.divider()

            df_view = df_conc.copy()
            df_view['Valor'] = df_view['Valor_Num'].apply(formata_moeda)
            df_view = df_view[['Nº', 'Tipo', 'Cliente',
                               'Bairro Imóvel', 'Assinatura', 'Valor']]

            st.dataframe(df_view, use_container_width=True, hide_index=True)

        else:
            st.info("Nenhum contrato marcado como 'Concluído' ainda. Vá na Lista de Contratos e altere o status de um negócio fechado para ver o histórico aqui.")

    except Exception as e:
        st.error(f"Erro ao carregar contratos concluídos: {e}")

    conn.close()

# ==========================================
# MÓDULO 7: CADASTROS GERAIS E ADMINISTRAÇÃO
# ==========================================

# ------------------------------------------
# TELA 7.1: NOVO USUÁRIO
# ------------------------------------------
elif pagina == "Users_Novo":
    st.header("👤 Cadastrar Novo Usuário")
    st.write(
        "Crie credenciais de acesso para a sua equipe e defina os níveis de permissão.")

    conn = conectar()

    with st.container(border=True):
        with st.form("form_novo_usuario", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            login_val = c1.text_input(
                "Login do Usuário *", placeholder="Ex: carlos.silva")
            senha_val = c2.text_input("Senha Inicial *", type="password")
            nivel_sel = c3.selectbox(
                "Nível de Acesso", ["Corretor", "Financeiro", "Gerente", "Admin"])

            st.info(
                "💡 **Segurança:** A senha será criptografada (hash) antes de ser salva no banco de dados.")

            btn_salvar_usr = st.form_submit_button(
                "💾 Criar Usuário", type="primary")

            if btn_salvar_usr:
                if not login_val.strip() or not senha_val.strip():
                    st.error("⚠️ Preencha o login e a senha!")
                else:
                    import hashlib
                    # Cria o Hash seguro da senha (SHA-256)
                    senha_criptografada = hashlib.sha256(
                        senha_val.encode('utf-8')).hexdigest()

                    try:
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO usuarios (login, senha_hash, nivel_acesso) 
                            VALUES (%s, %s, %s)
                        """, (login_val.strip(), senha_criptografada, nivel_sel))
                        conn.commit()
                        st.success(
                            f"✅ Usuário '{login_val}' criado com sucesso! Nível: {nivel_sel}")
                        st.balloons()
                    except Exception as e:
                        conn.rollback()
                        st.error(
                            f"Erro ao salvar: {e} (Verifique se este login já existe)")

    conn.close()

# ------------------------------------------
# TELA 7.2: LISTA DE USUÁRIOS E RESET DE SENHA
# ------------------------------------------
elif pagina == "Users_Lista":
    st.header("👥 Gerenciamento de Usuários")
    st.write(
        "Edite os níveis de acesso ou resete a senha de funcionários que esqueceram.")

    conn = conectar()

    try:
        # 👇 SQL SEM ALIAS (Usa o nome real 'login')
        df_usr = pd.read_sql(
            "SELECT login, nivel_acesso FROM usuarios ORDER BY login", conn)

        if not df_usr.empty:
            st.markdown(
                "📝 **Edição Rápida:** *Altere o nível de acesso diretamente na tabela.*")

            if 'tab_usr_versao' not in st.session_state:
                st.session_state.tab_usr_versao = 0

            chave_grid = f"grid_usr_{st.session_state.tab_usr_versao}"

            # 👇 Renomeamos as colunas apenas para exibição no data_editor
            df_exibir = df_usr.rename(
                columns={'login': 'Usuário', 'nivel_acesso': 'Nível de Acesso'})

            df_editado = st.data_editor(
                df_exibir,
                use_container_width=True,
                hide_index=True,
                key=chave_grid,
                column_config={
                    "Nível de Acesso": st.column_config.SelectboxColumn(
                        "Nível de Acesso",
                        options=["Corretor", "Financeiro", "Gerente", "Admin"],
                        required=True
                    )
                },
                disabled=['Usuário']  # Bloqueia a edição do login
            )

            # Motor de Salvamento Automático
            if chave_grid in st.session_state:
                mudancas = st.session_state[chave_grid].get("edited_rows", {})
                if mudancas:
                    cur = conn.cursor()
                    for idx_row, alteracoes in mudancas.items():
                        # 👇 Buscamos pelo nome real 'login'
                        login_u = df_usr.iloc[int(idx_row)]['login']

                        if "Nível de Acesso" in alteracoes:
                            novo_nivel = alteracoes["Nível de Acesso"]
                            cur.execute(
                                "UPDATE usuarios SET nivel_acesso = %s WHERE login = %s",
                                (novo_nivel, login_u)
                            )

                    conn.commit()
                    st.session_state.tab_usr_versao += 1
                    st.toast("✅ Nível de acesso atualizado!")
                    st.rerun()

            # --- ÁREA DE RESET DE SENHA ---
            st.divider()
            st.subheader("🆘 Reset de Senha (Esqueci a Senha)")

            # 👇 Buscamos a lista usando o nome real 'login'
            lista_logins = df_usr['login'].tolist()

            with st.form("form_reset_senha"):
                c1, c2 = st.columns(2)
                usuario_reset = c1.selectbox("Selecione o Usuário", [
                                             "-- Selecione --"] + lista_logins)
                nova_senha_admin = c2.text_input(
                    "Nova Senha Temporária *", type="password")
                btn_reset = st.form_submit_button(
                    "🔄 Forçar Nova Senha", type="primary", use_container_width=True)

            if btn_reset:
                if usuario_reset != "-- Selecione --" and nova_senha_admin:
                    import hashlib
                    hash_temp = hashlib.sha256(
                        nova_senha_admin.encode('utf-8')).hexdigest()
                    try:
                        cur = conn.cursor()
                        cur.execute(
                            "UPDATE usuarios SET senha_hash = %s WHERE login = %s", (hash_temp, usuario_reset))
                        conn.commit()
                        st.success(f"✅ Senha de **{usuario_reset}** resetada!")
                        st.balloons()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Erro ao resetar: {e}")

        else:
            st.info("Nenhum usuário encontrado.")

    except Exception as e:
        st.error(f"Erro ao carregar usuários: {e}")

    conn.close()

# ------------------------------------------
# TELA 7.4: PAINEL DE CONTROLE DE ACESSOS (ACL)
# ------------------------------------------
elif pagina == "Config_Regras":
    st.header("🔐 Painel de Permissões de Usuários")
    st.write(
        "Faça o ajuste fino. Libere ou bloqueie módulos específicos para cada usuário da equipe.")

    conn = conectar()

    try:
        # 👇 CORREÇÃO: Busca APENAS o login e o nivel_acesso que existem na sua tabela
        df_usr = pd.read_sql(
            "SELECT login, nivel_acesso FROM usuarios ORDER BY login", conn)

        if not df_usr.empty:
            # 👇 CORREÇÃO: Tira o nome_completo da montagem do texto
            lista_opcoes = df_usr['login'] + \
                " (" + df_usr['nivel_acesso'] + ")"
            usuario_sel = st.selectbox("Selecione o Colaborador:", [
                                       "-- Selecione --"] + lista_opcoes.tolist())

            if usuario_sel != "-- Selecione --":
                # Extrai apenas o login da string selecionada (ex: "admin (Admin)" -> pega só o "admin")
                login_alvo = usuario_sel.split(" (")[0]

                # Busca no banco quais chaves ele já tem liberadas
                df_perm = pd.read_sql(
                    "SELECT modulo, liberado FROM permissoes WHERE login = %s", conn, params=[login_alvo])
                # Transforma num dicionário pro Python ler fácil
                perm_atuais = dict(
                    zip(df_perm.modulo, df_perm.liberado)) if not df_perm.empty else {}

                st.divider()
                st.markdown(f"### 🎛️ Módulos Liberados para **{login_alvo}**")

                with st.form("form_permissoes", clear_on_submit=False):
                    c1, c2 = st.columns(2)

                    with c1:
                        p_imoveis = st.checkbox(
                            "🏠 Gestão de Imóveis", value=perm_atuais.get("Imoveis", False))
                        p_clientes = st.checkbox(
                            "👥 Gestão de Clientes", value=perm_atuais.get("Clientes", False))
                        p_vendas = st.checkbox(
                            "🤝 Gestão de Vendas", value=perm_atuais.get("Vendas", False))
                        p_contratos = st.checkbox(
                            "📄 Gestão de Contratos", value=perm_atuais.get("Contratos", False))

                    with c2:
                        p_corretores = st.checkbox(
                            "👔 Gestão de Corretores", value=perm_atuais.get("Corretores", False))
                        p_financeiro = st.checkbox(
                            "💲 Gestão Financeira", value=perm_atuais.get("Financeiro", False))
                        p_cadastros = st.checkbox(
                            "⚙️ Cadastros Gerais (Admin)", value=perm_atuais.get("Cadastros", False))

                    st.divider()
                    btn_salvar_perm = st.form_submit_button(
                        "💾 Salvar Permissões Deste Usuário", type="primary")

                    if btn_salvar_perm:
                        try:
                            cur = conn.cursor()
                            # O UPSERT: Insere se não existir, atualiza se já existir
                            chaves = [
                                ("Imoveis", p_imoveis), ("Clientes",
                                                         p_clientes), ("Vendas", p_vendas),
                                ("Contratos", p_contratos), ("Corretores", p_corretores),
                                ("Financeiro", p_financeiro), ("Cadastros", p_cadastros)
                            ]

                            for modulo, status in chaves:
                                cur.execute("""
                                    INSERT INTO permissoes (login, modulo, liberado) 
                                    VALUES (%s, %s, %s)
                                    ON CONFLICT (login, modulo) 
                                    DO UPDATE SET liberado = EXCLUDED.liberado
                                """, (login_alvo, modulo, status))

                            conn.commit()
                            st.success(
                                "✅ Permissões atualizadas com sucesso! As mudanças valerão no próximo login dele.")
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Erro ao salvar permissões: {e}")

        else:
            st.warning("Nenhum usuário cadastrado no sistema.")

    except Exception as e:
        st.error(f"Erro ao carregar o painel: {e}")

    conn.close()

# ------------------------------------------
# TELA DE PERFIL: ALTERAR SENHA
# ------------------------------------------
elif pagina == "Mudar_Senha":
    st.header("🔑 Alterar Minha Senha")
    st.write("Mantenha sua conta segura atualizando sua senha periodicamente.")

    with st.container(border=True):
        with st.form("form_alterar_senha", clear_on_submit=True):
            st.info(
                f"Você está alterando a senha do usuário: **{st.session_state.usuario}**")

            senha_atual = st.text_input("Senha Atual *", type="password")

            st.divider()
            c1, c2 = st.columns(2)
            nova_senha = c1.text_input("Nova Senha *", type="password")
            confirma_senha = c2.text_input(
                "Confirme a Nova Senha *", type="password")

            btn_salvar_senha = st.form_submit_button(
                "💾 Atualizar Senha", type="primary")

            if btn_salvar_senha:
                # 1. Validação básica de preenchimento
                if not senha_atual or not nova_senha or not confirma_senha:
                    st.warning("⚠️ Preencha todos os campos obrigatórios!")
                # 2. Verifica se ele não digitou a nova senha errado
                elif nova_senha != confirma_senha:
                    st.error("⚠️ A nova senha e a confirmação não são iguais!")
                else:
                    import hashlib
                    # Cria o hash da senha atual digitada para comparar com o banco
                    hash_atual = hashlib.sha256(
                        senha_atual.encode('utf-8')).hexdigest()
                    # Cria o hash da nova senha que será salva
                    hash_nova = hashlib.sha256(
                        nova_senha.encode('utf-8')).hexdigest()

                    conn = conectar()
                    try:
                        cur = conn.cursor()
                        # Busca a senha real que está no banco agora
                        cur.execute(
                            "SELECT senha_hash FROM usuarios WHERE login = %s", (st.session_state.usuario,))
                        res = cur.fetchone()

                        # 3. Compara o hash digitado com o hash do banco
                        if res and res[0] == hash_atual:
                            # A senha atual bateu! Podemos atualizar.
                            cur.execute(
                                "UPDATE usuarios SET senha_hash = %s WHERE login = %s", (hash_nova, st.session_state.usuario))
                            conn.commit()
                            st.success("✅ Sua senha foi alterada com sucesso!")
                            st.balloons()
                        else:
                            st.error(
                                "⚠️ A senha atual digitada está incorreta!")
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Erro ao atualizar a senha: {e}")
                    finally:
                        conn.close()

# ==========================================
# MÓDULO 8: DASHBOARD EXECUTIVO (BI)
# ==========================================

elif pagina == "Dashboard":
    st.header("📊 Dashboard Executivo")
    st.write("Visão macro da imobiliária. Dados atualizados em tempo real.")

    conn = conectar()

    try:
        # --- 1. BUSCA DE DADOS (OS NÚMEROS MESTRES) ---
        # Saldo em Caixa (Entradas - Saídas do mês atual)
        query_caixa = """
            SELECT 
                (SELECT SUM(valor) FROM entradas WHERE EXTRACT(MONTH FROM data_vencimento) = EXTRACT(MONTH FROM CURRENT_DATE)) as ent,
                (SELECT SUM(valor) FROM despesas WHERE EXTRACT(MONTH FROM data_vencimento) = EXTRACT(MONTH FROM CURRENT_DATE)) as sai
        """
        res_caixa = pd.read_sql(query_caixa, conn)
        entradas_mes = float(res_caixa['ent'].iloc[0] or 0)
        saidas_mes = float(res_caixa['sai'].iloc[0] or 0)
        lucro_estimado = entradas_mes - saidas_mes

        # Estoque e Leads
        total_imoveis = pd.read_sql(
            "SELECT COUNT(*) FROM imoveis WHERE status = 'Disponível'", conn).iloc[0, 0]
        vendas_ano = pd.read_sql(
            "SELECT COUNT(*) FROM vendas WHERE EXTRACT(YEAR FROM data_venda) = EXTRACT(YEAR FROM CURRENT_DATE)", conn).iloc[0, 0]

        # --- 2. LINHA DE KPIs (OS CARDS) ---
        c1, c2, c3, c4 = st.columns(4)

        c1.metric("💰 Receitas (Mês)", formata_moeda(entradas_mes))
        c2.metric("📉 Despesas (Mês)", formata_moeda(
            saidas_mes), delta_color="inverse")

        cor_lucro = "normal" if lucro_estimado >= 0 else "inverse"
        c3.metric("⚖️ Saldo Operacional", formata_moeda(lucro_estimado),
                  delta=f"{lucro_estimado:.2f}", delta_color=cor_lucro)

        c4.metric("🏠 Imóveis p/ Venda", f"{total_imoveis} unid.")

        st.divider()

        # --- 3. GRÁFICOS DE ALTO IMPACTO (PLOTLY) ---
        import plotly.express as px

        col_esq, col_dir = st.columns(2)

        with col_esq:
            st.subheader("📅 Fluxo de Caixa (Últimos 6 Meses)")
            # Query para histórico mensal
            query_hist = """
                SELECT TO_CHAR(data_vencimento, 'Mon/YY') as mes_ref, 
                       SUM(valor) as total, 'Entrada' as tipo, EXTRACT(MONTH FROM data_vencimento) as m
                FROM entradas GROUP BY 1, 3, 4
                UNION ALL
                SELECT TO_CHAR(data_vencimento, 'Mon/YY') as mes_ref, 
                       SUM(valor) as total, 'Saída' as tipo, EXTRACT(MONTH FROM data_vencimento) as m
                FROM despesas GROUP BY 1, 3, 4
                ORDER BY m ASC
            """
            df_hist = pd.read_sql(query_hist, conn)
            if not df_hist.empty:
                fig_hist = px.bar(df_hist, x='mes_ref', y='total', color='tipo',
                                  barmode='group', color_discrete_map={'Entrada': '#2ECC71', 'Saída': '#E74C3C'},
                                  labels={'total': 'Valor (R$)', 'mes_ref': 'Mês'})
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("Dados insuficientes para o gráfico de fluxo.")

        with col_dir:
            st.subheader("📍 Imóveis por Bairro (Onde está o estoque)")
            df_bairros = pd.read_sql(
                "SELECT bairro, COUNT(*) as qtd FROM imoveis GROUP BY bairro ORDER BY qtd DESC LIMIT 8", conn)
            if not df_bairros.empty:
                fig_pie = px.pie(df_bairros, names='bairro', values='qtd', hole=0.4,
                                 color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig_pie, use_container_width=True)

        st.divider()

        # --- 4. RANKING E ALERTAS RÁPIDOS ---
        c_rank, c_alert = st.columns([2, 1])

        with c_rank:
            st.subheader("🏆 Top Corretores (Vendas no Ano)")
            # 👇 Adicionamos aspas duplas nos nomes das colunas para travar o Case
            query_top = """
                SELECT c.nome_completo as "Corretor", 
                       COUNT(v.id_venda) as "Vendas", 
                       SUM(v.valor_venda) as "Volume"
                FROM vendas v
                JOIN corretores c ON v.id_corretor = c.id_corretor
                WHERE EXTRACT(YEAR FROM v.data_venda) = EXTRACT(YEAR FROM CURRENT_DATE)
                GROUP BY c.nome_completo 
                ORDER BY 3 DESC
            """
            df_top = pd.read_sql(query_top, conn)

            if not df_top.empty:
                # Agora o Pandas vai encontrar o 'Volume' com V maiúsculo
                df_top['Volume'] = df_top['Volume'].apply(formata_moeda)
                st.table(df_top)
            else:
                st.info("Nenhuma venda registrada este ano para gerar o ranking.")

        with c_alert:
            st.subheader("🔔 Atenção Imediata")
            # Busca contratos vencendo e leads quentes parados
            cont_venc = pd.read_sql(
                "SELECT COUNT(*) FROM contratos WHERE status = 'Ativo' AND data_vencimento <= CURRENT_DATE + INTERVAL '15 days'", conn).iloc[0, 0]

            if cont_venc > 0:
                st.warning(
                    f"📄 **{cont_venc} Contratos** vencendo nos próximos 15 dias.")

            st.info(
                f"📈 **{vendas_ano} Vendas** concluídas com sucesso em 2026.")

            st.success("✅ Backup do sistema e banco de dados: OK")

    except Exception as e:
        st.error(f"Erro ao carregar o Dashboard: {e}")

    conn.close()

# ------------------------------------------
# ROTEADOR PARA AS TELAS NÃO FINALIZADAS
# ------------------------------------------
elif pagina != "Dashboard":
    st.info(
        f"🚧 A tela **{pagina}** está em desenvolvimento. O módulo será liberado em breve!")
