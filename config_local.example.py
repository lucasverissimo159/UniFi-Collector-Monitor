"""
Exemplo de configuração LOCAL (NÃO versionada).

Copie este arquivo para  app/config_local.py  e preencha com os valores
REAIS da sua rede. O arquivo app/config_local.py está no .gitignore e
sobrescreve os valores de exemplo definidos em app/config.py.

    cp config_local.example.py app/config_local.py
"""

# --- UniFi Controller ---
UNIFI_HOST = "https://SEU_CONTROLADOR:8443"
UNIFI_USERNAME = "seu_usuario"
UNIFI_PASSWORD = "sua_senha"
UNIFI_SITE = "default"

# --- Rede dos coletores (base real dos IPs) ---
IP_BASE = "192.0.2"
IP_RANGE_BASE = "192.0.2"
IP_SCAN_START = 100
IP_SCAN_END = 199
