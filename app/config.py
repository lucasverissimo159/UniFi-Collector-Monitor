"""
Configurações da aplicação UniFi Collector Monitor v3.0
Edite este arquivo para ajustar as configurações do sistema
"""

import os
import sys

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DO ÍCONE (FUNCIONA EM DEV E .EXE) - v3.0
# ══════════════════════════════════════════════════════════════════════════════
"""
Sistema que detecta automaticamente se está rodando como:
- Script Python (.py) → Usa caminho relativo
- Executável (.exe) → Usa caminho do PyInstaller

Isso garante que o ícone funciona em:
✅ Desenvolvimento (python run.py)
✅ Executável (.exe gerado pelo PyInstaller)
"""

# Detecta se está rodando como .exe ou script Python
if getattr(sys, 'frozen', False):
    # Rodando como .exe compilado
    BASE_DIR = sys._MEIPASS
else:
    # Rodando como script Python
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Caminho do ícone (funciona em ambos os modos)
WINDOW_ICON_PATH = os.path.join(BASE_DIR, 'resources', 'icons', 'icon.ico')

# ==================== CONFIGURAÇÕES UNIFI ====================
UNIFI_HOST = "https://192.0.2.1:8443"       # Endereço do UniFi Controller
UNIFI_USERNAME = "usuario_exemplo"          # Usuário UniFi
UNIFI_PASSWORD = "senha_exemplo"            # Senha UniFi
UNIFI_SITE = "default"                      # Site UniFi

# ==================== CONFIGURAÇÕES DE REDE ====================
# Range de IPs para escanear coletores livres
# IMPORTANTE: Estes valores são os PADRÕES iniciais
# Podem ser alterados pela interface gráfica (Aba Configurações → Range de IPs)
IP_SCAN_START = 100                         # IP inicial do range
IP_SCAN_END = 199                           # IP final do range
IP_BASE = "203.0.113"                     # Base do IP (203.0.113.XXX)

# Timeout para ping (segundos)
PING_TIMEOUT = 2
PING_COUNT = 1

# Workers para ping paralelo (mais workers = mais rápido, mas mais recursos)
MAX_PING_WORKERS = 30

# ==================== CONFIGURAÇÕES DE ATUALIZAÇÃO ====================
# Intervalo de auto-atualização (milissegundos)
AUTO_UPDATE_INTERVAL = 15000  # 15 segundos

# Intervalo de piscar indicadores (milissegundos)
BLINK_INTERVAL = 800

# ==================== CONFIGURAÇÕES DE INTERFACE ====================
# Tamanho da janela
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
WINDOW_TITLE = "Monitor de Coletores UniFi v3.0"

# ==================== CONFIGURAÇÕES DE DADOS ====================
# Arquivo de dados dos colaboradores
DATA_FILE = "colaboradores_data.json"

# ==================== FILTROS PADRÃO ====================
STATUS_OPTIONS = ['Todos', 'Online', 'Offline', 'Livre', 'Alerta']

# ==================== CONFIGURAÇÕES DE HISTÓRICO ====================
MAX_HISTORY_RECORDS = 15          # Máximo de registros no histórico ativo
RETENTION_MONTHS = 12             # Manter apenas últimos 12 meses
ARCHIVE_FOLDER = "historico_arquivado"  # Pasta para arquivos antigos

# ==================== SISTEMA DE BLOQUEIO DE IPs (NOVO v3.0) ====================
"""
Sistema Inteligente de Bloqueio de Coletores com IP Incorreto

Funcionamento:
- Tentativas 1-4: Desbloqueia temporariamente → Verifica → Bloqueia se incorreto
- Tentativa 5+: BLOQUEIO DEFINITIVO (mantém bloqueado, mas continua verificando)
- Quando IP for corrigido: Desbloqueia automaticamente

Exemplo:
    Coletor 58 está usando IP do Coletor 29 (203.0.113.129)
    
    Tentativa 1: Bloqueia → Aguarda 60s → Desbloqueia 10s → Verifica → Ainda errado → Bloqueia
    Tentativa 2: Bloqueia → Aguarda 60s → Desbloqueia 10s → Verifica → Ainda errado → Bloqueia
    Tentativa 3: Bloqueia → Aguarda 60s → Desbloqueia 10s → Verifica → Ainda errado → Bloqueia
    Tentativa 4: Bloqueia → Aguarda 60s → Desbloqueia 10s → Verifica → Ainda errado → Bloqueia
    Tentativa 5+: BLOQUEIO DEFINITIVO → NÃO desbloqueia mais → MAS continua verificando
                  → Quando IP for 203.0.113.158 (correto) → Desbloqueia automaticamente ✅
"""

