# 📚 Exemplos de Uso

Casos de uso práticos do UniFi Collector Monitor v3.0.0 - Sistema Inteligente Completo

## 🔐 NOVIDADES v3.0: Autenticação e Segurança

### Exemplo 1: Primeiro Acesso Obrigatório (NOVO v3.0)

```
Cenário: Primeira vez executando o sistema

Passos:
1. Execute: python3 run.py
2. Dialog "🎯 Primeiro Acesso" aparece automaticamente
3. Credenciais padrão exibidas:
   Usuário: admin
   Senha: admin123
4. Digite NOVA senha (mínimo 6 caracteres)
   → Exemplo: "MinhaSenha2026!"
5. Escolha pergunta de segurança (10 opções):
   → Exemplo: "Qual o nome da sua mãe?"
6. Digite resposta (será criptografada SHA-256)
   → Exemplo: "Maria"
7. Clique "✅ Configurar e Acessar"

Resultado:
✅ Arquivo settings_auth.json criado
✅ Senha criptografada (SHA-256)
✅ Pergunta de segurança salva
✅ first_access = false
✅ Sistema pronto para usar!
```

### Exemplo 2: Login em Configurações (NOVO v3.0)

```
Cenário: Acessar configurações após primeiro acesso

Passos:
1. Aba "⚙️ Configurações"
2. Tela mostra: "🔒 Área Restrita"
3. Clique "🔐 Fazer Login"
4. Digite:
   Usuário: admin
   Senha: sua nova senha
5. Clique "✅ Entrar"

Resultado:
✅ Autenticado com sucesso
✅ Mostra 3 tabs de configuração:
   - 🌐 UniFi Controller
   - 📡 Range de IPs
   - 🚫 Bloqueios
```

### Exemplo 3: Recuperar Senha Esquecida (NOVO v3.0)

```
Cenário: Esqueceu a senha administrativa

Passos:
1. Aba "⚙️ Configurações"
2. Clique "Esqueceu a senha?"
3. Dialog mostra sua pergunta de segurança
4. Digite a resposta correta
5. Digite NOVA senha
6. Clique "✅ Redefinir"

Resultado:
✅ Senha redefinida com sucesso
✅ Nova senha criptografada (SHA-256)
✅ Pode fazer login normalmente
```

### Exemplo 4: Logout de Configurações (NOVO v3.0)

```
Cenário: Sair das configurações para proteger acesso

Passos:
1. Dentro de "⚙️ Configurações" (autenticado)
2. Clique "🚪 Sair" (canto superior direito)

Resultado:
✅ Volta à tela de login
✅ Configurações protegidas
✅ Próximo acesso requer login novamente
```

## 📡 IP RANGE CONFIGURÁVEL (NOVO v3.0)

### Exemplo 5: Configurar Range Padrão 100-199 (v3.0)

```
Cenário: Usar range tradicional (últimos 2 dígitos)

Passos:
1. Login em "⚙️ Configurações"
2. Tab "📡 Range de IPs"
3. Configurar:
   Base do IP: 203.0.113
   Range: 100 até 199
4. Preview mostra em tempo real:
   ┌────────────────────────────────────┐
   │ 📊 Modo PADRÃO (Últimos 2 Dígitos) │
   │                                    │
   │ Range: 203.0.113.100-199         │
   │ Regra: Coletor XX → .100XX         │
   │                                    │
   │ Exemplos:                          │
   │   Coletor 00 → 203.0.113.100     │
   │   Coletor 15 → 203.0.113.115     │
   │   Coletor 58 → 203.0.113.158     │
   │   Coletor 99 → 203.0.113.199     │
   └────────────────────────────────────┘
5. Clicar "💾 Salvar Configuração de IP Range"

Resultado:
✅ Arquivo ip_range_config.json criado
✅ Sistema reinicia coleta automaticamente
✅ Escaneia IPs de 100-199
✅ Detecta modo PADRÃO
```

### Exemplo 6: Configurar Range Completo 2-253 (v3.0)

```
Cenário: Usar range máximo (sequencial)

Passos:
1. Login em "⚙️ Configurações"
2. Tab "📡 Range de IPs"
3. Configurar:
   Base do IP: 203.0.113
   Range: 2 até 253
4. Preview mostra em tempo real:
   ┌────────────────────────────────────┐
   │ 📈 Modo OFFSET (Sequencial)        │
   │                                    │
   │ Range: 203.0.113.2-253           │
   │ Regra: Coletor XX → .(2+XX)        │
   │                                    │
   │ Exemplos:                          │
   │   Coletor 00 → 203.0.113.2       │
   │   Coletor 15 → 203.0.113.17      │
   │   Coletor 58 → 203.0.113.60      │
   │   Coletor 99 → 203.0.113.101     │
   └────────────────────────────────────┘
5. Clicar "💾 Salvar"

Resultado:
✅ Modo OFFSET detectado automaticamente
✅ Sistema escaneia IPs de 2-253
✅ Cálculo correto: IP = base + (start + numero)
```

