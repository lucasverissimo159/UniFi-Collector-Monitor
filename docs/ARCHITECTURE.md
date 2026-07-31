# 🏗️ Arquitetura do Sistema

Visão geral da arquitetura do UniFi Collector Monitor v3.0.0 - Sistema Inteligente Completo

## Diagrama de Componentes v3.0

```
┌─────────────────────────────────────────────────────────┐
│                      run.py (Entry Point)                │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │  UniFiCollectorGUI    │  (Main Window)
         │  gui/main_window.py   │
         └───────┬───────────────┘
                 │
      ┏━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
      ▼                    ▼                          ▼
┌─────────────┐     ┌──────────────────┐    ┌────────────────────┐
│ Monitor Tab │     │ Collaborators Tab│    │   Settings Tab     │
│             │     │                  │    │ 🔐 AUTENTICADO     │
│  • Tabela   │     │  • Atribuições   │    │                    │
│  • Filtros  │     │  • Histórico     │    │ [NOVO v3.0]        │
│  • Status   │     │  • IP Incorreto  │    │ 3 SUB-TABS:        │
└──────┬──────┘     │  • Piscar ️🔴     │    │                    │
       │            └────────┬─────────┘    │ 🌐 UniFi           │
       │                     │              │ 📡 IP Range        │
       │            ┌────────▼──────────┐   │ 🚫 Bloqueios       │
       │            │ IPMapping [NOVO]  │   └────────┬───────────┘
       │            │ ip_mapping.py     │            │
       │            │                   │   ┌────────▼───────────┐
       │            │ • Modo AUTO       │   │ AuthManager [NOVO] │
       │            │ • PADRÃO/OFFSET   │   │ auth_manager.py    │
       │            │ • get_expected_ip │   │                    │
       │            │ • is_ip_correct   │   │ • Login SHA-256    │
       │            └───────────────────┘   │ • Primeiro Acesso  │
       │                                    │ • Pergunta Segur.  │
       │            ┌───────────────────┐   │ • Reset Password   │
       │            │ IPBlocker [NOVO]  │   └────────────────────┘
       │            │ ip_blocker.py     │
       │            │                   │   ┌─────────────────────┐
       │            │ • Bloqueio 1-4    │   │ Dialogs [NOVO v3.0] │
       │            │ • Definitivo 5+   │   │                     │
       │            │ • Auto-Desbloqueia│   │ • LoginDialog       │
       │            │ • UniFiController │   │ • FirstAccessDialog │
       │            └───────────────────┘   │ • PasswordReset     │
       │                                    └─────────────────────┘
       │            ┌────────────────────┐
       │            │  DataManager       │
       │            │  data_manager.py   │
       │            │                    │
       │            │  • load_data()     │
       │            │  • save_data()     │
       │            │  • cleanup_history │
       │            └────────────────────┘
       │
┌──────▼───────────────┐
│      Workers         │
│                      │
│  • UniFiWorker       │
│    (Coleta dados)    │
│    ↳ IP Range Config │
│                      │
│  • StatusUpdateWorker│
│    (Verifica pings)  │
│                      │
│ workers/*.py         │
└──────┬───────────────┘
       │
┌──────▼──────────┐
│  UniFi API      │
│                 │
│  • /api/login   │
│  • /api/stat/*  │
│  • block_client │
│  • unblock_client│
└─────────────────┘
```

## Fluxo de Dados v3.0

### 1. Inicialização com Autenticação [NOVO v3.0]
```
run.py 
  → QApplication 
    → UniFiCollectorGUI.__init__()
      → create_monitor_tab()
      → create_collaborators_tab()
      → create_settings_tab() 
        → AuthManager.is_first_access()?
          ├─ SIM → FirstAccessDialog
          │   ├─ Trocar senha padrão
          │   ├─ Escolher pergunta segurança
          │   └─ Salvar em settings_auth.json
          └─ NÃO → LoginDialog (quando acessar)
      → start_collection() [auto]
        → load_unifi_credentials()
        → IPMapping.from_config_file() [NOVO v3.0]
```

### 2. Sistema de Autenticação [NOVO v3.0]
```
Settings Tab
  → Usuário clica "🔐 Fazer Login"
  → LoginDialog
    → Digita usuário/senha
    → AuthManager.verify_login()
      ├─ SHA-256 hash da senha
      ├─ Compara com settings_auth.json
      └─ Retorna True/False
  → Se autenticado:
    └─ Mostra 3 tabs de configuração
  → Se falhar:
    └─ Mensagem de erro
  
Recuperação de Senha:
  → Usuário clica "Esqueceu a senha?"
  → PasswordResetDialog
    → AuthManager.get_security_question()
    → Usuário responde
    → AuthManager.verify_security_answer()
      ├─ Verifica hash da resposta
      └─ Se correto: permite nova senha
```

