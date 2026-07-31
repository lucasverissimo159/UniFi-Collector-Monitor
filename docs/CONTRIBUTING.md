# 🤝 Guia de Contribuição

Obrigado por considerar contribuir com o UniFi Collector Monitor v3.0.0!

## Estrutura do Projeto v3.0

```
app/
├── config.py           # Configurações globais - VALORES PADRÃO
├── workers/            # Threads de background (coleta, ping)
│   ├── collection_worker.py  # IP Range configurável [v3.0]
│   └── status_worker.py
├── gui/                # Interface gráfica
│   ├── main_window.py
│   ├── collaborators_tab.py
│   ├── settings_tab.py       # 3 TABS! [v3.0]
│   ├── login_dialog.py       # 🔐 Login [NOVO v3.0]
│   ├── first_access_dialog.py # 🎯 Primeiro acesso [NOVO v3.0]
│   └── password_reset_dialog.py # 🔑 Recuperação [NOVO v3.0]
├── data/               # Persistência e lógica
│   ├── data_manager.py
│   ├── auth_manager.py       # 🔐 Autenticação [NOVO v3.0]
│   ├── ip_blocker.py         # 🚫 Bloqueio [NOVO v3.0]
│   └── ip_mapping.py         # 📡 IP/Coletor [NOVO v3.0]
└── utils/              # Funções auxiliares
```

## Novidades v3.0.0

### 🔐 Sistema de Autenticação (NOVO)
- Login obrigatório para configurações
- Senha criptografada (SHA-256)
- Primeiro acesso força troca de senha
- Pergunta de segurança para recuperação

### 🚫 Sistema de Bloqueio Inteligente (NOVO)
- Bloqueio progressivo (tentativas 1-4 temporárias, 5+ definitivo)
- Desbloqueio automático quando IP corrigido
- Persistência em `ip_blocks.json`

### 📡 IP Range Configurável (NOVO)
- Detecção automática de modo (PADRÃO vs OFFSET)
- Interface com preview em tempo real
- Suporta qualquer faixa (1-254)
- Persistência em `ip_range_config.json`

### ⚙️ Settings Tab - 3 Tabs (ATUALIZADO)
- Tab 1: 🌐 UniFi Controller
- Tab 2: 📡 Range de IPs (NOVO!)
- Tab 3: 🚫 Bloqueios (NOVO!)

## Como Adicionar Recursos

### Adicionar Novo Filtro

1. **Adicione a opção em `app/config.py`**:
```python
STATUS_OPTIONS = ['Todos', 'Online', 'Offline', 'Livre', 'Alerta', 'Bloqueado']
```

2. **Modifique `gui/main_window.py`**:
- Adicione combo no método `create_monitor_tab()`
- Atualize lógica em `apply_filters()`

### Modificar Tempo de Ping

Edite `app/config.py`:
```python
PING_TIMEOUT = 1  # mais rápido
MAX_PING_WORKERS = 50  # mais paralelo
```

### Adicionar Novo Setor

Em `workers/collection_worker.py`, método `extract_client_data()`:
```python
if re.search(r'\bEXP\b', name, re.IGNORECASE):
    setor = 'Expedição'
```

### Modificar IP Range Padrão (v3.0)

Edite `app/config.py`:
```python
IP_RANGE_BASE = "203.0.113"
IP_RANGE_START = 2      # ou 100
IP_RANGE_END = 253      # ou 199

# Sistema detecta automaticamente:
# - start % 100 == 0 → Modo PADRÃO (últimos 2 dígitos)
# - Caso contrário → Modo OFFSET (sequencial)
```

Ou configure pela interface:
```
Aba "⚙️ Configurações" → Login → Tab "📡 Range de IPs"
```

### Adicionar Nova Pergunta de Segurança (v3.0)

Em `gui/first_access_dialog.py`:
```python
self.question_combo.addItems([
    "Qual o nome da sua mãe?",
    "Qual sua cidade natal?",
    # ... perguntas existentes ...
    "Qual seu livro favorito?"  # NOVA
])
```

### Modificar Lógica de Bloqueio (v3.0)

Em `app/config.py`:
```python
MAX_TENTATIVAS_BLOQUEIO = 4  # Tentativas antes de bloqueio definitivo
TEMP_UNBLOCK_TIME = 10       # Tempo de desbloqueio temporário (segundos)
IP_BLOCK_CHECK_INTERVAL = 60 # Intervalo entre verificações (segundos)
```

### Mudar Cores da Interface

Em `gui/main_window.py` ou `gui/collaborators_tab.py`:
```python
# Exemplo: mudar cor de online
if status == 'ONLINE':
    status_item.setForeground(QColor(0, 255, 0))  # verde mais claro
```

