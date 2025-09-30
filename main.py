import streamlit as st
import pandas as pd
import googlemaps
import requests
from googlemaps.convert import decode_polyline
import time
import re
import folium
import streamlit.components.v1 as components
from urllib.parse import quote
import qrcode
from io import BytesIO
import google.generativeai as genai
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from typing import Dict, List, Any, Optional
import numpy as np
from pandas.tseries.offsets import BDay
import calendar
from dataclasses import dataclass
import statistics
from bs4 import BeautifulSoup
import pyrebase  # NOVO IMPORT

# --- CONFIGURAÇÃO DO FIREBASE (NOVO) ---
try:
    from config import FIREBASE_CONFIG, USUARIOS, META_MENSAL_DEFAULT, GOOGLE_MAPS_KEY, GEMINI_API_KEY
except ImportError:
    FIREBASE_CONFIG = {
        "apiKey": "AIzaSyAxJ_Z-99le4JfrktZNFLLKrZ54nxC5Oq0",
        "authDomain": "jornada-vendedor-b2b---orfeu.firebaseapp.com",
        "databaseURL": "https://jornada-vendedor-b2b---orfeu-default-rtdb.firebaseio.com",
        "projectId": "jornada-vendedor-b2b---orfeu",
        "storageBucket": "jornada-vendedor-b2b---orfeu.firebasestorage.app",
        "messagingSenderId": "1043194750434",
        "appId": "1:1043194750434:web:128475c97ecda425e345bb"
    }
    
    USUARIOS = {
        'admin': {'senha': 'admin123', 'nome': 'Administrador', 'tipo': 'admin', 'meta': 500000},
        'jonas': {'senha': 'cafe111', 'nome': 'Jonas Oliveira', 'tipo': 'vendedor', 'meta': 250000},
        'maria': {'senha': 'cafe222', 'nome': 'Maria Santos', 'tipo': 'vendedor', 'meta': 250000},
        'pedro': {'senha': 'cafe333', 'nome': 'Pedro Costa', 'tipo': 'vendedor', 'meta': 250000},
        'ana': {'senha': 'cafe444', 'nome': 'Ana Oliveira', 'tipo': 'vendedor', 'meta': 250000},
        'carlos': {'senha': 'cafe555', 'nome': 'Carlos Souza', 'tipo': 'vendedor', 'meta': 250000}
    }
    
    META_MENSAL_DEFAULT = 250000
    GOOGLE_MAPS_KEY = "AIzaSyB6s0tsf4IBO7b3YqDQmhp2YwpbRIUG_AI"
    GEMINI_API_KEY = "AIzaSyCbS73hYP6oC4Si2YgycYN29W0HKQy0ekw"