### Exemplo 7: Verificar Persistência de IP Range (v3.0)

```
Cenário: Confirmar que range salvo persiste

Passos:
1. Configure range 2-253
2. Salve a configuração
3. FECHE a aplicação completamente (X)
4. Reabra: python3 run.py
5. Login em "⚙️ Configurações"
6. Tab "📡 Range de IPs"

Verificar:
✅ Base IP: 203.0.113 (preservado)
✅ Range: 2 até 253 (preservado)
✅ Preview mostra "Modo OFFSET"
✅ Arquivo ip_range_config.json existe

Ir em "🖥️ Monitor":
✅ IPs livres são de 2-253 (não 100-199)
✅ Nomes corretos (Coletor 15 tem IP .17)
```

## 🚫 SISTEMA DE BLOQUEIO INTELIGENTE (NOVO v3.0)

### Exemplo 8: Bloqueio Progressivo (v3.0)

```
Cenário: Coletor 58 com IP incorreto (.129 ao invés de .158)

Fluxo Automático:

Tentativa 1:
├─ Sistema detecta IP incorreto
├─ Bloqueia no UniFi Controller
├─ Aguarda 60 segundos
├─ Desbloqueia temporariamente (10 segundos)
├─ Verifica se IP foi corrigido
└─ Ainda incorreto? Bloqueia novamente

Tentativas 2-4:
└─ Repete processo acima

Tentativa 5+:
├─ BLOQUEIO DEFINITIVO
├─ NÃO desbloqueia mais automaticamente
├─ MAS continua verificando em background
└─ Se IP corrigido: Desbloqueia automaticamente ✅

Arquivo: ip_blocks.json
{
  "AA:BB:CC:DD:EE:FF": {
    "mac": "AA:BB:CC:DD:EE:FF",
    "name": "Coletor 58 - SEP",
    "numero": 58,
    "tentativas": 5,
    "bloqueio_definitivo": true,
    "last_update": "16/02/2026 14:30:00"
  }
}
```

### Exemplo 9: Ver Estatísticas de Bloqueio (v3.0)

```
Cenário: Verificar quais coletores estão bloqueados

Passos:
1. Login em "⚙️ Configurações"
2. Tab "🚫 Bloqueios"
3. Ver estatísticas:

┌─────────────────────────────────────┐
│ 📊 ESTATÍSTICAS DE BLOQUEIO         │
│                                     │
│ Total de Bloqueios: 2               │
│   └─ Temporários (1-4): 0           │
│   └─ Definitivos (5+): 2            │
│                                     │
│ 🔍 DETALHES:                        │
│                                     │
│ 🔴 DEFINITIVO - Coletor 13 - SEP    │
│    Tentativas: 15                   │
│    Última atualização: 16/02 14:30  │
│                                     │
│ 🔴 DEFINITIVO - Coletor 68 - SEP    │
│    Tentativas: 15                   │
│    Última atualização: 16/02 14:30  │
└─────────────────────────────────────┘

4. Clicar "🔄 Atualizar Estatísticas"
```

### Exemplo 10: Desbloqueio Automático (v3.0)

```
Cenário: Corrigir IP e verificar desbloqueio

Situação Inicial:
- Coletor 58 bloqueado (15 tentativas)
- IP incorreto: 203.0.113.129
- IP correto: 203.0.113.158

Ação:
1. Corrigir configuração de rede do Coletor 58
2. Configurar IP: 203.0.113.158
3. Aguardar verificação automática (60 segundos)

Resultado:
✅ Sistema detecta IP correto
✅ Remove de ip_blocks.json
✅ Desbloqueia no UniFi Controller
✅ Coletor volta a funcionar normalmente
✅ Tab "🚫 Bloqueios" não mostra mais o coletor
```

## 📊 USO BÁSICO

### Exemplo 11: Filtrar Coletores Offline

1. No filtro "Status", selecione "Offline"
2. A tabela mostra apenas coletores offline
3. Contadores na barra de status mostram total geral

### Exemplo 12: Encontrar Coletor Específico

1. Digite "05" no filtro "Nome"
2. Sistema mostra "Coletor 05", "Coletor 105", etc.

Ou use filtro de IP:
1. Digite "203.0.113.105" no filtro "IP"
2. Mostra apenas o coletor com esse IP

### Exemplo 13: Atribuir Colaborador

