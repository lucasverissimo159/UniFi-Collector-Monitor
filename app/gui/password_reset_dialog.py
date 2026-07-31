"""
Dialog de Recuperação de Senha via Pergunta de Segurança
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class PasswordResetDialog(QDialog):
    """Dialog para recuperação de senha"""
    
    def __init__(self, security_question, parent=None):
        super().__init__(parent)
        self.security_question = security_question
        self.setWindowTitle("🔓 Recuperação de Senha")
        self.setFixedSize(500, 350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Título
        title = QLabel("🔓 Recuperar Senha")
        title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(title)
        
        # Instrução
        info = QLabel("Responda à pergunta de segurança para redefinir sua senha:")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(info)
        
        # Pergunta de segurança
        question_label = QLabel(f"❓ {self.security_question}")
        question_label.setWordWrap(True)
        question_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 12px;
                border-radius: 6px;
                color: #2c3e50;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        layout.addWidget(question_label)
        
        # Resposta
        answer_layout = QVBoxLayout()
        answer_label = QLabel("💭 Sua resposta:")
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Digite a resposta")
        self.answer_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        answer_layout.addWidget(answer_label)
        answer_layout.addWidget(self.answer_input)
        layout.addLayout(answer_layout)
        
        # Nova senha
        newpass_layout = QVBoxLayout()
        newpass_label = QLabel("🔑 Nova senha:")
        self.newpass_input = QLineEdit()
        self.newpass_input.setEchoMode(QLineEdit.Password)
        self.newpass_input.setPlaceholderText("Digite a nova senha")
        self.newpass_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        newpass_layout.addWidget(newpass_label)
        newpass_layout.addWidget(self.newpass_input)
        layout.addLayout(newpass_layout)
        
        # Confirmar senha
        confirm_layout = QVBoxLayout()
        confirm_label = QLabel("🔑 Confirmar senha:")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setPlaceholderText("Digite novamente")
        self.confirm_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.confirm_input.returnPressed.connect(self.validate_and_accept)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)
        layout.addLayout(confirm_layout)
        
        # Botões
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("✅ Redefinir Senha")
        reset_btn.setStyleSheet("""
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
        reset_btn.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(reset_btn)
        
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
        self.answer_input.setFocus()
    
    def validate_and_accept(self):
        """Valida dados antes de aceitar"""
        answer = self.answer_input.text().strip()
        new_pass = self.newpass_input.text()
        confirm = self.confirm_input.text()
        
        if not answer:
            QMessageBox.warning(self, "Atenção", "Digite a resposta da pergunta de segurança.")
            return
        
        if not new_pass:
            QMessageBox.warning(self, "Atenção", "Digite a nova senha.")
            return
        
        if len(new_pass) < 6:
            QMessageBox.warning(self, "Senha Fraca", "A senha deve ter pelo menos 6 caracteres.")
            return
        
        if new_pass != confirm:
            QMessageBox.warning(self, "Erro", "As senhas não coincidem.")
            return
        
        self.accept()
    
    def get_data(self):
        """Retorna resposta e nova senha"""
        return (
            self.answer_input.text().strip(),
            self.newpass_input.text()
        )