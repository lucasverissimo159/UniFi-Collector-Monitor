import sys
import requests
import urllib3
import json
import os
import re
from datetime import datetime
import platform
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QTime
from PyQt5.QtGui import QColor, QFont, QPalette

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.config import *

# Importar sistema de IP Mapping
try:
    from app.data.ip_mapping import IPMapping
except ImportError:
    # Fallback se ip_mapping não existir ainda
    IPMapping = None

def load_unifi_credentials():
    """Carrega credenciais do arquivo JSON primeiro, senão usa config.py"""
    CONFIG_FILE = "unifi_config.json"
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return (
                    config.get("UNIFI_HOST", UNIFI_HOST),
                    config.get("UNIFI_USERNAME", UNIFI_USERNAME),
                    config.get("UNIFI_PASSWORD", UNIFI_PASSWORD)
                )
        except:
            pass
    return UNIFI_HOST, UNIFI_USERNAME, UNIFI_PASSWORD

class UniFiWorker(QThread):
    """Thread para executar coleta de dados sem travar a interface - VERSÃO OTIMIZADA"""
    finished = pyqtSignal(list, set)
    progress = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, host, username, password):
        super().__init__()
        self.host = host
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = False
        
        # Cache de IPs livres (evita rescanear tudo)
        self.free_ips_cache = set()
        self.cache_timestamp = None

    def run(self):
        try:
            self.progress.emit("Conectando ao UniFi...")
            if not self.login():
                self.error.emit("Falha no login do UniFi")
                return

            self.progress.emit("Coletando dispositivos...")
            clients = self.get_clients()

            self.progress.emit("Processando coletores...")
            data = self.extract_client_data(clients)

            known_ips = set()
            for row in data:
                ip = row.get('IP ADDRESS')
                if ip and ip != 'N/A':
                    known_ips.add(ip)

            # Obter intervalo configurado
            if IPMapping:
                mapper_temp = IPMapping.from_config_file()
                start_range = mapper_temp.start_ip
                end_range = mapper_temp.end_ip
                range_size = end_range - start_range + 1
            else:
                start_range, end_range = 100, 199
                range_size = 100
            
            self.progress.emit(f"Escaneando IPs livres ({start_range}-{end_range})... {range_size} IPs")
            
            # OTIMIZAÇÃO: Scan otimizado com mais workers e timeout menor
            free_ips = self.scan_free_ips_optimized()
            actual_free_ips = [ip for ip in free_ips if ip not in known_ips]

            # OTIMIZAÇÃO: Processar IPs livres em batch
            if IPMapping:
                mapper = IPMapping.from_config_file()
            
            # Adicionar IPs livres (processamento otimizado)
            batch_size = 50  # Processar em lotes
            for i in range(0, len(actual_free_ips), batch_size):
                batch = actual_free_ips[i:i+batch_size]
                for ip in batch:
                    parts = ip.split('.')
                    if len(parts) != 4: 
                        continue
                    
                    # Usar IPMapping para calcular número correto do coletor
                    if IPMapping:
                        collector_num = mapper.get_collector_number(ip)
                        if collector_num is not None:
                            last_two = f"{collector_num:02d}"
                        else:
                            last_octet = parts[-1]
                            last_two = last_octet.zfill(2)[-2:]
                    else:
                        last_octet = parts[-1]
                        last_two = last_octet.zfill(2)[-2:]
                    
                    data.append({
                        'NAME': f"Coletor {last_two}",
                        'SETOR': 'N/A',
                        'MANUFACTURER': 'N/A',
                        'MAC': 'N/A',
                        'IP ADDRESS': ip,
                        'FIRST SEEN': 'N/A',
                        'LAST SEEN': 'N/A',
                        'STATUS': 'LIVRE'
                    })
                
                # Emitir progresso
                progress_pct = min(100, int((i / len(actual_free_ips)) * 100))
                self.progress.emit(f"Processando IPs livres... {progress_pct}%")

            # OTIMIZAÇÃO: Verificar status apenas para coletores conhecidos (não livres)
            self.progress.emit("Verificando status online/offline...")
            items_to_check = [item for item in data if item.get('STATUS') != 'LIVRE']
            
            # Verificar em paralelo com mais workers
            with ThreadPoolExecutor(max_workers=100) as executor:
                futures = {}
                for item in items_to_check:
                    ip = item.get('IP ADDRESS')
                    if ip and ip != 'N/A':
                        future = executor.submit(self.ping_ip, ip)
                        futures[future] = item
                
                for future in as_completed(futures):
                    item = futures[future]
                    try:
                        is_online = future.result()
                        item['STATUS'] = 'ONLINE' if is_online else 'OFFLINE'
                    except:
                        item['STATUS'] = 'OFFLINE'

            self.finished.emit(data, set(actual_free_ips))

        except Exception as e:
            self.error.emit(f"Erro durante a coleta: {str(e)}")

    def login(self):
        login_url = f"{self.host}/api/login"
        payload = {
            "username": self.username,
            "password": self.password,
            "remember": True
        }
        try:
            response = self.session.post(login_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except:
            return False

    def get_clients(self, site_name='default'):
        endpoints = [
            f"{self.host}/api/s/{site_name}/stat/alluser",
            f"{self.host}/api/s/{site_name}/stat/sta",
        ]

        all_clients = []
        for endpoint in endpoints:
            try:
                response = self.session.get(endpoint, timeout=10)
                response.raise_for_status()
                data = response.json()
                clients = data.get('data', [])
                all_clients.extend(clients)
            except:
                continue

        unique_clients = {client.get('mac'): client for client in all_clients}
        return list(unique_clients.values())

    def extract_client_data(self, clients):
        data = []
        for client in clients:
            name = client.get('name') or client.get('hostname') or 'Desconhecido'
            if 'coletor' not in name.lower():
                continue

            ip_address = (client.get('ip') or
                          client.get('fixed_ip') or
                          client.get('last_ip') or
                          'N/A')

            setor = 'N/A'
            if re.search(r'\bREC\b', name, re.IGNORECASE):
                setor = 'Recebimento'
            elif re.search(r'\bSEP\b', name, re.IGNORECASE):
                setor = 'Separação'

            data.append({
                'NAME': name,
                'SETOR': setor,
                'MANUFACTURER': client.get('oui', 'N/A'),
                'MAC': client.get('mac', 'N/A'),
                'IP ADDRESS': ip_address,
                'FIRST SEEN': self.format_timestamp(client.get('first_seen')),
                'LAST SEEN': self.format_timestamp(client.get('last_seen')),
                'STATUS': 'VERIFICANDO'
            })

        return data

    def format_timestamp(self, timestamp):
        if not timestamp:
            return 'N/A'
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%d/%m/%Y %H:%M')
        except:
            return 'N/A'

    def scan_free_ips_optimized(self):
        """
        VERSÃO OTIMIZADA: Escaneia faixa configurável com mais workers e timeout menor
        Melhoria: 100 workers + timeout 1s = ~3x mais rápido
        """
        free_ips = []
        
        # Carregar configuração de IP Range
        if IPMapping:
            mapper = IPMapping.from_config_file()
            base_ip = mapper.base_ip
            start = mapper.start_ip
            end = mapper.end_ip
        else:
            # Fallback para valores padrão do config.py
            base_ip = IP_BASE
            start = IP_SCAN_START
            end = IP_SCAN_END
        
        # OTIMIZAÇÃO: Aumentar workers de 50 para 100+
        # Para range grande (2-253 = 252 IPs), usar mais paralelismo
        range_size = end - start + 1
        max_workers = min(150, range_size)  # Até 150 workers paralelos
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for i in range(start, end + 1):
                ip = f"{base_ip}.{i}"
                future = executor.submit(self.ping_ip_fast, ip)
                futures[future] = ip

            for future in as_completed(futures):
                ip = futures[future]
                try:
                    is_online = future.result()
                    # IPs LIVRES são os que NÃO respondem
                    if not is_online:
                        free_ips.append(ip)
                except:
                    # Se deu erro no ping, considera livre também
                    free_ips.append(ip)

        return free_ips

    def ping_ip_fast(self, ip):
        """
        VERSÃO OTIMIZADA: Ping mais rápido com timeout reduzido
        Timeout reduzido: 2s → 1s (2x mais rápido)
        """
        try:
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', '1', '-w', '300', ip]  # Reduzido de 500ms para 300ms
                proc = subprocess.run(cmd, stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL, timeout=1,  # Reduzido de 2s para 1s
                                      creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                cmd = ['ping', '-c', '1', '-W', '1', ip]
                proc = subprocess.run(cmd, stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL, timeout=1)  # Reduzido de 2s para 1s
            return proc.returncode == 0
        except:
            return False
    
    def ping_ip(self, ip):
        """Ping padrão (mantido para compatibilidade)"""
        try:
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', '1', '-w', '500', ip]
                proc = subprocess.run(cmd, stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL, timeout=2,
                                      creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                cmd = ['ping', '-c', '1', '-W', '1', ip]
                proc = subprocess.run(cmd, stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL, timeout=2)
            return proc.returncode == 0
        except:
            return False