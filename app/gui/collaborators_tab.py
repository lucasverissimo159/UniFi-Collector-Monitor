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
from app.data.data_manager import DataManager

# Importar sistema de IP Mapping
try:
    from app.data.ip_mapping import check_collector_ip_mismatch
except ImportError:
    # Fallback se ip_mapping não existir
    check_collector_ip_mismatch = None

class AssignCollaboratorDialog(QDialog):
    """Diálogo para atribuir colaborador a um coletor"""

    def __init__(self, collector_name, collector_ip, parent=None):
        super().__init__(parent)
        self.collector_name = collector_name
        self.collector_ip = collector_ip
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Atribuir Colaborador - {self.collector_name}")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        # Aplicar ícone da aplicação
        if os.path.exists(WINDOW_ICON_PATH):
            self.setWindowIcon(QIcon(WINDOW_ICON_PATH))

        layout = QVBoxLayout()

        # Informações do coletor
        info_group = QGroupBox("Informações do Coletor")
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"<b>Nome:</b> {self.collector_name}"))
        info_layout.addWidget(QLabel(f"<b>IP:</b> {self.collector_ip}"))
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Dados do colaborador
        collab_group = QGroupBox("Dados do Colaborador")
        collab_layout = QVBoxLayout()

        collab_layout.addWidget(QLabel("Nome do Colaborador:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: JOÃO SILVA")
        self.name_input.textChanged.connect(self.convert_to_uppercase)
        collab_layout.addWidget(self.name_input)

        collab_layout.addWidget(QLabel("Função:"))
        self.function_input = QLineEdit()
        self.function_input.setPlaceholderText("Ex: OPERADOR DE SEPARAÇÃO")
        self.function_input.textChanged.connect(self.convert_to_uppercase)
        collab_layout.addWidget(self.function_input)

        collab_layout.addWidget(QLabel("Turno:"))
        self.shift_combo = QComboBox()
        self.shift_combo.addItems(["Manhã", "Tarde", "Noite", "Madrugada"])
        collab_layout.addWidget(self.shift_combo)

        # Horário de início
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Horário de Início:"))
        self.start_time = QTimeEdit()
        self.start_time.setDisplayFormat("HH:mm")
        self.start_time.setTime(QTime.currentTime())
        time_layout.addWidget(self.start_time)
        time_layout.addWidget(QLabel("Horário de Fim:"))
        self.end_time = QTimeEdit()
        self.end_time.setDisplayFormat("HH:mm")
        self.end_time.setTime(QTime.currentTime().addSecs(3600 * 8))
        time_layout.addWidget(self.end_time)
        collab_layout.addLayout(time_layout)

        collab_layout.addWidget(QLabel("Observações:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("OBSERVAÇÕES ADICIONAIS (OPCIONAL)")
        self.notes_input.textChanged.connect(self.convert_notes_to_uppercase)
        collab_layout.addWidget(self.notes_input)

        collab_group.setLayout(collab_layout)
        layout.addWidget(collab_group)

        # Botões
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        """Retorna os dados do colaborador"""
        return {
            'collector_name': self.collector_name,
            'collector_ip': self.collector_ip,
            'collaborator_name': self.name_input.text().strip(),
            'function': self.function_input.text().strip(),
            'shift': self.shift_combo.currentText(),
            'start_time': self.start_time.time().toString("HH:mm"),
            'end_time': self.end_time.time().toString("HH:mm"),
            'notes': self.notes_input.toPlainText().strip(),
            'assignment_date': datetime.now().strftime('%d/%m/%Y %H:%M')
        }

    def convert_to_uppercase(self, text):
        """Converte texto do QLineEdit para maiúsculas automaticamente"""
        sender = self.sender()
        if sender:
            # Salvar posição do cursor
            cursor_position = sender.cursorPosition()
            # Converter para maiúsculas
            sender.blockSignals(True)  # Evitar loop infinito
            sender.setText(text.upper())
            sender.setCursorPosition(cursor_position)
            sender.blockSignals(False)

    def convert_notes_to_uppercase(self):
        """Converte texto do QTextEdit (Observações) para maiúsculas automaticamente"""
        # Salvar posição do cursor
        cursor = self.notes_input.textCursor()
        position = cursor.position()
        # Converter para maiúsculas
        self.notes_input.blockSignals(True)  # Evitar loop infinito
        current_text = self.notes_input.toPlainText()
        self.notes_input.setPlainText(current_text.upper())
        # Restaurar posição do cursor
        cursor.setPosition(position)
        self.notes_input.setTextCursor(cursor)
        self.notes_input.blockSignals(False)



class EditCollaboratorDialog(QDialog):
    """Diálogo para editar colaborador existente"""

    def __init__(self, collector_name, collector_ip, collaborator_data, collaborator_index, parent=None):
        super().__init__(parent)
        self.collector_name = collector_name
        self.collector_ip = collector_ip
        self.collaborator_data = collaborator_data
        self.collaborator_index = collaborator_index
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle(f"Editar Colaborador - {self.collector_name}")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        # Aplicar ícone da aplicação
        if os.path.exists(WINDOW_ICON_PATH):
            self.setWindowIcon(QIcon(WINDOW_ICON_PATH))

        layout = QVBoxLayout()

        # Informações do coletor
        info_group = QGroupBox("Informações do Coletor")
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"<b>Nome:</b> {self.collector_name}"))
        info_layout.addWidget(QLabel(f"<b>IP:</b> {self.collector_ip}"))
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Dados do colaborador
        collab_group = QGroupBox("Dados do Colaborador")
        collab_layout = QVBoxLayout()

        collab_layout.addWidget(QLabel("Nome do Colaborador:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: JOÃO SILVA")
        self.name_input.textChanged.connect(self.convert_to_uppercase)
        collab_layout.addWidget(self.name_input)

        collab_layout.addWidget(QLabel("Função:"))
        self.function_input = QLineEdit()
        self.function_input.setPlaceholderText("Ex: OPERADOR DE SEPARAÇÃO")
        self.function_input.textChanged.connect(self.convert_to_uppercase)
        collab_layout.addWidget(self.function_input)

        collab_layout.addWidget(QLabel("Turno:"))
        self.shift_combo = QComboBox()
        self.shift_combo.addItems(["Manhã", "Tarde", "Noite", "Madrugada"])
        collab_layout.addWidget(self.shift_combo)

        # Horário de início
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Horário de Início:"))
        self.start_time = QTimeEdit()
        self.start_time.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.start_time)
        time_layout.addWidget(QLabel("Horário de Fim:"))
        self.end_time = QTimeEdit()
        self.end_time.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.end_time)
        collab_layout.addLayout(time_layout)

        collab_layout.addWidget(QLabel("Observações:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("OBSERVAÇÕES ADICIONAIS (OPCIONAL)")
        self.notes_input.textChanged.connect(self.convert_notes_to_uppercase)
        collab_layout.addWidget(self.notes_input)

        collab_group.setLayout(collab_layout)
        layout.addWidget(collab_group)

        # Botões
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def load_data(self):
        """Carrega os dados existentes do colaborador nos campos"""
        # Bloquear sinais durante o carregamento para evitar conversão automática
        self.name_input.blockSignals(True)
        self.function_input.blockSignals(True)
        self.notes_input.blockSignals(True)
        
        self.name_input.setText(self.collaborator_data.get('collaborator_name', ''))
        self.function_input.setText(self.collaborator_data.get('function', ''))
        
        # Selecionar turno
        shift = self.collaborator_data.get('shift', 'Manhã')
        index = self.shift_combo.findText(shift)
        if index >= 0:
            self.shift_combo.setCurrentIndex(index)
        
        # Definir horários
        start_time_str = self.collaborator_data.get('start_time', '08:00')
        end_time_str = self.collaborator_data.get('end_time', '17:00')
        self.start_time.setTime(QTime.fromString(start_time_str, "HH:mm"))
        self.end_time.setTime(QTime.fromString(end_time_str, "HH:mm"))
        
        # Observações
        self.notes_input.setPlainText(self.collaborator_data.get('notes', ''))
        
        # Reativar sinais
        self.name_input.blockSignals(False)
        self.function_input.blockSignals(False)
        self.notes_input.blockSignals(False)

    def get_data(self):
        """Retorna os dados atualizados do colaborador"""
        return {
            'collector_name': self.collector_name,
            'collector_ip': self.collector_ip,
            'collaborator_name': self.name_input.text().strip(),
            'function': self.function_input.text().strip(),
            'shift': self.shift_combo.currentText(),
            'start_time': self.start_time.time().toString("HH:mm"),
            'end_time': self.end_time.time().toString("HH:mm"),
            'notes': self.notes_input.toPlainText().strip(),
            'assignment_date': self.collaborator_data.get('assignment_date', datetime.now().strftime('%d/%m/%Y %H:%M')),
            'last_modified': datetime.now().strftime('%d/%m/%Y %H:%M')
        }

    def convert_to_uppercase(self, text):
        """Converte texto do QLineEdit para maiúsculas automaticamente"""
        sender = self.sender()
        if sender:
            cursor_position = sender.cursorPosition()
            sender.blockSignals(True)
            sender.setText(text.upper())
            sender.setCursorPosition(cursor_position)
            sender.blockSignals(False)

    def convert_notes_to_uppercase(self):
        """Converte texto do QTextEdit (Observações) para maiúsculas automaticamente"""
        cursor = self.notes_input.textCursor()
        position = cursor.position()
        self.notes_input.blockSignals(True)
        current_text = self.notes_input.toPlainText()
        self.notes_input.setPlainText(current_text.upper())
        cursor.setPosition(position)
        self.notes_input.setTextCursor(cursor)
        self.notes_input.blockSignals(False)


class CollaboratorManagementTab(QWidget):
    """Aba para gerenciamento de colaboradores - MÚLTIPLOS por coletor"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.collaborators_data = DataManager.load_data()
        
        # Timer para piscar linhas de alerta
        self.blink_state = False
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_blink)
        self.blink_timer.start(800)  # Pisca a cada 800ms
        
        self.init_ui()

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

    @staticmethod
    def get_expected_ip(collector_name):
        """Calcula o IP correto baseado no nome do coletor usando sistema inteligente"""
        if check_collector_ip_mismatch:
            # Usar sistema inteligente
            try:
                from app.data.ip_mapping import get_expected_ip_for_collector
                return get_expected_ip_for_collector(collector_name)
            except:
                pass
        
        # Fallback para lógica antiga (só funciona com 100-199)
        m = re.search(r'coletor\s*0*?(\d+)\b', collector_name, re.IGNORECASE)
        if not m:
            return None
        try:
            collector_num = int(m.group(1))
            # IP base: 203.0.113.(100 + número do coletor)
            # Ex: Coletor 19 → 203.0.113.119
            return f"203.0.113.{100 + collector_num}"
        except:
            return None

    def toggle_blink(self):
        """Alterna o estado de piscar das linhas de alerta"""
        self.blink_state = not self.blink_state
        
        # Percorrer todas as linhas da tabela e aplicar piscar nas marcadas
        for row in range(self.table.rowCount()):
            # Verificar se a linha está marcada para piscar (UserRole = 'BLINK')
            first_item = self.table.item(row, 0)
            if first_item and first_item.data(Qt.UserRole + 1) == 'BLINK':
                # Alternar entre cor vermelha intensa e vermelha clara
                if self.blink_state:
                    color = QColor(255, 100, 100)  # Vermelho intenso
                else:
                    color = QColor(255, 180, 180)  # Vermelho claro
                
                # Aplicar cor em todas as colunas da linha
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(color)

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # Cabeçalho
        header_layout = QHBoxLayout()
        title = QLabel("👥 Gestão de Colaboradores por Coletor")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # Filtros
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Setor:"))
        self.setor_filter = QComboBox()
        self.setor_filter.addItems(['Todos', 'Recebimento', 'Separação'])
        self.setor_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.setor_filter)
        
        filter_layout.addWidget(QLabel("Turno:"))
        self.turno_filter = QComboBox()
        self.turno_filter.addItems(['Todos', 'Manhã', 'Tarde', 'Noite', 'Madrugada'])
        self.turno_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.turno_filter)
        
        filter_layout.addWidget(QLabel("Nome:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("DIGITE O NOME DO COLETOR OU COLABORADOR...")
        self.filter_input.textChanged.connect(self.convert_filter_to_uppercase)
        filter_layout.addWidget(self.filter_input)

        # Botão Limpar Filtro
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

        main_layout.addLayout(filter_layout)

        # Tabela de atribuições - MODIFICADA para suportar múltiplos colaboradores
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'Coletor', 'IP', 'Colaboradores', 'Turnos',
            'Horários', 'Qtd', 'Ações'
        ])

        # Estilo da tabela
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        main_layout.addWidget(self.table)

        # ═══════════════════════════════════════════════════════════════════
        # 🧹 PAINEL DE GESTÃO DE HISTÓRICO (SEM BOTÃO DE LIMPEZA)
        # ═══════════════════════════════════════════════════════════════════
        
        cleanup_group = QGroupBox("📦 Sistema de Histórico Arquivado")
        cleanup_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #2c3e50;
            }
        """)
        
        cleanup_layout = QVBoxLayout()
        
        # Explicação do sistema
        info_label = QLabel(
            f"🔄 Sistema automático: Mantém {MAX_HISTORY_RECORDS} registros dos últimos {RETENTION_MONTHS} meses\n"
            f"📦 Histórico antigo (> {RETENTION_MONTHS} meses) é automaticamente movido para: {ARCHIVE_FOLDER}/"
        )
        info_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 10px;
                padding: 8px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """)
        cleanup_layout.addWidget(info_label)
        
        # Botão visualizar arquivos
        buttons_layout = QHBoxLayout()
        
        view_archive_btn = QPushButton("📂 Ver Histórico Arquivado")
        view_archive_btn.setToolTip("Visualiza registros arquivados (>12 meses)")
        view_archive_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 25px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                min-width: 220px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        view_archive_btn.clicked.connect(self.view_archived_history)
        buttons_layout.addWidget(view_archive_btn)
        
        buttons_layout.addStretch()
        cleanup_layout.addLayout(buttons_layout)
        
        cleanup_group.setLayout(cleanup_layout)
        main_layout.addWidget(cleanup_group)

        # Estatísticas
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        stats_layout.addWidget(self.stats_label)
        main_layout.addLayout(stats_layout)

        self.setLayout(main_layout)
        self.refresh_table()

    def save_data(self):
        """Salva dados dos colaboradores no arquivo JSON"""
        try:
            DataManager.save_data(self.collaborators_data)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao salvar dados: {str(e)}")

    # ═══════════════════════════════════════════════════════════════════════
    # 🔄 GESTÃO DE HISTÓRICO EM CASCATA - 3 ETAPAS
    # ═══════════════════════════════════════════════════════════════════════

    def cleanup_history_cascade(self, show_details=True):
        """
        Executa limpeza em cascata (3 etapas):
        1. Arquiva registros com +12 meses
        2. Remove registros com +12 meses do histórico ativo
        3. Limita a 15 registros mais recentes
        """
        results = DataManager.cleanup_history_cascade(self.collaborators_data)
        
        # Atualizar dados com resultado da limpeza
        self.collaborators_data = results['data']
        
        # Salvar dados atualizados
        if results['collectors_affected'] > 0:
            self.save_data()
        
        return results

    def view_archived_history(self):
        """Visualizador de histórico arquivado - Interface completa"""
        if not os.path.exists(ARCHIVE_FOLDER):
            QMessageBox.information(
                self,
                "📂 Histórico Arquivado",
                f"Nenhum arquivo encontrado.\n\n"
                f"A pasta '{ARCHIVE_FOLDER}' será criada automaticamente\n"
                f"quando houver registros para arquivar (>12 meses)."
            )
            return
        
        archive_files = sorted([f for f in os.listdir(ARCHIVE_FOLDER) if f.endswith('.json')],
                               reverse=True)
        
        if not archive_files:
            QMessageBox.information(
                self,
                "📂 Histórico Arquivado",
                f"Pasta '{ARCHIVE_FOLDER}' existe, mas está vazia.\n\n"
                f"Os arquivos serão criados automaticamente quando\n"
                f"houver registros com mais de 12 meses."
            )
            return
        
        # DIALOG PRINCIPAL - Lista de arquivos
        dialog = QDialog(self)
        dialog.setWindowTitle("📦 Visualizador de Histórico Arquivado")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        header = QLabel(f"📂 {len(archive_files)} período(s) arquivado(s)")
        header.setFont(QFont('Segoe UI', 14, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px;")
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        # Botão de informações
        info_btn = QPushButton("ℹ️ Info")
        info_btn.setToolTip("Informações sobre arquivamento")
        info_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        def show_info():
            QMessageBox.information(
                dialog,
                "ℹ️ Sobre o Arquivamento",
                f"📦 COMO FUNCIONA:\n\n"
                f"• Registros com mais de {RETENTION_MONTHS} meses são automaticamente\n"
                f"  movidos para a pasta '{ARCHIVE_FOLDER}'\n\n"
                f"• Os arquivos são organizados por mês/ano\n"
                f"  (exemplo: historico_2024-10.json)\n\n"
                f"• NENHUM dado é perdido - tudo fica preservado!\n\n"
                f"• Você pode visualizar os arquivos a qualquer momento\n"
                f"  através deste visualizador\n\n"
                f"📊 BENEFÍCIOS:\n\n"
                f"• Histórico ativo rápido e otimizado\n"
                f"• Todos os dados históricos preservados\n"
                f"• Fácil de fazer backup (copie a pasta)\n"
                f"• Auditoria completa disponível"
            )
        
        info_btn.clicked.connect(show_info)
        header_layout.addWidget(info_btn)
        layout.addLayout(header_layout)
        
        # Estatísticas gerais
        total_records = 0
        for filename in archive_files:
            filepath = os.path.join(ARCHIVE_FOLDER, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                    total_records += len(records)
            except:
                pass
        
        stats_label = QLabel(f"📊 Total de {total_records} registro(s) arquivado(s)")
        stats_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 8px;
                border-radius: 5px;
                font-size: 11px;
            }
        """)
        layout.addWidget(stats_label)
        
        # Lista de arquivos
        from PyQt5.QtWidgets import QListWidget
        list_widget = QListWidget()
        list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        
        for filename in archive_files:
            filepath = os.path.join(ARCHIVE_FOLDER, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                    count = len(records)
                    
                    # Extrair período do nome do arquivo
                    period = filename.replace('historico_', '').replace('.json', '')
                    year, month = period.split('-')
                    month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                                   'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                    month_name = month_names[int(month) - 1]
                    
                    item_text = f"📅 {month_name}/{year}  •  {count} registro(s)  •  {filename}"
                    list_widget.addItem(item_text)
            except:
                list_widget.addItem(f"⚠️ {filename} (erro ao ler)")
        
        layout.addWidget(list_widget)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        # Botão Visualizar
        view_btn = QPushButton("👁️ Visualizar Selecionado")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        def view_selected():
            current_row = list_widget.currentRow()
            if current_row < 0:
                QMessageBox.warning(dialog, "Atenção", "Selecione um período para visualizar!")
                return
            
            filename = archive_files[current_row]
            filepath = os.path.join(ARCHIVE_FOLDER, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                
                # DIALOG DE VISUALIZAÇÃO - Tabela detalhada
                view_dialog = QDialog(dialog)
                period = filename.replace('historico_', '').replace('.json', '')
                view_dialog.setWindowTitle(f"📄 Registros Arquivados - {period}")
                view_dialog.setMinimumWidth(1100)
                view_dialog.setMinimumHeight(700)
                
                view_layout = QVBoxLayout()
                
                # Header do período
                period_header = QLabel(f"📅 Período: {period}  •  {len(records)} registro(s)")
                period_header.setFont(QFont('Segoe UI', 13, QFont.Bold))
                period_header.setStyleSheet("color: #2c3e50; padding: 10px;")
                view_layout.addWidget(period_header)
                
                # Filtros
                filter_layout = QHBoxLayout()
                filter_layout.addWidget(QLabel("🔍 Filtrar:"))
                
                filter_input = QLineEdit()
                filter_input.setPlaceholderText("Digite nome do colaborador ou coletor...")
                filter_layout.addWidget(filter_input)
                view_layout.addLayout(filter_layout)
                
                # Tabela
                table = QTableWidget()
                table.setColumnCount(9)
                table.setHorizontalHeaderLabels([
                    'Coletor', 'IP', 'Colaborador', 'Função', 'Turno',
                    'Horário', 'Atribuído', 'Removido', 'Obs'
                ])
                
                table.setStyleSheet("""
                    QTableWidget {
                        border: 1px solid #bdc3c7;
                        border-radius: 5px;
                        gridline-color: #ecf0f1;
                    }
                    QHeaderView::section {
                        background-color: #34495e;
                        color: white;
                        padding: 8px;
                        border: none;
                        font-weight: bold;
                    }
                    QTableWidget::item {
                        padding: 5px;
                    }
                """)
                
                table.setAlternatingRowColors(True)
                
                def populate_table(filter_text=""):
                    table.setRowCount(0)
                    visible_records = []
                    
                    for record in records:
                        if filter_text:
                            collab_name = record.get('collaborator_name', '').lower()
                            collector_ip = record.get('archived_from_collector', '').lower()
                            if filter_text.lower() not in collab_name and filter_text.lower() not in collector_ip:
                                continue
                        visible_records.append(record)
                    
                    table.setRowCount(len(visible_records))
                    
                    for i, record in enumerate(visible_records):
                        collector_name = record.get('collector_name', 'N/A')
                        collector_ip = record.get('archived_from_collector', 'N/A')
                        
                        table.setItem(i, 0, QTableWidgetItem(collector_name))
                        table.setItem(i, 1, QTableWidgetItem(collector_ip))
                        table.setItem(i, 2, QTableWidgetItem(record.get('collaborator_name', 'N/A')))
                        table.setItem(i, 3, QTableWidgetItem(record.get('function', 'N/A')))
                        table.setItem(i, 4, QTableWidgetItem(record.get('shift', 'N/A')))
                        table.setItem(i, 5, QTableWidgetItem(
                            f"{record.get('start_time', 'N/A')}-{record.get('end_time', 'N/A')}"
                        ))
                        table.setItem(i, 6, QTableWidgetItem(record.get('assignment_date', 'N/A')))
                        table.setItem(i, 7, QTableWidgetItem(record.get('end_date', 'N/A')))
                        
                        obs = record.get('notes', '-')
                        obs_preview = obs[:40] + '...' if len(obs) > 40 else obs
                        table.setItem(i, 8, QTableWidgetItem(obs_preview))
                    
                    table.resizeColumnsToContents()
                
                populate_table()
                filter_input.textChanged.connect(populate_table)
                
                view_layout.addWidget(table)
                
                # Botões
                btn_layout = QHBoxLayout()
                
                export_btn = QPushButton("📤 Exportar CSV")
                export_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        padding: 8px 15px;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                
                def export_csv():
                    try:
                        import csv
                        csv_filename = filename.replace('.json', '.csv')
                        csv_path = os.path.join(ARCHIVE_FOLDER, csv_filename)
                        
                        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                            fieldnames = ['Coletor IP', 'Colaborador', 'Função', 'Turno',
                                          'Início', 'Fim', 'Atribuído', 'Removido', 'Observações']
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            writer.writeheader()
                            
                            for record in records:
                                writer.writerow({
                                    'Coletor IP': record.get('archived_from_collector', 'N/A'),
                                    'Colaborador': record.get('collaborator_name', 'N/A'),
                                    'Função': record.get('function', 'N/A'),
                                    'Turno': record.get('shift', 'N/A'),
                                    'Início': record.get('start_time', 'N/A'),
                                    'Fim': record.get('end_time', 'N/A'),
                                    'Atribuído': record.get('assignment_date', 'N/A'),
                                    'Removido': record.get('end_date', 'N/A'),
                                    'Observações': record.get('notes', '-')
                                })
                        
                        QMessageBox.information(
                            view_dialog,
                            "Sucesso",
                            f"Arquivo CSV exportado com sucesso!\n\n"
                            f"Local: {csv_path}"
                        )
                    except Exception as e:
                        QMessageBox.warning(view_dialog, "Erro", f"Erro ao exportar: {str(e)}")
                
                export_btn.clicked.connect(export_csv)
                btn_layout.addWidget(export_btn)
                
                btn_layout.addStretch()
                
                close_btn = QPushButton("Fechar")
                close_btn.clicked.connect(view_dialog.close)
                btn_layout.addWidget(close_btn)
                
                view_layout.addLayout(btn_layout)
                view_dialog.setLayout(view_layout)
                view_dialog.exec_()
                
            except Exception as e:
                QMessageBox.warning(dialog, "Erro", f"Erro ao ler arquivo:\n{str(e)}")
        
        view_btn.clicked.connect(view_selected)
        button_layout.addWidget(view_btn)
        
        button_layout.addStretch()
        
        # Botão Fechar
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec_()


    def add_assignment(self, collector_data):
        """Adiciona uma atribuição de colaborador - PERMITE MÚLTIPLOS"""
        dialog = AssignCollaboratorDialog(
            collector_data.get('NAME', 'N/A'),
            collector_data.get('IP ADDRESS', 'N/A'),
            self
        )

        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['collaborator_name']:
                QMessageBox.warning(self, "Atenção", "Nome do colaborador é obrigatório!")
                return

            collector_key = data['collector_ip']
            
            # Inicializar estrutura se não existir
            if collector_key not in self.collaborators_data:
                self.collaborators_data[collector_key] = {
                    'current': [],  # LISTA de colaboradores ativos
                    'history': []
                }

            # Garantir que current é uma lista
            if not isinstance(self.collaborators_data[collector_key]['current'], list):
                # Migrar formato antigo
                old_current = self.collaborators_data[collector_key]['current']
                if old_current:
                    self.collaborators_data[collector_key]['current'] = [old_current]
                else:
                    self.collaborators_data[collector_key]['current'] = []

            # Adicionar novo colaborador à lista de ativos
            self.collaborators_data[collector_key]['current'].append(data)

            self.save_data()
            self.refresh_table()
            QMessageBox.information(self, "Sucesso", "Colaborador atribuído com sucesso!")

    def edit_assignment(self, collector_ip, collector_name):
        """Edita um colaborador existente"""
        if collector_ip not in self.collaborators_data:
            QMessageBox.warning(self, "Atenção", "Nenhum colaborador encontrado para este coletor!")
            return

        current_list = self.collaborators_data[collector_ip].get('current', [])
        if not current_list:
            QMessageBox.warning(self, "Atenção", "Nenhum colaborador encontrado para este coletor!")
            return

        # Se há apenas 1 colaborador, edita direto
        if len(current_list) == 1:
            collaborator_index = 0
            collaborator_data = current_list[0]
        else:
            # Se há múltiplos, pergunta qual editar
            items = []
            for idx, collab in enumerate(current_list):
                name = collab.get('collaborator_name', 'N/A')
                shift = collab.get('shift', 'N/A')
                items.append(f"{name} ({shift})")
            
            item, ok = QInputDialog.getItem(
                self,
                "Selecionar Colaborador",
                "Escolha o colaborador que deseja editar:",
                items,
                0,
                False
            )
            
            if not ok:
                return
            
            collaborator_index = items.index(item)
            collaborator_data = current_list[collaborator_index]

        # Abrir diálogo de edição
        dialog = EditCollaboratorDialog(
            collector_name,
            collector_ip,
            collaborator_data,
            collaborator_index,
            self
        )

        if dialog.exec_() == QDialog.Accepted:
            updated_data = dialog.get_data()
            if not updated_data['collaborator_name']:
                QMessageBox.warning(self, "Atenção", "Nome do colaborador é obrigatório!")
                return

            # Atualizar o colaborador na lista
            self.collaborators_data[collector_ip]['current'][collaborator_index] = updated_data

            self.save_data()
            self.refresh_table()
            QMessageBox.information(self, "Sucesso", "Colaborador atualizado com sucesso!")

    def show_delete_dialog(self, collector_ip):
        """Mostra diálogo para selecionar qual colaborador excluir"""
        if collector_ip not in self.collaborators_data:
            return
        
        current_list = self.collaborators_data[collector_ip].get('current', [])
        if not isinstance(current_list, list) or not current_list:
            return
        
        # Se só tem 1 colaborador, excluir diretamente
        if len(current_list) == 1:
            self.remove_assignment(collector_ip, 0)
            return
        
        # Se tem múltiplos, mostrar diálogo de seleção
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecionar Colaborador para Excluir")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Selecione o colaborador que deseja excluir:"))
        
        # Lista de colaboradores
        list_widget = QTableWidget()
        list_widget.setColumnCount(3)
        list_widget.setHorizontalHeaderLabels(['Nome', 'Turno', 'Horário'])
        list_widget.setRowCount(len(current_list))
        list_widget.setSelectionBehavior(QTableWidget.SelectRows)
        list_widget.setSelectionMode(QTableWidget.SingleSelection)
        
        for idx, collab in enumerate(current_list):
            if isinstance(collab, dict):
                list_widget.setItem(idx, 0, QTableWidgetItem(collab.get('collaborator_name', 'N/A')))
                list_widget.setItem(idx, 1, QTableWidgetItem(collab.get('shift', 'N/A')))
                list_widget.setItem(idx, 2, QTableWidgetItem(
                    f"{collab.get('start_time', 'N/A')}-{collab.get('end_time', 'N/A')}"
                ))
        
        list_widget.resizeColumnsToContents()
        layout.addWidget(list_widget)
        
        # Botões
        button_layout = QHBoxLayout()
        delete_btn = QPushButton("Excluir Selecionado")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        def on_delete():
            selected = list_widget.currentRow()
            if selected >= 0:
                self.remove_assignment(collector_ip, selected)
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Atenção", "Selecione um colaborador!")
        
        delete_btn.clicked.connect(on_delete)
        button_layout.addWidget(delete_btn)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec_()

    def remove_assignment(self, collector_ip, collaborator_index):
        """Remove uma atribuição e aplica limpeza em cascata automaticamente"""
        reply = QMessageBox.question(
            self,
            'Confirmar Remoção',
            'Deseja realmente remover esta atribuição?',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if collector_ip in self.collaborators_data:
                current_list = self.collaborators_data[collector_ip].get('current', [])
                
                # Garantir que é lista
                if not isinstance(current_list, list):
                    return
                
                if 0 <= collaborator_index < len(current_list):
                    # Move para histórico
                    removed = current_list.pop(collaborator_index)
                    removed['end_date'] = datetime.now().strftime('%d/%m/%Y %H:%M')
                    self.collaborators_data[collector_ip]['history'].append(removed)

                self.save_data()
                
                # 🔄 APLICAR LIMPEZA EM CASCATA AUTOMATICAMENTE
                results = self.cleanup_history_cascade(show_details=False)
                
                self.refresh_table()
                
                # Mensagem personalizada
                message = "✅ Atribuição removida com sucesso!"
                
                if results['archived'] > 0 or results['removed_by_date'] > 0 or results['removed_by_limit'] > 0:
                    message += "\n\n🔄 Limpeza automática aplicada:"
                    if results['archived'] > 0:
                        message += f"\n   📦 {results['archived']} registro(s) arquivado(s)"
                    if results['removed_by_limit'] > 0:
                        message += f"\n   🔢 {results['removed_by_limit']} registro(s) excedente(s) removido(s)"
                
                QMessageBox.information(self, "Sucesso", message)

    def view_details(self, collector_ip):
        """Visualiza detalhes de todas as atribuições de um coletor"""
        if collector_ip not in self.collaborators_data:
            QMessageBox.information(self, "Detalhes", "Nenhuma atribuição disponível.")
            return

        current_list = self.collaborators_data[collector_ip].get('current', [])
        
        # Garantir que é lista
        if not isinstance(current_list, list):
            current_list = [current_list] if current_list else []
        
        history = self.collaborators_data[collector_ip].get('history', [])

        # Criar diálogo de detalhes
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detalhes Completos - {collector_ip}")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(500)
        
        # Aplicar ícone da aplicação
        if os.path.exists(WINDOW_ICON_PATH):
            dialog.setWindowIcon(QIcon(WINDOW_ICON_PATH))

        layout = QVBoxLayout()

        text = QTextEdit()
        text.setReadOnly(True)

        details_text = f"<h2>📋 Colaboradores Ativos</h2>"
        
        if current_list:
            for idx, entry in enumerate(current_list, 1):
                # Garantir que entry é um dict
                if not isinstance(entry, dict):
                    continue
                    
                details_text += f"""
                <div style='background-color: #d4edda; padding: 10px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #28a745;'>
                    <b>✅ Ativo #{idx}</b><br>
                    <b>Colaborador:</b> {entry.get('collaborator_name', 'N/A')}<br>
                    <b>Função:</b> {entry.get('function', 'N/A')}<br>
                    <b>Turno:</b> {entry.get('shift', 'N/A')}<br>
                    <b>Horário:</b> {entry.get('start_time', 'N/A')} às {entry.get('end_time', 'N/A')}<br>
                    <b>Data de Início:</b> {entry.get('assignment_date', 'N/A')}<br>
                    <b>Observações:</b> {entry.get('notes', 'Nenhuma')}
                </div>
                """
        else:
            details_text += "<p><i>Nenhum colaborador ativo no momento.</i></p>"

        details_text += f"<h2>📜 Histórico de Atribuições</h2>"
        
        if history:
            for idx, entry in enumerate(reversed(history), 1):
                details_text += f"""
                <div style='background-color: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 5px;'>
                    <b>Registro #{idx}</b><br>
                    <b>Colaborador:</b> {entry.get('collaborator_name', 'N/A')}<br>
                    <b>Função:</b> {entry.get('function', 'N/A')}<br>
                    <b>Turno:</b> {entry.get('shift', 'N/A')}<br>
                    <b>Horário:</b> {entry.get('start_time', 'N/A')} às {entry.get('end_time', 'N/A')}<br>
                    <b>Início:</b> {entry.get('assignment_date', 'N/A')}<br>
                    <b>Fim:</b> {entry.get('end_date', 'Atual')}<br>
                    <b>Observações:</b> {entry.get('notes', 'Nenhuma')}
                </div>
                """
        else:
            details_text += "<p><i>Nenhum histórico disponível.</i></p>"

        text.setHtml(details_text)
        layout.addWidget(text)

        close_btn = QPushButton("Fechar")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def _add_action_buttons(self, row, collector, collector_ip, is_wrong_ip=False):
        """Adiciona botões de ação a uma linha da tabela"""
        action_widget = QWidget()
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(4, 4, 4, 4)

        # ═══════════════════════════════════════════════════════════
        # Botão ➕ ADICIONAR - Só aparece se NÃO for IP errado
        # ═══════════════════════════════════════════════════════════
        if not is_wrong_ip:
            assign_btn = QPushButton("➕")
            assign_btn.setToolTip("Adicionar Colaborador")
            assign_btn.setFixedSize(40, 35)
            assign_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            assign_btn.clicked.connect(lambda checked, c=collector: self.add_assignment(c))
            action_layout.addWidget(assign_btn)

        # ═══════════════════════════════════════════════════════════
        # Botões ✏️ EDITAR e 🗑️ DELETAR - Aparecem se houver colaboradores
        # ═══════════════════════════════════════════════════════════
        if collector_ip in self.collaborators_data:
            current_list = self.collaborators_data[collector_ip].get('current', [])
            if isinstance(current_list, list) and current_list:
                # Botão de editar
                edit_btn = QPushButton("✏️")
                edit_btn.setToolTip("Editar Colaborador")
                edit_btn.setFixedSize(40, 35)
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f39c12;
                        color: white;
                        border: none;
                        padding: 8px;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #e67e22;
                    }
                """)
                collector_name = collector.get('NAME', 'N/A')
                edit_btn.clicked.connect(lambda checked, ip=collector_ip, name=collector_name: self.edit_assignment(ip, name))
                action_layout.addWidget(edit_btn)
                
                # Botão de exclusão
                delete_btn = QPushButton("🗑️")
                delete_btn.setToolTip("Excluir Colaborador")
                delete_btn.setFixedSize(40, 35)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        padding: 8px;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, ip=collector_ip: self.show_delete_dialog(ip))
                action_layout.addWidget(delete_btn)

        # ═══════════════════════════════════════════════════════════
        # Botão 📋 DETALHES - Só aparece se NÃO for IP errado
        # ═══════════════════════════════════════════════════════════
        if not is_wrong_ip:
            details_btn = QPushButton("📋")
            details_btn.setToolTip("Ver Detalhes")
            details_btn.setFixedSize(40, 35)
            details_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            details_btn.clicked.connect(lambda checked, ip=collector_ip: self.view_details(ip))
            action_layout.addWidget(details_btn)

        action_widget.setLayout(action_layout)
        self.table.setCellWidget(row, 6, action_widget)

    def _add_no_buttons(self, row):
        """🆕 Não adiciona botões (para linhas com IP incorreto ou vítimas)"""
        action_widget = QWidget()
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(4, 4, 4, 4)
        # Widget vazio, sem botões
        action_widget.setLayout(action_layout)
        self.table.setCellWidget(row, 6, action_widget)

    def collector_number_key(self, item):
        """Chave para ordenação numérica dos coletores"""
        name = item.get('NAME', '')
        try:
            match = re.search(r'Coletor\s*(\d+)', name, re.IGNORECASE)
            if match:
                return int(match.group(1))
        except:
            pass
        return 999

    def refresh_table(self):
        """Atualiza a tabela de atribuições - APENAS coletores com setor atribuído"""
        # SALVAR posição do scroll antes de atualizar
        scrollbar = self.table.verticalScrollBar()
        scroll_position = scrollbar.value()
        
        self.table.setRowCount(0)
        self.collaborators_data = DataManager.load_data()

        # 🆕 DEFINIR ALTURA PADRÃO DAS LINHAS - AUMENTADA
        self.table.verticalHeader().setDefaultSectionSize(50)  # 50 pixels

        assigned_count = 0
        total_collectors = 0
        total_collaborators = 0

        # Obter dados dos coletores do parent - FILTRAR apenas com setor != N/A
        if hasattr(self.parent_window, 'data'):
            collector_data_list = self.parent_window.data
            
            # FILTRAR: apenas coletores com setor atribuído (não N/A)
            filtered_collectors = [c for c in collector_data_list if c.get('SETOR') != 'N/A']
            
            # ORDENAR alfabeticamente/numericamente
            filtered_collectors = sorted(filtered_collectors, key=self.collector_number_key)
            
            total_collectors = len(filtered_collectors)
            
            # 🆕 CRIAR MAPA DE IPs USADOS INCORRETAMENTE
            # Mapeia IP -> Nome do coletor que está usando incorretamente
            incorrect_ip_usage = {}
            
            for collector in filtered_collectors:
                is_mismatch = self.collector_ip_mismatch(collector)
                if is_mismatch:
                    collector_ip = collector.get('IP ADDRESS', 'N/A')
                    collector_name = collector.get('NAME', 'N/A')
                    # Marcar que este IP está sendo usado incorretamente
                    incorrect_ip_usage[collector_ip] = collector_name

            # ═══════════════════════════════════════════════════════════════════
            # 🔧 PROCESSAR TODOS OS COLETORES
            # ═══════════════════════════════════════════════════════════════════
            for collector in filtered_collectors:
                collector_ip = collector.get('IP ADDRESS', 'N/A')
                collector_name = collector.get('NAME', 'N/A')
                collector_setor = collector.get('SETOR', 'N/A')

                # 🆕 VERIFICAR SE HÁ ALERTA DE IP (MISMATCH)
                is_alert = self.collector_ip_mismatch(collector)
                
                # 🆕 VERIFICAR SE ESTE COLETOR É A "VÍTIMA" (seu IP está sendo usado por outro)
                is_victim = False
                expected_ip_for_this = self.get_expected_ip(collector_name)
                if expected_ip_for_this and expected_ip_for_this in incorrect_ip_usage:
                    # Verifica se o coletor que está usando o IP não é ele mesmo
                    thief = incorrect_ip_usage[expected_ip_for_this]
                    if thief != collector_name:
                        is_victim = True

                # ═══════════════════════════════════════════════════════════
                # 🎯 NOVO: Se há mismatch, criar DUAS linhas
                # ═══════════════════════════════════════════════════════════
                if is_alert:
                    # Calcular IP correto
                    expected_ip = self.get_expected_ip(collector_name)
                    
                    # ───────────────────────────────────────────────────────
                    # LINHA 1: IP ERRADO (onde estão os colaboradores) - PISCANDO
                    # ───────────────────────────────────────────────────────
                    row_wrong = self.table.rowCount()
                    self.table.insertRow(row_wrong)
                    
                    # 🔧 BUSCAR DADOS DO COLABORADOR PARA MOSTRAR NO NOME
                    collaborator_display_wrong = ""
                    lookup_ip_for_name = expected_ip if expected_ip and expected_ip in self.collaborators_data else collector_ip
                    
                    if lookup_ip_for_name in self.collaborators_data:
                        current_list_for_name = self.collaborators_data[lookup_ip_for_name].get('current', [])
                        if not isinstance(current_list_for_name, list):
                            current_list_for_name = [current_list_for_name] if current_list_for_name else []
                        if current_list_for_name:
                            # Pegar nome do primeiro colaborador
                            first_collab = current_list_for_name[0]
                            if isinstance(first_collab, dict):
                                collaborator_display_wrong = f" - {first_collab.get('collaborator_name', '')}"
                    
                    # Nome com indicador de ERRO e nome do colaborador
                    name_item_wrong = QTableWidgetItem(f"⚠️ {collector_name}{collaborator_display_wrong} (IP INCORRETO)")
                    name_item_wrong.setData(Qt.UserRole, collector_setor)
                    name_item_wrong.setData(Qt.UserRole + 1, 'BLINK')  # Marcar para piscar
                    name_item_wrong.setForeground(QColor(139, 0, 0))  # Texto vermelho escuro
                    name_item_wrong.setFont(QFont('Segoe UI', 9, QFont.Bold))
                    self.table.setItem(row_wrong, 0, name_item_wrong)
                    
                    # IP errado
                    ip_item_wrong = QTableWidgetItem(f"❌ {collector_ip}")
                    ip_item_wrong.setForeground(QColor(139, 0, 0))
                    ip_item_wrong.setFont(QFont('Segoe UI', 9, QFont.Bold))
                    self.table.setItem(row_wrong, 1, ip_item_wrong)
                    
                    # 🔧 BUSCAR DADOS NO IP CORRETO (onde os colaboradores estão cadastrados)
                    # Tentar primeiro no expected_ip, depois no collector_ip
                    lookup_ip = expected_ip if expected_ip and expected_ip in self.collaborators_data else collector_ip
                    
                    if lookup_ip in self.collaborators_data:
                        current_list = self.collaborators_data[lookup_ip].get('current', [])
                        
                        if not isinstance(current_list, list):
                            current_list = [current_list] if current_list else []
                        
                        if current_list:
                            # Mostrar colaboradores encontrados
                            collab_names = []
                            shifts = []
                            times = []
                            
                            for c in current_list:
                                if isinstance(c, dict):
                                    collab_names.append(c.get('collaborator_name', 'N/A'))
                                    shifts.append(c.get('shift', 'N/A'))
                                    times.append(f"{c.get('start_time', 'N/A')}-{c.get('end_time', 'N/A')}")
                            
                            self.table.setItem(row_wrong, 2, QTableWidgetItem('\n'.join(collab_names)))
                            self.table.setItem(row_wrong, 3, QTableWidgetItem('\n'.join(shifts)))
                            self.table.setItem(row_wrong, 4, QTableWidgetItem('\n'.join(times)))
                            self.table.setItem(row_wrong, 5, QTableWidgetItem(str(len(current_list))))
                        else:
                            for col in range(2, 6):
                                self.table.setItem(row_wrong, col, QTableWidgetItem('-'))
                    else:
                        for col in range(2, 6):
                            self.table.setItem(row_wrong, col, QTableWidgetItem('-'))
                    
                    # Aplicar cor inicial (vermelho claro)
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row_wrong, col)
                        if item:
                            item.setBackground(QColor(255, 180, 180))
                        else:
                            placeholder = QTableWidgetItem()
                            placeholder.setBackground(QColor(255, 180, 180))
                            self.table.setItem(row_wrong, col, placeholder)
                    
                    # 🆕 NÃO ADICIONAR BOTÕES NA LINHA COM IP INCORRETO
                    self._add_no_buttons(row_wrong)
                    
                    # ───────────────────────────────────────────────────────
                    # LINHA 2: IP CORRETO (esperado) - Mostra o colaborador cadastrado
                    # ───────────────────────────────────────────────────────
                    if expected_ip:
                        row_correct = self.table.rowCount()
                        self.table.insertRow(row_correct)
                        
                        # 🔧 BUSCAR DADOS DO COLABORADOR PARA MOSTRAR NO NOME
                        collaborator_display = ""
                        lookup_ip_correct = expected_ip if expected_ip in self.collaborators_data else collector_ip
                        
                        if lookup_ip_correct in self.collaborators_data:
                            current_list_check = self.collaborators_data[lookup_ip_correct].get('current', [])
                            if not isinstance(current_list_check, list):
                                current_list_check = [current_list_check] if current_list_check else []
                            if current_list_check:
                                # Pegar nome do primeiro colaborador
                                first_collab = current_list_check[0]
                                if isinstance(first_collab, dict):
                                    collaborator_display = f" - {first_collab.get('collaborator_name', '')}"
                        
                        # Nome com indicador CORRETO e nome do colaborador
                        name_item_correct = QTableWidgetItem(f"✅ {collector_name}{collaborator_display} (IP CORRETO)")
                        name_item_correct.setData(Qt.UserRole, collector_setor)
                        name_item_correct.setForeground(QColor(0, 100, 0))  # Texto verde escuro
                        name_item_correct.setFont(QFont('Segoe UI', 9, QFont.Bold))
                        self.table.setItem(row_correct, 0, name_item_correct)
                        
                        # IP correto
                        ip_item_correct = QTableWidgetItem(f"✓ {expected_ip}")
                        ip_item_correct.setForeground(QColor(0, 100, 0))
                        ip_item_correct.setFont(QFont('Segoe UI', 9, QFont.Bold))
                        self.table.setItem(row_correct, 1, ip_item_correct)
                        
                        # 🔧 MOSTRAR OS DADOS DO COLABORADOR CADASTRADO NO IP CORRETO
                        if expected_ip in self.collaborators_data:
                            current_list_correct = self.collaborators_data[expected_ip].get('current', [])
                            
                            if not isinstance(current_list_correct, list):
                                current_list_correct = [current_list_correct] if current_list_correct else []
                            
                            if current_list_correct:
                                assigned_count += 1
                                total_collaborators += len(current_list_correct)
                                
                                collab_names_correct = []
                                shifts_correct = []
                                times_correct = []
                                
                                for c in current_list_correct:
                                    if isinstance(c, dict):
                                        collab_names_correct.append(c.get('collaborator_name', 'N/A'))
                                        shifts_correct.append(c.get('shift', 'N/A'))
                                        times_correct.append(f"{c.get('start_time', 'N/A')}-{c.get('end_time', 'N/A')}")
                                
                                self.table.setItem(row_correct, 2, QTableWidgetItem('\n'.join(collab_names_correct)))
                                self.table.setItem(row_correct, 3, QTableWidgetItem('\n'.join(shifts_correct)))
                                self.table.setItem(row_correct, 4, QTableWidgetItem('\n'.join(times_correct)))
                                self.table.setItem(row_correct, 5, QTableWidgetItem(str(len(current_list_correct))))
                            else:
                                for col in range(2, 6):
                                    self.table.setItem(row_correct, col, QTableWidgetItem('-'))
                        else:
                            # IP correto não tem dados
                            for col in range(2, 6):
                                self.table.setItem(row_correct, col, QTableWidgetItem('-'))
                        
                        # Aplicar cor verde claro
                        for col in range(self.table.columnCount()):
                            item = self.table.item(row_correct, col)
                            if item:
                                item.setBackground(QColor(200, 255, 200))
                            else:
                                placeholder = QTableWidgetItem()
                                placeholder.setBackground(QColor(200, 255, 200))
                                self.table.setItem(row_correct, col, placeholder)
                        
                        # 🆕 NÃO ADICIONAR BOTÕES NA LINHA COM IP CORRETO
                        self._add_no_buttons(row_correct)

                # ═══════════════════════════════════════════════════════════
                # 🆕 COLETOR "VÍTIMA" - Seu IP está sendo usado por outro
                # ═══════════════════════════════════════════════════════════
                elif is_victim:
                    row = self.table.rowCount()
                    self.table.insertRow(row)

                    # Nome normal (sem indicador)
                    name_item = QTableWidgetItem(collector_name)
                    name_item.setData(Qt.UserRole, collector_setor)
                    name_item.setData(Qt.UserRole + 1, 'BLINK')  # 🆕 MARCAR PARA PISCAR
                    self.table.setItem(row, 0, name_item)
                    
                    ip_item = QTableWidgetItem(collector_ip)
                    self.table.setItem(row, 1, ip_item)

                    # Verificar se há atribuições
                    if collector_ip in self.collaborators_data:
                        current_list = self.collaborators_data[collector_ip].get('current', [])
                        
                        if not isinstance(current_list, list):
                            if current_list:
                                current_list = [current_list]
                            else:
                                current_list = []
                            self.collaborators_data[collector_ip]['current'] = current_list
                            self.save_data()
                        
                        if current_list:
                            assigned_count += 1
                            total_collaborators += len(current_list)
                            
                            collab_names = []
                            shifts = []
                            times = []
                            
                            for c in current_list:
                                if isinstance(c, dict):
                                    collab_names.append(c.get('collaborator_name', 'N/A'))
                                    shifts.append(c.get('shift', 'N/A'))
                                    times.append(f"{c.get('start_time', 'N/A')}-{c.get('end_time', 'N/A')}")
                            
                            self.table.setItem(row, 2, QTableWidgetItem('\n'.join(collab_names)))
                            self.table.setItem(row, 3, QTableWidgetItem('\n'.join(shifts)))
                            self.table.setItem(row, 4, QTableWidgetItem('\n'.join(times)))
                            self.table.setItem(row, 5, QTableWidgetItem(str(len(current_list))))
                        else:
                            for col in range(2, 6):
                                self.table.setItem(row, col, QTableWidgetItem('-'))
                    else:
                        for col in range(2, 6):
                            self.table.setItem(row, col, QTableWidgetItem('-'))

                    # 🆕 APLICAR COR VERMELHA CLARA INICIAL (para piscar)
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(QColor(255, 180, 180))
                        else:
                            placeholder = QTableWidgetItem()
                            placeholder.setBackground(QColor(255, 180, 180))
                            self.table.setItem(row, col, placeholder)

                    # 🆕 NÃO ADICIONAR BOTÕES
                    self._add_no_buttons(row)
                
                # ═══════════════════════════════════════════════════════════
                # 🎯 Sem mismatch e não é vítima: criar UMA linha normal
                # ═══════════════════════════════════════════════════════════
                else:
                    row = self.table.rowCount()
                    self.table.insertRow(row)

                    # Informações do coletor
                    name_item = QTableWidgetItem(collector_name)
                    name_item.setData(Qt.UserRole, collector_setor)
                    self.table.setItem(row, 0, name_item)
                    
                    ip_item = QTableWidgetItem(collector_ip)
                    self.table.setItem(row, 1, ip_item)

                    # Verificar se há atribuições
                    if collector_ip in self.collaborators_data:
                        current_list = self.collaborators_data[collector_ip].get('current', [])
                        
                        # GARANTIR que current_list é uma lista
                        if not isinstance(current_list, list):
                            # Migrar formato antigo
                            if current_list:  # Se não é None/vazio
                                current_list = [current_list]
                            else:
                                current_list = []
                            self.collaborators_data[collector_ip]['current'] = current_list
                            self.save_data()
                        
                        if current_list:
                            assigned_count += 1
                            total_collaborators += len(current_list)
                            
                            # Montar string de colaboradores
                            collab_names = []
                            shifts = []
                            times = []
                            
                            for c in current_list:
                                # VERIFICAR se c é um dict
                                if isinstance(c, dict):
                                    collab_names.append(c.get('collaborator_name', 'N/A'))
                                    shifts.append(c.get('shift', 'N/A'))
                                    times.append(f"{c.get('start_time', 'N/A')}-{c.get('end_time', 'N/A')}")
                            
                            self.table.setItem(row, 2, QTableWidgetItem('\n'.join(collab_names)))
                            self.table.setItem(row, 3, QTableWidgetItem('\n'.join(shifts)))
                            self.table.setItem(row, 4, QTableWidgetItem('\n'.join(times)))
                            self.table.setItem(row, 5, QTableWidgetItem(str(len(current_list))))

                            # Colorir linha atribuída (VERDE)
                            for col in range(6):
                                item = self.table.item(row, col)
                                if item:
                                    item.setBackground(QColor(200, 255, 200))  # Verde claro
                        else:
                            # Sem atribuição atual
                            for col in range(2, 6):
                                self.table.setItem(row, col, QTableWidgetItem('-'))
                    else:
                        # Nunca foi atribuído
                        for col in range(2, 6):
                            self.table.setItem(row, col, QTableWidgetItem('-'))

                    # Ajustar altura da linha se houver múltiplos colaboradores
                    if collector_ip in self.collaborators_data:
                        current_list = self.collaborators_data[collector_ip].get('current', [])
                        if isinstance(current_list, list) and len(current_list) > 1:
                            self.table.setRowHeight(row, 50 * len(current_list))

                    # Adicionar botões de ação
                    self._add_action_buttons(row, collector, collector_ip, is_wrong_ip=False)

        # Atualizar estatísticas
        unassigned = total_collectors - assigned_count
        self.stats_label.setText(
            f"📊 Total de Coletores (com setor): {total_collectors} | "
            f"✅ Coletores Atribuídos: {assigned_count} | "
            f"👥 Total de Colaboradores: {total_collaborators} | "
            f"⚠️ Sem Atribuição: {unassigned}"
        )
        
        # Aplicar filtros após popular tabela
        self.apply_filters()
        
        # RESTAURAR posição do scroll após atualizar tudo
        scrollbar.setValue(scroll_position)

    def apply_filters(self):
        """Aplica filtros na tabela"""
        search_text = self.filter_input.text().lower()
        setor_filter = self.setor_filter.currentText()
        turno_filter = self.turno_filter.currentText()

        for row in range(self.table.rowCount()):
            show_row = False
            
            # Filtro de texto (nome do coletor ou colaborador)
            for col in range(3):  # Coletor, IP, Colaboradores
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            
            # Se não passou no filtro de texto, esconde
            if not show_row and search_text:
                self.table.setRowHidden(row, True)
                continue
            
            # Filtro de setor
            if setor_filter != 'Todos':
                name_item = self.table.item(row, 0)
                if name_item:
                    collector_setor = name_item.data(Qt.UserRole)
                    if collector_setor != setor_filter:
                        self.table.setRowHidden(row, True)
                        continue
            
            # Filtro de turno
            if turno_filter != 'Todos':
                turnos_item = self.table.item(row, 3)  # Coluna de Turnos
                if turnos_item:
                    turnos_text = turnos_item.text()
                    # Verifica se o turno filtrado está presente na lista de turnos
                    if turno_filter not in turnos_text:
                        self.table.setRowHidden(row, True)
                        continue
                else:
                    # Se não tem item de turno, esconde quando filtro está ativo
                    self.table.setRowHidden(row, True)
                    continue
            
            # Se passou em todos os filtros, mostra
            self.table.setRowHidden(row, False)

    def convert_filter_to_uppercase(self, text):
        """Converte texto do filtro para maiúsculas automaticamente e aplica filtros"""
        # Salvar posição do cursor
        cursor_position = self.filter_input.cursorPosition()
        # Converter para maiúsculas
        self.filter_input.blockSignals(True)  # Evitar loop infinito
        self.filter_input.setText(text.upper())
        self.filter_input.setCursorPosition(cursor_position)
        self.filter_input.blockSignals(False)
        # Aplicar filtros após conversão
        self.apply_filters()

    def clear_filters(self):
        """Limpa todos os filtros"""
        self.setor_filter.setCurrentText('Todos')
        self.turno_filter.setCurrentText('Todos')
        self.filter_input.clear()