import sys
from PyQt6.QtWidgets import QApplication
from src.ui.mainwindow import MainWindow

def main():
    app = QApplication(sys.argv)

    # Set a modern style via QSS
    app.setStyle("Fusion")

    # Optional: Custom Palette for Dark Mode if desired,
    # but Fusion with default is usually clean grey.
    # Let's add some basic styling for buttons and tables.
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px;
        }
        QPushButton {
            background-color: #0078d7;
            color: white;
            border-radius: 4px;
            padding: 6px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #005a9e;
        }
        QPushButton:disabled {
            background-color: #cccccc;
        }
        QLineEdit, QDoubleSpinBox, QDateEdit, QComboBox {
            padding: 4px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        QTableWidget {
            border: 1px solid #ccc;
            gridline-color: #eee;
            selection-background-color: #0078d7;
        }
        QHeaderView::section {
            background-color: #e0e0e0;
            padding: 4px;
            border: 1px solid #ccc;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
