# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [3.0.0] - 2026-02-16

### 🎉 VERSÃO MAJOR - Sistema Inteligente Completo

Esta versão representa uma reformulação completa do sistema de configurações e segurança.

### ✨ Adicionado

#### **Sistema de Autenticação Administrativa**
- **Login obrigatório** para acessar configurações
- **Senha criptografada** (SHA-256)
- **Primeiro acesso obrigatório** - força troca de senha padrão
- **Pergunta de segurança** para recuperação de senha
- **10 perguntas pré-definidas** para escolha do usuário
- **Logout** para proteção quando não utilizado
- **Arquivo**: `settings_auth.json` (credenciais criptografadas)

#### **Sistema de Bloqueio Inteligente de IPs Incorretos**
- **Bloqueio progressivo** de coletores com IP incorreto:
  - Tentativas 1-4: Desbloqueia temporariamente (10s) para verificação
  - Tentativa 5+: Bloqueio definitivo (sem desbloqueio temporário)
- **Desbloqueio automático** quando IP for corrigido
- **Persistência** em `ip_blocks.json`
- **Estatísticas** na aba de configurações:
  - Total de bloqueios
  - Bloqueios temporários vs definitivos
  - Detalhes de cada bloqueio (tentativas, última atualização)
- **Logs** em `monitor_bloqueio_coletores.log`

#### **Sistema de IP Range Configurável**
- **Detecção automática de modo**:
  - **Modo PADRÃO** (últimos 2 dígitos): Quando range inicia em múltiplo de 100
  - **Modo OFFSET** (sequencial): Quando range NÃO inicia em múltiplo de 100
- **4 casos suportados**:
  - ✅ 203.0.113.100-199 → Modo Padrão
  - ✅ 203.0.113.2-253 → Modo Offset
  - ✅ 203.0.113.100-253 → Modo Padrão
  - ✅ 203.0.113.2-199 → Modo Offset
- **Interface gráfica** para configuração:
  - Campo Base IP
  - Spinners para Start/End IP
  - Preview em tempo real do modo detectado
  - Exemplos de mapeamento
- **Persistência** em `ip_range_config.json`
- **Aplicação imediata** sem reiniciar

#### **Aba de Configurações Completa (3 Tabs)**
1. **🌐 UniFi Controller**
   - Host, Usuário, Senha
   - Testar conexão
   - Salvar configurações
   
2. **📡 Range de IPs** (NOVO!)
   - Configurar Base IP
   - Configurar Start/End IP
   - Preview em tempo real
   - Salvar configuração
   
3. **🚫 Bloqueios** (NOVO!)
   - Estatísticas de bloqueios
   - Lista de dispositivos bloqueados
   - Status (Temporário vs Definitivo)
   - Atualizar estatísticas

#### **Módulos Novos**
- `app/data/auth_manager.py` - Gerenciamento de autenticação
- `app/data/ip_blocker.py` - Sistema de bloqueio
- `app/data/ip_mapping.py` - Mapeamento inteligente IP/Coletor
- `app/gui/login_dialog.py` - Dialog de login
- `app/gui/first_access_dialog.py` - Dialog de primeiro acesso
- `app/gui/password_reset_dialog.py` - Dialog de recuperação

### 🔧 Melhorado

#### **collection_worker.py**
- Carrega IP Range de `ip_range_config.json`
- Escaneia range configurável
- Nomeação inteligente de IPs livres usando IPMapping

#### **main_window.py & collaborators_tab.py**
- Verificação de IP usando `check_collector_ip_mismatch()`
- Suporte para qualquer range configurado
- Detecção automática de modo

#### **settings_tab.py**
- Completamente reformulado
- Sistema de autenticação integrado
- 3 tabs organizadas
- Preview em tempo real
- Estatísticas de bloqueio

#### **config.py**
- Documentação completa de todas as configurações
- Seções organizadas:
  - Configurações UniFi
  - Configurações de Rede
  - Sistema de Bloqueio
  - IP Range Inteligente
  - Autenticação Administrativa
- Valores padrão bem definidos
- Changelog de versões

### 🐛 Corrigido
- **Nomeação de IPs livres** agora usa IPMapping corretamente
- **Persistência de configurações** funcionando 100%
- **Detecção de modo** automática e precisa
- **Aplicação imediata** de configurações

### 📁 Arquivos Novos
```
app/data/
├── auth_manager.py          # Sistema de autenticação
├── ip_blocker.py            # Sistema de bloqueio
└── ip_mapping.py            # Mapeamento IP/Coletor

app/gui/
├── login_dialog.py          # Dialog de login
├── first_access_dialog.py   # Dialog de primeiro acesso
└── password_reset_dialog.py # Dialog de recuperação

Arquivos de dados (auto-criados):
├── settings_auth.json       # Credenciais administrativas
├── ip_blocks.json           # Estado dos bloqueios
├── ip_range_config.json     # Configuração de IP Range
└── monitor_bloqueio_coletores.log # Logs de bloqueio
```