### Adicionar Nova Tab em Settings (v3.0)

Em `gui/settings_tab.py`, método `show_settings_screen()`:
```python
# Criar nova tab
nova_tab = self.create_nova_tab()
tabs.addTab(nova_tab, "📊 Estatísticas")

# Implementar método
def create_nova_tab(self):
    tab = QWidget()
    layout = QVBoxLayout()
    # Adicione widgets aqui
    tab.setLayout(layout)
    return tab
```

## Boas Práticas v3.0

### 1. Mantenha a Modularização
- Não adicione tudo no mesmo arquivo
- Use imports relativos: `from app.config import *`
- Separe lógica de apresentação

### 2. Siga o Padrão de Segurança
- **NUNCA** armazene senhas em texto plano
- Use SHA-256 para hashes
- Adicione arquivos sensíveis ao .gitignore

### 3. Teste Antes de Commitar
```bash
# Teste completo
python3 run.py

# Teste autenticação
# 1. Primeiro acesso
# 2. Login
# 3. Logout
# 4. Recuperação de senha

# Teste IP Range
# 1. Configurar range 2-253
# 2. Salvar
# 3. Verificar preview
# 4. Fechar e reabrir
# 5. Confirmar persistência

# Teste bloqueio
# 1. Simular IP incorreto
# 2. Verificar bloqueio
# 3. Corrigir IP
# 4. Verificar desbloqueio
```

### 4. Documente Mudanças
- Atualize README.md
- Adicione entry no CHANGELOG.md
- Crie exemplos em docs/EXAMPLES.md
- Atualize ARCHITECTURE.md se necessário

### 5. Configurações (v3.0)
- Valores padrão em `config.py`
- Usuários sobrescrevem via interface
- Persistência em arquivos JSON
- Prioridade: JSON > config.py

## Estrutura de Commit

```
[TIPO] Breve descrição

Descrição detalhada do que foi feito e por quê.

Refs: #issue_number
```

Tipos:
- `[FEAT]` - Nova funcionalidade
- `[FIX]` - Correção de bug
- `[DOCS]` - Documentação
- `[STYLE]` - Formatação
- `[REFACTOR]` - Refatoração de código
- `[TEST]` - Testes
- `[CHORE]` - Manutenção
- `[SECURITY]` - Melhorias de segurança [NOVO v3.0]

## Exemplos de Modificações Comuns v3.0

### Adicionar Novo Modo de IP Range

Em `data/ip_mapping.py`, método `_detect_mode()`:
```python
def _detect_mode(self):
    if self.start_ip % 100 == 0:
        return 'digits'  # Padrão
    elif self.start_ip == 1:
        return 'sequential'  # NOVO modo
    else:
        return 'offset'
```

### Modificar Critério de Bloqueio

Em `data/ip_blocker.py`, método `add_block()`:
```python
# Mudar número de tentativas antes do definitivo
MAX_TEMP_ATTEMPTS = 6  # Antes: 4

if tentativas >= MAX_TEMP_ATTEMPTS:
    bloqueio_definitivo = True
```

### Adicionar Auditoria de Login (v3.0)

Em `data/auth_manager.py`:
```python
@staticmethod
def verify_login(username, password):
    # ... verificação existente ...
    
    # NOVO: Registrar tentativa de login
    login_log = {
        "username": username,
        "timestamp": datetime.now().isoformat(),
        "success": result
    }
    
    with open("login_audit.json", "a") as f:
        f.write(json.dumps(login_log) + "\n")
    
    return result
```

### Mudar Range de IPs

Via Interface (Recomendado):
```
1. Aba "⚙️ Configurações"
2. Login
3. Tab "📡 Range de IPs"
4. Base: 203.0.113
5. Range: 2 até 253
6. Salvar
```

Via Código (Fallback):
```python
# app/config.py
IP_RANGE_BASE = "203.0.113"
IP_RANGE_START = 2
IP_RANGE_END = 253
```

### Adicionar Validação

Em `gui/collaborators_tab.py`, método `add_assignment()`:
```python
if not collaborator_name.strip():
    QMessageBox.warning(self, "Erro", "Nome obrigatório")
    return

# NOVO v3.0: Validar se coletor está bloqueado
if IPBlocker.is_blocked(collector_mac):
    QMessageBox.warning(
        self, "Atenção", 
        "Coletor bloqueado por IP incorreto. Corrija o IP antes de atribuir."
    )
    return
```

## Arquitetura v3.0.0

### Fluxo de Autenticação