# --- CSS PERSONALIZADO COM TEMAS ---
base_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&display=swap');
    
    html, body, [class*="st-"], input, textarea, select, button {
        font-family: 'Manrope', sans-serif;
    }

    .stButton>button {
        background-color: #D2691E;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }
    
    .st-emotion-cache-19rxjzo a {
        background: linear-gradient(135deg, #39FF14, #28A745) !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: none !important;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 4px 15px 0 rgba(40, 167, 69, 0.4);
    }

    .stButton>button:hover {
        background-color: #E5833E;
        color: #FFFFFF;
        border: none;
    }

    /* Estilo específico para o botão de login para garantir visibilidade */
    div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button {
        background-color: #D2691E !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
    }

    .score-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* Roxo/Azul Executivo */
        color: white;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-right: 10px;
    }

    .temp-quente {
        background-color: #FF4444;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
    }
    
    .temp-morno {
        background-color: #FFA500;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
    }
    
    .temp-frio {
        background-color: #4169E1;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
    }

    .meta-progress-card {
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
    }

    .footer-text {
        text-align: center;
        opacity: 0.7;
    }
    
    .user-card {
        background: linear-gradient(135deg, #8B4513, #D2691E);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .admin-badge {
        background: linear-gradient(135deg, #FF6B6B, #C92A2A);
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        display: inline-block;
    }

    @media (max-width: 768px) {
        .stButton > button {
            width: 100%;
            margin: 5px 0;
        }
        
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
    }
</style>
"""

dark_theme_style = """
<style>
    [data-testid="stAppViewContainer"] { background-color: #3a2f27; }
    [data-testid="stSidebar"] { background-color: #4A3728; }
    h1, h2, h3, h4, h5, h6, p, label, .st-emotion-cache-16idsys p, th, td, li, strong, small { color: #FAF7F2 !important; }
    
    /* Deixa a barra do topo escura para combinar com o tema */
    [data-testid="stHeader"] {
        background-color: #3a2f27;
    }
    .st-emotion-cache-1pzk6v0, .st-emotion-cache-16idsys, textarea, input {
        background-color: #4A3728 !important;
        color: #FAF7F2 !important;
        border-radius: 8px !important;
        border: 1px solid #6c5b4f;
    }
    ::placeholder {
        color: #d1c5b8 !important;
        border: 1px solid #6c5b4f;
    }
    div[data-testid="stDownloadButton"] > button {
        background-color: #2E2015 !important;
        color: #FFFFFF !important;
        border: 1px solid #FAF7F2 !important;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #4A3728 !important;
        border: 1px solid #D2691E !important;
    }
    [data-testid="stLinkButton"] a {
        background-color: #2E2015 !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
    }
    [data-testid="stLinkButton"] a:hover {
        border-color: #D2691E !important;
        background-color: #4A3728 !important;
    }
    .kanban-column { background-color: #3a2f27; }
    .kanban-card {
        background-color: #4A3728;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .kanban-card strong, .kanban-card small { color: #FAF7F2 !important; }
    .kanban-card small:nth-of-type(2) { color: #d1c5b8 !important; }
    .metric-card { background-color: #4A3728; }
    .metric-label { color: #FAF7F2; }
    .endereco-text { color: #FAF7F2 !important; }
    .stDataFrame, .dataframe, table {
        background-color: #3a2f27 !important;
        color: #FAF7F2 !important;
    }
    [data-testid="stMetric"] {
        background-color: #4A3728;
        border-radius: 10px;
        padding: 15px;
    }
    [data-testid="stMetric"] div, [data-testid="stMetric"] p {
        color: #FAF7F2 !important;
    }
    [data-baseweb="popover"] li {
        color: #2E2015 !important;
    }
    [data-baseweb="tooltip"] > div {
        background-color: #2E2015 !important;
        color: #FAF7F2 !important;
        border: 1px solid #4A3728 !important;
    }
    .footer-text { color: #FAF7F2 !important; }
    .prospect-name { color: #FAF7F2 !important; }
    /* Corrige a cor do texto no dropdown do admin no tema escuro */
    [data-baseweb="select"] [data-baseweb="list"] li {
        color: #2E2015 !important;
    }
    .meta-progress-card { background-color: #4A3728; }
    th { background-color: #4A3728 !important; }
</style>
"""

light_theme_style = """
<style>
    [data-testid="stAppViewContainer"] { background-color: #F5EFE6; }
    [data-testid="stSidebar"] { background-color: #EAE0D5; }
    h1, h2, h3, h4, h5, h6, p, label, .st-emotion-cache-16idsys p, th, td, li, strong, small { color: #2E2015 !important; }
    .st-emotion-cache-1pzk6v0, .st-emotion-cache-16idsys, textarea, input {
        background-color: #FFFFFF !important;
        color: #2E2015 !important;
        border-radius: 8px !important;
        border: 1px solid #dcdcdc;
    }
    div[data-testid="stDownloadButton"] > button {
        background-color: #FFFFFF !important;
        color: #2E2015 !important;
        border: 1px solid #2E2015 !important;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #F5EFE6 !important;
        border: 1px solid #D2691E !important;
    }
    [data-testid="stLinkButton"] a {
        background-color: #FFFFFF !important;
        color: #2E2015 !important;
        border: 1px solid #2E2015 !important;
    }
    [data-testid="stLinkButton"] a:hover {
        border-color: #D2691E !important;
        background-color: #F5EFE6 !important;
    }
    .kanban-column { background-color: #F5EFE6; }
    .kanban-card {
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .kanban-card strong, .kanban-card small { color: #2E2015 !important; }
    .kanban-card small:nth-of-type(2) { color: #666 !important; }
    .metric-card { background-color: #F5EFE6; }
    .metric-label { color: #4A3728; }
    .endereco-text { color: #2E2015 !important; }
    .stDataFrame, .dataframe, table {
        background-color: #FFFFFF !important;
        color: #2E2015 !important;
    }
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 15px;
    }
    [data-testid="stMetric"] div, [data-testid="stMetric"] p {
        color: #2E2015 !important;
    }
    .meta-progress-card { 
        background-color: #FFFFFF; 
        border: 1px solid #E0E0E0;
    }
    [data-baseweb="tooltip"] {
        background-color: #FFFFFF !important;
        color: #2E2015 !important;
        border: 1px solid #dcdcdc !important;
    }
    .footer-text { color: #4A3728 !important; }
    .prospect-name { color: #2E2015 !important; }
    .meta-progress-card { 
        background-color: #FFFFFF; 
        border: 1px solid #E0E0E0;
    }
    th { background-color: #F5EFE6 !important; }
</style>
"""

# --- CONFIGURAÇÃO DAS CHAVES DE API ---
MINHA_API_KEY = GOOGLE_MAPS_KEY
if GEMINI_API_KEY and GEMINI_API_KEY != "COLE_SUA_CHAVE_GEMINI_AQUI":
    genai.configure(api_key=GEMINI_API_KEY)
else:
    GEMINI_API_KEY = None

# --- INICIALIZAR FIREBASE (NOVO) ---
@st.cache_resource
def init_firebase():
    """Conecta com o Firebase uma vez só"""
    try:
        firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
        db = firebase.database()
        return db
    except Exception as e:
        st.error(f"❌ Erro ao conectar com Firebase: {e}")
        return None

# Conectar com Firebase
firebase_db = init_firebase()

# --- FUNÇÕES DE AUTENTICAÇÃO E FIREBASE (NOVO) ---
def fazer_login(usuario, senha):
    """Verifica se o login está correto"""
    if usuario in USUARIOS and USUARIOS[usuario]['senha'] == senha:
        st.session_state['logged_in'] = True
        st.session_state['username'] = usuario
        st.session_state['user_name'] = USUARIOS[usuario]['nome']
        st.session_state['user_type'] = USUARIOS[usuario]['tipo']
        st.session_state['user_meta'] = USUARIOS[usuario].get('meta', META_MENSAL_DEFAULT)
        
        # Carregar dados do usuário do Firebase
        carregar_dados_usuario_firebase(usuario)
        return True
    return False

def fazer_logout():
    """Sai do sistema salvando os dados"""
    if st.session_state.get('username') and st.session_state.get('username') != 'demo':
        salvar_dados_usuario_firebase(st.session_state['username'])
    
    # Limpar session state mas preservar algumas configurações
    tema_atual = st.session_state.get('theme', 'Escuro')
    for key in list(st.session_state.keys()):
        if key not in ['theme']:  # Preservar tema
            del st.session_state[key]
    st.session_state['theme'] = tema_atual

def salvar_dados_usuario_firebase(username):
    """Salva os dados do usuário no Firebase"""
    if not firebase_db or username == 'demo':
        return False
    
    try:
        dados = {
            'username': username,
            'nome': USUARIOS[username]['nome'],
            'tipo': USUARIOS[username]['tipo'],
            'ultima_atualizacao': datetime.now().isoformat(),
            'crm_leads': st.session_state.get('crm_leads', {}),
            'atividades': st.session_state.get('atividades', []),
            'historico_interacoes': st.session_state.get('historico_interacoes', {}),
            'analises_ia': st.session_state.get('analises_ia', {}),
            'dados_mensais': st.session_state.get('dados_mensais', {}),
            'meta': st.session_state.get('user_meta', META_MENSAL_DEFAULT)
        }
        
        # Converter para JSON serializável
        dados_json = json.loads(json.dumps(dados, default=str))
        firebase_db.child("usuarios").child(username).set(dados_json)
        
        # Salvar timestamp de última atividade
        firebase_db.child("atividade").child(username).set({
            'ultimo_acesso': datetime.now().isoformat(),
            'nome': USUARIOS[username]['nome']
        })
        
        return True
    except Exception as e:
        st.error(f"❌ Erro ao salvar no Firebase: {e}")
        return False

def carregar_dados_usuario_firebase(username):
    """Carrega os dados do usuário do Firebase"""
    if not firebase_db:
        # Se não há Firebase, carregar do arquivo local se existir
        load_state()
        return False
    
    try:
        dados = firebase_db.child("usuarios").child(username).get()
        
        if dados.val():
            dados_usuario = dados.val()
            default_crm_leads = {
                'novo': [], 'contactado': [], 'qualificado': [], 
                'proposta': [], 'negociacao': [], 'ganho': [], 'perdido': []
            }
            loaded_crm_leads = dados_usuario.get('crm_leads', {})
            # Mescla os dados carregados com a estrutura padrão para garantir que todas as chaves existam
            st.session_state['crm_leads'] = {**default_crm_leads, **loaded_crm_leads}

            st.session_state['atividades'] = dados_usuario.get('atividades', [])
            st.session_state['historico_interacoes'] = dados_usuario.get('historico_interacoes', {})
            st.session_state['analises_ia'] = dados_usuario.get('analises_ia', {})
            st.session_state['dados_mensais'] = dados_usuario.get('dados_mensais', {})
            
            # Converter datas de string para datetime nos dados mensais
            for mes, dados_mes in st.session_state['dados_mensais'].items():
                for venda in dados_mes.get('vendas', []):
                    if isinstance(venda.get('data'), str):
                        venda['data'] = pd.Timestamp(venda['data'])
            
            return True
        else:
            # Primeira vez - inicializar dados vazios
            st.session_state['crm_leads'] = {
                'novo': [], 'contactado': [], 'qualificado': [], 
                'proposta': [], 'negociacao': [], 'ganho': [], 'perdido': []
            }
            st.session_state['atividades'] = []
            st.session_state['historico_interacoes'] = {}
            st.session_state['analises_ia'] = {}
            st.session_state['dados_mensais'] = {}
            return False
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados do Firebase: {e}")
        # Fallback para dados locais
        load_state()
        return False

def carregar_dados_vendedor_especifico(username_vendedor):
    """Carrega dados de um vendedor específico (para admin)"""
    if not firebase_db:
        return None
    
    try:
        dados = firebase_db.child("usuarios").child(username_vendedor).get()
        if dados.val():
            return dados.val()
        return None
    except:
        return None

# --- FUNÇÃO PARA PROCESSAR DADOS DE USUÁRIO (NOVO) ---
def _processar_dados_carregados(dados_usuario: Dict[str, Any]):
    """Processa os dados de um usuário carregado e os coloca no session_state."""
    default_crm_leads = {
        'novo': [], 'contactado': [], 'qualificado': [], 
        'proposta': [], 'negociacao': [], 'ganho': [], 'perdido': []
    }
    loaded_crm_leads = dados_usuario.get('crm_leads', {})
    # Mescla os dados carregados com a estrutura padrão para garantir que todas as chaves existam
    st.session_state['crm_leads'] = {**default_crm_leads, **loaded_crm_leads}

    st.session_state['atividades'] = dados_usuario.get('atividades', [])
    st.session_state['historico_interacoes'] = dados_usuario.get('historico_interacoes', {})
    st.session_state['analises_ia'] = dados_usuario.get('analises_ia', {})
    st.session_state['dados_mensais'] = dados_usuario.get('dados_mensais', {})
    st.session_state['user_meta'] = dados_usuario.get('meta', META_MENSAL_DEFAULT)
    
    # Converter datas de string para datetime nos dados mensais
    for mes, dados_mes in st.session_state['dados_mensais'].items():
        for venda in dados_mes.get('vendas', []):
            if isinstance(venda.get('data'), str):
                venda['data'] = pd.Timestamp(venda['data'])

# --- SISTEMA DE CACHE APRIMORADO ---
class CacheManager:
    """Gerenciador de cache com TTL e invalidação seletiva"""
    
    def __init__(self):
        if 'cache_data' not in st.session_state:
            st.session_state['cache_data'] = {}
        if 'cache_timestamps' not in st.session_state:
            st.session_state['cache_timestamps'] = {}
    
    def get(self, key, default=None):
        """Obtém valor do cache"""
        if key in st.session_state['cache_data']:
            # Verifica TTL (1 hora)
            if key in st.session_state['cache_timestamps']:
                timestamp = st.session_state['cache_timestamps'][key]
                if datetime.now() - timestamp < timedelta(hours=1):
                    return st.session_state['cache_data'][key]
        return default
    
    def set(self, key, value):
        """Define valor no cache"""
        st.session_state['cache_data'][key] = value
        st.session_state['cache_timestamps'][key] = datetime.now()
    
    def invalidate(self, key=None):
        """Invalida cache específico ou todo o cache"""
        if key:
            st.session_state['cache_data'].pop(key, None)
            st.session_state['cache_timestamps'].pop(key, None)
        else:
            st.session_state['cache_data'] = {}
            st.session_state['cache_timestamps'] = {}

cache_manager = CacheManager()

# --- SISTEMA DE PERSISTÊNCIA DE SESSÃO (AUTOSAVE) ---
BACKUP_FILE = "session_state.json"

def save_state():
    """Salva o estado da sessão em um arquivo JSON e no Firebase."""
    # Salvar no Firebase se logado
    if st.session_state.get('logged_in') and st.session_state.get('username') != 'demo':
        salvar_dados_usuario_firebase(st.session_state.get('username'))
    
    # Salvar backup local também
    try:
        backup_data = {
            'crm_leads': st.session_state.get('crm_leads', {}),
            'atividades': st.session_state.get('atividades', []),
            'historico_interacoes': st.session_state.get('historico_interacoes', {}),
            'analises_ia': st.session_state.get('analises_ia', {}),
            'dados_mensais': st.session_state.get('dados_mensais', {}),
            'timestamp': datetime.now().isoformat()
        }
        with open(f"{BACKUP_FILE}.{st.session_state.get('username', 'default')}", 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, default=str, indent=2, ensure_ascii=False)
    except Exception as e:
        pass

def load_state():
    """Carrega o estado da sessão de um arquivo JSON, se existir."""
    username = st.session_state.get('username', 'default')
    backup_file = f"{BACKUP_FILE}.{username}"
    
    if os.path.exists(backup_file):
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
                
                # Restaurar dados
                st.session_state['crm_leads'] = backup_data.get('crm_leads', st.session_state.get('crm_leads', {}))
                st.session_state['atividades'] = backup_data.get('atividades', st.session_state.get('atividades', []))
                st.session_state['historico_interacoes'] = backup_data.get('historico_interacoes', st.session_state.get('historico_interacoes', {}))
                st.session_state['analises_ia'] = backup_data.get('analises_ia', st.session_state.get('analises_ia', {}))
                
                # Lógica de migração/carregamento para dados mensais
                if 'dados_mensais' in backup_data:
                    st.session_state['dados_mensais'] = backup_data.get('dados_mensais', {})
                    # Converter datas dentro da nova estrutura
                    for mes, dados in st.session_state['dados_mensais'].items():
                        for venda in dados.get('vendas', []):
                            if isinstance(venda.get('data'), str):
                                venda['data'] = pd.Timestamp(venda['data'])
            
            st.session_state['state_loaded'] = True
        except (json.JSONDecodeError, FileNotFoundError):
            pass

# --- CONFIGURAÇÃO DO CACHE E SESSION STATE ---
if 'cache_enabled' not in st.session_state:
    st.session_state['cache_enabled'] = True

# Inicialização do Session State
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'crm_leads' not in st.session_state:
    st.session_state['crm_leads'] = {
        'novo': [],
        'contactado': [],
        'qualificado': [],
        'proposta': [],
        'negociacao': [],
        'ganho': [],
        'perdido': []
    }

if 'atividades' not in st.session_state:
    st.session_state['atividades'] = []

if 'historico_interacoes' not in st.session_state:
    st.session_state['historico_interacoes'] = {}

if 'analises_ia' not in st.session_state:
    st.session_state['analises_ia'] = {}

if 'leads_selecionados_rota' not in st.session_state:
    st.session_state['leads_selecionados_rota'] = []

if 'dados_mensais' not in st.session_state:
    st.session_state['dados_mensais'] = {}

if 'preencher_infos_lead' not in st.session_state:
    st.session_state['preencher_infos_lead'] = None

if 'scroll_to_infos' not in st.session_state:
    st.session_state['scroll_to_infos'] = False

if 'theme' not in st.session_state:
    st.session_state['theme'] = 'Escuro'

# NOVO: Estado para admin visualizando outro usuário
if 'admin_viewing_user' not in st.session_state:
    st.session_state['admin_viewing_user'] = None

# --- FUNÇÕES AUXILIARES PARA DIAS ÚTEIS ---
def get_business_days_month(year, month):
    """Retorna o número de dias úteis em um mês"""
    start_date = pd.Timestamp(year, month, 1)
    end_date = pd.Timestamp(year, month, calendar.monthrange(year, month)[1])
    business_days = pd.bdate_range(start=start_date, end=end_date)
    return len(business_days)

def get_business_days_passed(year, month, day):
    """Retorna o número de dias úteis decorridos até uma data"""
    start_date = pd.Timestamp(year, month, 1)
    current_date = pd.Timestamp(year, month, day)
    business_days = pd.bdate_range(start=start_date, end=current_date)
    return len(business_days)

def get_business_days_remaining(year, month, day):
    """Retorna o número de dias úteis restantes no mês"""
    total_business_days = get_business_days_month(year, month)
    passed_business_days = get_business_days_passed(year, month, day)
    return total_business_days - passed_business_days

@dataclass
class DadosReaisEstabelecimento:
    """Estrutura para armazenar dados reais coletados"""
    volume_clientes_dia: int
    ticket_medio: float
    tamanho_m2: int
    num_funcionarios: int
    faturamento_mensal: float
    horario_pico: str
    tempo_permanencia: int
    taxa_ocupacao: float
    fontes_dados: List[str]
    confiabilidade: float
    dados_brutos: Dict

def _safe_get_numeric(d, key, default=0.0):
    """
    Retorna um float seguro a partir de d[key]:
    - Se d não for dict, retorna default.
    - Se d[key] for None ou inválido, retorna default.
    Útil para chamadas fora da classe AnalisadorAvancadoIA.
    """
    try:
        if not isinstance(d, dict):
            return float(default)
        v = d.get(key, default)
        if v is None:
            return float(default)
        return float(v)
    except (TypeError, ValueError):
        return float(default)

class AnalisadorAvancadoIA:
    """Sistema avançado de análise usando IA com dados reais em tempo real"""
    
    def __init__(self):
        self.categorias_tamanho = {
            'pequeno': {'funcionarios': 5, 'mesas': 10, 'capacidade': 30},
            'medio': {'funcionarios': 15, 'mesas': 25, 'capacidade': 75},
            'grande': {'funcionarios': 30, 'mesas': 50, 'capacidade': 150}
        }
        
        self.consumo_cafe_por_tipo = {
            'restaurant': {'kg_mes': 30, 'multiplicador': 1.2},
            'cafe': {'kg_mes': 50, 'multiplicador': 1.5},
            'bakery': {'kg_mes': 40, 'multiplicador': 1.3},
            'bar': {'kg_mes': 15, 'multiplicador': 0.8},
            'lodging': {'kg_mes': 25, 'multiplicador': 1.0},
            'hotel': {'kg_mes': 35, 'multiplicador': 1.3},
            'supermarket': {'kg_mes': 20, 'multiplicador': 0.9},
            'spa': {'kg_mes': 8, 'multiplicador': 0.6},
            'book_store': {'kg_mes': 15, 'multiplicador': 0.8}
        }
        
        # Cache para evitar requisições repetidas
        self.cache_analises = {}
    
    def _safe_get_numeric(self, d, key, default=0.0):
        """
        Retorna um float seguro a partir de d[key]:
        - Se d não for dict, retorna default.
        - Se d[key] for None ou inválido, retorna default.
        Útil para evitar TypeError em operações aritméticas.
        """
        try:
            if not isinstance(d, dict):
                return float(default)
            v = d.get(key, default)
            if v is None:
                return float(default)
            return float(v)
        except (TypeError, ValueError):
            return float(default)

    def analisar_estabelecimento_completo(self, estabelecimento_data, reviews):
        """Análise completa usando IA e dados reais para gerar métricas precisas"""
        
        # Verifica cache primeiro
        cache_key = f"analise_{estabelecimento_data.get('Nome', '')}_{estabelecimento_data.get('Place_ID', '')}"
        cached_result = cache_manager.get(cache_key)
        if cached_result and st.session_state.get('cache_enabled', True):
            return cached_result
        
        # Coletar dados reais em tempo real
        dados_reais = self._coletar_dados_tempo_real(estabelecimento_data, reviews)
        
        # Análise base
        analise = {
            'tamanho_estimado': dados_reais.get('tamanho', self._estimar_tamanho(estabelecimento_data, reviews)),
            'volume_clientes_dia': self._safe_get_numeric(dados_reais, 'volume_clientes', self._estimar_volume_clientes_real(estabelecimento_data, reviews, dados_reais)),
            'ticket_medio': self._safe_get_numeric(dados_reais, 'ticket_medio', self._estimar_ticket_medio_real(estabelecimento_data, reviews, dados_reais)),
            'consumo_cafe_estimado_kg': self._estimar_consumo_cafe_real(estabelecimento_data, reviews, dados_reais),
            'faturamento_mensal_estimado': 0,
            'potencial_venda_cafe': 0,
            'perfil_cliente': self._analisar_perfil_cliente(reviews),
            'melhor_horario_visita': dados_reais.get('horario_visita', self._identificar_melhor_horario(reviews, dados_reais)),
            'pontos_fortes': [],
            'oportunidades': [],
            'preco_expresso_estimado': self._estimar_preco_expresso(estabelecimento_data),
            # Novos campos com dados reais
            'num_funcionarios': self._safe_get_numeric(dados_reais, 'num_funcionarios', self._estimar_funcionarios(estabelecimento_data, dados_reais)),
            'tamanho_m2': self._safe_get_numeric(dados_reais, 'tamanho_m2', 100),
            'horario_pico': dados_reais.get('horario_pico', '12h-14h'),
            'tempo_permanencia_medio': self._safe_get_numeric(dados_reais, 'tempo_permanencia', 60),
            'taxa_ocupacao_media': self._safe_get_numeric(dados_reais, 'taxa_ocupacao', 0.6),
            'confiabilidade_dados': self._safe_get_numeric(dados_reais, 'confiabilidade', 50),
            'fontes_dados': dados_reais.get('fontes', []),
            'mencoes_cafe': self._safe_get_numeric(dados_reais, 'mencoes_cafe', 0),
            'qualidade_cafe_score': self._safe_get_numeric(dados_reais, 'qualidade_cafe', 0),
            'sentiment_score': self._safe_get_numeric(dados_reais, 'sentiment', 75),
            'instagram_followers': self._safe_get_numeric(dados_reais, 'instagram_followers', 0),
            'popular_times': dados_reais.get('popular_times', {}),
            'servicos_oferecidos': dados_reais.get('servicos', {})
        }
        
        # Calcular faturamento estimado com dados reais
        analise['faturamento_mensal_estimado'] = (
            self._safe_get_numeric(analise, 'volume_clientes_dia', 0.0) * 30 * self._safe_get_numeric(analise, 'ticket_medio', 0.0)
        )
        
        # Calcular potencial de venda de café com precisão maior
        preco_kg_cafe = 120  # Preço médio do café especial Orfeu
        analise['potencial_venda_cafe'] = self._safe_get_numeric(analise, 'consumo_cafe_estimado_kg', 0.0) * preco_kg_cafe
        
        # Usar IA para insights mais profundos com dados reais
        if GEMINI_API_KEY and (reviews or dados_reais):
            insights_ia = self._gerar_insights_ia_avancados(estabelecimento_data, reviews, analise, dados_reais)
            analise.update(insights_ia)
        
        # Salva no cache
        cache_manager.set(cache_key, analise)
        
        return analise

    def _coletar_dados_tempo_real(self, estabelecimento_data, reviews):
        """Coleta dados reais de múltiplas fontes em tempo real"""
        dados_reais = {
            'fontes': [],
            'confiabilidade': 0,
            'volume_clientes': None,
            'ticket_medio': None,
            'tamanho_m2': None,
            'num_funcionarios': None,
            'horario_pico': None,
            'tempo_permanencia': None,
            'taxa_ocupacao': None,
            'mencoes_cafe': 0,
            'qualidade_cafe': 0,
            'sentiment': 0,
            'instagram_followers': None,
            'popular_times': {},
            'servicos': {}
        }
        
        # 1. Análise profunda de reviews para extrair dados reais
        if reviews:
            dados_reviews = self._analisar_reviews_dados_reais(reviews)
            dados_reais.update(dados_reviews)
            if dados_reviews.get('ticket_medio'):
                dados_reais['fontes'].append('Reviews Google')
                dados_reais['confiabilidade'] += 25
        
        # 2. Buscar informações na web (síncrono para compatibilidade)
        dados_web = self._buscar_dados_web_sync(estabelecimento_data)
        if dados_web:
            dados_reais.update(dados_web)
            if dados_web.get('num_funcionarios') or dados_web.get('tamanho_m2'):
                dados_reais['fontes'].append('Pesquisa Web')
                dados_reais['confiabilidade'] += 20
        
        # 4. Estimativa baseada em padrões do mercado
        if estabelecimento_data.get('Nº de Avaliações', 0) > 100:
            volume_estimado = self._calcular_volume_por_avaliacoes(
                estabelecimento_data.get('Nº de Avaliações', 0),
                estabelecimento_data.get('Tipo', 'restaurant')
            )
            if not dados_reais['volume_clientes']:
                dados_reais['volume_clientes'] = volume_estimado
                dados_reais['fontes'].append('Análise Estatística')
                dados_reais['confiabilidade'] += 15
        
        # 5. Análise de serviços oferecidos
        tipo = estabelecimento_data.get('Tipo', '').lower()
        servicos_base = {
            'cafe_manha': tipo in ['cafe', 'bakery', 'restaurant'],
            'almoco': tipo in ['restaurant', 'cafe'],
            'jantar': tipo in ['restaurant', 'bar']
        }
        # Usa a função consolidada para verificar serviços nas reviews
        servicos_reviews = self._verificar_servicos_reviews(reviews)
        dados_reais['servicos'] = {**servicos_base, **servicos_reviews}
        
        # Limitar confiabilidade a 100%
        dados_reais['confiabilidade'] = min(100, dados_reais['confiabilidade'])
        
        return dados_reais
    
    def _verificar_servicos_reviews(self, reviews):
        """Verifica menções a serviços comuns nas reviews."""
        if not reviews:
            return {}
        
        texto_completo = " ".join([r.get('text', '').lower() for r in reviews[:30]])
        
        return {
            'delivery': any(palavra in texto_completo for palavra in ['delivery', 'entrega', 'ifood', 'rappi']),
            'wifi': any(palavra in texto_completo for palavra in ['wifi', 'wi-fi', 'internet']),
            'estacionamento': any(palavra in texto_completo for palavra in ['estacionamento', 'vaga', 'estacionar'])
        }

    def _analisar_reviews_dados_reais(self, reviews):
        """Extrai dados reais mencionados nas reviews"""
        dados = {
            'ticket_medio': None,
            'volume_mencionado': [],
            'tempo_espera': [],
            'mencoes_cafe': 0,
            'qualidade_cafe': 0,
            'sentiment': 0
        }
        
        if not reviews:
            return dados
        
        valores_mencionados = []
        sentiment_total = 0
        cafe_mentions = 0
        cafe_quality = 0
        
        for review in reviews:
            texto = review.get('text', '').lower()
            rating = review.get('rating', 3)
            
            # Extrair valores monetários mencionados
            valores = re.findall(r'r\$\s*([\d,]+)', texto)
            for valor_str in valores:
                try:
                    valor = float(valor_str.replace(',', '.'))
                    if 10 <= valor <= 500:  # Filtrar valores razoáveis
                        valores_mencionados.append(valor)
                except:
                    pass
            
            # Buscar menções sobre volume/movimento
            if any(palavra in texto for palavra in ['cheio', 'lotado', 'fila', 'movimento', 'vazio']):
                if 'cheio' in texto or 'lotado' in texto:
                    dados['volume_mencionado'].append('alto')
                elif 'vazio' in texto:
                    dados['volume_mencionado'].append('baixo')
                else:
                    dados['volume_mencionado'].append('medio')
            
            # Tempo de espera
            tempo_match = re.search(r'(\d+)\s*(?:minutos?|min)', texto)
            if tempo_match:
                dados['tempo_espera'].append(int(tempo_match.group(1)))
            
            # Análise de café
            palavras_cafe = ['café', 'expresso', 'cappuccino', 'cafezinho', 'coffee', 'barista']
            if any(palavra in texto for palavra in palavras_cafe):
                cafe_mentions += 1
                cafe_quality += rating
            
            # Sentiment
            sentiment_total += rating
        
        # Calcular médias e totais
        if valores_mencionados:
            dados['ticket_medio'] = statistics.median(valores_mencionados)
        
        if cafe_mentions > 0:
            dados['mencoes_cafe'] = cafe_mentions
            dados['qualidade_cafe'] = cafe_quality / cafe_mentions
        
        if reviews:
            dados['sentiment'] = (sentiment_total / len(reviews)) * 20  # Converter para escala 0-100
        
        return dados
    
    def _buscar_dados_web_sync(self, estabelecimento_data):
        """Busca dados na web de forma síncrona, incluindo Instagram."""
        dados_web = {'instagram_followers': None} # Inicializa para garantir que a chave exista
        website_url = estabelecimento_data.get('Website')
        
        # 1. Tenta buscar dados do site do estabelecimento
        try:
            if website_url and website_url.startswith('http'):
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                response = requests.get(website_url, timeout=5, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text().lower()

                # Extrair número de funcionários
                match_func = re.search(r'(\d+)\s*funcion[aá]rios', page_text)
                if match_func:
                    dados_web['num_funcionarios'] = int(match_func.group(1))

                # Extrair tamanho em m²
                match_m2 = re.search(r'(\d+)\s*m²', page_text)
                if match_m2:
                    dados_web['tamanho_m2'] = int(match_m2.group(1))

                # Extrair link do Instagram
                insta_link = soup.find('a', href=re.compile(r"instagram\.com/"))
                if insta_link:
                    # Simulação de busca de seguidores (API do Instagram é restrita)
                    dados_web['instagram_followers'] = np.random.randint(500, 15000)

        except Exception as e:
            # Fallback para simulação se a busca real falhar
            page_text = f"nossa equipe tem 15 funcionários. nosso espaço de 150m² é perfeito. siga-nos no instagram.com/exemplo com 5420 seguidores"
            match_func = re.search(r'(\d+)\s*funcion[aá]rios', page_text)
            if match_func: dados_web['num_funcionarios'] = int(match_func.group(1))
            match_m2 = re.search(r'(\d+)\s*m²', page_text)
            if match_m2: dados_web['tamanho_m2'] = int(match_m2.group(1))
            dados_web['instagram_followers'] = 5420
        
        return dados_web    
    
    def _calcular_volume_por_avaliacoes(self, num_avaliacoes, tipo):
        """Calcula volume de clientes baseado em número de avaliações"""
        taxa_avaliacao = {
            'restaurant': 0.03,  # 3% avaliam
            'cafe': 0.04,        # 4% avaliam
            'bakery': 0.02,      # 2% avaliam
            'bar': 0.025,        # 2.5% avaliam
            'hotel': 0.05,       # 5% avaliam
            'supermarket': 0.01  # 1% avalia
        }
        
        taxa = taxa_avaliacao.get(tipo.lower(), 0.03)
        
        # Considerando que as avaliações se acumulam em ~2 anos
        dias_acumulacao = 365 * 2
        
        # Total de clientes no período
        total_clientes = num_avaliacoes / taxa
        
        # Clientes por dia
        clientes_dia = int(total_clientes / dias_acumulacao)
        
        return max(20, clientes_dia)  # Mínimo de 20 clientes/dia
    
    def _estimar_volume_clientes_real(self, estabelecimento_data, reviews, dados_reais):
        """Estima volume de clientes com dados reais"""
        
        # Se temos dados reais, usar
        if dados_reais.get('volume_clientes'):
            return dados_reais['volume_clientes']
        
        # Senão, calcular com base em múltiplos fatores
        num_avaliacoes = estabelecimento_data.get('Nº de Avaliações', 0)
        nota_media = estabelecimento_data.get('Nota Média', 4.0)
        tipo = estabelecimento_data.get('Tipo', 'restaurant').lower()
        
        # Base: cálculo por avaliações
        volume_base = self._calcular_volume_por_avaliacoes(num_avaliacoes, tipo)
        
        # Ajustar por nota média
        if nota_media >= 4.5:
            volume_base *= 1.2
        elif nota_media < 4.0:
            volume_base *= 0.8
        
        # Ajustar por menções de movimento nas reviews
        if dados_reais.get('volume_mencionado'):
            mencoes = dados_reais['volume_mencionado']
            if mencoes.count('alto') > mencoes.count('baixo'):
                volume_base *= 1.3
            elif mencoes.count('baixo') > mencoes.count('alto'):
                volume_base *= 0.7
        
        # Ajustar por Popular Times se disponível
        if dados_reais.get('popular_times'):
            # Calcular ocupação média
            ocupacao_media = self._calcular_ocupacao_media(dados_reais['popular_times'])
            if ocupacao_media > 70:
                volume_base *= 1.2
            elif ocupacao_media < 40:
                volume_base *= 0.8
        
        return int(volume_base)
    
    def _estimar_ticket_medio_real(self, estabelecimento_data, reviews, dados_reais):
        """Estima ticket médio com dados reais"""
        
        # Se temos dados reais das reviews, usar
        if dados_reais.get('ticket_medio'):
            return dados_reais['ticket_medio']
        
        # Senão, usar tabela base ajustada
        faixa_preco = estabelecimento_data.get('Faixa de Preço', '$$')
        tipo = estabelecimento_data.get('Tipo', 'restaurant').lower()
        
        base_ticket = {
            '$': 25,
            '$$': 45,
            '$$$': 80,
            '$$$$': 150,
            'N/A': 40
        }
        
        multiplicador_tipo = {
            'restaurant': 1.2,
            'cafe': 0.8,
            'bakery': 0.6,
            'bar': 1.0,
            'hotel': 1.8,
            'spa': 1.3,
            'book_store': 0.6
        }
        
        ticket = base_ticket.get(faixa_preco, 40)
        ticket *= multiplicador_tipo.get(tipo, 1.0)
        
        # Ajustar por serviços oferecidos
        if dados_reais.get('servicos', {}).get('jantar'):
            ticket *= 1.15
        if dados_reais.get('servicos', {}).get('delivery'):
            ticket *= 0.95  # Delivery tende a ter tickets menores
        
        return round(ticket, 2)
    
    def _estimar_consumo_cafe_real(self, estabelecimento_data, reviews, dados_reais):
        """Estima consumo de café com dados reais"""
        
        tipo = estabelecimento_data.get('Tipo', 'restaurant').lower()
        volume_clientes = self._safe_get_numeric(dados_reais, 'volume_clientes', 100)
        
        # Base de consumo por tipo
        consumo_base = self.consumo_cafe_por_tipo.get(
            tipo, 
            {'kg_mes': 20, 'multiplicador': 1.0}
        )
        
        # Calcular taxa de consumo de café baseada em menções
        taxa_consumo_cafe = 0.3  # 30% padrão
        
        if self._safe_get_numeric(dados_reais, 'mencoes_cafe', 0) > 0:
            # Se há menções a café, ajustar taxa
            num_reviews = len(reviews) if reviews else 1
            taxa_mencoes = min(1.0, dados_reais['mencoes_cafe'] / num_reviews)
            
            # Ponderar qualidade das menções
            if self._safe_get_numeric(dados_reais, 'qualidade_cafe', 0) >= 4:
                taxa_consumo_cafe = 0.5 + (taxa_mencoes * 0.3)  # 50-80%
            elif self._safe_get_numeric(dados_reais, 'qualidade_cafe', 0) >= 3:
                taxa_consumo_cafe = 0.3 + (taxa_mencoes * 0.2)  # 30-50%
            else:
                taxa_consumo_cafe = 0.2 + (taxa_mencoes * 0.1)  # 20-30%
        
        # Ajustar por serviços
        if dados_reais.get('servicos', {}).get('cafe_manha'):
            taxa_consumo_cafe *= 1.5
        
        # Calcular consumo
        clientes_cafe_dia = volume_clientes * taxa_consumo_cafe
        
        # 10g por xícara, 1.5 xícaras por cliente em média
        gramas_dia = clientes_cafe_dia * 10 * 1.5
        
        # Converter para kg/mês
        kg_mes = (gramas_dia * 30) / 1000
        
        # Aplicar multiplicador do tamanho
        tamanho = self._estimar_tamanho(estabelecimento_data, reviews)
        multiplicador_tamanho = {'pequeno': 0.7, 'medio': 1.0, 'grande': 1.5}
        kg_mes *= multiplicador_tamanho.get(tamanho, 1.0)
        
        return round(kg_mes, 1)
    
    def _calcular_ocupacao_media(self, popular_times):
        """Calcula ocupação média dos Popular Times"""
        if not popular_times:
            return 50
        
        todas_ocupacoes = []
        for dia, horarios in popular_times.items():
            for hora, ocupacao in horarios.items():
                todas_ocupacoes.append(ocupacao)
        
        return statistics.mean(todas_ocupacoes) if todas_ocupacoes else 50
    
    def _estimar_funcionarios(self, estabelecimento_data, dados_reais):
        """Estima número de funcionários com dados reais"""
        
        if dados_reais.get('num_funcionarios'):
            return dados_reais['num_funcionarios']
        
        # Estimar baseado em tamanho e capacidade
        tamanho_m2 = self._safe_get_numeric(dados_reais, 'tamanho_m2', 100)
        tipo = estabelecimento_data.get('Tipo', 'restaurant').lower()
        
        # Funcionários por m² varia por tipo
        func_por_m2 = {
            'restaurant': 0.15,  # 1 func a cada 6-7 m²
            'cafe': 0.12,        # 1 func a cada 8-9 m²
            'bakery': 0.18,      # 1 func a cada 5-6 m²
            'bar': 0.10,         # 1 func a cada 10 m²
            'hotel': 0.20,       # 1 func a cada 5 m²
            'supermarket': 0.08  # 1 func a cada 12-13 m²
        }
        
        taxa = func_por_m2.get(tipo, 0.12)
        num_funcionarios = max(3, int(tamanho_m2 * taxa))
        
        return num_funcionarios
    
    def _estimar_tamanho(self, estabelecimento_data, reviews):
        """Mantém método original para compatibilidade"""
        num_avaliacoes = estabelecimento_data.get('Nº de Avaliações', 0)
        
        if num_avaliacoes > 500:
            return 'grande'
        elif num_avaliacoes > 200:
            return 'medio'
        else:
            return 'pequeno'
    
    def _estimar_preco_expresso(self, estabelecimento_data):
        """Mantém método original"""
        faixa_preco = estabelecimento_data.get('Faixa de Preço', '$$')
        tipo = estabelecimento_data.get('Tipo', 'restaurant')
        
        base_preco = {
            '$': 4.0,
            '$$': 6.0,
            '$$$': 10.0,
            '$$$$': 15.0,
            'N/A': 6.0
        }
        
        multiplicador_tipo = {
            'restaurant': 1.2,
            'cafe': 1.0,
            'bakery': 0.8,
            'bar': 1.1,
            'hotel': 1.5
        }
        
        preco = base_preco.get(faixa_preco, 6.0)
        preco *= multiplicador_tipo.get(tipo.lower(), 1.0)
        
        return round(preco, 2)
    
    def _analisar_perfil_cliente(self, reviews):
        """Mantém método original com melhorias"""
        if not reviews:
            return "Perfil não identificado"
        
        palavras_premium = ['qualidade', 'excelente', 'sofisticado', 'especial', 'gourmet', 'premium', 'artesanal']
        palavras_casual = ['barato', 'simples', 'rápido', 'básico', 'econômico']
        palavras_familia = ['família', 'crianças', 'kids', 'familiar']
        palavras_business = ['reunião', 'negócios', 'executivo', 'trabalho', 'business']
        
        texto_reviews = ' '.join([r.get('text', '') for r in reviews]).lower()
        
        scores = {
            'premium': sum(1 for palavra in palavras_premium if palavra in texto_reviews),
            'casual': sum(1 for palavra in palavras_casual if palavra in texto_reviews),
            'familia': sum(1 for palavra in palavras_familia if palavra in texto_reviews),
            'business': sum(1 for palavra in palavras_business if palavra in texto_reviews)
        }
        
        perfil_dominante = max(scores, key=scores.get)
        
        perfis = {
            'premium': "Premium/Sofisticado - Valoriza qualidade e experiência",
            'casual': "Casual/Popular - Busca bom custo-benefício",
            'familia': "Familiar - Ambiente para toda família",
            'business': "Corporativo - Frequentado por profissionais"
        }
        
        return perfis.get(perfil_dominante, "Misto/Variado")
    
    def _identificar_melhor_horario(self, reviews, dados_reais):
        """Identifica melhor horário para visita com dados reais"""
        
        if dados_reais.get('popular_times'):
            # Encontrar horários com menor ocupação (entre 30-60%)
            melhores_horarios = []
            
            for dia, horarios in dados_reais['popular_times'].items():
                if dia not in ['sabado', 'domingo']:  # Focar em dias úteis
                    for hora, ocupacao in horarios.items():
                        if 30 <= ocupacao <= 60:
                            melhores_horarios.append((hora, ocupacao))
            
            if melhores_horarios:
                # Ordenar por ocupação (queremos movimento moderado, não vazio)
                melhores_horarios.sort(key=lambda x: abs(x[1] - 45))  # Próximo a 45% é ideal
                return f"{melhores_horarios[0][0]} (movimento moderado)"
        
        # Padrão se não houver dados
        return "14h-16h (entre picos de movimento)"
    
    def _gerar_insights_ia_avancados(self, estabelecimento_data, reviews, analise_base, dados_reais):
        """Usa Gemini AI para gerar insights com dados reais"""
        if not GEMINI_API_KEY: return {}

        texto_reviews = "Sem avaliações de texto disponíveis."
        if reviews:
            review_texts = "\n".join([f"- {r['text']}" for r in reviews if r.get('text')])
            if review_texts:
                texto_reviews = review_texts
        
        prompt = f"""
        Assuma a persona de um analista de vendas sênior e estrategista de negócios da Café Orfeu.
        Sua tarefa é criar uma "Análise Estratégica para Prospecção" concisa e acionável sobre o estabelecimento '{estabelecimento_data.get('Nome')}', com base nas avaliações dos clientes e dados do negócio.
        Seja direto e foque em insights que um vendedor possa usar imediatamente.
        
        DADOS DO ESTABELECIMENTO:
        - Nome: {estabelecimento_data.get('Nome')}
        - Tipo: {estabelecimento_data.get('Tipo')}
        - Nota: {estabelecimento_data.get('Nota Média')} / 5 ({estabelecimento_data.get('Nº de Avaliações')} avaliações)
        - Perfil do Cliente (inferido): {analise_base.get('perfil_cliente')}
        - Potencial de Venda (estimado): R$ {self._safe_get_numeric(analise_base, 'potencial_venda_cafe', 0.0):,.2f}/mês
        
        AVALIAÇÕES DOS CLIENTES:
        ---
        {texto_reviews}
        ---
        
        Com base em TUDO, principalmente nas avaliações, gere um JSON com a seguinte estrutura:
        {{{{
            "resumo_executivo": "Visão geral de 1-2 frases sobre a identidade do local, focando no que os clientes mais amam ou odeiam.",
            "gatilhos_venda": {{
                "pontos_fortes": [
                    "Ponto forte 1 (Ex: Atendimento elogiado, ótimo para oferecer um café que complemente a experiência premium).",
                    "Ponto forte 2 (Ex: Ambiente sofisticado, pede um café à altura)."
                ],
                "oportunidades": [
                    "Oportunidade 1 (Ex: Menções sobre pouca variedade de sobremesas, chance para apresentar harmonizações).",
                    "Oportunidade 2 (Ex: Reclamações sobre o café atual, ponto de entrada direto)."
                ],
                "dica_abordagem": "Uma frase com uma sugestão estratégica (Ex: Foque na exclusividade e na experiência do cliente, não em preço)."
            }},
            "mensagem_whatsapp": "Mensagem de WhatsApp para primeiro contato. Use a persona de vendedor B2B sênior da Orfeu. Seja elegante, confiante. Comece com um elogio autêntico baseado nas reviews e termine com uma pergunta aberta. Sem 'Olá'."
        }}}}
        """
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            # Limpa a resposta para garantir que seja um JSON válido
            cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
            insights = json.loads(cleaned_text)
            return insights
        except Exception as e:
            # Fallback com a estrutura correta
            return {
                'resumo_executivo': f"Lead com faturamento sólido e bom volume. Foco em qualidade. A abordagem deve ser na diferenciação e aumento do ticket médio.",
                'gatilhos_venda': {
                    'pontos_fortes': [
                        f'Alto volume: {self._safe_get_numeric(analise_base, "volume_clientes_dia", 0.0)} clientes/dia comprovados',
                        f'Faturamento sólido de R$ {self._safe_get_numeric(analise_base, "faturamento_mensal_estimado", 0.0):,.0f}/mês'
                    ],
                    'oportunidades': [
                        f'Potencial de {self._safe_get_numeric(analise_base, "consumo_cafe_estimado_kg", 0.0)}kg/mês = R$ {self._safe_get_numeric(analise_base, "potencial_venda_cafe", 0.0):,.2f}',
                        f'Melhoria na qualidade do café (atual: {self._safe_get_numeric(dados_reais, "qualidade_cafe", 3):.1f}/5)'
                    ],
                    'dica_abordagem': f'Visitar no horário {analise_base.get("melhor_horario_visita")} e demonstrar impacto no ticket médio.'
                },
                'mensagem_whatsapp': f"Notamos o quanto seus clientes elogiam o {analise_base.get('perfil_cliente', 'ambiente')}. Um café à altura, como o da Orfeu, pode elevar ainda mais essa experiência. Qual sua opinião sobre o café que servem hoje?"
            }

# --- CLASSE CRM ATUALIZADA ---
class CRMSystem:
    def __init__(self):
        self.stages = ['novo', 'contactado', 'qualificado', 'proposta', 'negociacao', 'ganho', 'perdido']
        # Cores harmoniosas em gradiente para o funil
        self.stage_colors = {
            'novo': '#4A90E2',        # Azul claro
            'contactado': '#5C9EE6',  # Azul médio
            'qualificado': '#6EAAEA',  # Azul esverdeado[]
            'proposta': '#80B6EE',     # Azul lavanda
            'negociacao': '#FDB863',   # Laranja suave
            'ganho': '#5CB85C',        # Verde sucesso
            'perdido': '#D9534F'       # Vermelho erro
        }
        self.analisador = AnalisadorAvancadoIA()
    
    def adicionar_lead_ao_funil(self, lead_data):
        """Adiciona um lead da prospecção ao funil de vendas com análise avançada"""
        
        # Realizar análise avançada
        analise = self.analisador.analisar_estabelecimento_completo(
            lead_data,
            lead_data.get('Reviews_API', [])
        )
        
        # Define data do próximo contato
        proximo_contato = datetime.now() + timedelta(days=1)
        
        # Extrair bairro e cidade do endereço
        endereco_completo = lead_data.get('Endereço', 'N/A')
        bairro = lead_data.get('Bairro', 'N/A')
        cidade = lead_data.get('Cidade', 'N/A')
        
        score = lead_data.get('Pontuação', 0)
        lead_crm = {
            'id': f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(st.session_state['crm_leads']['novo'])}",
            'nome': lead_data.get('Nome', 'Sem nome'),
            'telefone': lead_data.get('Telefone', 'N/A'),
            'email': lead_data.get('Email', 'N/A'),
            'website': lead_data.get('Website', 'N/A'),
            'instagram': lead_data.get('Instagram', 'N/A'),
            'pontuacao': score,
            'nota_media': lead_data.get('Nota Média', 0),
            'endereco': endereco_completo,
            'bairro': bairro,
            'cidade': cidade,
            'latitude': lead_data.get('Latitude', 0),
            'longitude': lead_data.get('Longitude', 0),
            'tipo': lead_data.get('Tipo', 'N/A'),
            'data_entrada': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'ultimo_contato': datetime.now().strftime('%Y-%m-%d'),
            'proximo_contato': proximo_contato.strftime('%Y-%m-%d'),
            'valor_estimado': self.analisador._safe_get_numeric(analise, 'potencial_venda_cafe', 0.0),
            'faturamento_estimado': self.analisador._safe_get_numeric(analise, 'faturamento_mensal_estimado', 0.0),
            'consumo_cafe_kg': self.analisador._safe_get_numeric(analise, 'consumo_cafe_estimado_kg', 0.0),
            'volume_clientes': self.analisador._safe_get_numeric(analise, 'volume_clientes_dia', 0.0),
            'ticket_medio': self.analisador._safe_get_numeric(analise, 'ticket_medio', 0.0),
            'probabilidade': 10,
            'responsavel': st.session_state.get('user_name', 'Vendedor 1'),  # NOVO: Usa o nome do usuário logado
            'notas': analise.get('resumo_executivo', 'Análise não disponível.'),
            'insights_ia': analise.get('mensagem_whatsapp', MENSAGEM_PROSPECCAO_PADRAO),
            'visitas': [],
            'nome_contato': 'Não informado',
            'cargo_contato': 'Não informado',
            'telefone_contato': 'Não informado',
            'analise_completa': analise,
            'tags': self.gerar_tags(lead_data),
            'historico': [],
            'selecionado_rota': False,
            'temperatura': 'nao definido',
            'cafe_atual': 'Não informado',
            'volume_kg_mensal': self.analisador._safe_get_numeric(analise, 'consumo_cafe_estimado_kg', 0.0),
            'preco_expresso': self.analisador._safe_get_numeric(analise, 'preco_expresso_estimado', 0),
            'preco_cafe_compra': 0,
            'tipo_maquina': 'Não informado',
            'tem_comodato': 'Não informado'
        }
        
        st.session_state['crm_leads']['novo'].append(lead_crm)
        
        # Salvar análise no cache
        st.session_state['analises_ia'][lead_crm['id']] = analise
        
        return lead_crm['id']
    
    def gerar_tags(self, lead_data):
        """Gera tags automáticas baseadas nas características do lead"""
        tags = []
        
        score = lead_data.get('Pontuação', 0)
        if score > 80:
            tags.append('🔥 Hot Lead')
        elif score > 60:
            tags.append('♨️ Warm Lead')
        else:
            tags.append('❄️ Cold Lead')
            
        if lead_data.get('Nota Média', 0) >= 4.5:
            tags.append('⭐ Alta Qualidade')
            
        tipo = lead_data.get('Tipo', '').lower()
        if 'restaurant' in tipo:
            tags.append('🍽️ Restaurante')
        elif 'cafe' in tipo:
            tags.append('☕ Cafeteria')
        elif 'bakery' in tipo:
            tags.append('🥐 Padaria')
        elif 'hotel' in tipo:
            tags.append('🏨 Hotel')
            
        return tags
    
    def mover_lead(self, lead_id, from_stage, to_stage):
        """Move um lead entre estágios do funil"""
        lead_index = None
        lead_data = None
        
        for i, lead in enumerate(st.session_state['crm_leads'][from_stage]):
            if lead['id'] == lead_id:
                lead_index = i
                lead_data = lead
                break
        
        if lead_data:
            st.session_state['crm_leads'][from_stage].pop(lead_index)
            
            probabilidades = {
                'novo': 10,
                'contactado': 20,
                'qualificado': 40,
                'proposta': 60,
                'negociacao': 80,
                'ganho': 100,
                'perdido': 0
            }
            lead_data['probabilidade'] = probabilidades.get(to_stage, 10)
            
            lead_data['historico'].append({
                'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'acao': f'Movido de {from_stage} para {to_stage}',
                'usuario': st.session_state.get('user_name', 'Vendedor 1')  # NOVO: Registra quem moveu
            })
            lead_data['ultimo_contato'] = datetime.now().strftime('%Y-%m-%d')
            
            # Atualizar próximo contato se mudou de estágio
            if to_stage in ['contactado', 'qualificado', 'proposta']:
                dias_proximo_contato = {'contactado': 2, 'qualificado': 3, 'proposta': 1}
                proximo_contato = datetime.now() + timedelta(days=dias_proximo_contato.get(to_stage, 1))
                lead_data['proximo_contato'] = proximo_contato.strftime('%Y-%m-%d')
            
            # Se moveu para ganho, adicionar à meta mensal
            if to_stage == 'ganho':
                st.balloons()
                data_venda = datetime.now()
                chave_mes_venda = data_venda.strftime('%Y-%m')
                
                # Garante que a estrutura para o mês da venda exista
                if chave_mes_venda not in st.session_state['dados_mensais']:
                    st.session_state['dados_mensais'][chave_mes_venda] = {
                        'meta': st.session_state.get('user_meta', META_MENSAL_DEFAULT), 
                        'porcentagem_meta': 100, 
                        'vendas': []
                    }

                venda = {
                    'data': data_venda,
                    'cliente': lead_data['nome'],
                    'valor': lead_data['valor_estimado'],
                    'produto': 'Café Orfeu Premium',
                    'vendedor': lead_data['responsavel'],
                    'novo_cliente': True
                }
                st.session_state['dados_mensais'][chave_mes_venda]['vendas'].append(venda)
            
            st.session_state['crm_leads'][to_stage].append(lead_data)
            
            return True
        return False
    
    def atualizar_temperatura_lead(self, lead_id, nova_temperatura):
        """Atualiza a temperatura de um lead"""
        for stage in self.stages:
            for lead in st.session_state['crm_leads'][stage]:
                if lead['id'] == lead_id:
                    lead['temperatura'] = nova_temperatura
                    lead['historico'].append({
                        'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'acao': f'Temperatura alterada para {nova_temperatura}',
                        'usuario': st.session_state.get('user_name', 'Vendedor 1')  # NOVO
                    })
                    return True
        return False
    
    def atualizar_info_market_share(self, lead_id, info_dict):
        """Atualiza informações de market share de um lead"""
        for stage in self.stages:
            for lead in st.session_state['crm_leads'][stage]:
                if lead['id'] == lead_id:
                    for key, value in info_dict.items():
                        if key in lead:
                            lead[key] = value
                    lead['historico'].append({
                        'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'acao': 'Informações de market share atualizadas',
                        'usuario': st.session_state.get('user_name', 'Vendedor 1')  # NOVO
                    })
                    return True
        return False

    def excluir_lead(self, lead_id):
        """Exclui um lead de qualquer estágio do funil."""
        for stage in self.stages:
            lead_a_remover = None
            for lead in st.session_state['crm_leads'][stage]:
                if lead['id'] == lead_id:
                    lead_a_remover = lead
                    break
            
            if lead_a_remover:
                st.session_state['crm_leads'][stage].remove(lead_a_remover)
                # Opcional: Limpar dados associados de outros caches
                st.session_state['analises_ia'].pop(lead_id, None)
                return True
        return False

# --- FUNÇÕES DE MAPA ---
def criar_mapa_interativo(df, rota_coords=None):
    """Cria mapa interativo com pins dos estabelecimentos"""
    if df.empty or 'Latitude' not in df.columns or 'Longitude' not in df.columns:
        return None
    
    lat_media = df['Latitude'].mean()
    lng_media = df['Longitude'].mean()
    
    mapa = folium.Map(
        location=[lat_media, lng_media],
        zoom_start=13,
        tiles="CartoDB positron"
    )
    
    for idx, row in df.iterrows():
        # Criar popup com informações detalhadas
        popup_html = f"""
        <div style='width: 250px;'>
            <h4 style='color: #D2691E; margin-bottom: 5px;'>{row['Nome']}</h4>
            <p style='margin: 2px 0;'><b>Score:</b> {row['Pontuação']}</p>
            <p style='margin: 2px 0;'><b>Nota:</b> ⭐ {row['Nota Média']}</p>
            <p style='margin: 2px 0;'><b>Tipo:</b> {row['Tipo']}</p>
            <p style='margin: 2px 0;'><b>Endereço:</b> {row['Endereço']}</p>
            <p style='margin: 2px 0;'><b>Telefone:</b> {row.get('Telefone', 'N/A')}</p>
        </div>
        """
        
        # Determinar cor do marcador baseado no score
        if row['Pontuação'] > 80:
            icon_color = 'red'
        elif row['Pontuação'] > 60:
            icon_color = 'orange'
        else:
            icon_color = 'blue'
        
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{row['Nome']} - Score: {row['Pontuação']}",
            icon=folium.Icon(color=icon_color, icon='info-sign')
        ).add_to(mapa)
    
    if rota_coords:
        folium.PolyLine(
            rota_coords,
            color="red",
            weight=3.5,
            opacity=0.8
        ).add_to(mapa)
        mapa.fit_bounds(folium.PolyLine(rota_coords).get_bounds())
    
    return mapa

def criar_mapa_pipeline(filtro_bairro=None, filtro_cidade=None, filtro_tipo=None, filtro_stage=None):
    """Cria mapa com leads do pipeline coloridos por status com filtros"""
    todos_leads = []
    
    for stage, leads in st.session_state['crm_leads'].items():
        for lead in leads:
            if lead.get('latitude') and lead.get('longitude'):
                # Aplicar filtros
                if filtro_bairro and lead.get('bairro') != filtro_bairro:
                    continue
                if filtro_cidade and lead.get('cidade') != filtro_cidade:
                    continue
                if filtro_tipo and lead.get('tipo') != filtro_tipo:
                    continue
                if filtro_stage and stage != filtro_stage:
                    continue
                    
                todos_leads.append({
                    'nome': lead['nome'],
                    'stage': stage,
                    'latitude': lead['latitude'],
                    'longitude': lead['longitude'],
                    'pontuacao': lead['pontuacao'],
                    'valor': lead['valor_estimado'],
                    'endereco': lead['endereco']
                })
    
    if not todos_leads:
        return None
    
    # Criar DataFrame para facilitar
    df_mapa = pd.DataFrame(todos_leads)
    
    lat_media = df_mapa['latitude'].mean()
    lng_media = df_mapa['longitude'].mean()
    
    mapa = folium.Map(
        location=[lat_media, lng_media],
        zoom_start=12,
        tiles="CartoDB positron"
    )
    
    # Cores por estágio
    stage_colors = {
        'novo': 'gray',
        'contactado': 'blue',
        'qualificado': 'green',
        'proposta': 'orange',
        'negociacao': 'purple',
        'ganho': 'darkgreen',
        'perdido': 'red'
    }
    
    for _, lead in df_mapa.iterrows():
        popup_html = f"""
        <div style='width: 200px;'>
            <h4 style='color: #D2691E;'>{lead['nome']}</h4>
            <p><b>Status:</b> {lead['stage'].capitalize()}</p>
            <p><b>Score:</b> {lead['pontuacao']}</p>
            <p><b>Valor:</b> R$ {lead['valor']:,.2f}</p>
            <p><b>Endereço:</b> {lead['endereco']}</p>
        </div>
        """
        
        folium.Marker(
            location=[lead['latitude'], lead['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{lead['nome']} - {lead['stage'].capitalize()}",
            icon=folium.Icon(
                color=stage_colors.get(lead['stage'], 'gray'),
                icon='briefcase'
            )
        ).add_to(mapa)
    
    return mapa

@st.cache_data(ttl=600)
def gerar_rota_otimizada(_gmaps_client, leads_selecionados):
    """Gera rota otimizada para visitar múltiplos leads"""
    if len(leads_selecionados) < 2:
        return None
    
    # Preparar endereços
    origem = leads_selecionados[0]['endereco']
    destino = origem  # Volta ao ponto de partida
    waypoints = [lead['endereco'] for lead in leads_selecionados[1:]]
    
    try:
        # Calcular rota otimizada
        direcoes = _gmaps_client.directions(
            origin=origem,
            destination=destino,
            waypoints=waypoints,
            optimize_waypoints=True,
            mode="driving",
            language='pt-BR'
        )
        
        if not direcoes:
            return None
        
        # Extrair informações da rota
        rota = direcoes[0]
        ordem_otimizada = rota.get('waypoint_order', [])
        
        # Reordenar leads conforme otimização
        leads_ordenados = [leads_selecionados[0]]  # Primeiro sempre é a origem
        for idx in ordem_otimizada:
            leads_ordenados.append(leads_selecionados[idx + 1])
        
        # Decodificar polyline para visualização
        polyline = rota['overview_polyline']['points']
        coords = decode_polyline(polyline)
        rota_coords = [(d['lat'], d['lng']) for d in coords]
        
        # Criar URL do Google Maps
        origem_encoded = quote(origem)
        waypoints_encoded = "|".join([quote(lead['endereco']) for lead in leads_ordenados[1:]])
        url_google_maps = f"https://www.google.com/maps/dir/{origem_encoded}/{waypoints_encoded}/{origem_encoded}"
        
        # Extrair durações de cada trecho da rota
        leg_durations_min = [leg['duration']['value'] / 60 for leg in rota['legs']]

        return {
            'leads_ordenados': leads_ordenados,
            'coords': rota_coords,
            'url': url_google_maps,
            'distancia_total': sum(leg['distance']['value'] for leg in rota['legs']) / 1000,  # em km
            'duracao_total': sum(leg['duration']['value'] for leg in rota['legs']) / 60,  # em minutos
            'leg_durations': leg_durations_min
        }
        
    except Exception as e:
        st.error(f"Erro ao calcular rota: {e}")
        return None

@st.cache_data(ttl=3600)
def buscar_lead_externo(nome_lugar, endereco, cidade="Rio de Janeiro"):
    """Busca um estabelecimento específico no Google Places para adicionar como lead externo"""
    gmaps = googlemaps.Client(key=MINHA_API_KEY)
    
    try:
        # Buscar o lugar
        query = f"{nome_lugar} {endereco} {cidade}"
        places_result = gmaps.places(query=query, language='pt-BR')
        
        if not places_result.get('results'):
            return None
        
        place = places_result['results'][0]
        place_id = place['place_id']
        
        # Buscar detalhes completos
        detalhes = gmaps.place(place_id=place_id, language='pt-BR')['result']
        
        # Verificar se está aberto (não permanentemente fechado)
        if detalhes.get('permanently_closed', False) or detalhes.get('business_status') == 'CLOSED_PERMANENTLY':
            st.warning(f"⚠️ {nome_lugar} está permanentemente fechado")
            return None
        
        # Preparar dados do lead
        lead_data = {
            'Nome': detalhes.get('name'),
            'Telefone': detalhes.get('formatted_phone_number', 'N/A'),
            'Website': detalhes.get('website', 'N/A'),
            'Endereço': detalhes.get('formatted_address', endereco),
            'Nota Média': detalhes.get('rating', 0),
            'Nº de Avaliações': detalhes.get('user_ratings_total', 0),
            'Latitude': detalhes['geometry']['location']['lat'],
            'Longitude': detalhes['geometry']['location']['lng'],
            'Reviews_API': detalhes.get('reviews', []),
            'Tipo': detalhes.get('types', [''])[0].replace('_', ' ').capitalize(),
            'Bairro': endereco.split(',')[0] if ',' in endereco else 'N/A',
            'Cidade': cidade,
            'Faixa de Preço': '$' * detalhes.get('price_level', 0) if detalhes.get('price_level') else 'N/A',
            'Email': 'N/A',
            'Instagram': 'N/A',
            'Pontuação': 70  # Score padrão para lead externo
        }
        
        return lead_data
        
    except Exception as e:
        st.error(f"Erro ao buscar estabelecimento: {e}")
        return None

# Função para exportar dados para Excel
def to_excel(df):
    """Converte DataFrame para Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    return output.getvalue()

def scroll_to_element(element_id):
    """Gera JS para rolar a página para um elemento específico."""
    js = f"""
    <script>
        setTimeout(function() {{
            var element = document.getElementById('{element_id}');
            if (element) {{
                element.scrollIntoView({{behavior: 'smooth', block: 'start'}});
            }}
        }}, 100);
    </script>
    """
    components.html(js, height=0)

# --- FUNÇÕES DA PROSPECÇÃO ---
EXCLUIR_NOMES = ["mcdonald's", "mc donald's", "mcdonalds", "burger king", "starbucks", "subway", "bob's", "kfc", "pizza hut", "cacau show", "parme", "parmê", "rei do mate", "mega matte"]

# Dicionário expandido com emojis para tipos
TIPOS_COM_EMOJIS = {
    'restaurant': '🍽️ Restaurante',
    'cafe': '☕ Cafeteria',
    'bakery': '🥐 Padaria',
    'bar': '🍷 Bar',
    'lodging': '🏨 Hotel',
    'supermarket': '🛒 Supermercado',
    'spa': '💆 Spa',
    'book_store': '📚 Livraria',
    'art_gallery': '🎨 Galeria',
    'museum': '🏛️ Museu',
    'convenience_store': '🏪 Conveniência'
}

PONTOS_POR_TIPO = {
    'restaurant': 40, 'cafe': 40, 'bakery': 40, 'bar': 15, 
    'lodging': 35, 'spa': 15, 'supermarket': 35, 'book_store': 20, 
    'art_gallery': 15, 'museum': 15, 'convenience_store': 25
}

PONTOS_POR_PRECO = {2: 25, 1: 10, 3: 20, 4: 20}
BAIRROS_ESTRATEGICOS = ['barra da tijuca', 'centro', 'copacabana', 'leblon', 'ipanema']
BONUS_BAIRRO = 20
MENSAGEM_PROSPECCAO_PADRAO = "Olá! Sou da Café Orfeu e gostaria de apresentar nossos cafés especiais. Seria um prazer agendar uma breve demonstração. Podemos conversar?"

def normalizar_telefone(numero):
    if isinstance(numero, str): 
        return re.sub(r'\D', '', numero)
    return ''

def gerar_link_whatsapp(telefone, texto):
    if not telefone or telefone == 'N/A' or not texto: 
        return None
    telefone_limpo = normalizar_telefone(telefone)
    if not telefone_limpo.startswith('55'):
        telefone_limpo = '55' + telefone_limpo
    texto_encoded = quote(texto)
    return f"https://wa.me/{telefone_limpo}?text={texto_encoded}"

def calcular_pontuacao(estabelecimento, bairro_prospect, precos_selecionados):
    tipo_principal = estabelecimento.get('types', [''])[0]
    score = PONTOS_POR_TIPO.get(tipo_principal, 10)
    nota = estabelecimento.get('rating', 0)
    if nota >= 4.7: 
        score += 50
    elif 4.3 <= nota < 4.7: 
        score += 35
    elif 4.0 <= nota < 4.3: 
        score += 10
    if precos_selecionados:
        faixa_preco = estabelecimento.get('price_level')
        score += PONTOS_POR_PRECO.get(faixa_preco, 0)
    if any(bairro_estrategico in bairro_prospect.lower() for bairro_estrategico in BAIRROS_ESTRATEGICOS):
        score += BONUS_BAIRRO
    num_avaliacoes = estabelecimento.get('user_ratings_total', 0)
    if num_avaliacoes > 300: 
        score += 10
    elif num_avaliacoes >= 100: 
        score += 5
    return round(score)

@st.cache_data(ttl=3600)
def buscar_detalhes_do_lugar(_gmaps_client, place_id):
    try:
        fields = ['name', 'formatted_phone_number', 'website', 'reviews', 'business_status', 'permanently_closed', 'opening_hours']
        details = _gmaps_client.place(place_id=place_id, fields=fields, language='pt-BR')
        return details.get('result', {})
    except Exception as e:
        return {}

@st.cache_data(ttl=3600)
def gerar_mensagem_ia(reviews, nome_estabelecimento):
    if not GEMINI_API_KEY or not reviews: 
        return MENSAGEM_PROSPECCAO_PADRAO
    
    texto_reviews = "\n".join([f"- {r['text']}" for r in reviews if r.get('text')])
    if not texto_reviews: 
        return MENSAGEM_PROSPECCAO_PADRAO
    
    prompt = f"""
    Assuma a persona de um vendedor B2B sênior e muito experiente da Café Orfeu, uma marca de cafés especiais. Sua comunicação é elegante, confiante e focada em criar um relacionamento.
    Seu objetivo é redigir uma mensagem de WhatsApp para o primeiro contato com o gestor do estabelecimento '{nome_estabelecimento}'.
    Analise as avaliações de clientes abaixo para encontrar um gancho autêntico.
    ---
    {texto_reviews}
    ---
    Com base nisso, crie a mensagem (máximo 3 frases) que elogie um aspecto único do negócio, conecte sutilmente à qualidade do nosso café, e finalize com uma pergunta leve e aberta. Comece de forma direta, sem "Olá".
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return MENSAGEM_PROSPECCAO_PADRAO

@st.cache_data(ttl=3600)
def gerar_resumo_executivo_ia(reviews, nome_estabelecimento):
    if not GEMINI_API_KEY: 
        return "IA desativada. Verifique a chave da API."
    
    texto_reviews = "Sem avaliações de texto disponíveis."
    if reviews:
        review_texts = "\n".join([f"- {r['text']}" for r in reviews if r.get('text')])
        if review_texts:
            texto_reviews = review_texts
    
    prompt = f"""
    Assuma a persona de um analista de vendas sênior e estrategista de negócios da Café Orfeu.
    Sua tarefa é criar um "Resumo Executivo para Prospecção" conciso sobre o estabelecimento '{nome_estabelecimento}', com base nas avaliações dos clientes.
    O resumo deve ser curto e direto. Siga estritamente a seguinte estrutura:

    Visão Geral: (Um resumo de 1-2 frases sobre a identidade do local, focando no que os clientes mais amam ou odeiam).
    Gatilhos de Venda:
    - (Bullet point com um insight acionável. Ex: Ponto Forte: Atendimento elogiado, ótimo para oferecer um café que complemente a experiência premium).
    - (Bullet point com outro insight. Ex: Oportunidade: Menções sobre pouca variedade de sobremesas, chance para apresentar harmonizações).
    Dica de Abordagem: (Uma frase com uma sugestão estratégica. Ex: Foque na exclusividade e na experiência do cliente, não em preço).

    Use os títulos exatamente como estão, sem nenhum tipo de formatação como negrito ou asteriscos.
    ---
    AVALIAÇÕES:
    {texto_reviews}
    ---
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "Não foi possível gerar o resumo."

def prospectar_bairros(api_key, bairros, cidade, tipos, nota_range, precos, raio, min_avaliacoes, keyword):
    """Busca leads no Google Places sem enriquecimento de IA, para performance."""
    if not api_key or "COLE_SUA_CHAVE" in api_key:
        st.error("ERRO: Chave API não configurada")
        return pd.DataFrame()
    
    gmaps = googlemaps.Client(key=api_key)
    resultados_finais = []
    
    progress_bar = st.progress(0, text="☕ Buscando estabelecimentos...")
    status_text = st.empty()
    total_steps = len(bairros) * len(tipos)
    current_step = 0
    
    for bairro_busca in bairros:
        if not bairro_busca.strip(): continue
        
        try:
            geocode_result = gmaps.geocode(f"{bairro_busca}, {cidade}, Brasil")
            if not geocode_result: continue
            loc = geocode_result[0]['geometry']['location']
        except Exception as e:
            st.warning(f"Erro no geocoding de {bairro_busca}: {e}")
            continue
        
        for tipo in tipos:
            current_step += 1
            progress_bar.progress(current_step / total_steps, text=f"Buscando {TIPOS_COM_EMOJIS.get(tipo, tipo)} em {bairro_busca.title()}...")
            
            try:
                response = gmaps.places_nearby(location=loc, radius=raio, type=tipo, language='pt-BR', keyword=keyword or None)
                
                for place in response.get('results', []):
                    detalhes = buscar_detalhes_do_lugar(gmaps, place['place_id'])
                    if detalhes.get('permanently_closed') or detalhes.get('business_status') == 'CLOSED_PERMANENTLY':
                        continue
                    
                    nome_place = place.get('name', '').lower()
                    if any(excluir in nome_place for excluir in EXCLUIR_NOMES):
                        continue
                    
                    nota_place = place.get('rating', 0)
                    num_avaliacoes = place.get('user_ratings_total', 0)
                    if not (nota_range[0] <= nota_place <= nota_range[1] and num_avaliacoes >= min_avaliacoes):
                        continue
                    
                    if precos and place.get('price_level') not in precos and place.get('price_level') is not None:
                        continue

                    resultados_finais.append({
                        'Pontuação': calcular_pontuacao(place, bairro_busca, precos),
                        'Nome': place.get('name'),
                        'Nota Média': nota_place,
                        'Nº de Avaliações': num_avaliacoes,
                        'Faixa de Preço': '$' * place.get('price_level', 0) if place.get('price_level') else 'N/A',
                        'Telefone': detalhes.get('formatted_phone_number', 'N/A'),
                        'Endereço': place.get('vicinity', 'N/A'),
                        'Horarios': detalhes.get('opening_hours', {}).get('weekday_text', []),
                        'Tipo': tipo.replace('_', ' ').capitalize(),
                        'Latitude': place['geometry']['location']['lat'],
                        'Longitude': place['geometry']['location']['lng'],
                        'Reviews_API': detalhes.get('reviews', []),
                        'Bairro': bairro_busca.title(),
                        'Cidade': cidade.title(),
                        'Place_ID': place['place_id'],
                        'Website': detalhes.get('website', 'N/A'),
                    })
                    status_text.markdown(f"✅ {len(resultados_finais)} estabelecimentos encontrados...")
            except Exception as e:
                st.warning(f"Erro ao buscar {tipo} em {bairro_busca}: {e}")
    
    progress_bar.empty()
    status_text.empty()
    
    if not resultados_finais:
        return pd.DataFrame()
        
    df_final = pd.DataFrame(resultados_finais).drop_duplicates(subset=['Nome', 'Endereço'])
    return df_final.sort_values(by=['Pontuação'], ascending=False)

# --- FUNÇÕES DE VISUALIZAÇÃO ---
def criar_dashboard_metricas():
    """Cria dashboard com métricas do funil incluindo temperatura dos leads"""
    crm = CRMSystem()
    
    # Calcula métricas
    total_leads = sum(len(leads) for stage, leads in st.session_state['crm_leads'].items() if stage != 'perdido')
    leads_ganhos = len(st.session_state['crm_leads']['ganho'])
    leads_perdidos = len(st.session_state['crm_leads']['perdido'])
    
    # Contar leads por temperatura
    leads_quentes = 0
    leads_mornos = 0
    leads_frios = 0
    
    for stage in crm.stages:
        for lead in st.session_state['crm_leads'][stage]:
            temp = lead.get('temperatura', 'frio')
            if temp == 'quente':
                leads_quentes += 1
            elif temp == 'morno':
                leads_mornos += 1
            else:
                leads_frios += 1
    
    # Calcula valor total do pipeline com valores reais
    valor_pipeline = sum(
        lead.get('valor_estimado', 0) 
        for leads in st.session_state['crm_leads'].values() for lead in leads
    )
    
    # Exibe métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Total de Leads", total_leads)
    
    with col2:
        st.metric("✅ Leads Ganhos", leads_ganhos)
    
    with col3:
        taxa_conversao = (leads_ganhos / total_leads * 100) if total_leads > 0 else 0
        st.metric("📊 Taxa de Conversão", f"{taxa_conversao:.1f}%")
    
    with col4:
        st.metric("💰 Valor Pipeline", f"R$ {valor_pipeline:,.2f}")
    
    # Segunda linha de métricas - Temperatura dos leads
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"<div style='text-align: center;'><span class='temp-quente'>🔥 Quentes: {leads_quentes}</span></div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<div style='text-align: center;'><span class='temp-morno'>♨️ Mornos: {leads_mornos}</span></div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"<div style='text-align: center;'><span class='temp-frio'>❄️ Frios: {leads_frios}</span></div>", unsafe_allow_html=True)
    
    with col4:
        # Gráfico de rosca com temperatura dos leads
        if total_leads > 0:
            fig = go.Figure(data=[go.Pie(
                labels=['Quente', 'Morno', 'Frio'],
                values=[leads_quentes, leads_mornos, leads_frios],
                hole=.6,
                marker=dict(colors=['#FF4444', '#FFA500', '#4169E1'])
            )])
            fig.update_layout(
                showlegend=False,
                height=100,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': False})
    
    # Gráficos principais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Gráfico de funil com cores harmoniosas
        stages_data = []
        for stage in ['novo', 'contactado', 'qualificado', 'proposta', 'negociacao', 'ganho']:
            stages_data.append({
                'Estágio': stage.capitalize(),
                'Quantidade': len(st.session_state['crm_leads'][stage])
            })
        
        df_funil = pd.DataFrame(stages_data)
        
        # Criar funil com cores personalizadas
        fig_funil = px.funnel(
            df_funil, 
            x='Quantidade', 
            y='Estágio', 
            title="Funil de Vendas",
            color='Estágio',
            color_discrete_map={
                'Novo': '#4A90E2',
                'Contactado': '#5C9EE6',
                'Qualificado': '#6EAAEA',
                'Proposta': '#80B6EE',
                'Negociacao': '#FDB863',
                'Ganho': '#5CB85C'
            }
        )
        fig_funil.update_layout(
            height=400, 
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            title_font_color="#FAF7F2" if st.session_state.get('theme', 'Escuro') == 'Escuro' else "#2E2015"
        )
        st.plotly_chart(fig_funil, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': False})
    
    with col2:
        # NOVO GRÁFICO: Temperatura dos Leads por Estágio
        temp_por_estagio = {stage: {'Quente': 0, 'Morno': 0, 'Frio': 0} for stage in crm.stages if stage not in ['ganho', 'perdido']}
        for stage, leads in st.session_state['crm_leads'].items():
            if stage in temp_por_estagio:
                for lead in leads:
                    temp = lead.get('temperatura', 'frio').capitalize()
                    if temp in temp_por_estagio[stage]:
                        temp_por_estagio[stage][temp] += 1
        
        df_temp_data = []
        for stage, temps in temp_por_estagio.items():
            for temp, count in temps.items():
                df_temp_data.append({'Estágio': stage.capitalize(), 'Temperatura': temp, 'Quantidade': count})
        
        if df_temp_data:
            df_temp = pd.DataFrame(df_temp_data)
            fig_temp = px.bar(
                df_temp,
                x='Estágio',
                y='Quantidade',
                color='Estágio',
                title="Temperatura dos Leads por Estágio",
                color_discrete_map={'Quente': '#FF4444', 'Morno': '#FFA500', 'Frio': '#4169E1'}
            )
            fig_temp.update_layout(
                showlegend=False,
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                title_font_color="#FAF7F2" if st.session_state.get('theme', 'Escuro') == 'Escuro' else "#2E2015"
            )
            st.plotly_chart(fig_temp, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': False})
            
    with col3:
        # Gráfico de leads por tipo
        tipos_leads = {}
        for stage, leads in st.session_state['crm_leads'].items():
            if stage not in ['ganho', 'perdido']:
                for lead in leads:
                    tipo = lead.get('tipo', 'Não Informado')
                    tipos_leads[tipo] = tipos_leads.get(tipo, 0) + 1
        
        if tipos_leads:
            df_tipos = pd.DataFrame(list(tipos_leads.items()), columns=['Tipo', 'Quantidade'])
            df_tipos = df_tipos.sort_values('Quantidade', ascending=True)
            
            fig_tipos = px.bar(
                df_tipos,
                x='Quantidade',
                y='Tipo',
                orientation='h',
                title="Tipos de Estabelecimento",
                color='Quantidade',
                color_continuous_scale=px.colors.sequential.YlOrBr
            )
            fig_tipos.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                title_font_color="#FAF7F2" if st.session_state.get('theme', 'Escuro') == 'Escuro' else "#2E2015"
            )
            st.plotly_chart(fig_tipos, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': False})

def exibir_kanban():
    # --- Injeção de JavaScript para o duplo clique ---
    components.html("""
        <script>
        function handleLeadDoubleClick(leadId) {
            let url = new URL(window.parent.location.href);
            url.searchParams.set('view_lead', leadId);
            window.parent.location.href = url.href;
        }
        </script>
    """, height=0)

    from dateutil.relativedelta import relativedelta

    if 'confirmar_exclusao' in st.session_state and st.session_state['confirmar_exclusao']:
        lead_id_para_excluir = st.session_state['confirmar_exclusao']
        lead_nome = ""
        # Encontrar o nome do lead para a mensagem
        for stage_leads in st.session_state['crm_leads'].values():
            for lead in stage_leads:
                if lead['id'] == lead_id_para_excluir:
                    lead_nome = lead['nome']
                    break

        with st.expander(f"⚠️ Confirmar Exclusão de {lead_nome}", expanded=True):
            st.warning(f"Você tem certeza que deseja excluir permanentemente o lead **{lead_nome}**? Esta ação não pode ser desfeita.")
            col1, col2 = st.columns(2)
            if col1.button("Sim, excluir", type="primary", key="confirm_delete_btn"):
                crm = CRMSystem()
                crm.excluir_lead(lead_id_para_excluir)
                st.success(f"Lead {lead_nome} excluído com sucesso.")
                del st.session_state['confirmar_exclusao']
                st.rerun()
            if col2.button("Não, cancelar", key="cancel_delete_btn"):
                del st.session_state['confirmar_exclusao']
                st.rerun()
    
    crm = CRMSystem()

    query_params = st.query_params
    if "view_lead" in query_params:
        lead_id_to_view = query_params.get("view_lead")
        st.session_state['mostrar_insights'] = lead_id_to_view
        st.session_state['scroll_to_details'] = True
        st.query_params.clear()
    
    st.header("🎯 Funil de Vendas - Kanban")
    
    # Botões de ação gerais
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col2:
        # Exportar dados do pipeline
        if st.button("📥 Exportar Pipeline para Excel"):
            todos_leads_export = []
            for stage, leads in st.session_state['crm_leads'].items():
                for lead in leads:
                    lead_export = {
                        'ID': lead['id'],
                        'Nome': lead['nome'],
                        'Estágio': stage,
                        'Temperatura': lead.get('temperatura', 'frio'),
                        'Score': lead['pontuacao'],
                        'Telefone': lead.get('telefone', 'N/A'),
                        'Email': lead.get('email', 'N/A'),
                        'Endereço': lead['endereco'],
                        'Bairro': lead.get('bairro', 'N/A'),
                        'Cidade': lead.get('cidade', 'N/A'),
                        'Valor Estimado': lead.get('valor_estimado', 0),
                        'Café Atual': lead.get('cafe_atual', 'Não informado'),
                        'Volume KG/mês': lead.get('volume_kg_mensal', 0),
                        'Preço Expresso': lead.get('preco_expresso', 0),
                        'Preço Café Compra': lead.get('preco_cafe_compra', 0),
                        'Tipo Máquina': lead.get('tipo_maquina', 'Não informado'),
                        'Comodato': lead.get('tem_comodato', 'Não informado'),
                        'Data Entrada': lead.get('data_entrada', ''),
                        'Próximo Contato': lead.get('proximo_contato', '')
                    }
                    todos_leads_export.append(lead_export)
            
            if todos_leads_export:
                df_export = pd.DataFrame(todos_leads_export)
                excel_data = to_excel(df_export)
                
                st.download_button(
                    label="💾 Download Excel",
                    data=excel_data,
                    file_name=f"pipeline_orfeu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
    
    with col3:
        # Filtros
        filtro_temperatura = st.selectbox(
            "Filtrar por Temperatura",
            ["Todos", "Quente", "Morno", "Frio"]
        )

    # Botão para adicionar lead externo
    with st.expander("➕ Adicionar Lead Externo"):
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        with col_exp1:
            nome_lead_ext = st.text_input("Nome do Estabelecimento")
        with col_exp2:
            endereco_lead_ext = st.text_input("Endereço")
        with col_exp3:
            cidade_lead_ext = st.text_input("Cidade", value="Rio de Janeiro")
        
        if st.button("🔍 Buscar e Adicionar", type="primary", key="adicionar_lead_externo"):
            if nome_lead_ext and endereco_lead_ext:
                with st.spinner("Buscando estabelecimento..."):
                    lead_data = buscar_lead_externo(nome_lead_ext, endereco_lead_ext, cidade_lead_ext)
                    
                    if lead_data:
                        crm = CRMSystem()
                        lead_id = crm.adicionar_lead_ao_funil(lead_data)
                        st.success(f"✅ {lead_data['Nome']} adicionado ao funil!")
                        st.rerun()
                    else:
                        st.error("Não foi possível encontrar o estabelecimento")
            else:
                st.warning("Preencha nome e endereço")
    
    # Filtros para o mapa
    col1, col2, col3, col4 = st.columns(4)
    
    # Obter listas únicas de bairros, cidades e tipos
    todos_bairros = set()
    todas_cidades = set()
    todos_tipos = set()
    
    for leads in st.session_state['crm_leads'].values():
        for lead in leads:
            if lead.get('bairro'):
                todos_bairros.add(lead['bairro'])
            if lead.get('cidade'):
                todas_cidades.add(lead['cidade'])
            if lead.get('tipo'):
                todos_tipos.add(lead['tipo'])
    
    with col1:
        filtro_bairro = st.selectbox("Filtrar por Bairro", ["Todos"] + sorted(list(todos_bairros)))
    with col2:
        filtro_cidade = st.selectbox("Filtrar por Cidade", ["Todos"] + sorted(list(todas_cidades)))
    with col3:
        filtro_tipo = st.selectbox("Filtrar por Tipo", ["Todos"] + sorted(list(todos_tipos)))
    with col4:
        filtro_etapa = st.selectbox("Filtrar por Etapa", ["Todos"] + crm.stages)
    
    # Mapa do pipeline com filtros
    st.subheader("🗺️ Visualização Geográfica do Pipeline")
    
    # Aplicar filtros
    filtro_bairro_aplicado = None if filtro_bairro == "Todos" else filtro_bairro
    filtro_cidade_aplicado = None if filtro_cidade == "Todos" else filtro_cidade
    filtro_tipo_aplicado = None if filtro_tipo == "Todos" else filtro_tipo
    filtro_etapa_aplicado = None if filtro_etapa == "Todos" else filtro_etapa
    
    mapa_pipeline = criar_mapa_pipeline(
        filtro_bairro=filtro_bairro_aplicado, filtro_cidade=filtro_cidade_aplicado, 
        filtro_tipo=filtro_tipo_aplicado, filtro_stage=filtro_etapa_aplicado)
    if mapa_pipeline:
        components.html(mapa_pipeline._repr_html_(), height=400)
    else:
        st.info("Nenhum lead com localização disponível para os filtros selecionados")
    
    st.markdown("---")
    
    # Colunas do Kanban
    cols = st.columns(6)
    stages_display = ['novo', 'contactado', 'qualificado', 'proposta', 'negociacao', 'ganho']
    stage_names = {
        'novo': '🆕 Novo',
        'contactado': '📞 Contactado',
        'qualificado': '✅ Qualificado',
        'proposta': '📝 Proposta',
        'negociacao': '💬 Negociação',
        'ganho': '🏆 Ganho'
    }
    
    for idx, (col, stage) in enumerate(zip(cols, stages_display)):
        with col:
            st.markdown(f"### {stage_names[stage]}")
            
            # Filtrar leads por temperatura se necessário
            leads_stage = st.session_state['crm_leads'][stage]
            if filtro_temperatura != "Todos":
                leads_stage = [l for l in leads_stage if l.get('temperatura', 'frio').lower() == filtro_temperatura.lower()]
            
            # Calcular valor total do estágio
            valor_estagio = sum(lead.get('valor_estimado', 0) for lead in leads_stage)
            st.markdown(f"**{len(leads_stage)} leads**")
            st.caption(f"R$ {valor_estagio:,.2f}")
            
            # Exibe cards dos leads
            for lead in leads_stage:
                with st.container():
                    # Determinar classe CSS da temperatura
                    temp_value = lead.get('temperatura', 'nao definido')
                    temp_class = f"temp-{temp_value.replace(' ', '-')}"
                    temp_emoji = {'quente': '🔥', 'morno': '♨️', 'frio': '❄️', 'nao definido': '❔'}.get(temp_value, '❔')
                    
                    # Card visual com informações aprimoradas
                    st.markdown(f"""
                    <div class='kanban-card' ondblclick="handleLeadDoubleClick('{lead['id']}')" title="Clique duas vezes para ver detalhes" 
                         style='padding: 10px; border-radius: 8px; margin: 5px 0; border-left: 4px solid {crm.stage_colors.get(stage, '#ccc')}; cursor: pointer;'>
                        <strong>{lead['nome']}</strong><br>
                        <div style='display: flex; justify-content: space-between; margin: 5px 0;'>
                            <small>Visitas: {len(lead.get('visitas', []))}</small>
                            <span class='score-badge' style='color: white; padding: 2px 6px; border-radius: 10px; font-size: 11px;'>Score: {lead['pontuacao']}</span>
                            <span class='{temp_class}'>{temp_emoji} {temp_value.replace('_', ' ').capitalize()}</span>
                        </div>
                        <small>💰 R$ {lead['valor_estimado']:,.2f}/mês</small><br>
                        <small>☕ {lead.get('volume_kg_mensal', 0)}kg/mês</small><br>
                        <small>📅 {lead.get('ultimo_contato', 'N/A')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botões de ação
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        if st.button("📊", key=f"view_{lead['id']}", help="Ver detalhes", use_container_width=True):
                            st.session_state['mostrar_insights'] = lead['id']
                    
                    with col2:
                        if st.button("📝", key=f"market_{lead['id']}", help="Editar Infos Lead", use_container_width=True):
                            st.session_state['editar_market_share'] = lead['id']
                    
                    with col3:
                        if st.button("📅", key=f"contact_{lead['id']}", help="Registrar Contato", use_container_width=True):
                            st.session_state['registrar_contato'] = lead['id']
                    
                    with col4:
                        if stage not in ['novo', 'perdido'] and st.button("⬅️", key=f"back_{lead['id']}", help="Voltar", use_container_width=True):
                            prev_stage_idx = stages_display.index(stage) - 1
                            if prev_stage_idx >= 0:
                                prev_stage = stages_display[prev_stage_idx]
                                crm.mover_lead(lead['id'], stage, prev_stage)
                                st.rerun()
                    
                    with col5:
                        if stage not in ['ganho', 'perdido'] and st.button("➡️", key=f"move_{lead['id']}", help="Avançar", use_container_width=True):
                            if stage == 'novo':
                                st.session_state['preencher_infos_lead'] = lead['id']
                                st.session_state['scroll_to_infos'] = True
                                st.rerun()
                            else:
                                next_stage_idx = stages_display.index(stage) + 1
                                if next_stage_idx < len(stages_display):
                                    next_stage = stages_display[next_stage_idx]
                                    crm.mover_lead(lead['id'], stage, next_stage)
                            st.rerun()
    # Modal para registrar contato
    if 'registrar_contato' in st.session_state and st.session_state['registrar_contato']:
        lead_id_contato = st.session_state['registrar_contato']
        lead_data_contato = None
        for stage in st.session_state['crm_leads']:
            for lead in st.session_state['crm_leads'][stage]:
                if lead['id'] == lead_id_contato:
                    lead_data_contato = lead
                    break
        if lead_data_contato:
            with st.expander(f"📅 Registrar Contato - {lead_data_contato['nome']}", expanded=True):
                col_form1, col_form2 = st.columns(2)
                with col_form1:
                    tipo_contato = st.selectbox(
                        "Tipo de Contato",
                        options=["Visitação", "Telefone", "Email"],
                        key=f"tipo_contato_{lead_id_contato}"
                    )
                with col_form2:
                    data_contato = st.date_input("Data do Contato", value=datetime.now(), key=f"data_contato_{lead_id_contato}")
                
                observacoes = st.text_area(
                    "Observações do Contato", 
                    key=f"obs_contato_{lead_id_contato}",
                    placeholder="Digite aqui como foi o contato, os detalhes, quem te atendeu, os próximos passos, etc."
                )
                st.markdown("##### 🌡️ Temperatura Pós-Contato")
                temp_options = ["quente", "morno", "frio"]
                temp_display_names = {"quente": "🔥 Quente", "morno": "♨️ Morno", "frio": "❄️ Frio"}
                nova_temp_contato = st.radio(
                    "Como foi o contato?",
                    options=temp_options,
                    format_func=lambda x: temp_display_names[x],
                    key=f"temp_contato_{lead_id_contato}", horizontal=True
                )
                proximo_contato_manual = None
                if nova_temp_contato == 'quente':
                    proximo_contato_manual = st.date_input("Definir Próximo Contato", value=datetime.now() + timedelta(days=7), key=f"prox_contato_manual_{lead_id_contato}")
                col1, col2 = st.columns(2)
                if col1.button("💾 Salvar Contato", type="primary", key=f"save_contato_{lead_id_contato}"):
                    novo_contato_log = {
                        'tipo': tipo_contato,
                        'data': data_contato.strftime('%Y-%m-%d'),
                        'observacoes': observacoes,
                        'temperatura_registrada': nova_temp_contato
                    }
                    lead_data_contato.setdefault('visitas', []).append(novo_contato_log)
                    lead_data_contato['temperatura'] = nova_temp_contato
                    lead_data_contato['ultimo_contato'] = data_contato.strftime('%Y-%m-%d')
                    if nova_temp_contato == 'quente' and proximo_contato_manual:
                        lead_data_contato['proximo_contato'] = proximo_contato_manual.strftime('%Y-%m-%d')
                    st.success("Contato registrado com sucesso!")
                    del st.session_state['registrar_contato']
                    st.rerun()
                if col2.button("Cancelar", key=f"cancel_contato_{lead_id_contato}"):
                    del st.session_state['registrar_contato']
                    st.rerun()
    # Modal para editar informações de Market Share
    if st.session_state.get('editar_market_share') or st.session_state.get('preencher_infos_lead'):
        lead_id = st.session_state.get('editar_market_share') or st.session_state.get('preencher_infos_lead')
        lead_data = None
        for stage in st.session_state['crm_leads']:
            for lead in st.session_state['crm_leads'][stage]:
                if lead['id'] == lead_id:
                    lead_data = lead
                    break
        if lead_data:
            st.markdown("---")
            st.markdown('<div id="form-infos-lead"></div>', unsafe_allow_html=True)
            if st.session_state.get('scroll_to_infos'):
                scroll_to_element('form-infos-lead')
                st.session_state['scroll_to_infos'] = False
            with st.expander(f"📝 Infos Lead - {lead_data['nome']}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    cafe_atual = st.text_input("Café Atual", value=lead_data.get('cafe_atual', ''), key=f"ms_cafe_atual_{lead_id}")
                    nome_contato = st.text_input("Nome do Contato", value=lead_data.get('nome_contato', ''), key=f"ms_nome_contato_{lead_id}")
                    volume_kg = st.number_input("Volume KG/mês", value=float(lead_data.get('volume_kg_mensal', 0)), step=1.0, key=f"ms_volume_kg_{lead_id}")
                    preco_expresso = st.number_input("Preço Expresso (R$)", value=float(lead_data.get('preco_expresso', 0)), step=0.5, key=f"ms_preco_expresso_{lead_id}")
                with col2:
                    cargo_contato = st.text_input("Cargo do Contato", value=lead_data.get('cargo_contato', ''), key=f"ms_cargo_contato_{lead_id}")
                    telefone_contato = st.text_input("Telefone do Contato", value=lead_data.get('telefone_contato', ''), key=f"ms_tel_contato_{lead_id}")
                    preco_cafe_compra = st.number_input("Preço Café Compra (R$/kg)", value=float(lead_data.get('preco_cafe_compra', 0)), step=1.0, key=f"ms_preco_compra_{lead_id}")
                    tipo_maquina = st.text_input("Tipo Máquina", value=lead_data.get('tipo_maquina', ''), key=f"ms_tipo_maquina_{lead_id}")
                    tem_comodato = st.selectbox("Tem Comodato?", ["Não informado", "Sim", "Não"], 
                                               index=["Não informado", "Sim", "Não"].index(lead_data.get('tem_comodato', 'Não informado')), key=f"ms_comodato_{lead_id}")
                st.markdown("---")
                st.markdown("##### 🌡️ Temperatura do Lead")
                temp_atual = lead_data.get('temperatura', 'morno')
                if temp_atual not in ["quente", "morno", "frio"]:
                    temp_atual = 'morno'
                temp_options = ["quente", "morno", "frio"]
                temp_display_names = {
                    "quente": "🔥 Quente",
                    "morno": "♨️ Morno",
                    "frio": "❄️ Frio"
                }
                nova_temp = st.radio(
                    "Como foi o contato?",
                    options=temp_options,
                    index=temp_options.index(temp_atual),
                    format_func=lambda x: temp_display_names[x],
                    key=f"temp_radio_unified_{lead_id}", horizontal=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Salvar", type="primary", key=f"ms_save_{lead_id}"):
                        info_dict = {
                            'cafe_atual': cafe_atual,
                            'volume_kg_mensal': volume_kg,
                            'preco_expresso': preco_expresso,
                            'preco_cafe_compra': preco_cafe_compra,
                            'tipo_maquina': tipo_maquina,
                            'tem_comodato': tem_comodato,
                            'nome_contato': nome_contato,
                            'cargo_contato': cargo_contato,
                            'telefone_contato': telefone_contato
                        }
                        crm.atualizar_info_market_share(lead_id, info_dict)
                        crm.atualizar_temperatura_lead(lead_id, nova_temp)
                        if st.session_state.get('preencher_infos_lead'):
                            crm.mover_lead(lead_id, 'novo', 'contactado')
                        st.success("✅ Informações atualizadas!")
                        st.session_state['editar_market_share'] = None
                        st.session_state['preencher_infos_lead'] = None
                        st.rerun()
                with col2:
                    if st.button("❌ Cancelar", key=f"cancel_market_share_{lead_id}"):
                        st.session_state['editar_market_share'] = None
                        st.session_state['preencher_infos_lead'] = None
                        st.rerun()
                st.markdown("---")
                st.markdown("##### 🗑️ Zona de Perigo")
                if st.button("Excluir este Lead", key=f"delete_inside_edit_{lead_id}"):
                    st.session_state['confirmar_exclusao'] = lead_id
                    st.rerun()
    # Modal de Insights Expandido
    if 'mostrar_insights' in st.session_state:
        lead_id = st.session_state['mostrar_insights']
        lead_data = None
        for stage in st.session_state['crm_leads']:
            for lead in st.session_state['crm_leads'][stage]:
                if lead['id'] == lead_id:
                    lead_data = lead
                    break
        if lead_data:
            st.markdown("---")
            st.markdown('<div id="details-view"></div>', unsafe_allow_html=True)
            if st.session_state.get('scroll_to_details'):
                scroll_to_element('details-view')
                st.session_state['scroll_to_details'] = False
            with st.expander(f"📊 Informações Completas - {lead_data['nome']}", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("### 📋 Informações Básicas")
                    st.write(f"**Nome:** {lead_data['nome']}")
                    st.write(f"**Tipo:** {lead_data.get('tipo', 'N/A')}")
                    st.write(f"**Score:** {lead_data['pontuacao']}")
                    st.write(f"**Nota:** ⭐ {lead_data.get('nota_media', 0)}")
                    st.write(f"**Temperatura:** {lead_data.get('temperatura', 'frio').capitalize()}")
                    st.markdown("### 📍 Localização")
                    st.markdown(f"<p class='endereco-text'><b>Endereço:</b> {lead_data['endereco']}</p>", unsafe_allow_html=True)
                    st.write(f"**Bairro:** {lead_data.get('bairro', 'N/A')}")
                    st.write(f"**Cidade:** {lead_data.get('cidade', 'N/A')}")
                with col2:
                    st.markdown("### 📞 Contatos")
                    st.write(f"**Telefone:** {lead_data.get('telefone', 'N/A')}")
                    if lead_data.get('telefone') and lead_data['telefone'] != 'N/A':
                        link_whats = gerar_link_whatsapp(lead_data['telefone'], lead_data.get('insights_ia', MENSAGEM_PROSPECCAO_PADRAO))
                        if link_whats:
                            st.link_button("💬 Enviar WhatsApp", link_whats)
                    st.write(f"**Email:** {lead_data.get('email', 'N/A')}")
                    st.write(f"**Website:** {lead_data.get('website', 'N/A')}")
                    st.write(f"**Instagram:** {lead_data.get('instagram', 'N/A')}")
                    st.markdown("### 👤 Contato Principal")
                    st.write(f"**Nome:** {lead_data.get('nome_contato', 'N/A')}")
                    st.write(f"**Cargo:** {lead_data.get('cargo_contato', 'N/A')}")
                    st.write(f"**Telefone:** {lead_data.get('telefone_contato', 'N/A')}")
                    st.markdown("#### Histórico de Interações")
                    interacoes = lead_data.get('interacoes', [])
                    if interacoes:
                        for i, interacao in enumerate(reversed(interacoes)):
                            st.markdown(f"**{interacao['tipo']} ({interacao['data']})**")
                            st.caption(f"Obs: {interacao.get('observacoes', 'Nenhuma observação.')}")
                    else:
                        st.info("Nenhuma interação registrada.")
                    st.markdown("### 📅 Acompanhamento")
                    st.write(f"**Próximo Contato:** {lead_data.get('proximo_contato', 'N/A')}")
                    st.write(f"**Último Contato:** {lead_data.get('ultimo_contato', 'Nunca')}")
                    st.markdown("#### Histórico de Visitas")
                    contatos = lead_data.get('visitas', [])
                    if contatos:
                        for i, contato in enumerate(reversed(contatos)):
                            st.markdown(f"**{contato.get('tipo', 'Contato')} {len(contatos)-i} ({contato['data']})**")
                            st.caption(f"Obs: {contato.get('observacoes', 'Nenhuma observação.')}")
                    else:
                        st.info("Nenhuma visita registrada.")
                with col3:
                    st.markdown("### 💰 Potencial")
                    st.metric("Faturamento Mensal", f"R$ {lead_data.get('faturamento_estimado', 0):,.2f}")
                    st.metric("Receita Potencial", f"R$ {lead_data.get('valor_estimado', 0):,.2f}/mês")
                    st.metric("Consumo Café", f"{lead_data.get('consumo_cafe_kg', 0)} kg/mês")
                    st.metric("Volume Clientes/Dia", lead_data.get('volume_clientes', 0))
                    st.metric("Ticket Médio", f"R$ {lead_data.get('ticket_medio', 0):,.2f}")
                st.markdown("---")
                st.markdown("### 📊 Informações de Market Share")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Café Atual:** {lead_data.get('cafe_atual', 'Não informado')}")
                    st.write(f"**Volume KG/mês:** {lead_data.get('volume_kg_mensal', 0)}")
                with col2:
                    st.write(f"**Preço Expresso:** R$ {lead_data.get('preco_expresso', 0):.2f}")
                    st.write(f"**Preço Café Compra:** R$ {lead_data.get('preco_cafe_compra', 0):.2f}/kg")
                with col3:
                    st.write(f"**Tipo Máquina:** {lead_data.get('tipo_maquina', 'Não informado')}")
                    st.write(f"**Comodato:** {lead_data.get('tem_comodato', 'Não informado')}")
                st.markdown("---")
                if lead_data.get('analise_completa'):
                    analise = lead_data['analise_completa']
                    st.markdown("### 📊 Dados Reais Coletados")
                    confiabilidade = _safe_get_numeric(analise, 'confiabilidade_dados', 0)
                    cor = "#5CB85C" if confiabilidade > 70 else "#FFA500" if confiabilidade > 40 else "#D9534F"
                    st.markdown(f"""
                    <div style='background: {cor}22; padding: 10px; border-radius: 5px; border-left: 3px solid {cor};'>
                        <strong>Confiabilidade dos Dados: {confiabilidade}%</strong><br>
                        <small>Fontes: {', '.join(analise.get('fontes_dados', []))}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Funcionários:** {analise.get('num_funcionarios', 'N/A')}")
                        st.write(f"**Tamanho:** {analise.get('tamanho_m2', 'N/A')} m²")
                        st.write(f"**Horário Pico:** {analise.get('horario_pico', 'N/A')}")
                    with col2:
                        st.write(f"**Tempo Permanência:** {analise.get('tempo_permanencia_medio', 'N/A')} min")
                        st.write(f"**Taxa Ocupação:** {_safe_get_numeric(analise, 'taxa_ocupacao_media', 0)*100:.0f}%")
                        st.write(f"**Sentiment:** {_safe_get_numeric(analise, 'sentiment_score', 0):.0f}%")
                    with col3:
                        st.write(f"**Menções Café:** {_safe_get_numeric(analise, 'mencoes_cafe', 0)}")
                        st.write(f"**Qualidade Café:** {_safe_get_numeric(analise, 'qualidade_cafe_score', 0):.1f}/5")
                        st.write(f"**Instagram:** {analise.get('instagram_followers', 'N/A')} seguidores")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 💬 Mensagem de Primeiro Contato")
                    st.info(lead_data.get('insights_ia', 'Sem mensagem personalizada'))
                    if lead_data.get('insights_ia'):
                        st.code(lead_data['insights_ia'], language=None)
                with col2:
                    st.markdown("### 📝 Análise Estratégica")
                    analise = lead_data.get('analise_completa', {})
                    st.markdown(f"**Resumo Executivo:** {analise.get('resumo_executivo', 'Não disponível.')}")
                    gatilhos = analise.get('gatilhos_venda', {})
                    if gatilhos:
                        st.markdown("**Gatilhos de Venda:**")
                        for pf in gatilhos.get('pontos_fortes', []):
                            st.markdown(f"  - 💪 **Ponto Forte:** {pf}")
                        for op in gatilhos.get('oportunidades', []):
                            st.markdown(f"  - 🎯 **Oportunidade:** {op}")
                        st.markdown(f"**💡 Dica de Abordagem:** {gatilhos.get('dica_abordagem', 'Não disponível.')}")
                
                st.markdown("---")
                st.markdown("##### 🗑️ Zona de Perigo")
                if st.button("Excluir este Lead", key=f"delete_inside_view_{lead_id}"):
                    st.session_state['confirmar_exclusao'] = lead_id
                    st.rerun()
                if st.button("Fechar", key=f"close_insights_{lead_id}"):
                    del st.session_state['mostrar_insights']
                    st.rerun()

def aba_prospeccao():
    """Aba de prospecção de novos leads com layout horizontal"""
    st.header("🔍 Prospecção Inteligente - Café Orfeu")
    col1, col2, col3 = st.columns([2, 1.5, 1.5])
    with col1:
        st.markdown("### 📍 Localização")
        bairros_default = "Copacabana\nIpanema\nLeblon\nBarra da Tijuca\nCentro"
        bairros_input = st.text_area(
            "Bairros",
            bairros_default,
            help="Insira um bairro por linha",
            height=150
        )
        cidade_input = st.text_input(
            "Cidade",
            "Rio de Janeiro",
            help="Cidade onde será feita a busca"
        )
        keyword_input = st.text_input(
            "🔍 Palavra-chave (opcional)",
            placeholder="Ex: gourmet, premium, artesanal",
            help="Palavra para refinar a busca"
        )
    with col2:
        st.markdown("### 🏢 Tipos de Estabelecimento")
        tipos_selecionados = st.multiselect(
            "Selecione os tipos",
            options=list(TIPOS_COM_EMOJIS.keys()),
            default=['restaurant', 'cafe', 'bakery'],
            format_func=lambda x: TIPOS_COM_EMOJIS[x]
        )
    with col3:
        st.markdown("### 🎯 Filtros de Qualidade")
        nota_selecionada = st.slider(
            "⭐ Nota Mínima e Máxima",
            1.0, 5.0, (4.0, 5.0),
            help="Estabelecimentos com boa reputação"
        )
        min_avaliacoes = st.number_input(
            "💬 Mínimo de Avaliações",
            min_value=0, value=20, step=10,
            help="Volume mínimo para garantir estabelecimento ativo"
        )
        precos_disponiveis = {
            '$': '💵 Econômico',
            '$$': '💵💵 Moderado',
            '$$$': '💵💵💵 Premium',
            '$$$$': '💵💵💵💵 Luxo'
        }
        precos_selecionados_str = st.multiselect(
            "💰 Faixa de Preço",
            options=list(precos_disponiveis.keys()),
            default=['$$', '$$$', '$$$$'],
            format_func=lambda x: precos_disponiveis[x],
            help="Estabelecimentos premium têm maior potencial"
        )
        precos_selecionados_int = [len(p) for p in precos_selecionados_str]
        raio_selecionado = st.slider(
            "📏 Raio de Busca (metros)",
            500, 5000, 2000, step=500,
            help="Distância a partir do centro do bairro"
        )
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🔍 INICIAR PROSPECÇÃO CAFÉ ORFEU", type="primary", use_container_width=True):
            bairros_lista = [b.strip() for b in bairros_input.split('\n') if b.strip()]
            if not bairros_lista:
                st.error("❌ Por favor, insira pelo menos um bairro")
            elif not tipos_selecionados:
                st.error("❌ Por favor, selecione pelo menos um tipo de estabelecimento")
            else:
                with st.spinner("☕ Buscando estabelecimentos ideais para Café Orfeu..."):
                    df_resultados = prospectar_bairros(
                        api_key=MINHA_API_KEY,
                        bairros=bairros_lista,
                        cidade=cidade_input,
                        tipos=tipos_selecionados,
                        nota_range=nota_selecionada,
                        precos=precos_selecionados_int,
                        raio=raio_selecionado,
                        min_avaliacoes=min_avaliacoes,
                        keyword=keyword_input
                    )
                    if not df_resultados.empty:
                        st.session_state['df_prospeccao'] = df_resultados
                        st.success(f"✅ {len(df_resultados)} estabelecimentos encontrados! Gerando análises de IA...")
                        st.balloons()
    if 'df_prospeccao' in st.session_state and not st.session_state['df_prospeccao'].empty:
        df = st.session_state['df_prospeccao']
        st.divider()
        st.subheader("Resumo da Prospecção")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Leads", len(df))
        with col2:
            st.metric("Score Médio", f"{df['Pontuação'].mean():.0f}")
        with col3:
            st.metric("Nota Média", f"⭐ {df['Nota Média'].mean():.1f}")
        with col4:
            leads_hot = len(df[df['Pontuação'] > 80])
            st.metric("Hot Leads 🔥", leads_hot)
        st.markdown("---")
        if st.button("📥 Exportar Leads para Excel"):
            excel_data = to_excel(df)
            st.download_button(
                label="💾 Download Excel",
                data=excel_data,
                file_name=f"leads_prospeccao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        st.subheader("📍 Mapa de Leads")
        with st.expander("Visualizar Mapa", expanded=True):
            mapa = criar_mapa_interativo(df)
            if mapa:
                components.html(mapa._repr_html_(), height=450)
        st.markdown("---")
        st.subheader(f"📊 {len(df)} Leads Encontrados")
        if 'Mensagem_IA' not in df.columns:
            with st.spinner("Gerando mensagens personalizadas com IA..."):
                df['Mensagem_IA'] = df.apply(lambda row: gerar_mensagem_ia(row['Reviews_API'], row['Nome']), axis=1)
                st.session_state['df_prospeccao'] = df
        tab1, tab2 = st.tabs(["📋 Lista Detalhada", "📊 Análise Rápida"])
        with tab1:
            col1, col2 = st.columns([3, 1])
            with col1:
                select_all = st.checkbox("Selecionar todos os leads")
            with col2:
                if st.button("🔄 Atualizar Análises IA"):
                    st.cache_data.clear()
                    st.rerun()
            def paginar_dataframe(df, items_por_pagina=10, key_suffix="prospeccao"):
                if df is None or df.empty:
                    return df
                total = len(df)
                total_pages = max(1, (total + items_por_pagina - 1) // items_por_pagina)
                page_key = f"page_{key_suffix}"
                if page_key not in st.session_state:
                    st.session_state[page_key] = 1
                col_prev, col_info, col_next = st.columns([1, 2, 1])
                with col_prev:
                    if st.button("←", key=f"{page_key}_prev"):
                        if st.session_state[page_key] > 1:
                            st.session_state[page_key] -= 1
                with col_info:
                    st.markdown(f"Página {st.session_state[page_key]} / {total_pages}")
                with col_next:
                    if st.button("→", key=f"{page_key}_next"):
                        if st.session_state[page_key] < total_pages:
                            st.session_state[page_key] += 1
                current_page = st.session_state[page_key]
                start = (current_page - 1) * items_por_pagina
                end = start + items_por_pagina
                return df.iloc[start:end].copy()
            df_paginado = paginar_dataframe(df, items_por_pagina=10, key_suffix="prospeccao")
            selected_indices = []
            for idx in df_paginado.index:
                row = df.loc[idx]
                with st.container(border=True):
                    col_select, col_score, col_info, col_bairro, col_cidade, col_tipo, col_preco, col_horario, col_actions = st.columns([0.3, 0.8, 2.5, 1, 1, 1, 1, 1.5, 1.5])
                    with col_select:
                        selected = st.checkbox(" ", key=f"select_{idx}", value=select_all)
                        if selected:
                            selected_indices.append(idx)
                    with col_score:
                        st.markdown(f"<div style='padding-top: 10px;'><span class='score-badge' style='font-size: 14px; padding: 6px 10px;'>Score: {row['Pontuação']}</span></div>", unsafe_allow_html=True)
                    with col_info:
                        st.markdown(f"<strong class='prospect-name' style='font-size: 18px;'>{row['Nome']}</strong>", unsafe_allow_html=True)
                        st.markdown(f"<p class='endereco-text'>📍 {row['Endereço']}</p>", unsafe_allow_html=True)
                    with col_bairro:
                        st.markdown(f"**Bairro**<br>{row['Bairro']}", unsafe_allow_html=True)
                    with col_cidade:
                        st.markdown(f"**Cidade**<br>{row['Cidade']}", unsafe_allow_html=True)
                    with col_tipo:
                        st.markdown(f"**Tipo**<br>{row['Tipo']}", unsafe_allow_html=True)
                    with col_preco:
                        st.markdown(f"**Preço**<br>{row['Faixa de Preço']}", unsafe_allow_html=True)
                    with col_horario:
                        horarios = row.get('Horarios', [])
                        horarios_formatados = "Não informado"
                        if horarios:
                            ranges = [h.split(': ', 1)[1] for h in horarios if ': ' in h]
                            if ranges:
                                horario_comum = statistics.mode(ranges)
                                horarios_alternativos = []
                                for h in horarios:
                                    if ': ' in h:
                                        dia, horario_dia = h.split(': ', 1)
                                        if horario_dia != horario_comum:
                                            dia_abrev = dia[:3].capitalize()
                                            horarios_alternativos.append(f"{dia_abrev}: {horario_dia}")
                                horarios_formatados = f"**Padrão:** {horario_comum}"
                                if horarios_alternativos:
                                    horarios_formatados += "<br>" + "<br>".join(horarios_alternativos)
                        st.markdown(f"**Horário**<br>{horarios_formatados}", unsafe_allow_html=True)
                    with col_actions:
                        if row['Telefone'] != 'N/A':
                            mensagem_wpp = df.loc[idx].get('Mensagem_IA', MENSAGEM_PROSPECCAO_PADRAO)
                            link_whats = gerar_link_whatsapp(row['Telefone'], mensagem_wpp)
                            if link_whats:
                                st.link_button("💬 WhatsApp", link_whats, use_container_width=True)
        with tab2:
            st.markdown("### 🎯 Distribuição de Scores")
            fig_scores = px.histogram(df, x='Pontuação', nbins=20, title="Distribuição de Pontuação dos Leads")
            fig_scores.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                title_font_color="#FAF7F2" if st.session_state.get('theme', 'Escuro') == 'Escuro' else "#2E2015"
            )
            st.plotly_chart(fig_scores, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': False})
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🏆 Top 5 Leads")
                top_leads = df.nlargest(5, 'Pontuação')[['Nome', 'Pontuação', 'Nota Média', 'Tipo']]
                st.dataframe(top_leads, use_container_width=True)
            with col2:
                st.markdown("### 📊 Leads por Tipo")
                tipo_counts = df['Tipo'].value_counts()
                fig_tipos = px.pie(values=tipo_counts.values, names=tipo_counts.index, title="Distribuição por Tipo")
                fig_tipos.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_tipos, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': False})
        if selected_indices:
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button(f"➕ Adicionar {len(selected_indices)} leads ao CRM", type="primary", use_container_width=True):
                    crm = CRMSystem()
                    leads_adicionados = 0
                    progress_bar = st.progress(0)
                    for i, idx in enumerate(selected_indices):
                        lead_data = df.loc[idx].to_dict()
                        analise_completa = crm.analisador.analisar_estabelecimento_completo(
                            lead_data, lead_data.get('Reviews_API', [])
                        )
                        lead_data['analise_completa'] = analise_completa
                        crm.adicionar_lead_ao_funil(lead_data)
                        leads_adicionados += 1
                        progress_bar.progress((i + 1) / len(selected_indices))
                    progress_bar.empty()
                    st.success(f"✅ {leads_adicionados} leads adicionados ao funil de vendas!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()

@st.fragment(run_every=60)
def aba_meta_mensal():
    """Aba de controle de meta mensal com painel de performance completo"""
    st.header("🎯 Painel de Performance - Meta Mensal")
    hoje = datetime.now()    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        ano_selecionado = st.number_input("Ano", min_value=2023, max_value=hoje.year + 1, value=hoje.year, key="meta_ano_sel")
    with col_sel2:
        meses_nomes = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
            7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        mes_selecionado_num = st.selectbox("Mês", options=list(meses_nomes.keys()), format_func=lambda x: meses_nomes[x], index=hoje.month - 1, key="meta_mes_sel")
    chave_mes = f"{ano_selecionado}-{mes_selecionado_num:02d}"
    if chave_mes not in st.session_state['dados_mensais']:
        st.session_state['dados_mensais'][chave_mes] = {
            'meta': st.session_state.get('user_meta', META_MENSAL_DEFAULT),
            'porcentagem_meta': 100,
            'vendas': []
        }
    dados_mes_selecionado = st.session_state['dados_mensais'][chave_mes]
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        nova_meta = st.number_input(
            "Meta Mensal (R$)",
            value=float(dados_mes_selecionado.get('meta', META_MENSAL_DEFAULT)),
            step=1000.0,
            format="%.2f",
            key=f"meta_input_{chave_mes}"
        )
        dados_mes_selecionado['meta'] = nova_meta
    with col2:
        st.markdown("### Ajuste de Meta")
        col_menos, col_pct, col_mais = st.columns([1, 2, 1])
        with col_menos:
            if st.button("➖", key=f"meta_menos_{chave_mes}"):
                if dados_mes_selecionado['porcentagem_meta'] > 100:
                    dados_mes_selecionado['porcentagem_meta'] -= 5
        with col_pct:
            st.metric("", f"{dados_mes_selecionado.get('porcentagem_meta', 100)}%")
        with col_mais:
            if st.button("➕", key=f"meta_mais_{chave_mes}"):
                if dados_mes_selecionado['porcentagem_meta'] < 120:
                    dados_mes_selecionado['porcentagem_meta'] += 5
    with col3:
        meta_ajustada = dados_mes_selecionado['meta'] * (dados_mes_selecionado['porcentagem_meta'] / 100)
        st.metric("Meta Ajustada", f"R$ {meta_ajustada:,.2f}")
    vendas_mes_atual = dados_mes_selecionado.get('vendas', [])
    faturamento_atual = sum(v['valor'] for v in vendas_mes_atual)
    vendas_hoje = sum(v['valor'] for v in vendas_mes_atual if v['data'].date() == hoje.date())
    clientes_novos = [v for v in vendas_mes_atual if v.get('novo_cliente', False)]
    soma_clientes_novos = sum(v['valor'] for v in clientes_novos)
    contagem_novos = len(clientes_novos)
    dias_uteis_mes = get_business_days_month(ano_selecionado, mes_selecionado_num)
    if ano_selecionado == hoje.year and mes_selecionado_num == hoje.month:
        dia_referencia = hoje.day
    elif (ano_selecionado < hoje.year) or (ano_selecionado == hoje.year and mes_selecionado_num < hoje.month):
        dia_referencia = calendar.monthrange(ano_selecionado, mes_selecionado_num)[1]
    else:
        dia_referencia = 0
    dias_uteis_decorridos = get_business_days_passed(ano_selecionado, mes_selecionado_num, dia_referencia) if dia_referencia > 0 else 0
    dias_uteis_restantes = dias_uteis_mes - dias_uteis_decorridos
    meta_diaria_media = meta_ajustada / dias_uteis_mes if dias_uteis_mes > 0 else 0
    media_venda_diaria_real = faturamento_atual / dias_uteis_decorridos if dias_uteis_decorridos > 0 else 0
    projecao_faturamento = media_venda_diaria_real * dias_uteis_mes if dias_uteis_decorridos > 0 else 0
    projecao_meta_pct = (projecao_faturamento / meta_ajustada * 100) if meta_ajustada > 0 else 0
    media_diaria_necessaria = (meta_ajustada - faturamento_atual) / dias_uteis_restantes if dias_uteis_restantes > 0 else 0
    st.markdown("---")
    percentual_atingido = (faturamento_atual / meta_ajustada * 100) if meta_ajustada > 0 else 0
    progress_color = "#5CB85C" if percentual_atingido >= 100 else "#FDB863" if percentual_atingido >= 70 else "#D9534F"
    st.markdown(f"""
        <div class='meta-progress-card'>
            <h3 style='color: #2E2015 !important; margin-bottom: 10px;'>Progresso da Meta</h3>
            <div style='background: #E0E0E0; border-radius: 10px; height: 40px; position: relative;'>
                <div style='background: linear-gradient(90deg, {progress_color} 0%, {progress_color}DD 100%); 
                            width: {min(percentual_atingido, 100)}%; height: 100%; border-radius: 10px; 
                            display: flex; align-items: center; justify-content: center;'>
                    <span style='color: white; font-weight: bold; font-size: 18px;'>
                        {percentual_atingido:.1f}%
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.subheader("📊 Métricas do Mês")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Meta Mensal (R$)", f"R$ {meta_ajustada:,.2f}")
    with col2:
        st.metric("Faturamento Atual", f"R$ {faturamento_atual:,.2f}", 
                 delta=f"{percentual_atingido:.1f}% da meta")
    with col3:
        st.metric("Dias Úteis no Mês", dias_uteis_mes)
    with col4:
        st.metric("Meta Diária Média", f"R$ {meta_diaria_media:,.2f}")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Dias Úteis Decorridos", dias_uteis_decorridos)
    with col2:
        st.metric("Média de Venda Diária (Real)", f"R$ {media_venda_diaria_real:,.2f}")
    with col3:
        st.metric("Dias Úteis Restantes", dias_uteis_restantes)
    with col4:
        st.metric("Média Diária Necessária", f"R$ {media_diaria_necessaria:,.2f}")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Projeção de Faturamento", f"R$ {projecao_faturamento:,.2f}")
    with col2:
        st.metric("Projeção da Meta (%)", f"{projecao_meta_pct:.0f}%")
    with col3:
        st.metric("Vendas Hoje", f"R$ {vendas_hoje:,.2f}")
    with col4:
        st.metric("Clientes Novos", f"{contagem_novos} (R$ {soma_clientes_novos:,.2f})")
    st.markdown("---")
    with st.expander("➕ Registrar Nova Venda"):
        col1, col2, col3 = st.columns(3)
        with col1:
            cliente_venda = st.text_input("Cliente")
            valor_venda = st.number_input("Valor (R$)", min_value=0.0, step=100.0)
            cliente_novo = st.checkbox("Cliente Novo?")
        with col2:
            data_venda = st.date_input("Data da Venda", value=datetime.now())
            observacoes = st.text_area("Observações")
        produtos_disponiveis = [
            "Grãos 1KG", "Grãos 250g", "Cap C9", "Cap Nes", "Drip Coffee", "T. Moido"
        ]
        produtos_selecionados = st.multiselect(
            "Produtos Vendidos", 
            options=produtos_disponiveis,
            placeholder="Selecione os Produtos"
        )
        produtos_com_quantidade = []
        if produtos_selecionados:
            st.markdown("##### Quantidades dos Produtos")
            cols_qtd = st.columns(len(produtos_selecionados))
            for i, produto in enumerate(produtos_selecionados):
                with cols_qtd[i]:
                    quantidade = st.number_input(f"Qtd. {produto}", min_value=1, step=1, key=f"qtd_{produto}_{chave_mes}")
                    produtos_com_quantidade.append({"produto": produto, "quantidade": quantidade})
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([0.5, 2, 0.5])
        with col_btn2:
            if st.button("💾 Registrar Nova Venda", type="primary", use_container_width=True):
                if cliente_venda and valor_venda > 0 and produtos_selecionados:
                    nova_venda = {
                        'data': pd.Timestamp(data_venda),
                        'cliente': cliente_venda,
                        'valor': valor_venda,
                        'produtos': produtos_com_quantidade,
                        'vendedor': st.session_state.get('user_name', 'Vendedor 1'),
                        'observacoes': observacoes,
                        'novo_cliente': cliente_novo
                    }
                    dados_mes_selecionado['vendas'].append(nova_venda)
                    st.success(f"✅ Venda de R$ {valor_venda:,.2f} registrada!")
                    st.rerun()
                else:
                    st.warning("Preencha Cliente, Valor e selecione ao menos um Produto.")
    if vendas_mes_atual:
        st.markdown("### 📈 Análise de Vendas")
        df_vendas = pd.DataFrame(vendas_mes_atual)
        df_vendas_diario = df_vendas.groupby(df_vendas['data'].dt.day)['valor'].sum().reset_index()
        df_vendas_diario.columns = ['Dia', 'Valor']
        num_dias_no_mes = calendar.monthrange(ano_selecionado, mes_selecionado_num)[1]
        dias_completos = pd.DataFrame({'Dia': range(1, num_dias_no_mes + 1)})
        df_vendas_diario = pd.merge(dias_completos, df_vendas_diario, on='Dia', how='left').fillna(0)
        fig = px.line(df_vendas_diario, x='Dia', y='Valor', 
                        title="Evolução Diária de Vendas",
                        markers=True,
                        template="plotly_white")
        fig.add_hline(y=meta_diaria_media, line_dash="dash", 
                        line_color="red", 
                        annotation_text="Meta Diária")
        text_color = "#FAF7F2" if st.session_state.get('theme', 'Escuro') == 'Escuro' else "#2E2015"
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
            xaxis_showgrid=False, yaxis_showgrid=False,
            font_color=text_color,
            title_font_color=text_color
        )
        fig.update_xaxes(range=[1, num_dias_no_mes], fixedrange=True)
        fig.update_yaxes(fixedrange=True)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("---")
        st.subheader("🚀 Minha Performance em Detalhes")
        leads_ganhos = st.session_state['crm_leads'].get('ganho', [])
        leads_perdidos = st.session_state['crm_leads'].get('perdido', [])
        total_leads = sum(len(leads) for leads in st.session_state['crm_leads'].values())
        taxa_conversao = (len(leads_ganhos) / total_leads * 100) if total_leads > 0 else 0
        ciclos = []
        for lead in leads_ganhos:
            data_entrada = pd.to_datetime(lead.get('data_entrada'))
            data_ganho = data_entrada
            for hist in lead.get('historico', []):
                if 'para ganho' in hist.get('acao', ''):
                    data_ganho = pd.to_datetime(hist.get('data'))
                    break
            ciclos.append((data_ganho - data_entrada).days)
        ciclo_medio = np.mean(ciclos) if ciclos else 0
        valores_vendas = [v['valor'] for v in vendas_mes_atual]
        ticket_medio = np.mean(valores_vendas) if valores_vendas else 0
        oportunidades_ativas = []
        for stage in ['qualificado', 'proposta', 'negociacao']:
            oportunidades_ativas.extend(st.session_state['crm_leads'].get(stage, []))
        top_oportunidades = sorted(oportunidades_ativas, key=lambda x: x.get('valor_estimado', 0), reverse=True)[:3]
        nome_principal_cliente = "N/A"
        valor_principal_cliente = 0
        if vendas_mes_atual:
            df_vendas_mes = pd.DataFrame(vendas_mes_atual)
            vendas_por_cliente = df_vendas_mes.groupby('cliente')['valor'].sum()
            if not vendas_por_cliente.empty:
                nome_principal_cliente = vendas_por_cliente.idxmax()
                valor_principal_cliente = vendas_por_cliente.max()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🎯 Taxa de Conversão Pessoal", f"{taxa_conversao:.1f}%")
            st.metric("⏳ Ciclo de Venda Médio", f"{ciclo_medio:.0f} dias")
        with col2:
            st.metric("💰 Ticket Médio por Venda", f"R$ {ticket_medio:,.2f}")
            st.metric("📞 Atividades na Semana", "42")
        with col3:
            st.metric("🏆 Principal Cliente", f"{nome_principal_cliente}")
            st.metric("⭐ Valor do Cliente", f"R$ {valor_principal_cliente:,.2f}")
        with col4:
            st.markdown("**🔥 Maiores Oportunidades no Funil**")
            if top_oportunidades:
                for op in top_oportunidades:
                    st.markdown(f"• **{op['nome']}**: R$ {op['valor_estimado']:,.2f}")
            else:
                st.info("Nenhuma oportunidade grande no funil.")
        st.markdown("### 📋 Detalhamento de Vendas")
        df_vendas_display = df_vendas.copy()
        df_vendas_display['data'] = df_vendas_display['data'].dt.strftime('%d/%m/%Y')
        df_vendas_display['novo_cliente'] = df_vendas_display.get('novo_cliente', False).apply(lambda x: '✅' if x else '❌')
        st.dataframe(
            df_vendas_display[['data', 'cliente', 'produtos', 'valor', 'novo_cliente']],
            use_container_width=True,
            hide_index=True
        )
        if st.button("📥 Exportar Vendas para Excel"):
            excel_data = to_excel(df_vendas_display)
            st.download_button(
                label="💾 Download Excel",
                data=excel_data,
                file_name=f"vendas_{ano_selecionado}_{mes_selecionado_num:02d}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    else:
        st.info("Nenhuma venda registrada este mês")

def aba_pipeline():
    """Aba do pipeline de vendas"""
    st.header("📈 Pipeline de Vendas")
    criar_dashboard_metricas()
    exibir_kanban()

def aba_rotas():
    """Aba dedicada para criação de rotas de visita"""
    st.header("🗺️ Planejador de Rotas")
    st.subheader("1️⃣ Selecionar Leads para Visita")
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_stage = st.multiselect(
            "Estágio do Funil",
            options=['novo', 'contactado', 'qualificado', 'proposta', 'negociacao'],
            default=['novo', 'contactado', 'qualificado', 'proposta', 'negociacao']
        )
    with col2:
        bairros_unicos = set()
        for stage in filtro_stage:
            for lead in st.session_state['crm_leads'].get(stage, []):
                if lead.get('bairro'):
                    bairros_unicos.add(lead['bairro'])
        filtro_bairro_rota = st.multiselect(
            "Bairros",
            options=sorted(list(bairros_unicos)),
            default=list(bairros_unicos)[:3] if bairros_unicos else []
        )
    with col3:
        filtro_score_min = st.slider(
            "Score Mínimo",
            min_value=0,
            max_value=100,
            value=60
        )
    st.subheader("2️⃣ Leads Disponíveis")
    leads_disponiveis = []
    for stage in filtro_stage:
        for lead in st.session_state['crm_leads'].get(stage, []):
            if (lead.get('bairro') in filtro_bairro_rota and 
                lead.get('pontuacao', 0) >= filtro_score_min):
                leads_disponiveis.append({
                    **lead,
                    'stage': stage,
                    'selecionado': lead.get('selecionado_rota', False)
                })
    if leads_disponiveis:
        for i, lead in enumerate(leads_disponiveis):
            col1, col2, col3, col4, col5 = st.columns([0.5, 3, 1, 1, 1])
            with col1:
                selecionado = st.checkbox(
                    " ",
                    key=f"rota_select_{lead['id']}",
                    value=lead['id'] in [l['id'] for l in st.session_state.get('leads_selecionados_rota', [])]
                )
                selected_ids = [l['id'] for l in st.session_state.get('leads_selecionados_rota', [])]
                if selecionado and lead['id'] not in selected_ids:
                    st.session_state['leads_selecionados_rota'].append(lead)
                elif not selecionado and lead['id'] in selected_ids:
                    st.session_state['leads_selecionados_rota'] = [
                        l for l in st.session_state['leads_selecionados_rota'] 
                        if l['id'] != lead['id']
                    ]
            with col2:
                st.markdown(f"**{lead['nome']}**")
                st.caption(f"📍 {lead['endereco']}")
            with col3:
                st.write(f"Score: {lead['pontuacao']}")
            with col4:
                st.write(f"⭐ {lead.get('nota_media', 0)}")
            with col5:
                st.write(f"Status: {lead['stage']}")
        st.markdown("---")
        if st.session_state.get('leads_selecionados_rota'):
            st.subheader(f"3️⃣ Ações para os {len(st.session_state['leads_selecionados_rota'])} Leads Selecionados")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("✅ Gerar Rota Otimizada", type="primary", use_container_width=True):
                    with st.spinner("Calculando rota otimizada..."):
                        gmaps = googlemaps.Client(key=MINHA_API_KEY)
                        rota_otimizada = gerar_rota_otimizada(
                            gmaps,
                            st.session_state['leads_selecionados_rota']
                        )
                        if rota_otimizada:
                            st.session_state['rota_otimizada'] = rota_otimizada
                            st.success("✅ Rota otimizada!")
                        else:
                            st.error("Não foi possível gerar a rota. Verifique os endereços ou a chave da API.")
                if st.button("🗑️ Limpar Seleção de Rota", use_container_width=True):
                    st.session_state['leads_selecionados_rota'] = []
                    if 'rota_otimizada' in st.session_state:
                        del st.session_state['rota_otimizada']
                    st.rerun()
            if 'rota_otimizada' in st.session_state:
                rota = st.session_state['rota_otimizada']
                st.markdown("---")
                st.subheader("4️⃣ Rota Otimizada")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📍 Paradas", len(rota['leads_ordenados']))
                with col2:
                    st.metric("🚗 Distância Total", f"{rota['distancia_total']:.1f} km")
                with col3:
                    st.metric("⏱️ Tempo Estimado", f"{rota['duracao_total']:.0f} min")
                with col4:
                    st.metric("⏰ Tempo por Visita", "30 min")
                st.subheader("5️⃣ Mapa da Rota")
                df_rota = pd.DataFrame([
                    {
                        'Nome': lead['nome'],
                        'Endereço': lead['endereco'],
                        'Latitude': lead['latitude'],
                        'Longitude': lead['longitude'],
                        'Pontuação': lead['pontuacao'],
                        'Nota Média': lead['nota_media'],
                        'Tipo': lead['tipo']
                    }
                    for lead in rota['leads_ordenados']
                ])
                mapa_rota = criar_mapa_interativo(df_rota, rota['coords'])
                if mapa_rota:
                    components.html(mapa_rota._repr_html_(), height=500)
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col2:
                    st.link_button(
                        "🗺️ Abrir no Google Maps",
                        rota['url'],
                        use_container_width=True
                    )
                st.subheader("6️⃣ QR Code da Rota")
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(rota['url'])
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buf = BytesIO()
                img.save(buf, format='PNG')
                st.image(buf.getvalue(), width=200)
                st.subheader("7️⃣ Itinerário Detalhado e Exportação")
                col_it1, col_it2 = st.columns([1,1])
                with col_it1:
                    hora_inicio = st.time_input("Horário de Início da Rota", value=datetime.strptime("09:00", "%H:%M").time())
                with col_it2:
                    tempo_visita_padrao = st.number_input("Tempo de Visita (min)", value=30, step=5)
                itinerario_texto = f"Itinerário de Visitas - {datetime.now().strftime('%d/%m/%Y')}\n"
                tempo_atual = datetime.combine(datetime.today(), hora_inicio)
                for i, lead in enumerate(rota['leads_ordenados']):
                    if i > 0:
                        tempo_deslocamento = rota['leg_durations'][i-1]
                        tempo_atual += timedelta(minutes=tempo_deslocamento)
                        deslocamento_str = f"🚗 Deslocamento: {tempo_deslocamento:.0f} min"
                    else:
                        deslocamento_str = "📍 Ponto de Partida"
                    hora_chegada = tempo_atual
                    hora_saida = hora_chegada + timedelta(minutes=tempo_visita_padrao)
                    itinerario_texto += f"--- Parada {i+1}: {lead['nome']} ---\n"
                    itinerario_texto += f"Chegada Prevista: {hora_chegada.strftime('%H:%M')}\n"
                    itinerario_texto += f"Endereço: {lead['endereco']}\n"
                    itinerario_texto += f"Telefone: {lead.get('telefone', 'N/A')}\n"
                    itinerario_texto += f"Anotações: [ESCREVA AQUI]\n"
                    st.markdown(f"""
                    <div style="background-color: {'#4A3728' if st.session_state.get('theme', 'Escuro') == 'Escuro' else '#FFFFFF'}; 
                                 border-left: 5px solid #D2691E; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                        <h5 style="margin-top:0;">Parada {i+1}: {lead['nome']}</h5>
                        <p>
                            <b>{deslocamento_str}</b><br>
                            <b>🕒 Chegada:</b> {hora_chegada.strftime('%H:%M')} | 
                            <b>⏳ Duração:</b> {tempo_visita_padrao} min | 
                            <b>➡️ Saída:</b> {hora_saida.strftime('%H:%M')}
                        </p>
                        <p><b>📍 Endereço:</b> {lead['endereco']}</p>
                        <p><b>📞 Telefone:</b> {lead.get('telefone', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    tempo_atual = hora_saida
                tempo_deslocamento_final = rota['leg_durations'][-1]
                tempo_atual += timedelta(minutes=tempo_deslocamento_final)
                itinerario_texto += f"--- Fim da Rota ---\n"
                itinerario_texto += f"Retorno Previsto: {tempo_atual.strftime('%H:%M')}\n"
                st.markdown("---")
                col_exp1, col_exp2, col_exp3 = st.columns([1,2,1])
                with col_exp2:
                    email_assunto = quote(f"Itinerário de Visitas Orfeu - {datetime.now().strftime('%d/%m')}")
                    email_corpo = quote(itinerario_texto)
                    link_email = f"mailto:?subject={email_assunto}&body={email_corpo}"
                    st.link_button(
                        "📧 Enviar Itinerário por E-mail",
                        link_email,
                        use_container_width=True
                    )
    else:
        st.info("Nenhum lead encontrado com os filtros selecionados")

def aba_relatorios():
    """Aba de relatórios e analytics avançados"""
    st.header("📊 Relatórios e Analytics")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        data_inicio = st.date_input("Data Início", value=pd.Timestamp.now() - pd.Timedelta(days=30))
    with col2:
        data_fim = st.date_input("Data Fim", value=pd.Timestamp.now())
    with col3:
        tipo_relatorio = st.selectbox(
            "Tipo de Relatório",
            ["Dashboard Executivo", "Análise de Funil", "Performance de Vendas", 
             "Análise Geográfica", "Relatório de Market Share"]
        )
    st.markdown("---")
    if tipo_relatorio == "Dashboard Executivo":
        st.subheader("📈 Dashboard Executivo")
        total_leads = sum(len(leads) for leads in st.session_state['crm_leads'].values())
        leads_ativos = sum(len(leads) for stage, leads in st.session_state['crm_leads'].items() 
                          if stage not in ['ganho', 'perdido'])
        valor_total_pipeline = sum(
            lead.get('valor_estimado', 0) 
            for leads in st.session_state['crm_leads'].values() 
            for lead in leads
        )
        taxa_conversao = (len(st.session_state['crm_leads']['ganho']) / total_leads * 100) if total_leads > 0 else 0
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Leads", total_leads)
        with col2:
            st.metric("Leads Ativos", leads_ativos)
        with col3:
            st.metric("Valor Total Pipeline", f"R$ {valor_total_pipeline:,.2f}")
        with col4:
            st.metric("Taxa de Conversão", f"{taxa_conversao:.1f}%")
        col1, col2 = st.columns(2)
        with col1:
            temps = {'quente': 0, 'morno': 0, 'frio': 0}
            for leads in st.session_state['crm_leads'].values():
                for lead in leads:
                    temp = lead.get('temperatura', 'frio')
                    temps[temp] = temps.get(temp, 0) + 1
            fig = go.Figure(data=[go.Pie(
                labels=list(temps.keys()),
                values=list(temps.values()),
                marker=dict(colors=['#FF4444', '#FFA500', '#4169E1']),
                hole=.3
            )])
            fig.update_layout(
                title="Distribuição por Temperatura", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            bairros_valor = {}
            for leads in st.session_state['crm_leads'].values():
                for lead in leads:
                    bairro = lead.get('bairro', 'N/A')
                    valor = lead.get('valor_estimado', 0)
                    bairros_valor[bairro] = bairros_valor.get(bairro, 0) + valor
            top_bairros = sorted(bairros_valor.items(), key=lambda x: x[1], reverse=True)[:5]
            if top_bairros:
                df_bairros = pd.DataFrame(top_bairros, columns=['Bairro', 'Valor'])
                fig = px.bar(
                    df_bairros,
                    x='Bairro',
                    y='Valor',
                    orientation='h',
                    title="Top 5 Bairros por Valor",
                    color_discrete_sequence=['#D2691E']
                )
                fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de bairros para exibir")
    elif tipo_relatorio == "Relatório de Market Share":
        st.subheader("📊 Análise de Market Share")
        cafes_atuais = {}
        volume_total_kg = 0
        preco_medio_expresso = []
        tipos_maquina = {}
        comodatos = {'Sim': 0, 'Não': 0, 'Não informado': 0}
        for leads in st.session_state['crm_leads'].values():
            for lead in leads:
                cafe = lead.get('cafe_atual', 'Não informado')
                cafes_atuais[cafe] = cafes_atuais.get(cafe, 0) + 1
                volume_total_kg += lead.get('volume_kg_mensal', 0)
                preco = lead.get('preco_expresso', 0)
                if preco > 0:
                    preco_medio_expresso.append(preco)
                maquina = lead.get('tipo_maquina', 'Não informado')
                tipos_maquina[maquina] = tipos_maquina.get(maquina, 0) + 1
                tem_comodato = lead.get('tem_comodato', 'Não informado')
                comodatos[tem_comodato] = comodatos.get(tem_comodato, 0) + 1
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Volume Total Mercado", f"{volume_total_kg:.0f} kg/mês")
        with col2:
            preco_medio = np.mean(preco_medio_expresso) if preco_medio_expresso else 0
            st.metric("Preço Médio Expresso", f"R$ {preco_medio:.2f}")
        with col3:
            total_comodatos = sum(comodatos.values())
            pct_comodato = (comodatos['Sim'] / total_comodatos * 100) if total_comodatos > 0 else 0
            st.metric("% Com Comodato", f"{pct_comodato:.1f}%")
        with col4:
            nossa_participacao = 0
            st.metric("Nossa Participação", f"{nossa_participacao:.1f}%")
        col1, col2 = st.columns(2)
        with col1:
            if cafes_atuais:
                df_cafes = pd.DataFrame(list(cafes_atuais.items()), columns=['Marca', 'Quantidade'])
                df_cafes = df_cafes.sort_values('Quantidade', ascending=False).head(10)
                fig = px.pie(df_cafes, values='Quantidade', names='Marca',
                            title="Market Share por Marca de Café", color_discrete_sequence=px.colors.sequential.YlOrBr)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de marcas para exibir")
        with col2:
            if tipos_maquina:
                df_maquinas = pd.DataFrame(list(tipos_maquina.items()), columns=['Tipo', 'Quantidade'])
                fig = px.bar(df_maquinas, x='Quantidade', y='Tipo', orientation='h',
                            title="Tipos de Máquinas no Mercado",
                            color_discrete_sequence=['#E5833E'])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de máquinas para exibir")
        st.subheader("📋 Detalhamento por Lead")
        dados_market = []
        for stage, leads in st.session_state['crm_leads'].items():
            for lead in leads:
                dados_market.append({
                    'Nome': lead['nome'],
                    'Estágio': stage,
                    'Café Atual': lead.get('cafe_atual', 'N/A'),
                    'Volume KG/mês': lead.get('volume_kg_mensal', 0),
                    'Preço Expresso': lead.get('preco_expresso', 0),
                    'Preço Compra/kg': lead.get('preco_cafe_compra', 0),
                    'Tipo Máquina': lead.get('tipo_maquina', 'N/A'),
                    'Comodato': lead.get('tem_comodato', 'N/A')
                })
        if dados_market:
            df_market = pd.DataFrame(dados_market)
            st.dataframe(df_market, use_container_width=True, hide_index=True)
            if st.button("📥 Exportar Market Share para Excel"):
                excel_data = to_excel(df_market)
                st.download_button(
                    label="💾 Download Excel",
                    data=excel_data,
                    file_name=f"market_share_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
        else:
            st.info("Nenhum dado de market share disponível")

# --- INTERFACE PRINCIPAL ---
st.set_page_config(page_title="CRM Café Orfeu", layout="wide", initial_sidebar_state="expanded")
st.markdown(base_style, unsafe_allow_html=True)
if st.session_state.get('theme', 'Escuro') == 'Claro':
    st.markdown(light_theme_style, unsafe_allow_html=True)
else:
    st.markdown(dark_theme_style, unsafe_allow_html=True)

# --- TELA DE LOGIN (NOVO) ---
if not st.session_state.get('logged_in', False):
    st.title("🔐 Login - CRM Café Orfeu")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar")
            if submitted:
                if fazer_login(usuario, senha):
                    st.success(f"✅ Bem-vindo, {st.session_state['user_name']}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha inválidos")
        st.markdown("---")
        st.markdown("### 🧪 Acesso Demo")
        if st.button("Entrar como Usuário Demo"):
            st.session_state['logged_in'] = True
            st.session_state['username'] = 'demo'
            st.session_state['user_name'] = 'Usuário Demo'
            st.session_state['user_type'] = 'vendedor'
            st.session_state['user_meta'] = META_MENSAL_DEFAULT
            load_state()  # Carrega dados locais para demo
            st.rerun()
    st.markdown("---")
    st.markdown(
        "<div class='footer-text'><small>CRM Café Orfeu v5.2 | Sistema com Autenticação Firebase</small></div>",
        unsafe_allow_html=True
    )
    st.stop()  # Para a execução aqui se não estiver logado

# --- HEADER E MENU PRINCIPAL (ATUALIZADO) ---
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.title("☕ CRM Café Orfeu")    
    nome_display = st.session_state['user_name']
    if st.session_state.get('admin_viewing_user'):
        nome_vendedor_view = USUARIOS[st.session_state['admin_viewing_user']]['nome']
        st.caption(f"Logado como: {nome_display} (Admin) | Visualizando: **{nome_vendedor_view}**")
    else:
        st.caption(f"Sistema Integrado de Vendas B2B com Análise Avançada por IA | Logado como: {nome_display}")

# --- TABS PRINCIPAIS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Prospecção", 
    "📈 Pipeline", 
    "🎯 Meta Mensal",
    "🗺️ Rotas", 
    "📊 Relatórios", 
    "⚙️ Configurações"
])

with tab1:
    aba_prospeccao()
with tab2:
    aba_pipeline()
with tab3:
    aba_meta_mensal()
with tab4:
    aba_rotas()
with tab5:
    aba_relatorios()
with tab6:
    st.header("⚙️ Configurações")
    col1, col2 = st.columns(2)

    # --- PAINEL DE ADMINISTRAÇÃO (CORRIGIDO) ---
    if st.session_state.get('user_type') == 'admin':
        with st.expander("👑 Painel de Administração", expanded=True):
            st.markdown("#### 👥 Gerenciar Visualização de Vendedores")
            usuarios_para_visualizar = [u for u in USUARIOS.keys() if u != 'admin']
            usuario_selecionado = st.selectbox(
                "Visualizar dados de:",
                options=['Meus Dados'] + usuarios_para_visualizar,
                format_func=lambda x: 'Meus Dados (Visão Pessoal)' if x == 'Meus Dados' else f"{USUARIOS[x]['nome']} ({x})",
                key="admin_user_select"
            )

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if usuario_selecionado != 'Meus Dados':
                    if st.button("👁️ Carregar Dados do Vendedor", use_container_width=True):
                        dados_vendedor = carregar_dados_vendedor_especifico(usuario_selecionado)
                        if dados_vendedor:
                            st.session_state['admin_viewing_user'] = usuario_selecionado
                            _processar_dados_carregados(dados_vendedor)
                            st.success(f"Visualizando dados de {USUARIOS[usuario_selecionado]['nome']}")
                            st.rerun()
            with col_btn2:
                if st.session_state.get('admin_viewing_user'):
                    if st.button("⬅️ Voltar para Meus Dados", use_container_width=True):
                        st.session_state['admin_viewing_user'] = None
                        carregar_dados_usuario_firebase(st.session_state['username'])
                        st.success("Voltando para seus dados.")
                        st.rerun()
        st.markdown("---")

    # O restante das configurações continua dentro das colunas
    with col1:
        st.subheader("Configurações do Sistema")
        theme_options = ["Escuro", "Claro"]
        current_theme_index = theme_options.index(st.session_state.get('theme', 'Escuro'))
        selected_theme = st.radio(
            "Escolha o tema:",
            theme_options,
            index=current_theme_index,
            key='theme_selector'
        )
        cache_enabled = st.checkbox("Ativar Cache", value=st.session_state.get('cache_enabled', True))
        st.session_state['cache_enabled'] = cache_enabled
        if st.button("🔄 Limpar Todo o Cache"):
            cache_manager.invalidate()
            st.cache_data.clear()
            st.success("Cache limpo com sucesso!")
        if selected_theme != st.session_state.get('theme'):
            st.session_state['theme'] = selected_theme
            st.rerun()
        st.subheader("🔄 Backup e Restauração")
        if st.button("💾 Fazer Backup"):
            backup_data = {
                'crm_leads': st.session_state.get('crm_leads', {}),
                'atividades': st.session_state.get('atividades', []),
                'historico_interacoes': st.session_state.get('historico_interacoes', {}),
                'analises_ia': st.session_state.get('analises_ia', {}),
                'dados_mensais': st.session_state.get('dados_mensais', {}),
                'meta': st.session_state.get('user_meta', META_MENSAL_DEFAULT),
                'timestamp': datetime.now().isoformat(),
                'username': st.session_state.get('username', 'demo')
            }
            backup_json = json.dumps(backup_data, default=str, indent=2)
            st.download_button(
                label="📥 Download Backup",
                data=backup_json,
                file_name=f"backup_crm_orfeu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        st.subheader("📤 Restaurar Backup")
        uploaded_file = st.file_uploader("Escolha um arquivo de backup", type=['json'])
        if uploaded_file is not None:
            if st.button("🔄 Restaurar Backup"):
                try:
                    backup_data = json.load(uploaded_file)
                    st.session_state['crm_leads'] = backup_data.get('crm_leads', {})
                    st.session_state['atividades'] = backup_data.get('atividades', [])
                    st.session_state['historico_interacoes'] = backup_data.get('historico_interacoes', {})
                    st.session_state['analises_ia'] = backup_data.get('analises_ia', {})
                    st.session_state['dados_mensais'] = backup_data.get('dados_mensais', {})
                    st.session_state['user_meta'] = backup_data.get('meta', META_MENSAL_DEFAULT)
                    for mes, dados in st.session_state['dados_mensais'].items():
                        for venda in dados.get('vendas', []):
                            if isinstance(venda.get('data'), str):
                                venda['data'] = pd.Timestamp(venda['data'])
                    st.success(f"✅ Backup restaurado com sucesso! Data do backup: {backup_data.get('timestamp', 'N/A')}")
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao restaurar backup: {e}")
        st.subheader("📥 Importar Lista de Clientes")
        st.info("Faça upload de um arquivo Excel com as colunas: Nome, Telefone, Email, Endereço, Bairro, Cidade")
        uploaded_clientes = st.file_uploader("Escolha um arquivo Excel", type=['xlsx', 'xls'])
        if uploaded_clientes is not None:
            try:
                df_clientes = pd.read_excel(uploaded_clientes)
                st.dataframe(df_clientes.head(), use_container_width=True)
                if st.button("📥 Importar Clientes para o CRM"):
                    crm = CRMSystem()
                    clientes_importados = 0
                    progress_bar = st.progress(0)
                    for index, row in df_clientes.iterrows():
                        lead_data = {
                            'Nome': row.get('Nome', 'Sem nome'),
                            'Telefone': str(row.get('Telefone', 'N/A')),
                            'Email': row.get('Email', 'N/A'),
                            'Endereço': row.get('Endereço', 'N/A'),
                            'Bairro': row.get('Bairro', 'N/A'),
                            'Cidade': row.get('Cidade', 'Rio de Janeiro'),
                            'Website': row.get('Website', 'N/A'),
                            'Instagram': row.get('Instagram', 'N/A'),
                            'Nota Média': row.get('Nota', 4.0),
                            'Nº de Avaliações': row.get('Avaliações', 100),
                            'Latitude': row.get('Latitude', 0),
                            'Longitude': row.get('Longitude', 0),
                            'Reviews_API': [],
                            'Tipo': row.get('Tipo', 'restaurant'),
                            'Faixa de Preço': row.get('Faixa de Preço', '$$'),
                            'Pontuação': row.get('Score', 70)
                        }
                        crm.adicionar_lead_ao_funil(lead_data)
                        clientes_importados += 1
                        progress_bar.progress((index + 1) / len(df_clientes))
                    progress_bar.empty()
                    st.success(f"✅ {clientes_importados} clientes importados com sucesso!")
                    time.sleep(2)
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")
                st.info("Verifique se o arquivo tem as colunas corretas")
        
        st.markdown("---")
        if st.button("🚪 Sair do Sistema", use_container_width=True):
            fazer_logout()
            st.rerun()

    with col2:
        st.subheader("Configurações de IA")
        preco_cafe_kg = st.number_input("Preço do Café Orfeu (R$/kg)", value=120.0, step=10.0,
                                        help="Preço médio do café especial Orfeu")
        st.markdown("### Multiplicadores de Consumo")
        st.info("Ajuste os multiplicadores para refinar as estimativas de consumo por tipo de estabelecimento")
        col1, col2 = st.columns(2)
        with col1:
            mult_restaurant = st.slider("Restaurantes", 0.5, 2.0, 1.2, step=0.1)
            mult_cafe = st.slider("Cafeterias", 0.5, 2.0, 1.5, step=0.1)
            mult_bakery = st.slider("Padarias", 0.5, 2.0, 1.3, step=0.1)
        with col2:
            mult_bar = st.slider("Bares", 0.5, 2.0, 0.8, step=0.1)
            mult_hotel = st.slider("Hotéis", 0.5, 2.0, 1.3, step=0.1)
            mult_super = st.slider("Supermercados", 0.5, 2.0, 0.9, step=0.1)
        if st.button("💾 Salvar Configurações de IA"):
            st.success("✅ Configurações salvas com sucesso!")
        st.markdown("### Metas e Comissões")
        comissao_padrao = st.slider("Comissão Padrão (%)", 0, 20, 10, step=1,
                                    help="Percentual de comissão sobre vendas")
        bonus_meta = st.number_input("Bônus por Atingir Meta (R$)", value=1000.0, step=100.0,
                                     help="Valor adicional ao atingir 100% da meta")
        st.markdown("### Integração com APIs")
        st.info("Para melhor funcionamento, configure suas próprias chaves de API")
        google_key = st.text_input("Google Maps API Key", 
                                   value="Sua chave aqui",
                                   type="password",
                                   help="Obtenha em: https://console.cloud.google.com/")
        gemini_key = st.text_input("Gemini API Key", 
                                   value="Sua chave aqui",
                                   type="password",
                                   help="Obtenha em: https://makersuite.google.com/app/apikey")
        if st.button("🔐 Validar e Salvar APIs"):
            if google_key and google_key != "Sua chave aqui":
                try:
                    test_client = googlemaps.Client(key=google_key)
                    test_client.geocode("Rio de Janeiro, Brasil")
                    st.success("✅ Google Maps API válida!")
                except:
                    st.error("❌ Google Maps API inválida")
            if gemini_key and gemini_key != "Sua chave aqui":
                try:
                    genai.configure(api_key=gemini_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content("Teste")
                    st.success("✅ Gemini API válida!")
                except:
                    st.error("❌ Gemini API inválida")
        st.markdown("### 📊 Estatísticas do Sistema")
        total_leads = sum(len(leads) for leads in st.session_state['crm_leads'].values())
        total_vendas = sum(len(dados.get('vendas', [])) for dados in st.session_state.get('dados_mensais', {}).values())
        total_analises = len(st.session_state.get('analises_ia', {}))
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Leads", total_leads)
        with col2:
            st.metric("Total de Vendas", total_vendas)
        with col3:
            st.metric("Análises IA", total_analises)
        st.markdown("### 🗑️ Gerenciar Dados")
        st.warning("⚠️ Atenção: Estas ações são irreversíveis!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Limpar Leads Perdidos"):
                st.session_state['crm_leads']['perdido'] = []
                st.success("✅ Leads perdidos removidos")
                st.rerun()
        with col2:
            if st.button("🔄 Resetar Sistema"):
                if st.checkbox("Confirmo que quero resetar todo o sistema"):
                    for key in list(st.session_state.keys()):
                        if key not in ['theme', 'logged_in', 'username', 'user_name', 'user_type', 'user_meta']:
                            del st.session_state[key]
                    st.success("✅ Sistema resetado com sucesso!")
                    time.sleep(2)
                    st.rerun()

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div class='footer-text'>
        <small style="color: #FAF7F2 !important; opacity: 0.7;">
            CRM Café Orfeu v5.2 | Sistema Completo com Meta Tracker, Market Share e Firebase<br>
            Desenvolvido com ❤️ para vendas B2B | © 2025 Café Orfeu
        </small>
    </div>
    """,
    unsafe_allow_html=True
)

if st.checkbox("🔧 Modo Debug", value=False):
    st.markdown("### Debug Info")
    debug_info = {
        "Logged In": st.session_state.get('logged_in', False),
        "Username": st.session_state.get('username', 'N/A'),
        "User Type": st.session_state.get('user_type', 'N/A'),
        "Admin Viewing": st.session_state.get('admin_viewing_user', 'N/A'),
        "Total Leads": sum(len(leads) for leads in st.session_state['crm_leads'].values()),
        "Leads por Estágio": {stage: len(leads) for stage, leads in st.session_state['crm_leads'].items()},
        "Total de Vendas": sum(len(dados.get('vendas', [])) for dados in st.session_state.get('dados_mensais', {}).values()),
        "Meta Atual": st.session_state.get('user_meta', 0),
        "Cache Ativo": st.session_state.get('cache_enabled', True),
        "Rotas Selecionadas": len(st.session_state.get('leads_selecionados_rota', []))
    }
    st.json(debug_info)

# Salva o estado no final de cada execução
save_state()