# Ativar/desativar sistema de bloqueio automático
ENABLE_IP_BLOCKING = True

# Número máximo de tentativas antes do bloqueio definitivo
# Tentativas 1-4: Desbloqueia temporariamente para verificação
# Tentativa 5+: Bloqueio definitivo (sem desbloqueio temporário)
MAX_TENTATIVAS_BLOQUEIO = 4

# Tempo de desbloqueio temporário durante verificação (segundos)
# Usado nas tentativas 1-4 para permitir que o coletor reconecte
TEMP_UNBLOCK_TIME = 10

# Intervalo entre verificações de IPs incorretos (segundos)
# A cada X segundos, o sistema:
# 1. Desbloqueia temporariamente coletores nas tentativas 1-4
# 2. Verifica se IPs foram corrigidos
# 3. Bloqueia novamente se ainda incorretos
# 4. Desbloqueia definitivamente se IPs foram corrigidos
IP_BLOCK_CHECK_INTERVAL = 60

# Arquivo de estado dos bloqueios (criado automaticamente)
IP_BLOCKS_FILE = "ip_blocks.json"

# ==================== CONFIGURAÇÃO DE IP RANGE INTELIGENTE (NOVO v3.0) ====================
"""
Sistema Inteligente de Mapeamento IP/Coletor

O sistema detecta AUTOMATICAMENTE qual modo usar baseado no IP inicial:

MODO 1 - PADRÃO (Últimos 2 Dígitos):
    Usado quando: IP inicial é múltiplo de 100 (100, 200, 300)
    Regra: Coletor XX tem IP Base.StartXX
    
    Exemplo com range 100-199:
    - Coletor 00 → 203.0.113.100
    - Coletor 15 → 203.0.113.115
    - Coletor 58 → 203.0.113.158
    
    Exemplo com range 100-253:
    - Coletor 00 → 203.0.113.100
    - Coletor 15 → 203.0.113.115
    - Coletor 99 → 203.0.113.199
    - Coletor 100 → 203.0.113.200

MODO 2 - OFFSET (Sequencial):
    Usado quando: IP inicial NÃO é múltiplo de 100 (2, 50, 150)
    Regra: Coletor N tem IP Base.(Start + N)
    
    Exemplo com range 2-253:
    - Coletor 00 → 203.0.113.2 (2 + 0)
    - Coletor 15 → 203.0.113.17 (2 + 15)
    - Coletor 58 → 203.0.113.60 (2 + 58)
    
    Exemplo com range 2-199:
    - Coletor 00 → 203.0.113.2 (2 + 0)
    - Coletor 15 → 203.0.113.17 (2 + 15)
    - Coletor 50 → 203.0.113.52 (2 + 50)

CASOS SUPORTADOS:
✅ 203.0.113.100-199 → Modo Padrão (últimos 2 dígitos)
✅ 203.0.113.2-253 → Modo Offset (sequencial)
✅ 203.0.113.100-253 → Modo Padrão (últimos 2 dígitos)
✅ 203.0.113.2-199 → Modo Offset (sequencial)

IMPORTANTE:
    Estas configurações abaixo são valores PADRÃO iniciais.
    Podem ser alterados pela interface gráfica:
    Aba Configurações → Login Administrativo → Range de IPs
    
    As configurações via interface são salvas em: ip_range_config.json
    E têm PRIORIDADE sobre estes valores.
"""

# Range de IPs configurável (valores padrão)
IP_RANGE_BASE = "203.0.113"     # Base do IP (203.0.113.X)
IP_RANGE_START = 100              # IP inicial (1-254)
IP_RANGE_END = 199                # IP final (1-254)

# Arquivo de configuração do IP Range (criado automaticamente pela interface)
IP_RANGE_CONFIG_FILE = "ip_range_config.json"

# ==================== AUTENTICAÇÃO ADMINISTRATIVA (NOVO v3.0) ====================
"""
Sistema de Autenticação para Acesso às Configurações

CREDENCIAIS PADRÃO (primeiro acesso):
    Usuário: admin
    Senha: admin123

⚠️ IMPORTANTE: No primeiro acesso, o sistema OBRIGA a troca da senha padrão
               e a configuração de uma pergunta de segurança para recuperação.

FUNCIONALIDADES:
    ✅ Senha criptografada (SHA-256)
    ✅ Pergunta de segurança para recuperação
    ✅ Proteção de acesso às configurações
    ✅ Histórico de mudanças de senha

ARQUIVOS:
    - settings_auth.json: Armazena credenciais criptografadas
    
SEGURANÇA:
    ⚠️ Adicione ao .gitignore: settings_auth.json
    ⚠️ Não compartilhe o arquivo de autenticação
    ⚠️ Faça backup em local seguro
"""

