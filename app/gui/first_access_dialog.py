"""
Dialog de Primeiro Acesso
Configura senha e pergunta de segurança
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class FirstAccessDialog(QDialog):
    """Dialog para configuração inicial (primeiro acesso)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎯 Primeiro Acesso - Configuração Inicial")
        self.setFixedSize(600, 550)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Título
        title = QLabel("🎯 Bem-vindo! Configuração Inicial")
        title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(title)
        
        # Aviso
        warning = QLabel(
            "⚠️ Este é o primeiro acesso ao sistema.\n"
            "Por segurança, você DEVE trocar a senha padrão e configurar uma pergunta de segurança."
        )
        warning.setWordWrap(True)
        warning.setAlignment(Qt.AlignCenter)
        warning.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                color: #856404;
                padding: 12px;
                border-radius: 6px;
                border: 2px solid #ffeaa7;
                font-size: 11px;
            }
        """)
        layout.addWidget(warning)
        
        # Senha padrão (info)
        default_info = QLabel(
            "📌 Credenciais padrão:\n"
            "   Usuário: admin\n"
            "   Senha: admin123"
        )
        default_info.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
                color: #2c3e50;
                font-size: 11px;
                font-family: 'Courier New';
            }
        """)
        layout.addWidget(default_info)
        
        # Nova senha
        newpass_layout = QVBoxLayout()
        newpass_label = QLabel("🔑 Nova senha (mínimo 6 caracteres):")
        newpass_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.newpass_input = QLineEdit()
        self.newpass_input.setEchoMode(QLineEdit.Password)
        self.newpass_input.setPlaceholderText("Digite sua nova senha")
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
        confirm_label = QLabel("🔑 Confirmar nova senha:")
        confirm_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
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
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)
        layout.addLayout(confirm_layout)
        
        # Separador
        separator = QLabel("─" * 80)
        separator.setAlignment(Qt.AlignCenter)
        separator.setStyleSheet("color: #bdc3c7;")
        layout.addWidget(separator)
        
        # Pergunta de segurança
        question_layout = QVBoxLayout()
        question_label = QLabel("❓ Pergunta de segurança (para recuperação de senha):")
        question_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.question_combo = QComboBox()
        self.question_combo.addItems([
            "Qual o nome da sua mãe?",
            "Qual o nome do seu primeiro animal de estimação?",
            "Qual sua cidade natal?",
            "Qual o nome da sua escola primária?",
            "Qual seu time de futebol favorito?",
            "Qual o nome do meio do seu pai?",
            "Em que ano você nasceu?",
            "Qual sua cor favorita?",
            "Qual o modelo do seu primeiro carro?",
            "Qual o nome do seu melhor amigo de infância?"
        ])
        self.question_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        question_layout.addWidget(question_label)
        question_layout.addWidget(self.question_combo)
        layout.addLayout(question_layout)
        
        # Resposta
        answer_layout = QVBoxLayout()
        answer_label = QLabel("💭 Resposta:")
        answer_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Digite a resposta (será criptografada)")
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
        self.answer_input.returnPressed.connect(self.validate_and_accept)
        answer_layout.addWidget(answer_label)
        answer_layout.addWidget(self.answer_input)
        layout.addLayout(answer_layout)
        
        # Dica
        hint = QLabel("💡 A resposta é case-insensitive e não diferencia maiúsculas/minúsculas")
        hint.setStyleSheet("color: #7f8c8d; font-size: 10px; font-style: italic;")
        layout.addWidget(hint)
        
        # Botão
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("✅ Configurar e Acessar")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 30px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        save_btn.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.newpass_input.setFocus()
    
    def validate_and_accept(self):
        """Valida dados antes de aceitar"""
        new_pass = self.newpass_input.text()
        confirm = self.confirm_input.text()
        question = self.question_combo.currentText()
        answer = self.answer_input.text().strip()
        
        if not new_pass:
            QMessageBox.warning(self, "Atenção", "Digite a nova senha.")
            return
        
        if len(new_pass) < 6:
            QMessageBox.warning(self, "Senha Fraca", "A senha deve ter pelo menos 6 caracteres.")
            return
        
        if new_pass != confirm:
            QMessageBox.warning(self, "Erro", "As senhas não coincidem.")
            return
        
        if not answer:
            QMessageBox.warning(self, "Atenção", "Digite a resposta da pergunta de segurança.")
            return
        
        self.accept()
    
    def get_data(self):
        """Retorna nova senha, pergunta e resposta"""
        return (
            self.newpass_input.text(),
            self.question_combo.currentText(),
            self.answer_input.text().strip()
        )