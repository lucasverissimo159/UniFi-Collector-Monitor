"""
Dialog de Login para Acesso às Configurações
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class LoginDialog(QDialog):
    """Dialog de autenticação administrativa"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Autenticação Administrativa")
        self.setFixedSize(450, 250)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Título
        title = QLabel("🔒 Acesso Restrito")
        title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(title)
        
        # Info
        info = QLabel("Digite as credenciais administrativas para acessar as configurações:")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(info)
        
        # Usuário
        user_layout = QHBoxLayout()
        user_label = QLabel("👤 Usuário:")
        user_label.setFixedWidth(80)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("admin")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.username_input)
        layout.addLayout(user_layout)
        
        # Senha
        pass_layout = QHBoxLayout()
        pass_label = QLabel("🔑 Senha:")
        pass_label.setFixedWidth(80)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Digite a senha")
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.password_input.returnPressed.connect(self.accept)
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.password_input)
        layout.addLayout(pass_layout)
        
        # Botões
        button_layout = QHBoxLayout()
        
        login_btn = QPushButton("✅ Entrar")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 25px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        login_btn.clicked.connect(self.accept)
        button_layout.addWidget(login_btn)
        
        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 25px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.username_input.setFocus()
    
    def get_credentials(self):
        """Retorna credenciais digitadas"""
        return (
            self.username_input.text().strip(),
            self.password_input.text()
        )