# Credenciais administrativas padrão (usadas apenas no primeiro acesso)
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASS = "admin123"

# Arquivo de autenticação (criado automaticamente)
AUTH_FILE = "settings_auth.json"

# Forçar troca de senha no primeiro acesso
FORCE_PASSWORD_CHANGE_FIRST_ACCESS = True

# Tamanho mínimo da senha
MIN_PASSWORD_LENGTH = 6

# ==================== ARQUIVOS AUTO-CRIADOS (NÃO EDITAR) ====================
"""
Arquivos criados automaticamente pelo sistema:

1. unifi_config.json
   - Credenciais do UniFi Controller (editadas via interface)
   - Prioridade: JSON > config.py
   
2. colaboradores_data.json
   - Dados dos colaboradores e histórico
   
3. settings_auth.json
   - Credenciais administrativas criptografadas
   - ⚠️ ADICIONAR AO .gitignore
   
4. ip_blocks.json
   - Estado dos bloqueios de IPs
   - ⚠️ ADICIONAR AO .gitignore (opcional)
   
5. ip_range_config.json
   - Configuração de IP Range (editada via interface)
   - Prioridade: JSON > config.py

ADICIONAR AO .gitignore:
    unifi_config.json
    settings_auth.json
    ip_blocks.json
    ip_range_config.json
    colaboradores_data.json
"""

# ==================== LOGS E DEBUG ====================
# Habilitar logs de debug (para desenvolvimento)
DEBUG_MODE = False

# Arquivo de log do sistema de bloqueio
BLOCK_LOG_FILE = "monitor_bloqueio_coletores.log"

# ==================== INFORMAÇÕES DA VERSÃO ====================
VERSION = "3.0.0"
VERSION_DATE = "16/02/2026"
VERSION_NAME = "Sistema Inteligente Completo"

VERSION_CHANGELOG = """
v3.0.0 - Sistema Inteligente Completo (16/02/2026)
    ✨ NOVO: Sistema de bloqueio inteligente de IPs incorretos
             - Tentativas 1-4: Desbloqueia temporariamente
             - Tentativa 5+: Bloqueio definitivo
             - Desbloqueia automaticamente quando corrigido
    
    ✨ NOVO: Sistema de IP Range configurável
             - Detecta automaticamente modo (Padrão vs Offset)
             - Suporta 4 casos: 100-199, 2-253, 100-253, 2-199
             - Configurável via interface gráfica
    
    ✨ NOVO: Autenticação administrativa
             - Senha criptografada (SHA-256)
             - Pergunta de segurança para recuperação
             - Primeiro acesso obrigatório
    
    🔧 MELHORADO: Aba de Configurações
             - Login administrativo
             - Configuração de IP Range
             - Gerenciamento de bloqueios
             - Configurações de segurança

v2.1.0 - Settings Tab e IP Detection (06/11/2025)
    ✨ NOVO: Aba de Configurações pela interface
    🎯 MELHORADO: Detecção de IP incorreto aprimorada
    🔄 MELHORADO: Aplicação imediata de configurações

v2.0.0 - Estrutura Modular (Anterior)
    🗂️ Estrutura modular completa
    ✅ Sem flickering na tabela
    ✅ Filtros preservados
    ✅ Gestão de colaboradores
"""

# ==================== CONSTANTES DO SISTEMA ====================
# Setor padrão para coletores sem identificação
DEFAULT_SETOR = "N/A"

# Turnos disponíveis
AVAILABLE_SHIFTS = ["Manhã", "Tarde", "Noite", "Madrugada"]

# Status possíveis dos coletores
COLLECTOR_STATUS = {
    'ONLINE': '🟢 Online',
    'OFFLINE': '🔴 Offline',
    'LIVRE': '🔵 Livre',
    'ALERTA': '🟠 Alerta',
    'VERIFICANDO': '⏳ Verificando',
    'BLOQUEADO': '🚫 Bloqueado'
}

# ══════════════════════════════════════════════════════════════════════════════
# OVERRIDE LOCAL (credenciais/IPs reais - NAO versionado)
# ══════════════════════════════════════════════════════════════════════════════
# Os valores acima sao apenas EXEMPLOS (faixas RFC 5737 e placeholders).
# Para uso real, copie 'config_local.example.py' para 'app/config_local.py'
# e defina ali UNIFI_HOST, UNIFI_USERNAME, UNIFI_PASSWORD, IP_BASE, etc.
# O arquivo app/config_local.py esta no .gitignore e sobrescreve os valores acima.
try:
    from app.config_local import *  # noqa: F401,F403
except Exception:
    pass
