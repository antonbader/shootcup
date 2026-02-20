from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

class SecondWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShootCup - Anzeige")

        # Determine if we go fullscreen later (controlled by main window)
        # self.showFullScreen()

        # Dark Theme for contrast or clean white? Let's go with a clean high-contrast look.
        # Maybe dark background with light text looks "modern" for displays.
        self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # --- Header ---
        header_layout = QHBoxLayout()

        # Left: Tournament Info
        info_layout = QVBoxLayout()
        self.name_label = QLabel("Turniername")
        self.name_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.date_label = QLabel("Datum")
        self.date_label.setFont(QFont("Arial", 16))
        self.date_label.setStyleSheet("color: #aaaaaa;")

        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.date_label)
        header_layout.addLayout(info_layout)

        header_layout.addStretch()

        # Right: Target Teiler
        target_layout = QVBoxLayout()
        target_title = QLabel("Zielteiler")
        target_title.setFont(QFont("Arial", 14))
        target_title.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.target_teiler_label = QLabel("0,0")
        self.target_teiler_label.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        self.target_teiler_label.setStyleSheet("color: #4CAF50;") # Green
        self.target_teiler_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        target_layout.addWidget(target_title)
        target_layout.addWidget(self.target_teiler_label)
        header_layout.addLayout(target_layout)

        # Close Button (X)
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff4444;
                border-radius: 20px;
            }
        """)
        self.close_btn.clicked.connect(self.close)

        # Add a bit of spacing/margin for the close button
        close_container = QVBoxLayout()
        close_container.addWidget(self.close_btn)
        close_container.addStretch()
        header_layout.addLayout(close_container)

        self.layout.addLayout(header_layout)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #444; color: #444;")
        self.layout.addWidget(line)

        # --- Content Area ---
        # We will use a Grid Layout to simulate columns.
        # We need to manually rebuild this layout when data updates.
        self.content_widget = QWidget()
        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.content_widget)
        self.layout.addStretch() # Push content up

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    def update_data(self, name, date_str, target_teiler, entries):
        """
        entries: List of dicts.
        """
        self.name_label.setText(name)
        self.date_label.setText(date_str)
        self.target_teiler_label.setText(f"{target_teiler:.1f}".replace('.', ','))

        # Clear existing items
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not entries:
            return

        # Layout Logic
        # We target ~15 rows per column.
        rows_per_col = 15

        current_col = 0
        current_row = 0

        # Sort entries by difference to target teiler (closest first)
        # Assuming entries are passed already sorted, but let's be sure.
        # But wait, MainWindow passes 'entries' which might be sorted by something else if table sort is changed.
        # The requirement says: "In dem Fenster wird ... die Einträge mit Platzierung, Namen und Teiler die am nächsten am Zielteiler sind."
        # So this window ALWAYS sorts by diff.

        sorted_entries = sorted(entries, key=lambda x: (abs(x['teiler'] - target_teiler), x['teiler']))

        for rank, entry in enumerate(sorted_entries, 1):
            # Create a widget for the entry
            entry_widget = QWidget()
            h_layout = QHBoxLayout(entry_widget)
            h_layout.setContentsMargins(5, 2, 5, 2)

            lbl_rank = QLabel(f"{rank}.")
            lbl_rank.setFixedWidth(40)
            lbl_rank.setStyleSheet("color: #888; font-weight: bold;")

            lbl_name = QLabel(entry['name'])
            lbl_name.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffffff;")

            diff = abs(entry['teiler'] - target_teiler)
            teiler_color = "#ffffff"
            if diff == 0:
                teiler_color = "#00ff00" # Perfect Green
            elif diff <= 1.0:
                teiler_color = "#aaffaa" # Light Green

            lbl_teiler = QLabel(f"{entry['teiler']:.1f}".replace('.', ','))
            lbl_teiler.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl_teiler.setStyleSheet(f"color: {teiler_color}; font-size: 16px; font-weight: bold;")

            h_layout.addWidget(lbl_rank)
            h_layout.addWidget(lbl_name)
            h_layout.addWidget(lbl_teiler)

            self.content_layout.addWidget(entry_widget, current_row, current_col)

            current_row += 1
            if current_row >= rows_per_col:
                current_row = 0
                current_col += 1
