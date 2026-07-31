# 📁 Pasta de Ícones

## 🎨 Ícone da Aplicação

Coloque o ícone da aplicação nesta pasta com o nome **`icon.png`**

### 📋 Requisitos do Ícone:

- **Nome do arquivo**: `icon.png`
- **Formato**: PNG (recomendado)
- **Tamanho recomendado**: 256x256 pixels ou 512x512 pixels
- **Transparência**: Suportada (opcional)

### 📍 Caminho Completo:

```
unifi-collector-monitor/
└── resources/
    └── icons/
        └── icon.png  ← COLOQUE SEU ÍCONE AQUI
```

### ✅ O que acontece quando você adiciona o ícone:

1. O ícone aparece na barra de título da janela principal
2. O ícone aparece em todos os diálogos (atribuir colaborador, detalhes, etc.)
3. O ícone aparece na barra de tarefas do sistema operacional
4. No Windows: aparece no menu Iniciar e na lista de aplicativos

### 🔧 Como funciona:

O código em `app/config.py` define o caminho:
```python
WINDOW_ICON_PATH = "resources/icons/icon.png"
```

Os arquivos `app/gui/main_window.py` e `app/gui/collaborators_tab.py` carregam o ícone automaticamente:
```python
if os.path.exists(WINDOW_ICON_PATH):
    self.setWindowIcon(QIcon(WINDOW_ICON_PATH))
```

### 📝 Nota:

Se você não colocar nenhum ícone, a aplicação funcionará normalmente, mas usará o ícone padrão do sistema operacional.

### 🎨 Dica de Design:

Para melhor resultado, use um ícone:
- Simples e reconhecível
- Com boa visibilidade em tamanhos pequenos (16x16, 32x32)
- Que represente bem a aplicação (ex: um gráfico de rede, ícone WiFi, etc.)

### 🔄 Formatos Alternativos:

Embora o código espere `icon.png`, você pode modificar em `app/config.py` para aceitar outros formatos:
- `icon.ico` (Windows)
- `icon.svg` (vetorial)
- `icon.jpg` (não recomendado - sem transparência)

---

**Estrutura atual:**
```
resources/
└── icons/
    ├── README.md         (este arquivo)
    └── icon.png          (← coloque seu ícone aqui)
```