### 3. Configuração de IP Range [NOVO v3.0]
```
Settings Tab (autenticado)
  → Tab "📡 Range de IPs"
  → Usuário configura:
    ├─ Base IP: 203.0.113
    ├─ Start: 2 (ou 100)
    └─ End: 253 (ou 199)
  → IPMapping detecta modo:
    ├─ start_ip % 100 == 0? → PADRÃO (últimos 2 dígitos)
    └─ Caso contrário → OFFSET (sequencial)
  → Preview em tempo real
  → Clica "💾 Salvar"
    ├─ IPMapping.save_config() → ip_range_config.json
    └─ self.parent_window.start_collection()
  → Próxima coleta usa novo range ✅
```

### 4. Coleta de Dados com IP Range [ATUALIZADO v3.0]
```
start_collection()
  → load_unifi_credentials()
    ├─ if existe unifi_config.json:
    │   └─ Usa credenciais do JSON
    └─ else:
        └─ Usa credenciais do config.py
  
  → IPMapping.from_config_file() [NOVO v3.0]
    ├─ if existe ip_range_config.json:
    │   ├─ Carrega base_ip, start_ip, end_ip
    │   └─ Detecta modo automaticamente
    └─ else:
        └─ Usa valores de config.py
  
  → UniFiWorker(host, user, pass)
    → login() → UniFi API
    → get_clients() → UniFi API
    → extract_client_data()
    → scan_free_ips() 
      ├─ Usa range configurável [NOVO v3.0]
      └─ Nomeia IPs com IPMapping [NOVO v3.0]
    → ping_ip() [paralelo]
  
  → finished.emit(data, free_ips)
    → on_collection_finished()
      → apply_filters()
      → update_status_counts()
```

### 5. Sistema de Bloqueio Inteligente [NOVO v3.0]
```
Detecção de IP Incorreto:
  → check_collector_ip_mismatch(name, ip)
    ├─ IPMapping.from_config_file()
    ├─ Extrai número do coletor
    ├─ Calcula IP esperado
    └─ Compara: ip_atual == ip_esperado?

Se IP Incorreto:
  → IPBlocker.add_block(mac, name, numero)
    ├─ Salva em ip_blocks.json
    ├─ Tentativas 1-4:
    │   ├─ Bloqueia no UniFi
    │   ├─ Aguarda 60 segundos
    │   ├─ Desbloqueia temporariamente (10s)
    │   ├─ Verifica se corrigiu
    │   └─ Se ainda errado: bloqueia novamente
    └─ Tentativa 5+:
        ├─ BLOQUEIO DEFINITIVO
        ├─ NÃO desbloqueia mais
        └─ MAS continua verificando

Quando IP Corrigido:
  → IPBlocker.remove_block(mac)
    ├─ Remove de ip_blocks.json
    └─ Desbloqueia no UniFi ✅
```

### 6. Atualização Automática com Bloqueio
```
QTimer (15s)
  → auto_update_status()
    → manual_update_status()
      → start_collection()
        ├─ Coleta dados
        ├─ Verifica IPs incorretos
        └─ Atualiza bloqueios
```

### 7. Gestão de Colaboradores
```
add_assignment()
  → AssignCollaboratorDialog
    → Usuário preenche dados
    → accept()
  → save_data()
    → DataManager.save_data()
      → JSON.dump() → colaboradores_data.json
```

## Threads e Concorrência

### Thread Principal (Qt Event Loop)
- Interface gráfica
- Eventos de usuário
- Timers (piscar, auto-atualização, bloqueio)
- Autenticação (SHA-256)

### Thread de Coleta (UniFiWorker)
- Requisições HTTP ao UniFi
- Processamento de dados
- Carregamento dinâmico de credenciais
- **IP Range configurável** [NOVO v3.0]
- **Nomeação inteligente de IPs** [NOVO v3.0]
- Emite sinais para thread principal

### Thread de Status (StatusUpdateWorker)
- Ping paralelo (ThreadPoolExecutor)
- Atualização de status
- Emite sinais para thread principal

### Thread Pool (Ping)
- 30 workers simultâneos
- Pings não-bloqueantes
- Timeout de 2 segundos
- **Range configurável** [NOVO v3.0]

