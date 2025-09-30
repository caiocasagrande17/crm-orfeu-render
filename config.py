import os

# ========================================
# CONFIGURAÇÃO DO FIREBASE
# ========================================
# SUAS CREDENCIAIS DO FIREBASE (já configuradas!)
FIREBASE_CONFIG = {
    "apiKey": os.environ.get("FIREBASE_API_KEY"),
    "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.environ.get("FIREBASE_DATABASE_URL"),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
    "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.environ.get("FIREBASE_APP_ID")
}

# ========================================
# USUÁRIOS DO SISTEMA
# ========================================
# ATENÇÃO: Armazenar senhas em texto plano é inseguro.
# O ideal é usar o sistema de autenticação do Firebase.
USUARIOS = {
    # Administrador
    'admin': {
        'senha': 'admin123',
        'nome': 'Administrador',
        'tipo': 'admin'
    },
    
    # Vendedores (10 usuários)
    'jonas': {
        'senha': 'cafe111',
        'nome': 'Jonas Oliveira',
        'tipo': 'vendedor'
    },
    'ana': {
        'senha': 'cafe222',
        'nome': 'Ana Argenta',
        'tipo': 'vendedor'
    },
    'janaina': {
        'senha': 'cafe333',
        'nome': 'Janaina Silveira',
        'tipo': 'vendedor'
    },
    'julio': {
        'senha': 'cafe444',
        'nome': 'Julio Salgado',
        'tipo': 'vendedor'
    },
    'luvisnai': {
        'senha': 'cafe555',
        'nome': 'Luvisnai Pires',
        'tipo': 'vendedor'
    },
    'rosangela': {
        'senha': 'cafe666',
        'nome': 'Rosangela Gomes',
        'tipo': 'vendedor'
    },
    'leila': {
        'senha': 'cafe777',
        'nome': 'Leila Vasconcelos',
        'tipo': 'vendedor'
    },
    'patricia': {
        'senha': 'cafe888',
        'nome': 'Patricia Alves',
        'tipo': 'vendedor'
    },
    'fernando': {
        'senha': 'cafe999',
        'nome': 'Fernando Dias',
        'tipo': 'vendedor'
    },
    'juliana': {
        'senha': 'cafe000',
        'nome': 'Juliana Ramos',
        'tipo': 'vendedor'
    }
}

# ========================================
# OUTRAS CONFIGURAÇÕES
# ========================================
GOOGLE_MAPS_KEY = os.environ.get("GOOGLE_MAPS_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
META_MENSAL_DEFAULT = 250000  # Meta padrão