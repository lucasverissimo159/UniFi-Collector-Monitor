"""
Aba de Configurações Completa v3.0
- Configurações UniFi
- Configuração de IP Range (com preview do modo)
- Estatísticas de bloqueio
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import json
import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Imports dos módulos
try:
    from app.data.auth_manager import AuthManager
    from app.data.ip_blocker import IPBlocker
    from app.data.ip_mapping import IPMapping
    from app.gui.login_dialog import LoginDialog
    from app.gui.password_reset_dialog import PasswordResetDialog
    from app.gui.first_access_dialog import FirstAccessDialog
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    IPMapping = None

from app.config import WINDOW_ICON_PATH

CONFIG_FILE = "unifi_config.json"


class SettingsTab(QWidget):
    """Aba de Configurações com autenticação e IP Range"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.authenticated = False
        
        # Inicializar IPBlocker
        if AUTH_AVAILABLE:
            self.blocker = IPBlocker()
        
        # Verificar primeiro acesso
        if AUTH_AVAILABLE and AuthManager.is_first_access():
            self.show_first_access_dialog()
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa interface baseada no estado de autenticação"""
        # Limpar layout existente
        if self.layout() is not None:
            QWidget().setLayout(self.layout())
        
        # Criar novo layout
        layout = QVBoxLayout()
        
        if not AUTH_AVAILABLE or not self.authenticated:
            self.show_login_screen(layout)
        else:
            self.show_settings_screen(layout)
        
        self.setLayout(layout)
    
    def show_login_screen(self, layout):
        """Tela de login"""
        layout.setSpacing(30)
        
        title = QLabel("🔒 Área Restrita - Configurações Administrativas")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; padding: 20px;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        login_btn = QPushButton("🔐 Fazer Login para Acessar Configurações")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 15px 40px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-width: 350px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        login_btn.clicked.connect(self.do_login)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(login_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        if AUTH_AVAILABLE and AuthManager.has_security_question():
            forgot_link = QLabel('<a href="#" style="color: #3498db; font-size: 12px;">Esqueceu a senha?</a>')
            forgot_link.setAlignment(Qt.AlignCenter)
            forgot_link.linkActivated.connect(self.reset_password)
            layout.addWidget(forgot_link)
        
        layout.addStretch()
        
        info = QLabel(
            "ℹ️ Credenciais padrão (primeiro acesso):\n"
            "Usuário: admin | Senha: admin123"
        )
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 11px;
                padding: 15px;
                background-color: #ecf0f1;
                border-radius: 6px;
            }
        """)
        layout.addWidget(info)
    
    def show_settings_screen(self, layout):
        """Tela de configurações completa com tabs"""
        layout.setSpacing(20)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        title = QLabel("⚙️ Configurações do Sistema")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        logout_btn = QPushButton("🚪 Sair")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)
        layout.addLayout(header_layout)
        
        # Tabs de configuração
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
        """)
        
        # Tab 1: Configurações UniFi
        unifi_tab = self.create_unifi_tab()
        tabs.addTab(unifi_tab, "🌐 UniFi Controller")
        
        # Tab 2: Configuração de IP Range
        iprange_tab = self.create_iprange_tab()
        tabs.addTab(iprange_tab, "📡 Range de IPs")
        
        # Tab 3: Estatísticas de Bloqueio (opcional)
        if AUTH_AVAILABLE:
            block_tab = self.create_blocking_tab()
            tabs.addTab(block_tab, "🚫 Bloqueios")
        
        layout.addWidget(tabs)
    
    # ========== TAB 1: CONFIGURAÇÕES UNIFI ==========
    
    def create_unifi_tab(self):
        """Cria tab de configurações UniFi"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Grupo de configurações
        config_group = QGroupBox("Credenciais do UniFi Controller")
        config_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
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
            }
        """)
        
        config_layout = QVBoxLayout()
        
        # Host
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("Host:"))
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Ex: https://203.0.113.1:8443")
        self.host_input.setText(self.load_unifi_config()[0])
        self.host_input.setStyleSheet("padding: 8px; border: 1px solid #bdc3c7; border-radius: 5px;")
        host_layout.addWidget(self.host_input)
        config_layout.addLayout(host_layout)
        
        # Username
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("Usuário:"))
        self.username_input = QLineEdit()
        self.username_input.setText(self.load_unifi_config()[1])
        self.username_input.setStyleSheet("padding: 8px; border: 1px solid #bdc3c7; border-radius: 5px;")
        user_layout.addWidget(self.username_input)
        config_layout.addLayout(user_layout)
        
        # Password
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Senha:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText(self.load_unifi_config()[2])
        self.password_input.setStyleSheet("padding: 8px; border: 1px solid #bdc3c7; border-radius: 5px;")
        pass_layout.addWidget(self.password_input)
        config_layout.addLayout(pass_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Botões
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Salvar")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 25px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        save_btn.clicked.connect(self.save_unifi_settings)
        button_layout.addWidget(save_btn)
        
        test_btn = QPushButton("🔌 Testar Conexão")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 25px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        test_btn.clicked.connect(self.test_unifi_connection)
        button_layout.addWidget(test_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Status
        self.unifi_status_label = QLabel("📊 Pronto para configurar")
        self.unifi_status_label.setStyleSheet("""
            QLabel {
                background-color: #95a5a6;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.unifi_status_label)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    # ========== TAB 2: CONFIGURAÇÃO DE IP RANGE ==========
    
    def create_iprange_tab(self):
        """Cria tab de configuração de IP Range"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Título
        title = QLabel("📡 Configuração de Range de IPs dos Coletores")
        title.setFont(QFont('Segoe UI', 13, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Grupo de configuração
        config_group = QGroupBox("Faixa de IPs")
        config_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e67e22;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #fef5e7;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
            }
        """)
        
        config_layout = QVBoxLayout()
        
        # Carregar configuração atual
        if IPMapping:
            current_config = IPMapping.load_config()
        else:
            current_config = ("203.0.113", 100, 199)
        
        # Base IP
        base_layout = QHBoxLayout()
        base_layout.addWidget(QLabel("Base do IP:"))
        self.base_ip_input = QLineEdit(current_config[0])
        self.base_ip_input.setPlaceholderText("Ex: 203.0.113")
        self.base_ip_input.setStyleSheet("padding: 8px; border: 1px solid #bdc3c7; border-radius: 5px;")
        self.base_ip_input.textChanged.connect(self.update_iprange_preview)
        base_layout.addWidget(self.base_ip_input)
        config_layout.addLayout(base_layout)
        
        # Range Start/End
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("Range:"))
        self.start_ip_input = QSpinBox()
        self.start_ip_input.setRange(1, 254)
        self.start_ip_input.setValue(current_config[1])
        self.start_ip_input.setStyleSheet("padding: 8px;")
        self.start_ip_input.valueChanged.connect(self.update_iprange_preview)
        range_layout.addWidget(self.start_ip_input)
        
        range_layout.addWidget(QLabel("até"))
        
        self.end_ip_input = QSpinBox()
        self.end_ip_input.setRange(1, 254)
        self.end_ip_input.setValue(current_config[2])
        self.end_ip_input.setStyleSheet("padding: 8px;")
        self.end_ip_input.valueChanged.connect(self.update_iprange_preview)
        range_layout.addWidget(self.end_ip_input)
        
        range_layout.addStretch()
        config_layout.addLayout(range_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Preview do modo
        self.iprange_preview = QTextEdit()
        self.iprange_preview.setReadOnly(True)
        self.iprange_preview.setMaximumHeight(200)
        self.iprange_preview.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
                font-family: 'Courier New';
                font-size: 11px;
            }
        """)
        layout.addWidget(self.iprange_preview)
        
        # Atualizar preview inicial
        self.update_iprange_preview()
        
        # Botão salvar
        save_btn = QPushButton("💾 Salvar Configuração de IP Range")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                padding: 12px 30px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        save_btn.clicked.connect(self.save_iprange_config)
        layout.addWidget(save_btn)
        
        # Status
        self.iprange_status_label = QLabel("ℹ️ Configure o range e clique em Salvar")
        self.iprange_status_label.setStyleSheet("""
            QLabel {
                background-color: #95a5a6;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.iprange_status_label)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def update_iprange_preview(self):
        """Atualiza preview do modo de IP Range"""
        if not IPMapping:
            self.iprange_preview.setText("❌ Módulo ip_mapping não disponível")
            return
        
        try:
            base_ip = self.base_ip_input.text().strip()
            start_ip = self.start_ip_input.value()
            end_ip = self.end_ip_input.value()
            
            # Criar mapper temporário
            mapper = IPMapping(base_ip, start_ip, end_ip)
            info = mapper.get_config_info()
            
            # Montar preview
            preview_text = f"""
╔══════════════════════════════════════════════════════════════╗
║  PREVIEW DO MAPEAMENTO IP/COLETOR                            ║
╚══════════════════════════════════════════════════════════════╝

{info['description']}

══════════════════════════════════════════════════════════════

📊 RESUMO:
   Total de IPs: {info['total_ips']}
   Total de Coletores: {info['total_collectors']}
   
   {info['first_collector']}
   {info['last_collector']}

══════════════════════════════════════════════════════════════

📝 EXEMPLOS:
"""
            
            # Adicionar alguns exemplos
            examples = [0, 5, 15, 25, 50, 58, 99]
            for num in examples:
                expected = mapper.get_expected_ip(num)
                if expected:
                    preview_text += f"   Coletor {num:02d} → {expected}\n"
            
            self.iprange_preview.setText(preview_text)
            
        except Exception as e:
            self.iprange_preview.setText(f"❌ Erro ao gerar preview: {str(e)}")
    
    def save_iprange_config(self):
        """Salva configuração de IP Range"""
        if not IPMapping:
            QMessageBox.warning(self, "Erro", "Módulo ip_mapping não disponível.")
            return
        
        try:
            base_ip = self.base_ip_input.text().strip()
            start_ip = self.start_ip_input.value()
            end_ip = self.end_ip_input.value()
            
            # Validações
            if not base_ip:
                QMessageBox.warning(self, "Erro", "Digite o Base IP.")
                return
            
            if start_ip >= end_ip:
                QMessageBox.warning(self, "Erro", "O IP inicial deve ser menor que o final.")
                return
            
            # Salvar
            if IPMapping.save_config(base_ip, start_ip, end_ip):
                self.iprange_status_label.setText("✅ Configuração salva com sucesso!")
                self.iprange_status_label.setStyleSheet("""
                    QLabel {
                        background-color: #27ae60;
                        color: white;
                        padding: 12px;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                """)
                
                QMessageBox.information(
                    self, "Sucesso",
                    "✅ Configuração de IP Range salva!\n\n"
                    "O sistema agora usará o novo range para:\n"
                    "• Escanear IPs livres\n"
                    "• Verificar IPs incorretos\n"
                    "• Calcular IPs esperados"
                )
                
                # Forçar nova coleta
                if self.parent_window:
                    self.parent_window.start_collection()
            else:
                raise Exception("Falha ao salvar arquivo")
                
        except Exception as e:
            self.iprange_status_label.setText("❌ Erro ao salvar")
            self.iprange_status_label.setStyleSheet("""
                QLabel {
                    background-color: #e74c3c;
                    color: white;
                    padding: 12px;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)
            QMessageBox.warning(self, "Erro", f"Erro ao salvar:\n{str(e)}")
    
    # ========== TAB 3: ESTATÍSTICAS DE BLOQUEIO ==========
    
    def create_blocking_tab(self):
        """Cria tab de estatísticas de bloqueio"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        title = QLabel("🚫 Sistema de Bloqueio de IPs Incorretos")
        title.setFont(QFont('Segoe UI', 13, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Estatísticas
        stats_group = QGroupBox("📊 Estatísticas")
        stats_layout = QVBoxLayout()
        
        self.block_stats_label = QLabel("Carregando...")
        self.block_stats_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        stats_layout.addWidget(self.block_stats_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Botão atualizar
        refresh_btn = QPushButton("🔄 Atualizar Estatísticas")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        refresh_btn.clicked.connect(self.refresh_block_stats)
        layout.addWidget(refresh_btn)
        
        # Atualizar stats inicial
        self.refresh_block_stats()
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def refresh_block_stats(self):
        """Atualiza estatísticas de bloqueio - RECARREGA automaticamente do arquivo"""
        if not AUTH_AVAILABLE:
            return
        
        # Verificar se o label existe (só existe após login e criação da aba)
        if not hasattr(self, 'block_stats_label'):
            return
        
        try:
            # IMPORTANTE: Recarregar dados do arquivo antes de exibir
            # Isso garante que sempre mostramos os dados mais recentes
            # mesmo que sejam atualizados pelo worker em background
            self.blocker.blocks_data = self.blocker.load_blocks()
            
            stats = self.blocker.get_statistics()
            
            text = f"""
📊 ESTATÍSTICAS DE BLOQUEIO (Atualização Automática)

Total de Bloqueios: {stats['total']}
   └─ Temporários (1-4 tentativas): {stats['temporary']}
   └─ Definitivos (5+ tentativas): {stats['definitive']}

🔍 DETALHES:
"""
            
            if stats['blocks']:
                for mac, info in sorted(stats['blocks'].items(), key=lambda x: x[1]['numero']):
                    status = "🔴 DEFINITIVO" if info.get('bloqueio_definitivo') else "🟡 TEMPORÁRIO"
                    text += f"\n   {status} - {info['name']}"
                    text += f"\n      Tentativas: {info['tentativas']}"
                    text += f"\n      Última atualização: {info.get('last_update', 'N/A')}\n"
            else:
                text += "\n   ✅ Nenhum bloqueio ativo"
            
            self.block_stats_label.setText(text)
            
        except AttributeError as e:
            # Label ainda não foi criado (usuário não fez login)
            pass
        except Exception as e:
            # Outros erros - tentar mostrar no label se existir
            if hasattr(self, 'block_stats_label'):
                self.block_stats_label.setText(f"❌ Erro ao carregar: {str(e)}")
    
    # ========== AUTENTICAÇÃO ==========
    
    def show_first_access_dialog(self):
        """Dialog de primeiro acesso"""
        dialog = FirstAccessDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_pass, question, answer = dialog.get_data()
            AuthManager.change_password(new_pass)
            if AuthManager.setup_security_question(question, answer):
                QMessageBox.information(self, "Sucesso", "✅ Configuração inicial concluída!")
    
    def do_login(self):
        """Login"""
        if not AUTH_AVAILABLE:
            QMessageBox.warning(self, "Erro", "Sistema de autenticação indisponível.")
            return
        
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            username, password = dialog.get_credentials()
            
            if AuthManager.verify_login(username, password):
                self.authenticated = True
                self.init_ui()
                QMessageBox.information(self, "Sucesso", "✅ Login realizado!")
            else:
                QMessageBox.warning(self, "Erro", "❌ Credenciais incorretas.")
    
    def reset_password(self):
        """Recuperar senha"""
        if not AUTH_AVAILABLE:
            return
        
        question = AuthManager.get_security_question()
        dialog = PasswordResetDialog(question, self)
        
        if dialog.exec_() == QDialog.Accepted:
            answer, new_pass = dialog.get_data()
            
            if AuthManager.reset_password_with_security(answer, new_pass):
                QMessageBox.information(self, "Sucesso", "✅ Senha redefinida!")
            else:
                QMessageBox.warning(self, "Erro", "❌ Resposta incorreta.")
    
    def logout(self):
        """Logout"""
        self.authenticated = False
        self.init_ui()
    
    # ========== CONFIGURAÇÕES UNIFI ==========
    
    def load_unifi_config(self):
        """Carrega config UniFi"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return (
                        config.get("UNIFI_HOST", "https://192.0.2.1:8443"),
                        config.get("UNIFI_USERNAME", "usuario_exemplo"),
                        config.get("UNIFI_PASSWORD", "senha_exemplo")
                    )
            except:
                pass
        from app.config import UNIFI_HOST, UNIFI_USERNAME, UNIFI_PASSWORD
        return UNIFI_HOST, UNIFI_USERNAME, UNIFI_PASSWORD
    
    def save_unifi_settings(self):
        """Salva config UniFi"""
        host = self.host_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not all([host, username, password]):
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return
        
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({
                    "UNIFI_HOST": host,
                    "UNIFI_USERNAME": username,
                    "UNIFI_PASSWORD": password
                }, f, indent=4)
            
            import app.config as config_module
            config_module.UNIFI_HOST = host
            config_module.UNIFI_USERNAME = username
            config_module.UNIFI_PASSWORD = password
            
            self.unifi_status_label.setText("✅ Salvo!")
            self.unifi_status_label.setStyleSheet("""
                QLabel { background-color: #27ae60; color: white;
                padding: 12px; border-radius: 5px; font-weight: bold; }
            """)
            
            if self.parent_window:
                self.parent_window.start_collection()
            
            QMessageBox.information(self, "Sucesso", "✅ Configurações salvas!")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro: {str(e)}")
    
    def test_unifi_connection(self):
        """Testa conexão UniFi"""
        host = self.host_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not all([host, username, password]):
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return
        
        self.unifi_status_label.setText("🔄 Testando...")
        self.unifi_status_label.setStyleSheet("""
            QLabel { background-color: #3498db; color: white;
            padding: 12px; border-radius: 5px; font-weight: bold; }
        """)
        QApplication.processEvents()
        
        session = requests.Session()
        session.verify = False
        
        try:
            response = session.post(
                f"{host}/api/login",
                json={"username": username, "password": password, "remember": True},
                timeout=10
            )
            
            if response.status_code == 200:
                self.unifi_status_label.setText("✅ Conexão bem-sucedida!")
                self.unifi_status_label.setStyleSheet("""
                    QLabel { background-color: #27ae60; color: white;
                    padding: 12px; border-radius: 5px; font-weight: bold; }
                """)
                QMessageBox.information(self, "Sucesso", "✅ Conexão OK!")
            else:
                raise Exception(f"Código {response.status_code}")
        except Exception as e:
            self.unifi_status_label.setText("❌ Falha na conexão")
            self.unifi_status_label.setStyleSheet("""
                QLabel { background-color: #e74c3c; color: white;
                padding: 12px; border-radius: 5px; font-weight: bold; }
            """)
            QMessageBox.warning(self, "Erro", f"Erro: {str(e)}")