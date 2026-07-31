#!/usr/bin/env python3
"""
UniFi Collector Monitor - Main Entry Point
Ponto de entrada principal da aplicação
"""
import sys
import os

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor, QIcon
from app.gui.main_window import UniFiCollectorGUI


def resource_path(rel_path):
    """Localiza recursos durante desenvolvimento e quando empacotado com PyInstaller."""
    if getattr(sys, "frozen", False):
        # Quando empacotado, os recursos estão em _MEIPASS
        base = sys._MEIPASS
    else:
        # Durante desenvolvimento, usa o diretório atual
        base = os.path.abspath(".")
    return os.path.join(base, rel_path)


def main():
    """Inicializa e executa a aplicação"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Caminho correto do ícone (baseado no --add-data "resources;resources")
    icon_path = resource_path(os.path.join("resources", "icons", "icon.ico"))
    
    # Verifica se o ícone existe e define
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    
    # Definir paleta de cores moderna
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(236, 240, 241))
    palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
    app.setPalette(palette)

    # Criar e exibir janela principal
    window = UniFiCollectorGUI()
    
    # Reforça o ícone na janela (se existir)
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()