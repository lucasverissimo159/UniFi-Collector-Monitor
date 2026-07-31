# 📦 Pasta de Recursos (Resources)

Esta pasta contém recursos estáticos da aplicação.

## 📂 Estrutura:

```
resources/
├── icons/              # Ícones da aplicação
│   ├── icon.png       # Ícone principal (OBRIGATÓRIO)
│   └── README.md      # Instruções
│
└── README.md          # Este arquivo
```

## 🎯 Como usar:

### 1. Ícones (`icons/`)

Coloque o ícone principal da aplicação aqui:
- **Arquivo**: `icon.png`
- **Tamanho**: 256x256 ou 512x512 pixels
- **Formato**: PNG com transparência

Veja instruções detalhadas em: `icons/README.md`

### 2. Expansões Futuras:

Você pode adicionar outras pastas conforme necessário:

```
resources/
├── icons/          # Ícones
├── images/         # Imagens da interface
├── styles/         # Arquivos CSS/QSS
├── sounds/         # Sons/notificações
└── fonts/          # Fontes customizadas
```

## 🔧 Configuração:

Os caminhos dos recursos são definidos em `app/config.py`:

```python
# Ícone da aplicação
WINDOW_ICON_PATH = "resources/icons/icon.png"

# Adicione mais recursos aqui conforme necessário
```

## ⚠️ Importante:

- Mantenha os arquivos organizados em subpastas
- Use nomes descritivos para os arquivos
- Documente novos recursos adicionados
- Não commite arquivos muito grandes

## 📝 Notas:

- Esta pasta está no `.gitignore` por padrão para recursos opcionais
- Apenas o ícone principal (`icon.png`) é obrigatório
- Outros recursos são opcionais e para expansões futuras
