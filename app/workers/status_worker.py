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

class StatusUpdateWorker(QThread):
    """Thread para atualizar status dos coletores sem travar a interface - VERSÃO OTIMIZADA"""
    status_updated = pyqtSignal(list)

    def __init__(self, data):
        super().__init__()
        self.data = data

    def run(self):
        ips_to_check = []
        for item in self.data:
            if item.get('STATUS') != 'LIVRE':
                ip = item.get('IP ADDRESS')
                if ip and ip != 'N/A':
                    ips_to_check.append((item, ip))

        # OTIMIZAÇÃO: Aumentar workers de 30 para 100
        # Para range grande (até 252 IPs), mais paralelismo = mais rápido
        max_workers = min(100, len(ips_to_check)) if ips_to_check else 30
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for item, ip in ips_to_check:
                future = executor.submit(self.ping_ip_quick, ip)
                futures[future] = item

            for future in as_completed(futures):
                item = futures[future]
                try:
                    is_online = future.result()
                    new_status = 'ONLINE' if is_online else 'OFFLINE'
                    item['STATUS'] = new_status
                except:
                    item['STATUS'] = 'OFFLINE'

        self.status_updated.emit(self.data)

    def ping_ip_quick(self, ip):
        """
        VERSÃO OTIMIZADA: Ping mais rápido com timeout reduzido
        Timeout: 2s → 1s, Wait: 500ms → 300ms
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