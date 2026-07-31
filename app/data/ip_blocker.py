"""
Sistema Inteligente de Bloqueio de IPs com Monitoramento Automático
Baseado no sistema de tentativas progressivas com bloqueio definitivo
Versão 3.1 - Integrado com PyQt5 e Log Rotation
"""

import json
import os
import requests
import urllib3
import logging
from datetime import datetime
from time import sleep
from PyQt5.QtCore import QThread, pyqtSignal

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Importar sistema de log rotation
try:
    from app.utils.log_rotation import setup_rotating_logger, LogRotationManager
    LOG_ROTATION_AVAILABLE = True
except ImportError:
    LOG_ROTATION_AVAILABLE = False
    # Fallback para logging básico se log_rotation não disponível
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('monitor_bloqueio_coletores.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

# Arquivo de estado dos bloqueios
BLOCKS_FILE = "ip_blocks.json"

# Arquivo de log principal
LOG_FILE = "monitor_bloqueio_coletores.log"


class IPBlocker:
    """Gerencia bloqueio inteligente de coletores com IP incorreto"""
    
    def __init__(self, controller=None):
        """
        Args:
            controller: Instância de UniFiController (opcional, pode ser setado depois)
        """
        self.controller = controller
        self.blocks_data = self.load_blocks()
    
    def set_controller(self, controller):
        """Define o controller UniFi"""
        self.controller = controller
    
    def load_blocks(self):
        """Carrega estado dos bloqueios"""
        if os.path.exists(BLOCKS_FILE):
            try:
                with open(BLOCKS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_blocks(self):
        """Salva estado dos bloqueios"""
        try:
            with open(BLOCKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.blocks_data, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    def get_block_info(self, mac):
        """Retorna informações de bloqueio de um MAC"""
        return self.blocks_data.get(mac, None)
    
    def is_blocked(self, mac):
        """Verifica se um MAC está bloqueado"""
        return mac in self.blocks_data
    
    def is_definitive_block(self, mac):
        """Verifica se é bloqueio definitivo (5+ tentativas)"""
        info = self.get_block_info(mac)
        if info:
            return info.get('bloqueio_definitivo', False)
        return False
    
    def add_block(self, mac, name, numero, tipo, tentativas=1):
        """
        Adiciona ou atualiza bloqueio
        
        Args:
            mac: MAC address
            name: Nome do coletor
            numero: Número do coletor
            tipo: Tipo (REC/SEP)
            tentativas: Número de tentativas
        """
        # Verificar se já existe
        if mac in self.blocks_data:
            # Incrementar tentativas
            self.blocks_data[mac]['tentativas'] = tentativas
            self.blocks_data[mac]['last_update'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
            # Se chegou a 5 tentativas, marcar como definitivo
            if tentativas >= 5:
                self.blocks_data[mac]['bloqueio_definitivo'] = True
        else:
            # Novo bloqueio
            self.blocks_data[mac] = {
                'name': name,
                'numero': numero,
                'tipo': tipo,
                'tentativas': tentativas,
                'bloqueio_definitivo': False,
                'created_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        
        self.save_blocks()
    
    def remove_block(self, mac):
        """Remove bloqueio (quando IP for corrigido)"""
        if mac in self.blocks_data:
            del self.blocks_data[mac]
            self.save_blocks()
            return True
        return False
    
    def get_all_blocks(self):
        """Retorna todos os bloqueios"""
        return self.blocks_data.copy()
    
    def get_temporary_blocks(self):
        """Retorna bloqueios temporários (tentativas 1-4)"""
        return {
            mac: info for mac, info in self.blocks_data.items()
            if not info.get('bloqueio_definitivo', False)
        }
    
    def get_definitive_blocks(self):
        """Retorna bloqueios definitivos (tentativas 5+)"""
        return {
            mac: info for mac, info in self.blocks_data.items()
            if info.get('bloqueio_definitivo', False)
        }
    
    def get_statistics(self):
        """Retorna estatísticas dos bloqueios"""
        temp = self.get_temporary_blocks()
        defin = self.get_definitive_blocks()
        
        return {
            'total': len(self.blocks_data),
            'temporary': len(temp),
            'definitive': len(defin),
            'blocks': self.blocks_data.copy()
        }
    
    def clear_all_blocks(self):
        """Remove todos os bloqueios (usar com cuidado!)"""
        self.blocks_data = {}
        self.save_blocks()


class UniFiController:
    """Classe para interagir com UniFi Controller"""
    
    def __init__(self, host, username, password, site='default', logger=None):
        self.host = host
        self.username = username
        self.password = password
        self.site = site
        self.session = requests.Session()
        self.session.verify = False
        self.cookies = None
        # Usar logger fornecido ou fallback para logging padrão
        self.logger = logger if logger else logging.getLogger(__name__)
    
    def login(self):
        """Fazer login no controller"""
        url = f"{self.host}/api/login"
        payload = {
            "username": self.username,
            "password": self.password,
            "remember": True
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.cookies = response.cookies
                self.logger.info("[OK] Login realizado com sucesso no UniFi!")
                return True
            else:
                self.logger.error(f"[ERRO] Falha na autenticação: Status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"[ERRO] Erro ao conectar: {e}")
            return False
    
    def get_all_clients(self):
        """Obter TODOS os clientes (online e offline)"""
        url = f"{self.host}/api/s/{self.site}/stat/alluser"
        
        try:
            response = self.session.get(url, cookies=self.cookies, timeout=10)
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                return []
        except:
            return []
    
    def get_online_clients(self):
        """Obter apenas clientes ONLINE"""
        url = f"{self.host}/api/s/{self.site}/stat/sta"
        
        try:
            response = self.session.get(url, cookies=self.cookies, timeout=10)
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                return []
        except:
            return []
    
    def block_client(self, mac_address, device_name=""):
        """Bloquear cliente por MAC address"""
        url = f"{self.host}/api/s/{self.site}/cmd/stamgr"
        payload = {
            "cmd": "block-sta",
            "mac": mac_address
        }
        
        try:
            response = self.session.post(url, json=payload, cookies=self.cookies, timeout=10)
            if response.status_code == 200:
                self.logger.warning(f"[BLOQUEADO] {device_name} (MAC: {mac_address})")
                return True
            else:
                self.logger.error(f"[ERRO] Falha ao bloquear {device_name}: Status {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"[ERRO] Erro ao bloquear {device_name}: {e}")
            return False
    
    def unblock_client(self, mac_address, device_name=""):
        """Desbloquear cliente por MAC address"""
        url = f"{self.host}/api/s/{self.site}/cmd/stamgr"
        payload = {
            "cmd": "unblock-sta",
            "mac": mac_address
        }
        
        try:
            response = self.session.post(url, json=payload, cookies=self.cookies, timeout=10)
            if response.status_code == 200:
                self.logger.info(f"[DESBLOQUEADO] {device_name} (MAC: {mac_address})")
                return True
            else:
                self.logger.error(f"[ERRO] Falha ao desbloquear {device_name}: Status {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"[ERRO] Erro ao desbloquear {device_name}: {e}")
            return False


class BlockMonitorWorker(QThread):
    """
    Worker Thread para monitoramento contínuo de bloqueios
    Roda em background verificando e bloqueando coletores com IP incorreto
    """
    
    # Sinais para comunicação com a interface
    status_update = pyqtSignal(str)  # Mensagem de status
    statistics_update = pyqtSignal(dict)  # Estatísticas atualizadas
    error_occurred = pyqtSignal(str)  # Erro ocorrido
    
    def __init__(self, host, username, password, check_interval=60, temp_unblock_time=10, max_tentativas=4):
        """
        Args:
            host: UniFi host URL
            username: UniFi username
            password: UniFi password
            check_interval: Intervalo entre verificações (segundos)
            temp_unblock_time: Tempo de desbloqueio temporário (segundos)
            max_tentativas: Máximo de tentativas antes de bloqueio definitivo
        """
        super().__init__()
        self.host = host
        self.username = username
        self.password = password
        self.check_interval = check_interval
        self.temp_unblock_time = temp_unblock_time
        self.max_tentativas = max_tentativas
        
        self.controller = None
        self.blocker = IPBlocker()
        self.running = True
        self.verificacao_num = 0
        
        # Configurar logger com log rotation (se disponível)
        if LOG_ROTATION_AVAILABLE:
            self.logger, self.rotation_manager = setup_rotating_logger(
                name='bloqueio_monitor',
                log_file=LOG_FILE,
                level=logging.INFO,
                max_size_mb=5,  # Rotaciona quando ultrapassar 5 MB
                backup_count=7   # Mantém últimos 7 backups
            )
            self.logger.info("[LOG ROTATION] Sistema de rotação de logs ATIVO")
            self.logger.info(f"[LOG ROTATION] Configuração: max={5}MB, backups={7}, retenção={30}dias")
        else:
            # Fallback para logger padrão
            self.logger = logging.getLogger('bloqueio_monitor')
            self.rotation_manager = None
            self.logger.warning("[LOG ROTATION] Sistema de rotação NÃO disponível - usando logging básico")
    
    def stop(self):
        """Para o worker"""
        self.running = False
    
    def run(self):
        """Loop principal de monitoramento"""
        self.logger.info("="*100)
        self.logger.info("SISTEMA DE BLOQUEIO AUTOMÁTICO INICIADO")
        self.logger.info("="*100)
        
        # Conectar ao UniFi
        self.controller = UniFiController(self.host, self.username, self.password, logger=self.logger)
        
        if not self.controller.login():
            self.error_occurred.emit("Falha ao conectar no UniFi Controller")
            self.logger.error("[ERRO] Não foi possível conectar ao UniFi")
            return
        
        self.blocker.set_controller(self.controller)
        self.status_update.emit("Sistema de bloqueio automático ativo")
        
        # Loop de monitoramento
        while self.running:
            try:
                self.verificacao_num += 1
                self.logger.info(f"\n{'#'*100}")
                self.logger.info(f"VERIFICAÇÃO #{self.verificacao_num} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                self.logger.info(f"{'#'*100}")
                
                # Verificar se precisa rotacionar log (a cada 10 verificações, ~10 minutos)
                if self.rotation_manager and self.verificacao_num % 10 == 0:
                    if self.rotation_manager.should_rotate():
                        self.logger.info("[LOG ROTATION] Arquivo de log precisa rotacionar - Iniciando rotação...")
                        
                        # Obter stats antes de rotacionar
                        stats = self.rotation_manager.get_log_stats()
                        self.logger.info(f"[LOG ROTATION] Tamanho atual: {stats['current_size_mb']} MB")
                        self.logger.info(f"[LOG ROTATION] Backups existentes: {stats['backup_count']}")
                        
                        # Rotacionar
                        self.rotation_manager.rotate()
                        
                        # Reconfigurar logger após rotação
                        self.logger, self.rotation_manager = setup_rotating_logger(
                            name='bloqueio_monitor',
                            log_file=LOG_FILE,
                            level=logging.INFO,
                            max_size_mb=5,
                            backup_count=7
                        )
                        
                        # Atualizar logger no controller
                        self.controller.logger = self.logger
                        
                        self.logger.info("[LOG ROTATION] Rotação concluída com sucesso!")
                        
                        # Stats após rotação
                        stats = self.rotation_manager.get_log_stats()
                        self.logger.info(f"[LOG ROTATION] Novo tamanho: {stats['current_size_mb']} MB")
                        self.logger.info(f"[LOG ROTATION] Total de backups: {stats['backup_count']}")
                
                self.verificar_e_agir()
                
                # Emitir estatísticas atualizadas
                stats = self.blocker.get_statistics()
                self.statistics_update.emit(stats)
                
                # Aguardar próxima verificação
                self.logger.info(f"[AGUARDANDO] Próxima verificação em {self.check_interval} segundos...")
                
                # Sleep interruptível
                for _ in range(self.check_interval):
                    if not self.running:
                        break
                    sleep(1)
                
            except Exception as e:
                self.logger.error(f"[ERRO] Erro durante verificação: {e}")
                self.error_occurred.emit(f"Erro: {str(e)}")
                sleep(10)  # Aguardar antes de tentar novamente
        
        self.logger.info("\n" + "="*100)
        self.logger.info("[ENCERRADO] Sistema de bloqueio automático parado")
        self.logger.info("="*100)
    
    def verificar_e_agir(self):
        """
        Verifica coletores com sistema de tentativas e bloqueio definitivo inteligente
        Baseado no teste_1.py
        """
        
        self.logger.info("\nINICIANDO VERIFICAÇÃO")
        self.logger.info("="*100)
        
        # Importar funções de IP Mapping
        try:
            from app.data.ip_mapping import extract_collector_number_from_name, get_expected_ip_for_collector
        except ImportError:
            self.logger.error("[ERRO] Módulo ip_mapping não encontrado")
            return
        
        # FASE 1: Desbloquear temporariamente APENAS os que ainda estão nas primeiras 4 tentativas
        temporarios = self.blocker.get_temporary_blocks()
        definitivos = self.blocker.get_definitive_blocks()
        
        if temporarios:
            self.logger.info(f"\n[FASE 1A] DESBLOQUEIO TEMPORÁRIO ({len(temporarios)} dispositivos nas primeiras {self.max_tentativas} tentativas)")
            self.logger.info(f"Desbloqueando por {self.temp_unblock_time} segundos para verificar se IP foi corrigido...")
            
            for mac, info in temporarios.items():
                self.logger.info(f"  [TEMP] {info['name']:<25} Tentativa: {info['tentativas']}/{self.max_tentativas}")
                self.controller.unblock_client(mac, info['name'])
            
            self.logger.info(f"\n[AGUARDANDO] {self.temp_unblock_time} segundos para dispositivos reconectarem...")
            sleep(self.temp_unblock_time)
        
        if definitivos:
            self.logger.info(f"\n[FASE 1B] BLOQUEIO DEFINITIVO ({len(definitivos)} dispositivos após {self.max_tentativas} tentativas)")
            self.logger.info("Estes permanecem BLOQUEADOS, mas continuam sendo MONITORADOS.")
            self.logger.info("Quando o IP for corrigido, serão DESBLOQUEADOS AUTOMATICAMENTE.")
            
            for mac, info in definitivos.items():
                self.logger.info(f"  [DEFINITIVO] {info['name']:<25} Tentativa: {info['tentativas']}")
        
        # FASE 2: Coletar todos os clientes e verificar IPs
        self.logger.info("\n[FASE 2] COLETA DE CLIENTES E VERIFICAÇÃO DE IPs")
        
        all_clients = self.controller.get_all_clients()
        online_clients = self.controller.get_online_clients()
        online_macs = {c.get('mac') for c in online_clients}
        
        self.logger.info(f"  Total de clientes: {len(all_clients)}")
        self.logger.info(f"  Clientes online: {len(online_clients)}")
        
        # Identificar coletores com IP incorreto
        coletores_incorretos = []
        
        for client in all_clients:
            name = client.get('name') or client.get('hostname') or 'Desconhecido'
            
            # Filtrar apenas coletores
            if 'coletor' not in name.lower():
                continue
            
            mac = client.get('mac')
            ip_atual = client.get('ip') or client.get('fixed_ip') or client.get('last_ip')
            
            if not mac or not ip_atual:
                continue
            
            # Extrair número do coletor
            numero = extract_collector_number_from_name(name)
            if numero is None:
                continue
            
            # Verificar IP esperado
            ip_esperado = get_expected_ip_for_collector(name)
            if not ip_esperado:
                continue
            
            # Verificar se IP está incorreto
            if ip_atual != ip_esperado:
                # Determinar tipo (REC/SEP)
                import re
                tipo = 'N/A'
                if re.search(r'\bREC\b', name, re.IGNORECASE):
                    tipo = 'REC'
                elif re.search(r'\bSEP\b', name, re.IGNORECASE):
                    tipo = 'SEP'
                
                coletores_incorretos.append({
                    'mac': mac,
                    'name': name,
                    'numero': numero,
                    'tipo': tipo,
                    'ip_atual': ip_atual,
                    'ip_esperado': ip_esperado,
                    'online': mac in online_macs
                })
        
        self.logger.info(f"\n  Coletores com IP incorreto encontrados: {len(coletores_incorretos)}")
        
        # FASE 3: Aplicar bloqueios e desbloquear corrigidos
        self.logger.info("\n[FASE 3] APLICAÇÃO DE BLOQUEIOS")
        
        bloqueados_agora = 0
        passou_definitivo = 0
        desbloqueados_agora = 0
        
        # Novo dicionário de monitorados
        novos_monitorados = {}
        
        if coletores_incorretos:
            for coletor in coletores_incorretos:
                mac = coletor['mac']
                info = self.blocker.get_block_info(mac)
                
                if info:
                    # Já está monitorado
                    tentativa = info['tentativas'] + 1
                    
                    if tentativa > self.max_tentativas:
                        # Bloqueio definitivo
                        self.logger.warning(f"  [BLOQUEIO DEFINITIVO] {coletor['name']:<25}")
                        self.logger.info(f"             Status: {'ONLINE' if coletor['online'] else 'OFFLINE'}")
                        self.logger.info(f"             IP: {coletor['ip_atual']} (esperado: {coletor['ip_esperado']})")
                        self.logger.info(f"             Tentativa: {tentativa} (definitivo)")
                        
                        self.controller.block_client(mac, coletor['name'])
                        passou_definitivo += 1
                        
                        novos_monitorados[mac] = {
                            'name': coletor['name'],
                            'numero': coletor['numero'],
                            'tipo': coletor['tipo'],
                            'tentativas': tentativa,
                            'bloqueio_definitivo': True
                        }
                        
                    else:
                        # Bloquear normalmente
                        self.logger.info(f"  [BLOQUEIO] {coletor['name']:<25}")
                        self.logger.info(f"             Status: {'ONLINE' if coletor['online'] else 'OFFLINE'}")
                        self.logger.info(f"             IP: {coletor['ip_atual']} (esperado: {coletor['ip_esperado']})")
                        self.logger.info(f"             Tentativa: {tentativa}/{self.max_tentativas}")
                        
                        if tentativa == self.max_tentativas:
                            self.logger.warning(f"             *** ÚLTIMA CHANCE! Próxima será bloqueio definitivo ***")
                        
                        self.controller.block_client(mac, coletor['name'])
                        bloqueados_agora += 1
                        
                        novos_monitorados[mac] = {
                            'name': coletor['name'],
                            'numero': coletor['numero'],
                            'tipo': coletor['tipo'],
                            'tentativas': tentativa,
                            'bloqueio_definitivo': False
                        }
                
                else:
                    # Primeira vez - bloquear
                    self.logger.info(f"  [NOVO] {coletor['name']:<25}")
                    self.logger.info(f"         Status: {'ONLINE' if coletor['online'] else 'OFFLINE'}")
                    self.logger.info(f"         IP: {coletor['ip_atual']} (esperado: {coletor['ip_esperado']})")
                    self.logger.info(f"         Tentativa: 1/{self.max_tentativas}")
                    self.logger.info(f"         AÇÃO: BLOQUEANDO pela primeira vez")
                    
                    self.controller.block_client(mac, coletor['name'])
                    bloqueados_agora += 1
                    
                    novos_monitorados[mac] = {
                        'name': coletor['name'],
                        'numero': coletor['numero'],
                        'tipo': coletor['tipo'],
                        'tentativas': 1,
                        'bloqueio_definitivo': False
                    }
        
        # FASE 4: Verificar se IPs foram corrigidos (desbloquear)
        all_blocks = self.blocker.get_all_blocks()
        coletores_map = {c['mac']: c for c in coletores_incorretos}
        
        for mac in list(all_blocks.keys()):
            if mac not in coletores_map:
                # IP foi corrigido! Desbloquear
                info = all_blocks[mac]
                self.logger.info(f"\n  [CORRIGIDO] {info['name']:<25}")
                self.logger.info(f"              IP foi corrigido! Desbloqueando...")
                
                self.controller.unblock_client(mac, info['name'])
                self.blocker.remove_block(mac)
                desbloqueados_agora += 1
        
        # Atualizar bloqueios
        for mac, info in novos_monitorados.items():
            self.blocker.add_block(
                mac, 
                info['name'], 
                info['numero'], 
                info['tipo'], 
                info['tentativas']
            )
        
        # RESUMO
        temporarios_count = len([m for m in novos_monitorados.values() if not m['bloqueio_definitivo']])
        definitivos_count = len([m for m in novos_monitorados.values() if m['bloqueio_definitivo']])
        
        self.logger.info("\n" + "="*100)
        self.logger.info("RESUMO DA VERIFICAÇÃO")
        self.logger.info("="*100)
        self.logger.info(f"  Ações executadas:")
        self.logger.info(f"    - Novos bloqueios/re-bloqueios:      {bloqueados_agora}")
        self.logger.info(f"    - Passaram para bloqueio definitivo: {passou_definitivo}")
        self.logger.info(f"    - Corrigidos (desbloqueados):        {desbloqueados_agora}")
        self.logger.info(f"\n  Status atual:")
        self.logger.info(f"    - Bloqueados temporariamente (1-{self.max_tentativas}):  {temporarios_count}")
        self.logger.info(f"    - Bloqueio definitivo ({self.max_tentativas+1}+):          {definitivos_count}")
        self.logger.info(f"    - Total monitorados:                 {len(novos_monitorados)}")
        
        if len(novos_monitorados) == 0:
            self.logger.info("\n  [OK] Todos os coletores estão com IP correto!")
        else:
            self.logger.info(f"\n  Próxima verificação em {self.check_interval} segundos")
        
        self.logger.info("="*100 + "\n")