```
Cenário: João trabalha no Coletor 15 (Recebimento) no turno da manhã

Passos:
1. Aba "👥 Gestão de Colaboradores"
2. Localizar "Coletor REC 15"
3. Clicar "➕"
4. Preencher:
   - Nome: JOÃO SILVA
   - Função: OPERADOR DE SEPARAÇÃO
   - Turno: Manhã
   - Início: 08:00
   - Fim: 12:00
   - Observações: Experiência com separação express
5. Clicar "Salvar"

Resultado: Coletor 15 agora mostra JOÃO SILVA atribuído
```

### Exemplo 14: Múltiplos Colaboradores

```
Cenário: Coletor 20 tem 2 colaboradores em turnos diferentes

Passos:
1. Adicionar MARIA (Manhã: 08:00-12:00)
2. Clicar "➕" novamente no mesmo coletor
3. Adicionar PEDRO (Tarde: 13:00-17:00)

Resultado: Tabela mostra ambos com turnos distintos
```

### Exemplo 15: Monitorar Setor Específico

```
Objetivo: Ver apenas coletores do Recebimento

Passos:
1. Filtro "Setor" → Selecionar "Recebimento"
2. Tabela mostra só coletores REC
3. Barra de status mostra totais gerais (não apenas filtrados)
```

## 🔧 DETECÇÃO DE IP INCORRETO (v3.0)

### Exemplo 16: Detectar IP Incorreto com Bloqueio (v3.0)

```
Cenário: Coletor 58 está usando IP do Coletor 29

Visualização na aba "👥 Gestão de Colaboradores":

┌───────────────────────────────────────────────────────┐
│ Coletor 29 - SEP | 203.0.113.129                    │  ← 🔴 Pisca vermelho
│ [SEM BOTÕES]                                           │     (Vítima - IP roubado)
├───────────────────────────────────────────────────────┤
│ ⚠️ Coletor 58 - SEP (IP INCORRETO) | ❌ 203.0.113.129│  ← 🔴 Pisca vermelho  
│ [SEM BOTÕES]                                           │     (Usando IP errado)
├───────────────────────────────────────────────────────┤
│ ✅ Coletor 58 - SEP (IP CORRETO) | ✓ 203.0.113.158  │  ← 🟢 Fundo verde
│ [➕][✏️][🗑️][📋]                                         │     (IP correto + ações)
└───────────────────────────────────────────────────────┘

Sistema Automático (v3.0):
1. Detecta IP incorreto ✅
2. Adiciona a ip_blocks.json ✅
3. Bloqueia no UniFi Controller ✅
4. Tentativas 1-4: Desbloqueia temp. (10s) ✅
5. Tentativa 5+: Bloqueio definitivo ✅
6. Quando corrigir: Desbloqueia auto ✅

Ação Necessária:
1. Identificar que Coletor 58 está usando .129 (errado)
2. Corrigir configuração de rede do Coletor 58
3. Configurar IP correto: 203.0.113.158
4. Aguardar verificação automática
5. Alertas desaparecem quando corrigido
6. Bloqueio removido automaticamente
```

**Indicadores visuais v3.0:**
- ⚠️  = IP Incorreto
- ❌  = Marca de erro
- ✅  = IP Correto
- ✓   = Marca de sucesso
- 🔴  = Piscar vermelho (alerta + bloqueio)
- 🟢  = Fundo verde (OK)

## ⚙️ CONFIGURAÇÕES

### Exemplo 17: Mudar Configurações UniFi (v3.0)

```
Objetivo: Conectar a outro UniFi Controller

Passos:
1. Login em "⚙️ Configurações"
2. Tab "🌐 UniFi Controller"
3. Editar:
   - Host: https://192.0.2.1:8443
   - Usuário: admin
   - Senha: novasenha
4. (Opcional) Clicar "🔌 Testar Conexão"
   └─ Aguardar validação
5. Se OK → Clicar "💾 Salvar"
6. Ir em "🖥️ Monitor de Coletores"
7. Sistema coleta dados automaticamente

Resultado: Conecta ao novo controller imediatamente!
```

**Arquivo criado**: `unifi_config.json` com as novas credenciais

### Exemplo 18: Testar Conexão antes de Salvar (v3.0)

```
Cenário: Validar credenciais antes de aplicar

Passos:
1. Tab "🌐 UniFi Controller"
2. Editar campos:
   - Host: https://203.0.113.1:8443
   - Usuário: usuario_exemplo
   - Senha: senha_exemplo
3. Clicar "🔌 Testar Conexão"

Resultados Possíveis:

✅ Sucesso:
   └─ Mensagem: "✅ Conexão estabelecida com sucesso!"
   └─ Status verde
   └─ Pode clicar "💾 Salvar"

❌ Falha:
   └─ Mensagem: "❌ Falha na autenticação (código 401)"
   └─ Status vermelho
   └─ Corrigir credenciais antes de salvar
```