```
Primeiro Acesso:
  → FirstAccessDialog
    → Trocar senha padrão
    → Escolher pergunta de segurança
    → AuthManager.setup_security_question()
      → SHA-256 hash da resposta
      → Salva em settings_auth.json

Login Normal:
  → LoginDialog
    → AuthManager.verify_login()
      → SHA-256 hash da senha digitada
      → Compara com hash salvo
      → Retorna True/False

Recuperação:
  → PasswordResetDialog
    → AuthManager.verify_security_answer()
      → SHA-256 hash da resposta
      → Compara com hash salvo
      → Se correto: permite nova senha
```

### Fluxo de IP Range

```
Configuração:
  → Tab "📡 Range de IPs"
  → Usuário edita campos
  → IPMapping temporário criado
  → Preview em tempo real
    ├─ Modo detectado
    ├─ Exemplos de mapeamento
    └─ Primeiro e último coletor
  → Salvar → ip_range_config.json

Uso:
  → collection_worker.py
    → IPMapping.from_config_file()
      ├─ Carrega JSON (se existir)
      ├─ Detecta modo
      └─ Calcula IPs esperados
  → scan_free_ips()
    ├─ Usa range configurável
    └─ Nomeia com IPMapping
```

### Fluxo de Bloqueio

```
Detecção:
  → check_collector_ip_mismatch(name, ip)
    ├─ IPMapping.from_config_file()
    ├─ Extrai número do coletor
    ├─ Calcula IP esperado
    └─ Compara

Bloqueio:
  → IPBlocker.add_block(mac, name, numero)
    ├─ Tentativas 1-4: Temp
    │   ├─ Bloqueia
    │   ├─ Aguarda 60s
    │   ├─ Desbloqueia 10s
    │   └─ Verifica
    └─ Tentativa 5+: Definitivo

Desbloqueio:
  → When IP corrected:
    └─ IPBlocker.remove_block(mac)
```

## Reportar Bugs

Ao reportar bugs, inclua:
- Python version: `python3 --version`
- PyQt5 version: `pip3 show PyQt5`
- OS: Windows/Linux/Mac
- **Versão do sistema**: 3.0.0
- Passos para reproduzir
- Mensagem de erro completa
- Screenshots se aplicável
- **Arquivos de log** (se disponíveis)

## Pedir Ajuda

- Leia o README.md completo
- Veja EXAMPLES.md para casos de uso (20+)
- Consulte QUICKSTART.md para início rápido
- Revise ARCHITECTURE.md para detalhes técnicos v3.0
- Verifique CHANGELOG.md para novidades v3.0

## Código de Conduta

- Seja respeitoso
- Mantenha profissionalismo
- Ajude outros desenvolvedores
- Documente bem suas mudanças
- **Respeite segurança e privacidade** [v3.0]

## Melhorias Futuras

### Sugestões para Próximas Versões
- ✅ Autenticação SHA-256 (v3.0)
- ✅ Bloqueio inteligente (v3.0)
- ✅ IP Range configurável (v3.0)
- 🔮 Criptografia AES para senhas em JSON
- 🔮 Banco de dados SQLite
- 🔮 WebSocket para updates em tempo real
- 🔮 Auditoria completa de acessos
- 🔮 Múltiplos usuários administrativos
- 🔮 Exportação de relatórios
- 🔮 Gráficos de disponibilidade
- 🔮 Notificações push

## Segurança v3.0

### Ao Trabalhar com Autenticação
```python
# ✅ CORRETO: Usar SHA-256
password_hash = hashlib.sha256(password.encode()).hexdigest()

# ❌ ERRADO: Texto plano
password = "admin123"  # Nunca faça isso!
```

### Ao Trabalhar com Arquivos Sensíveis
```bash
# .gitignore OBRIGATÓRIO
unifi_config.json
settings_auth.json
ip_blocks.json
ip_range_config.json
colaboradores_data.json
*.log
```

### Ao Testar
```bash
# NÃO commitar arquivos de teste com senhas reais
# Use senhas de teste/desenvolvimento

# Exemplo:
TEST_PASSWORD = "test123"  # OK para testes
PROD_PASSWORD = "senha_real"  # NÃO commitar!
```

---

## 🎯 Checklist do Contribuidor v3.0

Antes de submeter PR:
- [ ] Código testado manualmente
- [ ] Autenticação funcionando
- [ ] IP Range configurável funciona
- [ ] Bloqueio inteligente funciona
- [ ] Documentação atualizada
- [ ] CHANGELOG.md atualizado
- [ ] Arquivos sensíveis no .gitignore
- [ ] Sem senhas em texto plano
- [ ] Screenshots (se UI mudou)

---

Obrigado por contribuir! 🚀

**Versão**: 3.0.0 - Sistema Inteligente Completo  
**Última Atualização**: 16/02/2026