## Gerenciamento de Estado v3.0

### Estado de Autenticação [NOVO v3.0]
```python
# settings_auth.json
{
    "username": "admin",
    "password_hash": "sha256...",
    "security_question": "Qual sua cor favorita?",
    "security_answer_hash": "sha256...",
    "first_access": False,
    "created_at": "16/02/2026 10:00:00",
    "last_password_change": "16/02/2026 10:05:00"
}
```

### Estado de IP Range [NOVO v3.0]
```python
# ip_range_config.json
{
    "base_ip": "203.0.113",
    "start_ip": 2,
    "end_ip": 253,
    "updated_at": "16/02/2026 10:10:00"
}

# IPMapping detecta automaticamente:
mode = 'offset'  # porque start_ip (2) não é múltiplo de 100
```

### Estado de Bloqueios [NOVO v3.0]
```python
# ip_blocks.json
{
    "AA:BB:CC:DD:EE:FF": {
        "mac": "AA:BB:CC:DD:EE:FF",
        "name": "Coletor 58 - SEP",
        "numero": 58,
        "tipo": "SEP",
        "tentativas": 5,
        "bloqueio_definitivo": True,
        "last_update": "16/02/2026 14:30:00"
    }
}
```

### Estado Global (self.data)
```python
self.data = [
    {
        'NAME': 'Coletor 01',
        'SETOR': 'Recebimento',
        'IP ADDRESS': '203.0.113.101',
        'STATUS': 'ONLINE',
        'MAC': 'AA:BB:CC:DD:EE:FF',
        ...
    },
    ...
]
```

### Persistência de Credenciais UniFi
```json
// unifi_config.json
{
  "UNIFI_HOST": "https://203.0.113.1:8443",
  "UNIFI_USERNAME": "usuario_exemplo",
  "UNIFI_PASSWORD": "senha_exemplo"
}
```

### Persistência de Colaboradores
```json
// colaboradores_data.json
{
  "203.0.113.101": {
    "current": [
      {
        "collaborator_name": "João",
        "shift": "Manhã",
        "start_time": "08:00",
        "end_time": "12:00"
      }
    ],
    "history": [...]
  }
}
```

## Comunicação Entre Componentes

### Sinais Qt (PyQt5)
```python
# Worker → GUI
finished = pyqtSignal(list, set)
progress = pyqtSignal(str)
error = pyqtSignal(str)

# Conexões
self.worker.finished.connect(self.on_collection_finished)
self.worker.progress.connect(self.show_status_message)
```

### Callbacks
```python
# Botões → Métodos
assign_btn.clicked.connect(lambda: self.add_assignment(collector))
save_btn.clicked.connect(self.save_settings)
test_btn.clicked.connect(self.test_connection)
login_btn.clicked.connect(self.do_login) # [NOVO v3.0]
logout_btn.clicked.connect(self.logout)   # [NOVO v3.0]
```

## Prioridade de Configurações v3.0

```
1. Credenciais UniFi:
   ├─ unifi_config.json (se existir)
   └─ config.py (fallback)

2. IP Range:
   ├─ ip_range_config.json (se existir) [NOVO v3.0]
   └─ config.py (fallback)

3. Autenticação:
   ├─ settings_auth.json (sempre usado) [NOVO v3.0]
   └─ DEFAULT_ADMIN_USER/PASS (primeiro acesso)

4. Bloqueios:
   └─ ip_blocks.json (sempre usado) [NOVO v3.0]
```

## Otimizações v3.0

### 1. Sem Flickering
```python
self.table.setUpdatesEnabled(False)
# ... modificações ...
self.table.setUpdatesEnabled(True)
```

### 2. Cache de Filtros
```python
if current_filters == self.last_filters:
    return  # Não recalcular
```

### 3. Ping Paralelo com Range Configurável [NOVO v3.0]
```python
# Carrega range configurável
mapper = IPMapping.from_config_file()
start = mapper.start_ip  # 2 ou 100
end = mapper.end_ip      # 253 ou 199

with ThreadPoolExecutor(max_workers=30) as executor:
    futures = {
        executor.submit(ping, f"{mapper.base_ip}.{i}"): i 
        for i in range(start, end + 1)
    }
```

### 4. Preservação de Scroll
```python
scroll_position = scrollbar.value()
# ... atualização ...
scrollbar.setValue(scroll_position)
```

### 5. Criptografia SHA-256 [NOVO v3.0]
```python
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Uso:
password_hash = hash_password("admin123")
# → "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
```

