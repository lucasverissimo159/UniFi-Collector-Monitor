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
from PyQt5.QtGui import QColor, QFont, QPalette, QIcon

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.config import *
from app.workers.collection_worker import UniFiWorker, load_unifi_credentials
from app.workers.status_worker import StatusUpdateWorker
from app.gui.collaborators_tab import CollaboratorManagementTab
from app.gui.settings_tab import SettingsTab

# Importar sistema de IP Mapping
try:
    from app.data.ip_mapping import check_collector_ip_mismatch
except ImportError:
    # Fallback se ip_mapping não existir
    check_collector_ip_mismatch = None

# Importar sistema de bloqueio automático
try:
    from app.data.ip_blocker import BlockMonitorWorker
    BLOCK_MONITOR_AVAILABLE = True
except ImportError:
    BLOCK_MONITOR_AVAILABLE = False
    BlockMonitorWorker = None

class UniFiCollectorGUI(QMainWindow):
    """Interface principal com sistema de abas"""

    def __init__(self):
        super().__init__()
        self.data = []
        self.free_ips = set()
        self.last_filters = {}
        self.blink_state = False
        self.update_worker = None
        self.block_worker = None  # Worker para bloqueio automático
        # Variáveis para filtros de Nome e IP (só aplicam ao clicar em Filtrar)
        self.applied_name_filter = ""
        self.applied_ip_filter = ""
        
        # OTIMIZAÇÃO: Cache para melhorar performance
        self._last_filters = {}  # Cache de filtros
        self._visible_rows_cache = None  # Cache de linhas visíveis
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Monitor de Coletores UniFi - Versão 3.0')
        self.setGeometry(100, 100, 1400, 800)
        
        # Maximizar janela ao abrir
        self.showMaximized()
        
        # Carregar e aplicar ícone da aplicação
        if os.path.exists(WINDOW_ICON_PATH):
            self.setWindowIcon(QIcon(WINDOW_ICON_PATH))

        # Aplicar tema moderno
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #bdc3c7;
                color: #2c3e50;
                padding: 10px 30px;
                min-width: 159px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #34495e;
                color: white;
            }
        """)

        # Widget central com tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Sistema de abas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #3498db;
                border-radius: 5px;
            }
        """)

        # Aba 1: Monitor de Coletores
        self.monitor_tab = self.create_monitor_tab()
        self.tabs.addTab(self.monitor_tab, "🖥️ Monitor de Coletores")

        # Aba 2: Gestão de Colaboradores
        self.collaborators_tab = CollaboratorManagementTab(self)
        self.tabs.addTab(self.collaborators_tab, "👥 Gestão de Colaboradores")

        # Aba 3: Configurações
        self.settings_tab = SettingsTab(self)
        self.tabs.addTab(self.settings_tab, "⚙️ Configurações")

        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                padding: 5px;
            }
        """)
        
        # Label permanente para contadores (lado esquerdo - FIXO)
        self.status_counter_label = QLabel("Carregando...")
        self.status_counter_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                padding: 0px 10px;
            }
        """)
        self.status_bar.addWidget(self.status_counter_label)
        
        # Label para mensagens temporárias (lado direito)
        self.status_message_label = QLabel("")
        self.status_message_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-weight: bold;
                padding: 0px 10px;
                font-style: italic;
            }
        """)
        self.status_bar.addPermanentWidget(self.status_message_label)

        # Timer para piscar
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.toggle_blink)

        # Timer para auto-atualização
        self.auto_update_timer = QTimer(self)
        self.auto_update_timer.timeout.connect(self.auto_update_status)

        # ADICIONAR ESTA LINHA AQUI:
        self.auto_update_checkbox.setChecked(True)
        
        # Iniciar coleta automaticamente
        QTimer.singleShot(500, self.start_collection)
        
        # Iniciar sistema de bloqueio automático
        if BLOCK_MONITOR_AVAILABLE:
            QTimer.singleShot(2000, self.start_block_monitor)  # Aguardar 2s antes de iniciar bloqueio

    def create_monitor_tab(self):
        """Cria a aba de monitoramento"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Cabeçalho COM CONTADORES
        header_layout = QHBoxLayout()
        title = QLabel("📡 Monitor de Coletores UniFi")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        header_layout.addWidget(title)
        
        # CONTADORES AO LADO DO TÍTULO
        self.counter_label = QLabel()
        self.counter_label.setFont(QFont('Segoe UI', 11, QFont.Bold))
        self.counter_label.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
            }
        """)
        header_layout.addWidget(self.counter_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Filtros - TUDO EM UMA LINHA HORIZONTAL
        filter_group = QGroupBox("Filtros")
        filter_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        filter_layout = QHBoxLayout()  # Layout horizontal único
        
        # SEÇÃO 1: Filtros automáticos (Status, Setor, Fabricante)
        filter_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(['Todos', 'Online', 'Offline', 'Livre', 'Alerta'])
        self.status_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.status_combo)

        filter_layout.addWidget(QLabel("Setor:"))
        self.setor_combo = QComboBox()
        self.setor_combo.addItems(['Todos'])
        self.setor_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.setor_combo)

        filter_layout.addWidget(QLabel("Fabricante:"))
        self.manufacturer_combo = QComboBox()
        self.manufacturer_combo.addItems(['Todos'])
        self.manufacturer_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.manufacturer_combo)
        
        # Separador visual
        separator = QWidget()
        separator.setFixedWidth(20)
        filter_layout.addWidget(separator)
        
        # SEÇÃO 2: Container visual para Nome, IP e botão Filtrar (agrupados)
        search_group = QWidget()
        search_group.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        search_group_layout = QHBoxLayout()
        search_group_layout.setSpacing(8)
        search_group_layout.setContentsMargins(10, 5, 10, 5)
        
        # Campo Nome
        name_label = QLabel("🔍 Nome:")
        name_label.setStyleSheet("border: none; background: transparent; font-weight: bold;")
        search_group_layout.addWidget(name_label)
        
        self.name_filter = QLineEdit()
        self.name_filter.setPlaceholderText("Digite o nome...")
        self.name_filter.setFixedWidth(150)
        self.name_filter.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 6px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2ecc71;
            }
        """)
        # Permitir Enter para filtrar
        self.name_filter.returnPressed.connect(self.on_search_button_clicked)
        search_group_layout.addWidget(self.name_filter)

        # Campo IP
        ip_label = QLabel("🌐 IP:")
        ip_label.setStyleSheet("border: none; background: transparent; font-weight: bold;")
        search_group_layout.addWidget(ip_label)
        
        self.ip_filter = QLineEdit()
        self.ip_filter.setPlaceholderText("Digite o IP...")
        self.ip_filter.setFixedWidth(150)
        self.ip_filter.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 6px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2ecc71;
            }
        """)
        # Permitir Enter para filtrar
        self.ip_filter.returnPressed.connect(self.on_search_button_clicked)
        search_group_layout.addWidget(self.ip_filter)

        # Botão Filtrar
        search_btn = QPushButton("🔍 Filtrar")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        search_btn.clicked.connect(self.on_search_button_clicked)
        search_group_layout.addWidget(search_btn)
        
        search_group.setLayout(search_group_layout)
        filter_layout.addWidget(search_group)
        
        # Separador visual
        separator2 = QWidget()
        separator2.setFixedWidth(10)
        filter_layout.addWidget(separator2)
        
        # Botão Limpar
        clear_btn = QPushButton("🔄 Limpar")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        clear_btn.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_btn)
        
        filter_layout.addStretch()

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            'Status', 'Nome', 'Setor', 'Fabricante', 'MAC',
            'IP', 'Primeira Vez', 'Última Vez'
        ])

        # Estilo da tabela
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #ecf0f1;
                border: 2px solid #3498db;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 10px 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # Definir altura mínima das linhas
        self.table.verticalHeader().setDefaultSectionSize(35)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)

        layout.addWidget(self.table)

        # Controles de atualização
        controls_layout = QHBoxLayout()

        self.auto_update_checkbox = QCheckBox("Auto-atualizar status (15s)")
        self.auto_update_checkbox.stateChanged.connect(self.toggle_auto_update)
        self.auto_update_checkbox.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(self.auto_update_checkbox)

        controls_layout.addStretch()

        refresh_status_btn = QPushButton("🔄 Atualizar Status")
        refresh_status_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_status_btn.clicked.connect(self.manual_update_status)
        controls_layout.addWidget(refresh_status_btn)

        layout.addLayout(controls_layout)

        widget.setLayout(layout)
        return widget

    def start_collection(self):
        """Inicia a coleta de dados automaticamente com credenciais embutidas"""
        self.show_status_message("Coletando dados... Por favor aguarde.")
        # Não limpar a tabela para evitar flickering durante atualizações
        # self.table.setRowCount(0)

        # 🆕 CARREGAR CREDENCIAIS DO ARQUIVO JSON (se existir) OU config.py
        host, username, password = load_unifi_credentials()
        self.worker = UniFiWorker(host, username, password)
        self.worker.finished.connect(self.on_collection_finished)
        self.worker.progress.connect(lambda msg: self.show_status_message(msg))
        self.worker.error.connect(self.on_collection_error)
        self.worker.start()

    def on_collection_finished(self, data, free_ips):
        """Chamado quando a coleta termina"""
        self.data = data
        self.free_ips = free_ips

        # SALVAR seleções atuais dos filtros
        current_status = self.status_combo.currentText()
        current_setor = self.setor_combo.currentText()
        current_manufacturer = self.manufacturer_combo.currentText()

        # Atualizar combos de filtro
        setores = sorted(set(d.get('SETOR', 'N/A') for d in data if d.get('SETOR') != 'N/A'))
        manufacturers = sorted(set(d.get('MANUFACTURER', 'N/A') for d in data))

        # Bloquear sinais para evitar múltiplas aplicações de filtros
        self.setor_combo.blockSignals(True)
        self.manufacturer_combo.blockSignals(True)
        self.status_combo.blockSignals(True)

        self.setor_combo.clear()
        self.setor_combo.addItems(['Todos'] + setores)

        self.manufacturer_combo.clear()
        self.manufacturer_combo.addItems(['Todos'] + manufacturers)

        # RESTAURAR seleções anteriores
        status_index = self.status_combo.findText(current_status)
        if status_index >= 0:
            self.status_combo.setCurrentIndex(status_index)

        setor_index = self.setor_combo.findText(current_setor)
        if setor_index >= 0:
            self.setor_combo.setCurrentIndex(setor_index)
        
        manufacturer_index = self.manufacturer_combo.findText(current_manufacturer)
        if manufacturer_index >= 0:
            self.manufacturer_combo.setCurrentIndex(manufacturer_index)

        # Desbloquear sinais
        self.setor_combo.blockSignals(False)
        self.manufacturer_combo.blockSignals(False)
        self.status_combo.blockSignals(False)

        # FORÇAR atualização resetando o cache de filtros
        self.last_filters = {}
        
        self.apply_filters()
        self.blink_timer.start(800)

        # Atualizar contadores
        self.update_status_counts()

        # Atualizar aba de colaboradores
        self.collaborators_tab.refresh_table()

    def on_collection_error(self, error_msg):
        """Chamado quando há erro na coleta"""
        QMessageBox.critical(self, "Erro", error_msg)
        self.show_status_message("Erro na coleta de dados.")

    def on_search_button_clicked(self):
        """Aplica os filtros de Nome e IP quando o botão Filtrar é clicado"""
        # Armazenar os valores dos campos nos filtros aplicados
        self.applied_name_filter = self.name_filter.text().lower().strip()
        self.applied_ip_filter = self.ip_filter.text().lower().strip()
        
        # Aplicar todos os filtros
        self.apply_filters()
        
        # Feedback visual
        if self.applied_name_filter or self.applied_ip_filter:
            filters_text = []
            if self.applied_name_filter:
                filters_text.append(f"Nome: '{self.applied_name_filter}'")
            if self.applied_ip_filter:
                filters_text.append(f"IP: '{self.applied_ip_filter}'")
            self.show_status_message(f"Filtros aplicados: {' | '.join(filters_text)}")
        else:
            self.show_status_message("Filtros de busca limpos")

    def clear_filters(self):
        """Limpa todos os filtros"""
        self.status_combo.setCurrentText('Todos')
        self.setor_combo.setCurrentText('Todos')
        self.manufacturer_combo.setCurrentText('Todos')
        self.name_filter.clear()
        self.ip_filter.clear()
        # Limpar também os filtros aplicados
        self.applied_name_filter = ""
        self.applied_ip_filter = ""
        # Aplicar filtros para atualizar a tabela
        self.apply_filters()

    @staticmethod
    def collector_number_key(item):
        """Extrai o número do coletor para ordenação - MESMO DO ORIGINAL"""
        name = item.get('NAME', '') or ''
        m = re.search(r'coletor\s*0*?(\d+)\b', name, re.IGNORECASE)
        if m:
            try:
                return int(m.group(1))
            except:
                pass
        return 9999

    @staticmethod
    def collector_ip_mismatch(item):
        """Verifica incompatibilidade usando sistema inteligente de IP Mapping"""
        if check_collector_ip_mismatch:
            # Usar sistema inteligente (suporta qualquer range)
            name = item.get('NAME', '')
            ip = item.get('IP ADDRESS', '')
            return check_collector_ip_mismatch(name, ip)
        else:
            # Fallback para lógica antiga (só funciona com 100-199)
            name = item.get('NAME', '') or ''
            ip = item.get('IP ADDRESS', '') or ''
            m = re.search(r'coletor\s*0*?(\d+)\b', name, re.IGNORECASE)
            if not m:
                return False
            try:
                collector_num_str = m.group(1).zfill(2)
                last_octet = int(ip.split('.')[-1])
                last_two_digits = str(last_octet)[-2:].zfill(2)
                return last_two_digits != collector_num_str
            except Exception:
                return False

    def apply_filters(self):
        """Aplica os filtros à tabela"""
        status_filter = self.status_combo.currentText()
        setor_filter = self.setor_combo.currentText()
        manufacturer_filter = self.manufacturer_combo.currentText()
        # Usar variáveis aplicadas ao invés dos campos diretamente
        name_filter = self.applied_name_filter
        ip_filter = self.applied_ip_filter

        current_filters = {
            'status': status_filter,
            'setor': setor_filter,
            'manufacturer': manufacturer_filter,
            'name': name_filter,
            'ip': ip_filter
        }
        if current_filters == self.last_filters:
            return
        self.last_filters = current_filters

        self.blink_timer.stop()

        filtered_data = self.data

        if status_filter != 'Todos':
            if status_filter == 'Alerta':
                filtered_data = [d for d in filtered_data if self.collector_ip_mismatch(d)]
            else:
                filtered_data = [d for d in filtered_data
                                 if d.get('STATUS', '').upper() == status_filter.upper()]

        if setor_filter != 'Todos':
            filtered_data = [d for d in filtered_data
                             if d.get('SETOR') == setor_filter]

        if manufacturer_filter != 'Todos':
            filtered_data = [d for d in filtered_data
                             if d.get('MANUFACTURER') == manufacturer_filter]

        if name_filter:
            filtered_data = [d for d in filtered_data
                             if name_filter in d.get('NAME', '').lower()]

        if ip_filter:
            filtered_data = [d for d in filtered_data
                             if ip_filter in d.get('IP ADDRESS', '').lower()]

        filtered_data = sorted(filtered_data, key=self.collector_number_key)

        # Desabilitar atualizações visuais para evitar flickering
        self.table.setUpdatesEnabled(False)
        
        self.table.setRowCount(len(filtered_data))
        for row, item in enumerate(filtered_data):
            self.populate_row(row, item)
        
        # Reabilitar atualizações visuais
        self.table.setUpdatesEnabled(True)

        self.update_status_counts()
        self.blink_timer.start(800)

    def populate_row(self, row, item):
        """Popula uma linha da tabela"""
        status = item.get('STATUS', 'OFFLINE')
        is_mismatch = self.collector_ip_mismatch(item)

        status_item = QTableWidgetItem()
        if is_mismatch:
            status_item.setText('🟠 Alerta')
            status_item.setForeground(QColor(255, 140, 0))
        elif status == 'ONLINE':
            status_item.setText('🟢 Online')
            status_item.setForeground(QColor(0, 170, 0))
        elif status == 'OFFLINE':
            status_item.setText('🔴 Offline')
            status_item.setForeground(QColor(255, 0, 0))
        else:
            status_item.setText('🔵 Livre')
            status_item.setForeground(QColor(0, 102, 204))

        status_item.setFont(QFont('Segoe UI', 10, QFont.Bold))
        status_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, status_item)

        columns = [
            item.get('NAME', 'N/A'),
            item.get('SETOR', 'N/A'),
            item.get('MANUFACTURER', 'N/A'),
            item.get('MAC', 'N/A'),
            item.get('IP ADDRESS', 'N/A'),
            item.get('FIRST SEEN', 'N/A'),
            item.get('LAST SEEN', 'N/A')
        ]

        for col_idx, value in enumerate(columns, 1):
            cell_item = QTableWidgetItem(str(value))
            cell_item.setTextAlignment(Qt.AlignCenter)
            cell_item.setFont(QFont('Segoe UI', 10))

            if is_mismatch:
                cell_item.setBackground(QColor(255, 230, 180))
            elif col_idx == 5:  # coluna IP
                if status == 'ONLINE':
                    cell_item.setBackground(QColor(200, 255, 200))
                elif status == 'OFFLINE':
                    cell_item.setBackground(QColor(255, 200, 200))
                else:
                    cell_item.setBackground(QColor(200, 225, 255))
            self.table.setItem(row, col_idx, cell_item)

    """def toggle_blink(self):
        # Alterna o estado de piscar
        self.blink_state = not self.blink_state
        for row in range(self.table.rowCount()):
            status_item = self.table.item(row, 0)
            ip_item = self.table.item(row, 5)

            if status_item and ip_item:
                status_text = status_item.text()
                if self.blink_state:
                    if '🟠' in status_text:
                        ip_item.setBackground(QColor(255, 200, 100))
                        ip_item.setFont(QFont('Segoe UI', 10, QFont.Bold))
                    elif 'Online' in status_text:
                        ip_item.setBackground(QColor(100, 255, 100))
                        ip_item.setFont(QFont('Segoe UI', 10, QFont.Bold))
                    elif 'Offline' in status_text:
                        ip_item.setBackground(QColor(255, 100, 100))
                        ip_item.setFont(QFont('Segoe UI', 10, QFont.Bold))
                    else:
                        ip_item.setBackground(QColor(100, 180, 255))
                        ip_item.setFont(QFont('Segoe UI', 10, QFont.Bold))
                else:
                    if '🟠' in status_text:
                        ip_item.setBackground(QColor(255, 230, 180))
                        ip_item.setFont(QFont('Segoe UI', 10))
                    elif 'Online' in status_text:
                        ip_item.setBackground(QColor(200, 255, 200))
                        ip_item.setFont(QFont('Segoe UI', 10))
                    elif 'Offline' in status_text:
                        ip_item.setBackground(QColor(255, 200, 200))
                        ip_item.setFont(QFont('Segoe UI', 10))
                    else:
                        ip_item.setBackground(QColor(200, 225, 255))
                        ip_item.setFont(QFont('Segoe UI', 10))"""

    def toggle_blink(self):
        """Alterna o estado de piscar - VERSÃO OTIMIZADA"""
        self.blink_state = not self.blink_state
        
        # OTIMIZAÇÃO: Processar apenas linhas visíveis (10-20x mais rápido!)
        visible_range = self.get_visible_rows()
        if not visible_range:
            return
        
        start_row, end_row = visible_range
        
        # Processar linhas visíveis + buffer de 5 linhas
        for row in range(start_row, min(end_row + 5, self.table.rowCount())):
            status_item = self.table.item(row, 0)
            
            if not status_item:
                continue
                
            status_text = status_item.text()
            
            # 🆕 EFEITO DE PISCAR PARA ALERTAS (LINHA INTEIRA)
            if '🟠' in status_text:
                # Manter o negrito sempre na coluna 0 (Status)
                status_item.setFont(QFont('Segoe UI', 10, QFont.Bold))
                
                if self.blink_state:
                    # Estado LIGADO - Amarelo forte e negrito nas outras colunas
                    for col in range(1, self.table.columnCount()):  # Começa da coluna 1
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(QColor(255, 200, 100))  # Amarelo forte
                            item.setFont(QFont('Segoe UI', 10, QFont.Bold))
                else:
                    # Estado DESLIGADO - Amarelo claro e negrito apenas na coluna 0
                    for col in range(1, self.table.columnCount()):
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(QColor(255, 230, 180))  # Amarelo claro
                            item.setFont(QFont('Segoe UI', 10))  # Sem negrito
            
            # 🆕 COMPORTAMENTO ORIGINAL APENAS PARA IP (mantido para outros status)
            elif status_item and self.table.item(row, 5):
                ip_item = self.table.item(row, 5)
                
                if self.blink_state:
                    if 'Online' in status_text:
                        ip_item.setBackground(QColor(100, 255, 100))
                        ip_item.setFont(QFont('Segoe UI', 10, QFont.Bold))
                    elif 'Offline' in status_text:
                        ip_item.setBackground(QColor(255, 100, 100))
                        ip_item.setFont(QFont('Segoe UI', 10, QFont.Bold))
                    else:
                        ip_item.setBackground(QColor(100, 180, 255))
                        ip_item.setFont(QFont('Segoe UI', 10, QFont.Bold))
                else:
                    if 'Online' in status_text:
                        ip_item.setBackground(QColor(200, 255, 200))
                        ip_item.setFont(QFont('Segoe UI', 10))
                    elif 'Offline' in status_text:
                        ip_item.setBackground(QColor(255, 200, 200))
                        ip_item.setFont(QFont('Segoe UI', 10))
                    else:
                        ip_item.setBackground(QColor(200, 225, 255))
                        ip_item.setFont(QFont('Segoe UI', 10))

    def get_visible_rows(self):
        """
        Retorna range de linhas visíveis na tabela
        OTIMIZAÇÃO: Processa apenas linhas visíveis no toggle_blink
        """
        try:
            viewport = self.table.viewport()
            top = self.table.rowAt(0)
            bottom = self.table.rowAt(viewport.height())

            if top == -1:
                top = 0
            if bottom == -1:
                bottom = self.table.rowCount() - 1

            return (top, bottom)
        except:
            # Fallback seguro: retorna todas as linhas
            return (0, self.table.rowCount() - 1)

    def update_status_counts(self):
        """Atualiza os contadores de status - NO CABEÇALHO E STATUS BAR"""
        online_count = sum(1 for d in self.data if d.get('STATUS') == 'ONLINE')
        offline_count = sum(1 for d in self.data if d.get('STATUS') == 'OFFLINE')
        free_count = sum(1 for d in self.data if d.get('STATUS') == 'LIVRE')
        mismatch_count = sum(1 for d in self.data if self.collector_ip_mismatch(d))
        total = len(self.data)
        
        # Texto dos contadores
        counter_text = (
            f'Total: {total} | 🟢 {online_count} | 🔴 {offline_count} | '
            f'🔵 {free_count} | 🟠 {mismatch_count}'
        )
        
        # Atualizar label no cabeçalho
        self.counter_label.setText(counter_text)
        
        # Atualizar label permanente na status bar (lado esquerdo - fixo)
        self.status_counter_label.setText(counter_text)
    
    def show_status_message(self, message, duration=0):
        """Mostra mensagem temporária no lado direito da status bar"""
        self.status_message_label.setText(message)
        if duration > 0:
            QTimer.singleShot(duration, lambda: self.status_message_label.setText(""))

    def toggle_auto_update(self, state):
        """Ativa/desativa auto-atualização"""
        if state == Qt.Checked:
            self.auto_update_timer.start(15000)  # 15 segundos
            self.show_status_message("Auto-atualização ativada (15s)", 3000)
        else:
            self.auto_update_timer.stop()
            self.show_status_message("Auto-atualização desativada", 3000)

    def auto_update_status(self):
        """Atualiza automaticamente o status"""
        if not self.data:
            return
        self.manual_update_status()

    def manual_update_status(self):
        """Atualização manual do status - COLETA COMPLETA"""
        if self.worker and self.worker.isRunning():
            return
        
        if self.update_worker and self.update_worker.isRunning():
            return

        self.show_status_message("Atualizando dados completos...")
        
        # Fazer apenas coleta completa (que já atualiza tudo incluindo status)
        self.start_collection()

    def on_status_updated(self, updated_data):
        """Chamado quando o status é atualizado"""
        self.data = updated_data
        self.apply_filters()
        self.update_status_counts()
    
    # ========== SISTEMA DE BLOQUEIO AUTOMÁTICO ==========
    
    def start_block_monitor(self):
        """Inicia o sistema de bloqueio automático"""
        if not BLOCK_MONITOR_AVAILABLE:
            return
        
        # Verificar se bloqueio está habilitado
        try:
            from app.config import ENABLE_IP_BLOCKING
            if not ENABLE_IP_BLOCKING:
                return
        except:
            pass
        
        # Se já existe um worker rodando, não iniciar outro
        if self.block_worker and self.block_worker.isRunning():
            return
        
        # Carregar credenciais UniFi
        host, username, password = load_unifi_credentials()
        
        # Carregar configurações de bloqueio do config.py
        # USAR AS VARIÁVEIS QUE JÁ EXISTEM NO CONFIG.PY DO USUÁRIO
        try:
            from app.config import IP_BLOCK_CHECK_INTERVAL, TEMP_UNBLOCK_TIME, MAX_TENTATIVAS_BLOQUEIO
            check_interval = IP_BLOCK_CHECK_INTERVAL
            temp_unblock_time = TEMP_UNBLOCK_TIME
            max_tentativas = MAX_TENTATIVAS_BLOQUEIO
        except:
            # Valores padrão se não houver no config
            check_interval = 60
            temp_unblock_time = 10
            max_tentativas = 4
        
        # Criar e configurar worker
        self.block_worker = BlockMonitorWorker(
            host=host,
            username=username,
            password=password,
            check_interval=check_interval,
            temp_unblock_time=temp_unblock_time,
            max_tentativas=max_tentativas
        )
        
        # Conectar sinais
        self.block_worker.status_update.connect(self.on_block_status_update)
        self.block_worker.statistics_update.connect(self.on_block_statistics_update)
        self.block_worker.error_occurred.connect(self.on_block_error)
        
        # Iniciar worker
        self.block_worker.start()
        
        self.show_status_message("🔒 Sistema de bloqueio automático iniciado", 5000)
    
    def on_block_status_update(self, message):
        """Handler para atualizações de status do bloqueio"""
        # Mostrar mensagem na status bar temporariamente
        self.show_status_message(f"🔒 {message}", 3000)
    
    def on_block_statistics_update(self, stats):
        """Handler para estatísticas de bloqueio"""
        # Atualizar estatísticas na aba de configurações, se estiver disponível
        try:
            if hasattr(self, 'settings_tab') and hasattr(self.settings_tab, 'refresh_block_stats'):
                self.settings_tab.refresh_block_stats()
        except AttributeError:
            # Aba de bloqueios ainda não foi criada ou não existe
            pass
        except Exception as e:
            # Outros erros são silenciados para não quebrar o bloqueio
            pass
    
    def on_block_error(self, error_message):
        """Handler para erros do sistema de bloqueio"""
        self.show_status_message(f"⚠️ Bloqueio: {error_message}", 5000)
    
    def stop_block_monitor(self):
        """Para o sistema de bloqueio automático"""
        if self.block_worker and self.block_worker.isRunning():
            self.block_worker.stop()
            self.block_worker.wait(3000)  # Aguardar até 3 segundos
            self.show_status_message("🔒 Sistema de bloqueio parado", 3000)
    
    def closeEvent(self, event):
        """Evento de fechamento da janela - parar workers"""
        # Parar sistema de bloqueio
        if self.block_worker and self.block_worker.isRunning():
            self.block_worker.stop()
            self.block_worker.wait(3000)
        
        # Parar outros workers se necessário
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            self.worker.wait(2000)
        
        if self.update_worker and self.update_worker.isRunning():
            self.update_worker.wait(2000)
        
        event.accept()