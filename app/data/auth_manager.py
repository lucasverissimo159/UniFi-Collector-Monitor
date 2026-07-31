"""
Sistema de Autenticação para Configurações
Gerencia usuário administrativo com senha criptografada e recuperação
"""

import json
import os
import hashlib
from datetime import datetime

# Arquivo de autenticação
AUTH_FILE = "settings_auth.json"

# Credenciais padrão (primeiro acesso)
DEFAULT_USER = "admin"
DEFAULT_PASSWORD = "admin123"  # Será trocada no primeiro acesso


class AuthManager:
    """Gerencia autenticação do usuário administrativo"""
    
    @staticmethod
    def hash_password(password):
        """Criptografa senha usando SHA-256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    @staticmethod
    def initialize_auth():
        """Inicializa arquivo de autenticação se não existir"""
        if not os.path.exists(AUTH_FILE):
            # Criar arquivo com credenciais padrão
            auth_data = {
                "username": DEFAULT_USER,
                "password_hash": AuthManager.hash_password(DEFAULT_PASSWORD),
                "security_question": "",
                "security_answer_hash": "",
                "first_access": True,
                "created_at": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                "last_password_change": ""
            }
            
            with open(AUTH_FILE, 'w', encoding='utf-8') as f:
                json.dump(auth_data, f, indent=4, ensure_ascii=False)
            
            return True
        return False
    
    @staticmethod
    def load_auth_data():
        """Carrega dados de autenticação"""
        AuthManager.initialize_auth()
        
        try:
            with open(AUTH_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    @staticmethod
    def save_auth_data(data):
        """Salva dados de autenticação"""
        try:
            with open(AUTH_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    @staticmethod
    def verify_login(username, password):
        """Verifica login do usuário"""
        auth_data = AuthManager.load_auth_data()
        
        if not auth_data:
            return False
        
        # Verificar username e senha
        if username != auth_data.get("username"):
            return False
        
        password_hash = AuthManager.hash_password(password)
        if password_hash != auth_data.get("password_hash"):
            return False
        
        return True
    
    @staticmethod
    def is_first_access():
        """Verifica se é primeiro acesso"""
        auth_data = AuthManager.load_auth_data()
        if auth_data:
            return auth_data.get("first_access", False)
        return True
    
    @staticmethod
    def setup_security_question(question, answer):
        """Configura pergunta de segurança (primeiro acesso)"""
        auth_data = AuthManager.load_auth_data()
        if not auth_data:
            return False
        
        auth_data["security_question"] = question
        auth_data["security_answer_hash"] = AuthManager.hash_password(answer.lower().strip())
        auth_data["first_access"] = False
        auth_data["last_password_change"] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        return AuthManager.save_auth_data(auth_data)
    
    @staticmethod
    def change_password(new_password):
        """Troca senha do usuário"""
        auth_data = AuthManager.load_auth_data()
        if not auth_data:
            return False
        
        auth_data["password_hash"] = AuthManager.hash_password(new_password)
        auth_data["last_password_change"] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        return AuthManager.save_auth_data(auth_data)
    
    @staticmethod
    def verify_security_answer(answer):
        """Verifica resposta da pergunta de segurança"""
        auth_data = AuthManager.load_auth_data()
        if not auth_data:
            return False
        
        answer_hash = AuthManager.hash_password(answer.lower().strip())
        return answer_hash == auth_data.get("security_answer_hash", "")
    
    @staticmethod
    def get_security_question():
        """Obtém pergunta de segurança"""
        auth_data = AuthManager.load_auth_data()
        if auth_data:
            return auth_data.get("security_question", "")
        return ""
    
    @staticmethod
    def has_security_question():
        """Verifica se pergunta de segurança está configurada"""
        question = AuthManager.get_security_question()
        return bool(question and question.strip())
    
    @staticmethod
    def reset_password_with_security(answer, new_password):
        """Reseta senha usando pergunta de segurança"""
        if not AuthManager.verify_security_answer(answer):
            return False
        
        return AuthManager.change_password(new_password)
    
    @staticmethod
    def get_auth_info():
        """Retorna informações de autenticação (sem senhas)"""
        auth_data = AuthManager.load_auth_data()
        if not auth_data:
            return None
        
        return {
            "username": auth_data.get("username", ""),
            "first_access": auth_data.get("first_access", True),
            "has_security_question": AuthManager.has_security_question(),
            "created_at": auth_data.get("created_at", ""),
            "last_password_change": auth_data.get("last_password_change", "")
        }


# Inicializar ao importar
AuthManager.initialize_auth()