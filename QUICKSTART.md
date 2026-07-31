# 🚀 Quick Start Guide

Guia rápido para começar a usar o UniFi Collector Monitor v3.0 em 5 minutos.

## Passo 1: Instalação

```bash
pip install -r requirements.txt
```

## Passo 1.5: Credenciais (opcional)

Os valores em `app/config.py` são apenas **exemplos** (faixas RFC 5737 e
placeholders). Para usar com a sua rede, há duas opções:

- Preencher host/usuário/senha do UniFi pela própria interface
  (aba **Configurações → Login Administrativo**), ou
- Copiar o template de configuração local (não versionado):
  ```bash
  cp config_local.example.py app/config_local.py
  # edite app/config_local.py com UNIFI_HOST, UNIFI_USERNAME, UNIFI_PASSWORD, IP_BASE...
  ```
  O arquivo `app/config_local.py` está no `.gitignore` e sobrescreve os
  valores de exemplo. Da mesma forma, `colaboradores_data.example.json` pode
  ser copiado para `colaboradores_data.json` como massa de dados inicial.

## Passo 2: Execução

```bash
python3 run.py
```

## Passo 3: Primeiro Acesso (NOVO v3.0) 🔐

Na primeira execução, você **DEVE** configurar a senha administrativa:

1. **Dialog de Primeiro Acesso** aparece automaticamente
2. Credenciais padrão exibidas:
   ```
   Usuário: admin
   Senha: admin123
   ```
3. **Digite nova senha** (mínimo 6 caracteres)
4. **Escolha pergunta de segurança** (10 opções)
5. **Digite resposta** (será criptografada)
6. Clique **"✅ Configurar e Acessar"**

## Passo 4: Login em Configurações

Para acessar configurações:

1. Vá para aba **"⚙️ Configurações"**
2. Clique **"🔐 Fazer Login"**
3. Digite:
   - Usuário: `admin`
   - Senha: sua nova senha
4. Clique **"✅ Entrar"**

## Passo 5: Configurar UniFi Controller

Na aba **"🌐 UniFi Controller"**:

1. **Host**: `https://203.0.113.1:8443`
2. **Usuário**: `usuario_exemplo`
3. **Senha**: `senha_exemplo`
4. **(Opcional)** **"🔌 Testar Conexão"**
5. **"💾 Salvar"**

## Passo 6: Configurar IP Range (NOVO v3.0) 📡

Na aba **"📡 Range de IPs"**:

### Exemplo 1: Range Padrão (100-199)
```
Base do IP: 203.0.113
Range: 100 até 199

Preview mostra:
📊 Modo PADRÃO (Últimos 2 Dígitos)
   Coletor 00 → 203.0.113.100
   Coletor 15 → 203.0.113.115
```

### Exemplo 2: Range Completo (2-253)
```
Base do IP: 203.0.113
Range: 2 até 253

Preview mostra:
📈 Modo OFFSET (Sequencial)
   Coletor 00 → 203.0.113.2
   Coletor 15 → 203.0.113.17 (2+15)
```

**Salvar:** Clique **"💾 Salvar Configuração de IP Range"**

## Passo 7: Uso Básico

### Monitor de Coletores
- 🟢 Online | 🔴 Offline | 🔵 Livre | 🟠 Alerta
- Use filtros para localizar coletores
- Auto-atualização a cada 15s

### Gestão de Colaboradores
1. Aba **"👥 Gestão"**
2. Clique **"➕"** no coletor
3. Preencha: Nome, Turno, Horários
4. **"Salvar"**

### Estatísticas de Bloqueio (NOVO v3.0)
1. Aba **"🚫 Bloqueios"**
2. Ver bloqueios ativos
3. Temporários vs Definitivos
4. **"🔄 Atualizar"**

## Entendendo Alertas (v3.0)

### IP Incorreto:
```
Coletor 29         | 203.0.113.129  ← 🔴 Vítima (sem botões)
⚠️ Coletor 58 (IP INCORRETO) | ❌ .129  ← 🔴 Erro (sem botões)
✅ Coletor 58 (IP CORRETO)   | ✓ .158  ← 🟢 Correto (com botões)
```

### Sistema de Bloqueio Automático:
```
Tentativas 1-4: ⏸️ Desbloqueia 10s → Verifica → Bloqueia
Tentativa 5+:   🔴 Bloqueio definitivo
Quando corrigir: ✅ Desbloqueia automaticamente
```

## Recuperar Senha 🔑

Se esquecer a senha:

1. Aba **"⚙️ Configurações"**
2. Clique **"Esqueceu a senha?"**
3. Responda pergunta de segurança
4. Digite nova senha
5. **"✅ Redefinir"**

## Logout 🚪

Para sair das configurações:

1. Dentro de **"⚙️ Configurações"**
2. Clique **"🚪 Sair"** (canto superior direito)

## Arquivos Criados Automaticamente

```
unifi_config.json          # Credenciais UniFi
settings_auth.json         # Credenciais admin (criptografadas)
ip_range_config.json       # Configuração de IP Range
ip_blocks.json             # Estado dos bloqueios
colaboradores_data.json    # Dados dos colaboradores
```

⚠️ **Adicione ao .gitignore!**

---

**Pronto!** Sistema configurado e seguro! 🎉

Consulte [README.md](README.md) para documentação completa.

**Versão**: 3.0.0 - Sistema Inteligente Completo  
**Data**: 16/02/2026