### 🔒 Segurança

#### **Credenciais Administrativas**
- Senha padrão: `admin` / `admin123` (primeiro acesso)
- **Primeiro acesso obriga troca**
- SHA-256 hash para senhas
- Pergunta de segurança criptografada
- Arquivo `settings_auth.json` deve estar no .gitignore

#### **Arquivo .gitignore Recomendado**
```
unifi_config.json
settings_auth.json
ip_blocks.json
ip_range_config.json
colaboradores_data.json
monitor_bloqueio_coletores.log
*.log
```

### 📊 Estatísticas

#### **Sistema de Bloqueio**
- Monitora coletores com IP incorreto
- Bloqueia automaticamente no UniFi
- Mantém contagem de tentativas
- Desbloqueia quando IP correto

#### **IP Range**
- Suporta qualquer faixa (1-254)
- Calcula automaticamente IPs esperados
- Valida IPs de coletores
- Mostra preview em tempo real

### 🎯 Fluxos Principais

#### **Fluxo de Primeiro Acesso**
```
1. Aplicação abre
2. FirstAccessDialog aparece
3. Usuário troca senha padrão
4. Escolhe pergunta de segurança
5. Define resposta (criptografada)
6. Sistema marca first_access=false
7. Próximo acesso: LoginDialog normal
```

#### **Fluxo de Configuração de IP Range**
```
1. Login em Configurações
2. Tab "📡 Range de IPs"
3. Configurar: Base, Start, End
4. Preview mostra modo detectado
5. Salvar → ip_range_config.json
6. Sistema reinicia coleta
7. Novo range aplicado imediatamente
```

#### **Fluxo de Bloqueio**
```
1. Coletor detectado com IP errado
2. Sistema adiciona ao ip_blocks.json
3. Tentativa 1: Bloqueia → Aguarda 60s → Desbloqueia 10s → Verifica
4. Se ainda errado: Repete até tentativa 4
5. Tentativa 5+: Bloqueio definitivo
6. Continua verificando em background
7. Quando IP correto: Desbloqueia automaticamente
```

### 📝 Documentação
- README.md atualizado para v3.0
- ARCHITECTURE.md com novos componentes
- EXAMPLES.md com 20+ exemplos
- INSTALLATION.txt com guia completo
- PROJECT_SUMMARY.txt atualizado
- QUICKSTART.md simplificado

### ⚙️ Configurações Padrão v3.0

```python
# Bloqueio
ENABLE_IP_BLOCKING = True
MAX_TENTATIVAS_BLOQUEIO = 4
TEMP_UNBLOCK_TIME = 10
IP_BLOCK_CHECK_INTERVAL = 60

# IP Range
IP_RANGE_BASE = "203.0.113"
IP_RANGE_START = 100
IP_RANGE_END = 199

# Autenticação
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASS = "admin123"
MIN_PASSWORD_LENGTH = 6
```

---

## [2.1.0] - 2025-11-06

### ✨ Adicionado
- **Aba de Configurações** (⚙️ Settings Tab)
- **Detecção Aprimorada de IP Incorreto**
- **Função `load_unifi_credentials()`**

### 🔧 Melhorado
- Aplicação imediata de configurações
- Interface de tabs
- Gestão de colaboradores

### 🐛 Corrigido
- Configurações não eram aplicadas
- Botões em linhas incorretas

---

## [2.0.0] - 2025-01-XX

### ✨ Adicionado
- Estrutura modular do projeto
- Documentação completa
- Suporte a ícone personalizado

### 🔧 Melhorado
- Tabela sem flickering
- Barra de status dividida
- Filtros mantidos

---

## [1.0.0] - 2024-XX-XX

### ✨ Inicial
- Monitor de coletores UniFi
- Gestão de colaboradores
- Sistema de filtros
- Auto-atualização

---

## Convenções deste Changelog

### Tipos de Mudança
- `✨ Adicionado` - Novas funcionalidades
- `🔧 Melhorado` - Melhorias em funcionalidades existentes
- `🐛 Corrigido` - Correções de bugs
- `📝 Documentação` - Mudanças na documentação
- `📁 Arquivos Novos` - Novos arquivos adicionados
- `🔒 Segurança` - Melhorias de segurança
- `⚠️ Deprecated` - Funcionalidades marcadas como obsoletas
- `🗑️ Removido` - Funcionalidades removidas

### Formato de Versionamento
O projeto segue [Semantic Versioning](https://semver.org/):
- **MAJOR** (X.0.0) - Mudanças incompatíveis ou reformulação significativa
- **MINOR** (0.X.0) - Novas funcionalidades compatíveis
- **PATCH** (0.0.X) - Correções de bugs compatíveis

---

**Última Atualização**: 16/02/2026  
**Versão Atual**: 3.0.0 - Sistema Inteligente Completo
