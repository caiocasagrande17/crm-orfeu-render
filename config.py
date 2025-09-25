# ========================================
# CONFIGURAÇÃO DO FIREBASE
# ========================================
# SUAS CREDENCIAIS DO FIREBASE (já configuradas!)
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyAxJ_Z-99le4JfrktZNFLLKrZ54nxC5Oq0",
    "authDomain": "jornada-vendedor-b2b---orfeu.firebaseapp.com",
    "databaseURL": "https://jornada-vendedor-b2b---orfeu-default-rtdb.firebaseio.com",
    "projectId": "jornada-vendedor-b2b---orfeu",
    "storageBucket": "jornada-vendedor-b2b---orfeu.firebasestorage.app",
    "messagingSenderId": "1043194750434",
    "appId": "1:1043194750434:web:128475c97ecda425e345bb"
}

# ========================================
# USUÁRIOS DO SISTEMA
# ========================================
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
GOOGLE_MAPS_KEY = "AIzaSyB6s0tsf4IBO7b3YqDQmhp2YwpbRIUG_AI"  # Sua chave do Google Maps
GEMINI_API_KEY = "AIzaSyCbS73hYP6oC4Si2YgycYN29W0HKQy0ekw"  # Sua chave do Gemini
META_MENSAL_DEFAULT = 250000  # Meta padrão