## 🔄 AUTO-ATUALIZAÇÃO

### Exemplo 19: Auto-Atualização Contínua

```
Monitoramento contínuo:

1. Marcar checkbox "Auto-atualização"
2. Sistema atualiza a cada 15 segundos
3. Filtros permanecem ativos
4. Posição de scroll mantida
5. Sem flickering na tabela
6. Bloqueios verificados automaticamente (v3.0)
7. IPs incorretos detectados automaticamente (v3.0)
```

## 📋 HISTÓRICO E DETALHES

### Exemplo 20: Visualizar Histórico

```
Ver quem já trabalhou em um coletor:

1. Clicar "📋 Ver Detalhes" no coletor
2. Janela mostra:
   - Colaboradores atuais
   - Histórico completo de atribuições
   - Datas e horários de cada período
   - Observações registradas
```

## 💾 BACKUP E DADOS

### Exemplo 21: Backup de Dados v3.0

```bash
# Backup manual dos arquivos importantes

# 1. Credenciais UniFi
cp unifi_config.json ~/backups/unifi_$(date +%Y%m%d).json

# 2. Credenciais Admin (v3.0)
cp settings_auth.json ~/backups/auth_$(date +%Y%m%d).json

# 3. IP Range (v3.0)
cp ip_range_config.json ~/backups/iprange_$(date +%Y%m%d).json

# 4. Bloqueios (v3.0)
cp ip_blocks.json ~/backups/blocks_$(date +%Y%m%d).json

# 5. Dados dos colaboradores
cp colaboradores_data.json ~/backups/colaboradores_$(date +%Y%m%d).json

# Script de backup automático (crontab)
0 2 * * * cd /caminho/projeto && \
  cp unifi_config.json ~/backups/unifi_$(date +%Y%m%d).json && \
  cp settings_auth.json ~/backups/auth_$(date +%Y%m%d).json && \
  cp ip_range_config.json ~/backups/iprange_$(date +%Y%m%d).json && \
  cp colaboradores_data.json ~/backups/colaboradores_$(date +%Y%m%d).json
```

### Exemplo 22: Dados em JSON v3.0

```json
// colaboradores_data.json
{
  "203.0.113.15": {
    "current": [
      {
        "collaborator_name": "JOÃO SILVA",
        "function": "OPERADOR",
        "shift": "Manhã",
        "start_time": "08:00",
        "end_time": "12:00",
        "notes": "Experiência com separação"
      }
    ],
    "history": [...]
  }
}

// settings_auth.json (v3.0)
{
  "username": "admin",
  "password_hash": "sha256_hash_aqui",
  "security_question": "Qual o nome da sua mãe?",
  "security_answer_hash": "sha256_hash_aqui",
  "first_access": false
}

// ip_range_config.json (v3.0)
{
  "base_ip": "203.0.113",
  "start_ip": 2,
  "end_ip": 253,
  "updated_at": "16/02/2026 10:00:00"
}

// ip_blocks.json (v3.0)
{
  "AA:BB:CC:DD:EE:FF": {
    "mac": "AA:BB:CC:DD:EE:FF",
    "name": "Coletor 58 - SEP",
    "numero": 58,
    "tentativas": 5,
    "bloqueio_definitivo": true,
    "last_update": "16/02/2026 14:30:00"
  }
}
```

## 🔐 SEGURANÇA

### Exemplo 23: Prioridade de Configurações (v3.0)

```
Sistema de Carregamento Inteligente:

Cenário 1: Primeira execução
├─ Não existe unifi_config.json
├─ Não existe ip_range_config.json
├─ Não existe settings_auth.json
└─ Usa valores de app/config.py

Cenário 2: Após configurar pela interface
├─ Existe unifi_config.json → Usa credenciais UniFi do JSON
├─ Existe ip_range_config.json → Usa range do JSON
├─ Existe settings_auth.json → Requer login
└─ Prioridade: JSON > config.py

Cenário 3: Resetar configurações
├─ Deletar unifi_config.json
├─ Deletar ip_range_config.json
├─ Manter settings_auth.json (segurança)
└─ Volta a usar valores de config.py (exceto auth)
```

**Comando para resetar:**
```bash
rm unifi_config.json ip_range_config.json
# Próxima execução usa config.py
# MAS mantém autenticação (settings_auth.json)
```

---

**Mais dúvidas?** Veja o [README.md](README.md) principal.

**Versão**: 3.0.0 - Sistema Inteligente Completo  
**Última Atualização**: 16/02/2026