### 6. Detecção Automática de Modo [NOVO v3.0]
```python
def _detect_mode(self):
    if self.start_ip % 100 == 0:
        return 'digits'  # 100, 200 → Padrão
    else:
        return 'offset'  # 2, 50 → Offset
```

## Dependências v3.0

```
PyQt5 ─────┐
           ▼
    UniFiCollectorGUI
           │
           ├─► Settings Tab (3 TABS v3.0)
           │     ├─► AuthManager [NOVO v3.0]
           │     ├─► IPMapping [NOVO v3.0]
           │     └─► IPBlocker [NOVO v3.0]
           │
           ├─► Dialogs [NOVO v3.0]
           │     ├─► LoginDialog
           │     ├─► FirstAccessDialog
           │     └─► PasswordResetDialog
           │
           ├─► Workers (QThread)
           │     ├─► load_credentials
           │     ├─► IPMapping (range configurável)
           │     ├─► requests (UniFi API)
           │     └─► subprocess (ping)
           │
           └─► DataManager
                 └─► json (persistência)
```

## Extensibilidade v3.0

### Adicionar Nova Aba
1. Criar classe herdando QWidget
2. Implementar interface
3. Adicionar em `__init__()`: `self.tabs.addTab()`
4. Exemplo: Settings Tab com 3 sub-tabs v3.0

### Adicionar Novo Módulo de Segurança
1. Criar em `app/data/`
2. Herdar estrutura de AuthManager
3. Implementar métodos necessários
4. Integrar na interface

### Adicionar Novo Sistema de Bloqueio
1. Criar em `app/data/`
2. Seguir padrão de IPBlocker
3. Definir lógica de bloqueio
4. Integrar com UniFi API

## Performance v3.0

### Métricas Típicas
- Coleta completa: ~3-5 segundos
- Ping de range configurável: ~1-3 segundos (paralelo)
- Atualização da tabela: <100ms (sem flickering)
- Login (SHA-256): <50ms
- Salvamento de config: <100ms
- Uso de memória: ~60-120 MB
- Teste de conexão: ~1-2 segundos

### Gargalos
- Rede: Latência para UniFi API
- CPU: Ping paralelo de muitos IPs
- I/O: Leitura/escrita do JSON
- **Criptografia: SHA-256 (mínimo)** [NOVO v3.0]

### Melhorias Implementadas v3.0
- ✅ Autenticação SHA-256 (rápida)
- ✅ IP Range configurável (qualquer faixa)
- ✅ Detecção automática de modo
- ✅ Bloqueio inteligente progressivo
- ✅ Cache de configurações
- ✅ Preview em tempo real

### Melhorias Futuras
- Cache de dados do UniFi (reduzir requests)
- Banco de dados SQLite (ao invés de JSON)
- WebSocket para updates em tempo real
- Criptografia AES para senhas em JSON
- Auditoria de acessos
- Múltiplos usuários administrativos

## Segurança v3.0

### Autenticação [NOVO v3.0]
- **Senha criptografada**: SHA-256 (não reversível)
- **Primeiro acesso obrigatório**: Força troca de senha padrão
- **Pergunta de segurança**: Recuperação de senha
- **Logout**: Proteção quando não utilizado
- **Arquivo**: settings_auth.json (criptografado)

### Arquivos Sensíveis
```bash
# .gitignore (CRÍTICO!)
unifi_config.json           # Credenciais UniFi
settings_auth.json          # Credenciais admin
ip_blocks.json              # Bloqueios
ip_range_config.json        # IP Range
colaboradores_data.json     # Dados
monitor_bloqueio_coletores.log  # Logs
*.log
```

### Boas Práticas v3.0
1. **Trocar senha padrão** no primeiro acesso
2. **Adicionar arquivos ao .gitignore**
3. **chmod 600** em settings_auth.json (Linux/Mac)
4. **Fazer backup** em local seguro
5. **NÃO compartilhar** arquivos JSON
6. **Trocar senha** periodicamente

### Mitigações de Risco
- ✅ SHA-256 (não reversível)
- ✅ Primeiro acesso obrigatório
- ✅ Pergunta de segurança
- ⚠️ Senha em texto plano no unifi_config.json
- 🔒 Considerar AES para produção

---

**Versão Atual**: 3.0.0 - Sistema Inteligente Completo  
**Data**: 16/02/2026  
**Mantenedor**: Atualize este documento ao fazer mudanças arquiteturais significativas.
