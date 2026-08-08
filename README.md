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
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model: Gerenciamento de configurações persistentes em JSON."""

import json
import base64
import logging
from pathlib import Path


class ConfigManager:
    """Gerencia configurações salvas em arquivo JSON com ofuscação de senha."""

    _KEY = b"chave-de-exemplo"

    DEFAULTS = {
        "username": "",
        "password": "",
        "port": "8443",
        "last_ip": "",
        "validate_cpf_online": True,
        "theme": "dark",
        "custom_ips": [],
    }

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.data: dict = dict(self.DEFAULTS)
        self.load()

    def load(self):
        """Carrega configurações do arquivo."""
        if not self.filepath.exists():
            return
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            if raw.get("_pw"):
                try:
                    raw["password"] = self._deobfuscate(raw.pop("_pw"))
                except Exception:
                    raw["password"] = ""
            self.data.update(raw)
        except Exception as e:
            logging.warning(f"[CONFIG] Erro ao carregar: {e}")

    def save(self):
        """Salva configurações no arquivo."""
        to_save = dict(self.data)
        pw = to_save.pop("password", "")
        if pw:
            to_save["_pw"] = self._obfuscate(pw)
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"[CONFIG] Erro ao salvar: {e}")

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value):
        self.data[key] = value

    def update(self, **kwargs):
        self.data.update(kwargs)

    def _obfuscate(self, text: str) -> str:
        key = self._KEY
        result = bytes([ord(c) ^ key[i % len(key)] for i, c in enumerate(text)])
        return base64.b64encode(result).decode()

    def _deobfuscate(self, encoded: str) -> str:
        key = self._KEY
        raw = base64.b64decode(encoded.encode())
        return ''.join(chr(b ^ key[i % len(key)]) for i, b in enumerate(raw))
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
