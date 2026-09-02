# 📡 UniFi Collector Monitor v3.0.0 - Complete Smart System

UniFi Collector Monitor with Employee Management, Administrative Authentication, Smart Blocking and Configurable IP Range - Professional graphical interface for real-time monitoring.

> ⚠️ **Repository available for portfolio only.** The code can
> be viewed, but **cannot** be copied, downloaded, used or
> reused in other projects. See the [License](#-license) section and the
> file [`LICENSE`](./LICENSE).

## 🎉 NEWS v3.0.0 (02/16/2026)

### 🔐 **Administrative Authentication System** (NEW!)
- Login required to access settings
- Encrypted password (SHA-256)
- First access requires changing the default password
- Security question for recovery
- Logout for protection

### 🚫 **Smart Lock System** (NEW!)
- Progressive blocking of collectors with incorrect IP
- Attempts 1-4: Temporary lock with unlock (10s) for verification
- Attempt 5+: Definitive blocking
- Automatic unlocking when IP is fixed
- Real-time statistics

### 📡 **Configurable IP Range** (NEW!)
- Automatic mode detection:
  - **STANDARD** (100-199): Last 2 digits
  - **OFFSET** (2-253): Sequential
- Interface with real-time preview
- Supports any range (1-254)
- Immediate application without restarting

### ⚙️ **Settings - 3 Tabs** (UPDATED!)
- Tab 1: 🌐 UniFi Controller
- Tab 2: 📡 IP Range (NEW!)
- Tab 3: 🚫 Locks (NEW!)

---

## 🚀 Features

- **🔐 Secure Authentication**: SHA-256 login, first login required, password recovery
- **🚫 Smart Blocking**: Automatic progressive blocking of incorrect IPs
- **📡 Configurable IP Range**: Any range (2-253, 100-199, etc) with automatic detection
- **⚙️ Configuration through the Interface**: 3 organized tabs (UniFi, IP Range, Blocks)
- **Real-Time Monitoring**: Collector status (Online/Offline/Free/Alert)
- **Auto-update**: Automatic update every 15 seconds
- **Employee Management**: Assignment of employees per collector with shifts
- **Incorrect IP Detection**: Visual alert + automatic blocking
- **Advanced Filters**: Filters by status, sector, manufacturer, name and IP
- **Modern Interface**: PyQt5 with professional design
- **Full Persistence**: All settings saved in JSON

---

## 📋 Requirements

- Python 3.7+
- PyQt5 >= 5.15.0
- requests >= 2.28.0
- urllib3 >= 1.26.0

---

## 🔧 Installation

### 1. Clone or download the project
```bash
cd unifi-collector-monitor
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python3 run.py
```

### 4. First Access (NEW v3.0) 🔐

**MANDATORY** in the first run:
```
┌────────────────────────────────────┐
│ 🎯 Primeiro Acesso Obrigatório     │
├────────────────────────────────────┤
│ Credenciais padrão:                │
│   Usuário: admin                   │
│   Senha: admin123                  │
│                                    │
│ 1. Digite NOVA senha (min 6 chars)│
│ 2. Escolha pergunta de segurança  │
│ 3. Digite resposta (criptografada)│
│ 4. Clique "✅ Configurar"         │
└────────────────────────────────────┘
```

### 5. Configure the System (v3.0)

1. Login to **"⚙️ Settings"**
2. **Tab 🌐 UniFi**: Edit UniFi credentials
3. **Tab 📡 IP Range**: Configure IP range
4. **Tab 🚫 Blocks**: View statistics
5. Done! ✅

---

## 📁 Project Structure v3.0
```
unifi-collector-monitor/
│
├── app/
│   ├── __init__.py
│   ├── config.py                    # ⚙️ Configurações padrão v3.0
│   │
│   ├── workers/                     # ⚡ Threads de processamento
│   │   ├── __init__.py
│   │   ├── collection_worker.py    # Coleta UniFi + IP Range [v3.0]
│   │   └── status_worker.py        # Verificação de status
│   │
│   ├── gui/                         # 🖥️ Interface gráfica
│   │   ├── __init__.py
│   │   ├── main_window.py          # Janela principal
│   │   ├── collaborators_tab.py    # Aba de Colaboradores
│   │   ├── settings_tab.py         # ⚙️ 3 TABS Config [v3.0]
│   │   ├── login_dialog.py         # 🔐 Login [NOVO v3.0]
│   │   ├── first_access_dialog.py  # 🎯 Primeiro Acesso [NOVO v3.0]
│   │   └── password_reset_dialog.py # 🔑 Recuperação [NOVO v3.0]
│   │
│   └── data/                        # 💾 Gerenciamento de dados
│       ├── __init__.py
│       ├── data_manager.py         # Persistência colaboradores
│       ├── auth_manager.py         # 🔐 Autenticação [NOVO v3.0]
│       ├── ip_blocker.py           # 🚫 Bloqueio [NOVO v3.0]
│       └── ip_mapping.py           # 📡 IP/Coletor [NOVO v3.0]
│
├── docs/                            # 📚 Documentação v3.0
│   ├── EXAMPLES.md                 # 23 exemplos práticos
│   ├── CONTRIBUTING.md             # Guia desenvolvedores
│   └── ARCHITECTURE.md             # Arquitetura v3.0
│
├── resources/                       # 🎨 Recursos visuais
│   └── icons/
│       ├── icon.png                # Ícone da aplicação
│       └── README.md
│
├── .gitignore                      # Git ignore (CRÍTICO v3.0!)
├── CHANGELOG.md                    # Histórico completo v3.0
├── QUICKSTART.md                   # Guia rápido 5 minutos
├── INSTALACAO.txt                  # Guia instalação completo
├── PROJECT_SUMMARY.txt             # Estrutura resumida
├── README.md                       # 📖 Este arquivo
├── requirements.txt                # 📦 Dependências Python
├── setup.sh                        # 🔧 Script de instalação
├── run.py                          # 🚀 EXECUTAR AQUI!
│
├── unifi_config.json               # 🌐 Credenciais UniFi [AUTO]
├── settings_auth.json              # 🔐 Credenciais Admin [AUTO v3.0]
├── ip_range_config.json            # 📡 Config IP Range [AUTO v3.0]
├── ip_blocks.json                  # 🚫 Bloqueios [AUTO v3.0]
└── colaboradores_data.json         # 💾 Colaboradores [AUTO]
```---

## 🎯 Main Features v3.0

### 🔐 Administrative Authentication (NEW v3.0)

**First Access Mandatory:**
- Default credentials: `admin` / `admin123`
- System **REQUIRES** password change on first run
- Choose security question (10 options)
- Encrypted response (SHA-256)
- File: `settings_auth.json` (SHA-256 password)

**Login:**
- Access to settings requires authentication
- SHA-256 encrypted password (not reversible)
- Logout for protection

**Password Recovery:**
- Forgot your password? Use security question
- Response verified via SHA-256 hash
- Set new password if correct answer

### 🚫 Smart Lock System (NEW v3.0)

**Progressive Lock:**
```
Coletor detectado com IP incorreto:

Tentativa 1:
├─ Bloqueia no UniFi Controller
├─ Aguarda 60 segundos
├─ Desbloqueia temporariamente (10 segundos)
├─ Verifica se IP foi corrigido
└─ Ainda incorreto? → Bloqueia novamente

Tentativas 2-4: Repete processo acima

Tentativa 5+:
├─ BLOQUEIO DEFINITIVO
├─ NÃO desbloqueia mais automaticamente
├─ MAS continua verificando em background
└─ Se IP corrigido: Desbloqueia automaticamente ✅
```

**Statistics:**
- Total blocks
- Temporary vs Permanent
- Details of each block (attempts, last update)
- File: `ip_blocks.json`

**Logs:**
- File: `monitor_bloqueio_coletores.log`
- Record of all blocking/unblocking actions

### 📡 Configurable IP Range (NEW v3.0)

**Automatic Mode Detection:**

| Range | Detected Mode | Calculation |
|-------|----------------|---------|
| 100-199 | PATTERN (Last 2 digits) | Collector 15 → .115 |
| 2-253 | OFFSET (Sequential) | Collector 15 → .17 (2+15) |
| 100-253 | PATTERN | Collector 15 → .115 |
| 2-199 | OFFSET | Collector 15 → .17 |

**Detection Rule:**
```python
if start_ip % 100 == 0:
    modo = "PADRÃO"  # 100, 200 → Últimos 2 dígitos
else:
    modo = "OFFSET"  # 2, 50 → Sequencial
```

**Interface:**
- IP Base Field
- Spinners Start/End IP (1-254)
- **Real-Time Preview:**
  - Automatically detected mode
  - Mapping examples
  - First and last collector
- Immediate application when saving
- File: `ip_range_config.json`

### ⚙️ Settings - 3 Tabs (UPDATED v3.0)

**Login Required** to access:

**Tab 1: 🌐 UniFi Controller**
- Host, User, Password
- Test connection before saving
- Save settings

**Tab 2: 📡 IP Range** (NEW!)
- IP base
- Start/End IP
- Real-time preview
- Save configuration

**Tab 3: 🚫 Locks** (NEW!)
- Blocking statistics
- List of blocked devices
- Status (Temporary vs Definitive)
- Update statistics

### 🖥️ Collector Monitor

- Real-time status view
- Visual indicators: 🟢 Online | 🔴 Offline | 🔵 Free | 🟠 Alert
- Automatic detection of free IPs (configurable range v3.0)
- Parallel ping for quick checking
- Multiple simultaneous filters

### 👥 Employee Management

- Assignment of collaborators by collector
- Definition of shifts (Morning/Afternoon/Night/Dawn)
- Customized schedules
- Assignment history

**Incorrect IP Detection with Blocking (v3.0):**

When Collector 58 uses Collector 29's IP:

```
┌───────────────────────────────────────────────────────┐
│ Coletor 29 - SEP | 203.0.113.129                    │  ← 🔴 Pisca vermelho
│ [SEM BOTÕES]                                           │     (Vítima - IP roubado)
├───────────────────────────────────────────────────────┤
│ ⚠️ Coletor 58 - SEP (IP INCORRETO) | ❌ 203.0.113.129│  ← 🔴 Pisca + BLOQUEADO
│ [SEM BOTÕES]                                           │     (Usando IP errado)
├───────────────────────────────────────────────────────┤
│ ✅ Coletor 58 - SEP (IP CORRETO) | ✓ 203.0.113.158  │  ← 🟢 Fundo verde
│ [➕][✏️][🗑️][📋]                                         │     (IP correto + ações)
└───────────────────────────────────────────────────────┘
```

**Automatic System (v3.0):**
1. Detects incorrect IP ✅
2. Adds to `ip_blocks.json` ✅
3. Blocks on UniFi Controller ✅
4. Attempts 1-4: Unlock temp. (10s) for verification ✅
5. Attempt 5+: Permanent block ✅
6. When to fix: Automatically unlocks ✅

---

## ⚙️ Configuration

### Method 1: Via Graphical Interface (Recommended) ⭐

#### Step 1: First Access (v3.0)
```bash
python3 run.py
```

Dialog appears automatically:
1. **Enter new password** (minimum 6 characters)
2. **Choose security question** (10 options)
3. **Enter response** (will be encrypted)
4. Click **"✅ Configure and Access"**

#### Step 2: Login

1. **"⚙️ Settings"** tab
2. Click **"🔐 Login"**
3. User: `admin` / Password: your new password
4. Click **"✅ Enter"**

#### Step 3: Configure UniFi

1. Tab **"🌐 UniFi Controller"**
2. Host: `https://203.0.113.1:8443`
3. User: `user_example`
4. Password: `example_password`
5. (Optional) **"🔌 Test Connection"**
6. **"💾 Save"**

#### Step 4: Configure IP Range (NEW v3.0)

1. Tab **"📡 IP Range"**
2. Base IP: `203.0.113`
3. Range: `100` to `199` (or `2` to `253`)
4. See real-time preview
5. **"💾 Save IP Range Setting"**

#### Step 5: View Blocks (NEW v3.0)

1. Tab **"🚫 Locks"**
2. View real-time statistics
3. **"🔄 Update Statistics"**

### Method 2: Via config.py File (Optional)
```python
# Conexão UniFi
UNIFI_HOST = "https://203.0.113.1:8443"
UNIFI_USERNAME = "usuario"
UNIFI_PASSWORD = "senha"

# IP Range (v3.0)
IP_RANGE_BASE = "203.0.113"
IP_RANGE_START = 100  # ou 2
IP_RANGE_END = 199    # ou 253

# Bloqueio (v3.0)
ENABLE_IP_BLOCKING = True
MAX_TENTATIVAS_BLOQUEIO = 4
TEMP_UNBLOCK_TIME = 10
IP_BLOCK_CHECK_INTERVAL = 60

# Atualização
AUTO_UPDATE_INTERVAL = 15000  # 15 segundos
BLINK_INTERVAL = 800          # 0.8 segundos

# Interface
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
```
**Note:** Interface overrides these values!

### Load Priority v3.0
```
🔍 Sistema de Carregamento Inteligente:

1. Credenciais UniFi:
   ├─ unifi_config.json existe? → Usa JSON
   └─ Não existe? → Usa config.py

2. IP Range:
   ├─ ip_range_config.json existe? → Usa JSON [v3.0]
   └─ Não existe? → Usa config.py (100-199)

3. Autenticação:
   ├─ settings_auth.json existe? → Requer login [v3.0]
   └─ Não existe? → Primeiro acesso obrigatório

4. Bloqueios:
   └─ ip_blocks.json (sempre usado) [v3.0]
```---

## 📖 How to Use

### 1. First Run (v3.0)

**First Access Mandatory:**
- Run: `python3 run.py`
- Dialog appears automatically
- **Change default password** (required!)
- Configure security question
- Click "✅ Configure"

**Login:**
- **"⚙️ Settings"** tab
- Click **"🔐 Login"**
- Use new password

**Configure:**
- Tab **"🌐 UniFi"**: UniFi Credentials
- Tab **"📡 IP Range"**: IP range
- Tab **"🚫 Blocks"**: Statistics

### 2. Monitoring

- The application automatically starts the collection
- Active auto-update (15 seconds)
- Use filters to find collectors
- Click **"🔄 Update Status"** for manual

### 3. Employee Management

- Tab **"👥 Employee Management"**
- Click **"➕"** to add
- Fill in: Name, Function, Shift, Schedule
- Click **"✏️"** to edit
- Click **"🗑️"** to remove
- Click **"📋"** for details and history
- ⚠️ **Lines with INCORRECT IP (red) do not allow editing**
- 🚫 **Blocked collectors appear in the Blocks tab (v3.0)**

### 4. Recover Password (v3.0)

If you forget your password:
1. **"⚙️ Settings"** tab
2. Click **"Forgot password?"**
3. Answer security question
4. Enter new password
5. Click **"✅ Reset"**

### 5. Filters

- **Status**: All, Online, Offline, Free, Alert
- **Sector**: All, Receiving, Separation
- **Manufacturer**: Filters by device manufacturer
- **Name**: Textual search in the name of the collector
- **IP**: Textual search on IP address

---

## 🔐 Security v3.0

### Sensitive Files

**⚠️ CRITICAL: Add to .gitignore!**
```bash
# .gitignore
unifi_config.json           # Credenciais UniFi
settings_auth.json          # Credenciais admin (SHA-256)
ip_blocks.json              # Bloqueios
ip_range_config.json        # IP Range
colaboradores_data.json     # Dados
monitor_bloqueio_coletores.log  # Logs
*.log
```

### Good Practices

1. **Change default password** on first access (mandatory)
2. **Add files to .gitignore**
3. **chmod 600 settings_auth.json** (Linux/Mac)
4. **Back up** in a safe location
5. **DO NOT share** JSON files
6. **Change password** periodically

### Risk Mitigations

- ✅ SHA-256 (non-reversible)
- ✅ First access required
- ✅ Security question
- ⚠️ UniFi in plain text (`unifi_config.json`)
- 🔒 Consider AES for production

---

## 🛠️ Maintenance and Development

### Modify Tab Width

In `app/gui/main_window.py` (line ~55):
```python
QTabBar::tab {
    padding: 10px 60px;    # Segundo valor = largura
    min-width: 250px;
}
```

### Add New Sector

To add a new sector, update the settings and filters in the interface.

### Example 1: First Access Required
```text
1. Execute: python3 run.py
2. Digite NOVA senha (mínimo 6 caracteres)
3. Escolha uma pergunta de segurança.
4. Escolher pergunta: "Qual o nome da sua mãe?"
5. Resposta: "Maria" (criptografada)
6. ✅ Sistema pronto!
```

### Example 2: Configure Range 2-253
```
1. Login em ⚙️ Configurações
2. Tab "📡 Range de IPs"
3. Base: 203.0.113
4. Range: 2 até 253
5. Preview mostra: "Modo OFFSET (Sequencial)"
6. Exemplo: Coletor 15 → 203.0.113.17
7. 💾 Salvar
8. ✅ Sistema escaneia 2-253!
```

### Example 3: Automatic Lock
```
Coletor 58 com IP .129 (errado, deveria ser .158):

1. Sistema detecta IP incorreto
2. Bloqueia no UniFi
3. Tentativas 1-4: Desbloqueia temp. (10s)
4. Tentativa 5+: Bloqueio definitivo
5. Quando corrigir para .158: Desbloqueia auto ✅
```

More examples: [docs/EXAMPLES.md](docs/EXAMPLES.md)

---

## 🤝 Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
- Project structure
- Good practices v3.0
- Examples of modifications
- Authentication, IP Range and blocking flows

---

## 📄 License

This repository **is not open source**. It is publicly available
for portfolio/technical demonstration purposes only.

- ✅ Allowed: viewing the code through the GitHub interface.
- ❌ Prohibited: copying, downloading, cloning for reuse, using, modifying, executing
  or redistribute this code, in whole or in part, without prior authorization
  and in writing from the author.

All rights are reserved. See full terms at
[`LICENSE`](./LICENSE).

---

## 👨‍💻 Developer

**Lucas Veríssimo de Oliveira**
Company

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete history.

### v3.0.0 (02/16/2026) - Complete Intelligent System
- ✅ Administrative authentication (SHA-256)
- ✅ Progressive smart lock
- ✅ Configurable IP Range
- ✅ 3 configuration tabs
- ✅ Automatic mode detection
- ✅ Dialogs (Login, FirstAccess, PasswordReset)

### v2.1.0 (06/11/2025)
- ✅ Configuration via the interface
- ✅ Improved bad IP detection
- ✅ Immediate application of settings

### v2.0.0 (01/01/2025)
- ✅ Modular structure
- ✅ Table without flickering
- ✅ Complete documentation

---

## 🎉 Ready to Use!
```bash
# Instalar
pip install -r requirements.txt

# Executar
python3 run.py

# Primeiro acesso: trocar senha
# Login: configurar sistema
# Usar: monitorar coletores!
```

**Version 3.0.0 - Smart, Secure and Configurable System** 🔐📡🚫

---

# 📡 UniFi Collector Monitor v3.0.0 - Sistema Inteligente Completo

Monitor de Coletores UniFi com Gestão de Colaboradores, Autenticação Administrativa, Bloqueio Inteligente e IP Range Configurável - Interface gráfica profissional para monitoramento em tempo real.

> ⚠️ **Repositório disponibilizado apenas para portfólio.** O código pode
> ser visualizado, mas **não** pode ser copiado, baixado, usado ou
> reaproveitado em outros projetos. Veja a seção [Licença](#-licença) e o
> arquivo [`LICENSE`](./LICENSE).

## 🎉 NOVIDADES v3.0.0 (16/02/2026)

### 🔐 **Sistema de Autenticação Administrativa** (NOVO!)
- Login obrigatório para acessar configurações
- Senha criptografada (SHA-256)
- Primeiro acesso obriga troca de senha padrão
- Pergunta de segurança para recuperação
- Logout para proteção

### 🚫 **Sistema de Bloqueio Inteligente** (NOVO!)
- Bloqueio progressivo de coletores com IP incorreto
- Tentativas 1-4: Bloqueio temporário com desbloqueio (10s) para verificação
- Tentativa 5+: Bloqueio definitivo
- Desbloqueio automático quando IP for corrigido
- Estatísticas em tempo real

### 📡 **IP Range Configurável** (NOVO!)
- Detecção automática de modo:
  - **PADRÃO** (100-199): Últimos 2 dígitos
  - **OFFSET** (2-253): Sequencial
- Interface com preview em tempo real
- Suporta qualquer faixa (1-254)
- Aplicação imediata sem reiniciar

### ⚙️ **Configurações - 3 Tabs** (ATUALIZADO!)
- Tab 1: 🌐 UniFi Controller
- Tab 2: 📡 Range de IPs (NOVO!)
- Tab 3: 🚫 Bloqueios (NOVO!)

---

## 🚀 Características

- **🔐 Autenticação Segura**: Login SHA-256, primeiro acesso obrigatório, recuperação de senha
- **🚫 Bloqueio Inteligente**: Bloqueio progressivo automático de IPs incorretos
- **📡 IP Range Configurável**: Qualquer faixa (2-253, 100-199, etc) com detecção automática
- **⚙️ Configuração pela Interface**: 3 tabs organizadas (UniFi, IP Range, Bloqueios)
- **Monitoramento em Tempo Real**: Status de coletores (Online/Offline/Livre/Alerta)
- **Auto-atualização**: Atualização automática a cada 15 segundos
- **Gestão de Colaboradores**: Atribuição de colaboradores por coletor com turnos
- **Detecção de IP Incorreto**: Alerta visual + bloqueio automático
- **Filtros Avançados**: Filtros por status, setor, fabricante, nome e IP
- **Interface Moderna**: PyQt5 com design profissional
- **Persistência Completa**: Todas as configurações salvas em JSON

---

## 📋 Requisitos

- Python 3.7+
- PyQt5 >= 5.15.0
- requests >= 2.28.0
- urllib3 >= 1.26.0

---

## 🔧 Instalação

### 1. Clone ou baixe o projeto


```bash
cd unifi-collector-monitor
```

### 2. Instale as dependências


```bash
pip install -r requirements.txt
```

### 3. Execute a aplicação


```bash
python3 run.py
```

### 4. Primeiro Acesso (NOVO v3.0) 🔐

**OBRIGATÓRIO** na primeira execução:

```
┌────────────────────────────────────┐
│ 🎯 Primeiro Acesso Obrigatório     │
├────────────────────────────────────┤
│ Credenciais padrão:                │
│   Usuário: admin                   │
│   Senha: admin123                  │
│                                    │
│ 1. Digite NOVA senha (min 6 chars)│
│ 2. Escolha pergunta de segurança  │
│ 3. Digite resposta (criptografada)│
│ 4. Clique "✅ Configurar"         │
└────────────────────────────────────┘
```

### 5. Configure o Sistema (v3.0)

1. Login em **"⚙️ Configurações"**
2. **Tab 🌐 UniFi**: Editar credenciais UniFi
3. **Tab 📡 IP Range**: Configurar faixa de IPs
4. **Tab 🚫 Bloqueios**: Ver estatísticas
5. Pronto! ✅

---

## 📁 Estrutura do Projeto v3.0

```
unifi-collector-monitor/
│
├── app/
│   ├── __init__.py
│   ├── config.py                    # ⚙️ Configurações padrão v3.0
│   │
│   ├── workers/                     # ⚡ Threads de processamento
│   │   ├── __init__.py
│   │   ├── collection_worker.py    # Coleta UniFi + IP Range [v3.0]
│   │   └── status_worker.py        # Verificação de status
│   │
│   ├── gui/                         # 🖥️ Interface gráfica
│   │   ├── __init__.py
│   │   ├── main_window.py          # Janela principal
│   │   ├── collaborators_tab.py    # Aba de Colaboradores
│   │   ├── settings_tab.py         # ⚙️ 3 TABS Config [v3.0]
│   │   ├── login_dialog.py         # 🔐 Login [NOVO v3.0]
│   │   ├── first_access_dialog.py  # 🎯 Primeiro Acesso [NOVO v3.0]
│   │   └── password_reset_dialog.py # 🔑 Recuperação [NOVO v3.0]
│   │
│   └── data/                        # 💾 Gerenciamento de dados
│       ├── __init__.py
│       ├── data_manager.py         # Persistência colaboradores
│       ├── auth_manager.py         # 🔐 Autenticação [NOVO v3.0]
│       ├── ip_blocker.py           # 🚫 Bloqueio [NOVO v3.0]
│       └── ip_mapping.py           # 📡 IP/Coletor [NOVO v3.0]
│
├── docs/                            # 📚 Documentação v3.0
│   ├── EXAMPLES.md                 # 23 exemplos práticos
│   ├── CONTRIBUTING.md             # Guia desenvolvedores
│   └── ARCHITECTURE.md             # Arquitetura v3.0
│
├── resources/                       # 🎨 Recursos visuais
│   └── icons/
│       ├── icon.png                # Ícone da aplicação
│       └── README.md
│
├── .gitignore                      # Git ignore (CRÍTICO v3.0!)
├── CHANGELOG.md                    # Histórico completo v3.0
├── QUICKSTART.md                   # Guia rápido 5 minutos
├── INSTALACAO.txt                  # Guia instalação completo
├── PROJECT_SUMMARY.txt             # Estrutura resumida
├── README.md                       # 📖 Este arquivo
├── requirements.txt                # 📦 Dependências Python
├── setup.sh                        # 🔧 Script de instalação
├── run.py                          # 🚀 EXECUTAR AQUI!
│
├── unifi_config.json               # 🌐 Credenciais UniFi [AUTO]
├── settings_auth.json              # 🔐 Credenciais Admin [AUTO v3.0]
├── ip_range_config.json            # 📡 Config IP Range [AUTO v3.0]
├── ip_blocks.json                  # 🚫 Bloqueios [AUTO v3.0]
└── colaboradores_data.json         # 💾 Colaboradores [AUTO]
```

---

## 🎯 Funcionalidades Principais v3.0

### 🔐 Autenticação Administrativa (NOVO v3.0)

**Primeiro Acesso Obrigatório:**
- Credenciais padrão: `admin` / `admin123`
- Sistema **OBRIGA** troca de senha na primeira execução
- Escolha pergunta de segurança (10 opções)
- Resposta criptografada (SHA-256)
- Arquivo: `settings_auth.json` (senha SHA-256)

**Login:**
- Acesso a configurações requer autenticação
- Senha criptografada SHA-256 (não reversível)
- Logout para proteção

**Recuperação de Senha:**
- Esqueceu a senha? Use pergunta de segurança
- Resposta verificada via hash SHA-256
- Defina nova senha se resposta correta

### 🚫 Sistema de Bloqueio Inteligente (NOVO v3.0)

**Bloqueio Progressivo:**


```
Coletor detectado com IP incorreto:

Tentativa 1:
├─ Bloqueia no UniFi Controller
├─ Aguarda 60 segundos
├─ Desbloqueia temporariamente (10 segundos)
├─ Verifica se IP foi corrigido
└─ Ainda incorreto? → Bloqueia novamente

Tentativas 2-4: Repete processo acima

Tentativa 5+:
├─ BLOQUEIO DEFINITIVO
├─ NÃO desbloqueia mais automaticamente
├─ MAS continua verificando em background
└─ Se IP corrigido: Desbloqueia automaticamente ✅
```

**Estatísticas:**
- Total de bloqueios
- Temporários vs Definitivos
- Detalhes de cada bloqueio (tentativas, última atualização)
- Arquivo: `ip_blocks.json`

**Logs:**
- Arquivo: `monitor_bloqueio_coletores.log`
- Registro de todas as ações de bloqueio/desbloqueio

### 📡 IP Range Configurável (NOVO v3.0)

**Detecção Automática de Modo:**

| Range | Modo Detectado | Cálculo |
|-------|----------------|---------|
| 100-199 | PADRÃO (Últimos 2 dígitos) | Coletor 15 → .115 |
| 2-253 | OFFSET (Sequencial) | Coletor 15 → .17 (2+15) |
| 100-253 | PADRÃO | Coletor 15 → .115 |
| 2-199 | OFFSET | Coletor 15 → .17 |

**Regra de Detecção:**

```python
if start_ip % 100 == 0:
    modo = "PADRÃO"  # 100, 200 → Últimos 2 dígitos
else:
    modo = "OFFSET"  # 2, 50 → Sequencial
```

**Interface:**
- Campo Base IP
- Spinners Start/End IP (1-254)
- **Preview em Tempo Real:**
  - Modo detectado automaticamente
  - Exemplos de mapeamento
  - Primeiro e último coletor
- Aplicação imediata ao salvar
- Arquivo: `ip_range_config.json`

### ⚙️ Configurações - 3 Tabs (ATUALIZADO v3.0)

**Login Obrigatório** para acessar:

**Tab 1: 🌐 UniFi Controller**
- Host, Usuário, Senha
- Testar conexão antes de salvar
- Salvar configurações

**Tab 2: 📡 Range de IPs** (NOVO!)
- Base do IP
- Start/End IP
- Preview em tempo real
- Salvar configuração

**Tab 3: 🚫 Bloqueios** (NOVO!)
- Estatísticas de bloqueios
- Lista de dispositivos bloqueados
- Status (Temporário vs Definitivo)
- Atualizar estatísticas

### 🖥️ Monitor de Coletores

- Visualização em tempo real do status
- Indicadores visuais: 🟢 Online | 🔴 Offline | 🔵 Livre | 🟠 Alerta
- Detecção automática de IPs livres (range configurável v3.0)
- Ping paralelo para verificação rápida
- Filtros múltiplos simultâneos

### 👥 Gestão de Colaboradores

- Atribuição de colaboradores por coletor
- Definição de turnos (Manhã/Tarde/Noite/Madrugada)
- Horários personalizados
- Histórico de atribuições

**Detecção de IP Incorreto com Bloqueio (v3.0):**

Quando Coletor 58 usa IP do Coletor 29:

```
┌───────────────────────────────────────────────────────┐
│ Coletor 29 - SEP | 203.0.113.129                    │  ← 🔴 Pisca vermelho
│ [SEM BOTÕES]                                           │     (Vítima - IP roubado)
├───────────────────────────────────────────────────────┤
│ ⚠️ Coletor 58 - SEP (IP INCORRETO) | ❌ 203.0.113.129│  ← 🔴 Pisca + BLOQUEADO
│ [SEM BOTÕES]                                           │     (Usando IP errado)
├───────────────────────────────────────────────────────┤
│ ✅ Coletor 58 - SEP (IP CORRETO) | ✓ 203.0.113.158  │  ← 🟢 Fundo verde
│ [➕][✏️][🗑️][📋]                                         │     (IP correto + ações)
└───────────────────────────────────────────────────────┘
```

**Sistema Automático (v3.0):**
1. Detecta IP incorreto ✅
2. Adiciona a `ip_blocks.json` ✅
3. Bloqueia no UniFi Controller ✅
4. Tentativas 1-4: Desbloqueia temp. (10s) para verificação ✅
5. Tentativa 5+: Bloqueio definitivo ✅
6. Quando corrigir: Desbloqueia automaticamente ✅

---

## ⚙️ Configuração

### Método 1: Via Interface Gráfica (Recomendado) ⭐

#### Passo 1: Primeiro Acesso (v3.0)


```bash
python3 run.py
```

Dialog aparece automaticamente:
1. **Digite nova senha** (mínimo 6 caracteres)
2. **Escolha pergunta de segurança** (10 opções)
3. **Digite resposta** (será criptografada)
4. Clique **"✅ Configurar e Acessar"**

#### Passo 2: Login

1. Aba **"⚙️ Configurações"**
2. Clique **"🔐 Fazer Login"**
3. Usuário: `admin` / Senha: sua nova senha
4. Clique **"✅ Entrar"**

#### Passo 3: Configurar UniFi

1. Tab **"🌐 UniFi Controller"**
2. Host: `https://203.0.113.1:8443`
3. Usuário: `usuario_exemplo`
4. Senha: `senha_exemplo`
5. (Opcional) **"🔌 Testar Conexão"**
6. **"💾 Salvar"**

#### Passo 4: Configurar IP Range (NOVO v3.0)

1. Tab **"📡 Range de IPs"**
2. Base do IP: `203.0.113`
3. Range: `100` até `199` (ou `2` até `253`)
4. Ver preview em tempo real
5. **"💾 Salvar Configuração de IP Range"**

#### Passo 5: Ver Bloqueios (NOVO v3.0)

1. Tab **"🚫 Bloqueios"**
2. Ver estatísticas em tempo real
3. **"🔄 Atualizar Estatísticas"**

### Método 2: Via Arquivo config.py (Opcional)


```python
# Conexão UniFi
UNIFI_HOST = "https://203.0.113.1:8443"
UNIFI_USERNAME = "usuario"
UNIFI_PASSWORD = "senha"

# IP Range (v3.0)
IP_RANGE_BASE = "203.0.113"
IP_RANGE_START = 100  # ou 2
IP_RANGE_END = 199    # ou 253

# Bloqueio (v3.0)
ENABLE_IP_BLOCKING = True
MAX_TENTATIVAS_BLOQUEIO = 4
TEMP_UNBLOCK_TIME = 10
IP_BLOCK_CHECK_INTERVAL = 60

# Atualização
AUTO_UPDATE_INTERVAL = 15000  # 15 segundos
BLINK_INTERVAL = 800          # 0.8 segundos

# Interface
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
```

**Nota:** Interface sobrescreve estes valores!

### Prioridade de Carregamento v3.0

```
🔍 Sistema de Carregamento Inteligente:

1. Credenciais UniFi:
   ├─ unifi_config.json existe? → Usa JSON
   └─ Não existe? → Usa config.py

2. IP Range:
   ├─ ip_range_config.json existe? → Usa JSON [v3.0]
   └─ Não existe? → Usa config.py (100-199)

3. Autenticação:
   ├─ settings_auth.json existe? → Requer login [v3.0]
   └─ Não existe? → Primeiro acesso obrigatório

4. Bloqueios:
   └─ ip_blocks.json (sempre usado) [v3.0]
```

---

## 📖 Como Usar

### 1. Primeira Execução (v3.0)

**Primeiro Acesso Obrigatório:**
- Execute: `python3 run.py`
- Dialog aparece automaticamente
- **Troque senha padrão** (obrigatório!)
- Configure pergunta de segurança
- Clique "✅ Configurar"

**Login:**
- Aba **"⚙️ Configurações"**
- Clique **"🔐 Fazer Login"**
- Use nova senha

**Configurar:**
- Tab **"🌐 UniFi"**: Credenciais UniFi
- Tab **"📡 IP Range"**: Faixa de IPs
- Tab **"🚫 Bloqueios"**: Estatísticas

### 2. Monitoramento

- A aplicação inicia automaticamente a coleta
- Auto-atualização ativa (15 segundos)
- Use filtros para localizar coletores
- Clique **"🔄 Atualizar Status"** para manual

### 3. Gestão de Colaboradores

- Aba **"👥 Gestão de Colaboradores"**
- Clique **"➕"** para adicionar
- Preencha: Nome, Função, Turno, Horários
- Clique **"✏️"** para editar
- Clique **"🗑️"** para remover
- Clique **"📋"** para detalhes e histórico
- ⚠️ **Linhas com IP INCORRETO (vermelhas) não permitem edição**
- 🚫 **Coletores bloqueados aparecem na tab Bloqueios (v3.0)**

### 4. Recuperar Senha (v3.0)

Se esquecer a senha:
1. Aba **"⚙️ Configurações"**
2. Clique **"Esqueceu a senha?"**
3. Responda pergunta de segurança
4. Digite nova senha
5. Clique **"✅ Redefinir"**

### 5. Filtros

- **Status**: Todos, Online, Offline, Livre, Alerta
- **Setor**: Todos, Recebimento, Separação
- **Fabricante**: Filtra por fabricante do dispositivo
- **Nome**: Busca textual no nome do coletor
- **IP**: Busca textual no endereço IP

---

## 🔐 Segurança v3.0

### Arquivos Sensíveis

**⚠️ CRÍTICO: Adicione ao .gitignore!**


```bash
# .gitignore
unifi_config.json           # Credenciais UniFi
settings_auth.json          # Credenciais admin (SHA-256)
ip_blocks.json              # Bloqueios
ip_range_config.json        # IP Range
colaboradores_data.json     # Dados
monitor_bloqueio_coletores.log  # Logs
*.log
```

### Boas Práticas

1. **Trocar senha padrão** no primeiro acesso (obrigatório)
2. **Adicionar arquivos ao .gitignore**
3. **chmod 600 settings_auth.json** (Linux/Mac)
4. **Fazer backup** em local seguro
5. **NÃO compartilhar** arquivos JSON
6. **Trocar senha** periodicamente

### Mitigações de Risco

- ✅ SHA-256 (não reversível)
- ✅ Primeiro acesso obrigatório
- ✅ Pergunta de segurança
- ⚠️ UniFi em texto plano (`unifi_config.json`)
- 🔒 Considerar AES para produção

---

## 🛠️ Manutenção e Desenvolvimento

### Modificar Largura das Tabs

Em `app/gui/main_window.py` (linha ~55):


```python
QTabBar::tab {
    padding: 10px 60px;    # Segundo valor = largura
    min-width: 250px;
}
```

### Adicionar Novo Setor

Para adicionar um novo setor, atualize as configurações e filtros na interface.

### Exemplo 1: Primeiro Acesso Obrigatório


```text
1. Execute: python3 run.py
2. Digite NOVA senha (mínimo 6 caracteres)
3. Escolha uma pergunta de segurança.
4. Escolher pergunta: "Qual o nome da sua mãe?"
5. Resposta: "Maria" (criptografada)
6. ✅ Sistema pronto!
```

### Exemplo 2: Configurar Range 2-253


```
1. Login em ⚙️ Configurações
2. Tab "📡 Range de IPs"
3. Base: 203.0.113
4. Range: 2 até 253
5. Preview mostra: "Modo OFFSET (Sequencial)"
6. Exemplo: Coletor 15 → 203.0.113.17
7. 💾 Salvar
8. ✅ Sistema escaneia 2-253!
```

### Exemplo 3: Bloqueio Automático


```
Coletor 58 com IP .129 (errado, deveria ser .158):

1. Sistema detecta IP incorreto
2. Bloqueia no UniFi
3. Tentativas 1-4: Desbloqueia temp. (10s)
4. Tentativa 5+: Bloqueio definitivo
5. Quando corrigir para .158: Desbloqueia auto ✅
```

Mais exemplos: [docs/EXAMPLES.md](docs/EXAMPLES.md)

---

## 🤝 Contribuindo

Veja [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) para:
- Estrutura do projeto
- Boas práticas v3.0
- Exemplos de modificações
- Fluxos de autenticação, IP Range e bloqueio

---

## 📄 Licença

Este repositório **não é open source**. Ele é disponibilizado publicamente
apenas para fins de portfólio/demonstração técnica.

- ✅ Permitido: visualizar o código pela interface do GitHub.
- ❌ Proibido: copiar, baixar, clonar para reuso, usar, modificar, executar
  ou redistribuir este código, no todo ou em parte, sem autorização prévia
  e por escrito do autor.

Todos os direitos são reservados. Veja os termos completos em
[`LICENSE`](./LICENSE).

---

## 👨‍💻 Desenvolvedor

**Lucas Veríssimo de Oliveira**  
Empresa

---

## 📝 Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para histórico completo.

### v3.0.0 (16/02/2026) - Sistema Inteligente Completo
- ✅ Autenticação administrativa (SHA-256)
- ✅ Bloqueio inteligente progressivo
- ✅ IP Range configurável
- ✅ 3 tabs de configuração
- ✅ Detecção automática de modo
- ✅ Dialogs (Login, FirstAccess, PasswordReset)

### v2.1.0 (06/11/2025)
- ✅ Configuração pela interface
- ✅ Detecção aprimorada de IP incorreto
- ✅ Aplicação imediata de configurações

### v2.0.0 (01/01/2025)
- ✅ Estrutura modular
- ✅ Tabela sem flickering
- ✅ Documentação completa

---

## 🎉 Pronto para Usar!


```bash
# Instalar
pip install -r requirements.txt

# Executar
python3 run.py

# Primeiro acesso: trocar senha
# Login: configurar sistema
# Usar: monitorar coletores!
```

**Versão 3.0.0 - Sistema Inteligente, Seguro e Configurável** 🔐📡🚫
