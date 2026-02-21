from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QFrame,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor

class SecondWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShootCup - Anzeige")

        # Style
        self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # --- Header (Fixed at Top) ---
        header_layout = QHBoxLayout()

        # Left: Tournament Info
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Align to top
        info_layout.setSpacing(0) # Reduce space between Name and Date

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
        target_layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Align to top
        target_layout.setSpacing(0) # Reduce space between Title and Value

        target_title = QLabel("Zielteiler")
        target_title.setFont(QFont("Arial", 14)) # Smaller font than Name, but visually aligned at top
        # To make it "gleicher Höhe" visually, we might need to adjust margin or padding if the fonts differ too much in ascender.
        # But logically, AlignTop puts them at y=0 relative to the container.
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

        # --- Content Area (Scrollable) ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("background-color: transparent; border: none;")

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: transparent;")
        self.content_layout = QHBoxLayout(self.content_widget) # Horizontal Layout for Columns!
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(40) # Space between columns

        self.scroll_area.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll_area)

        # --- Scrolling Logic ---
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.scroll_step)
        self.scroll_speed = 2 # Pixels per tick
        self.is_scrolling = False
        self.scroll_pos = 0.0

        # Data storage for seamless looping
        self.current_entries = []
        self.current_target_teiler = 0.0
        self.seamless_duplicate_threshold = 0 # If content width > screen width

        # For seamless scrolling, we need to know the width of the original content
        self.original_content_width = 0

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    def set_scroll_active(self, active):
        self.is_scrolling = active
        if active:
            self.scroll_timer.start(50) # 20 FPS updates
        else:
            self.scroll_timer.stop()

    def set_scroll_speed(self, speed):
        # speed range 1-100?
        # let's map it roughly.
        self.scroll_speed = max(1, speed)

    def scroll_step(self):
        if not self.is_scrolling:
            return

        max_val = self.scroll_area.horizontalScrollBar().maximum()

        self.scroll_pos += self.scroll_speed

        # Seamless Logic:
        # If we have scrolled past the original content width, we jump back to 0 (or close to 0)
        # Assuming we duplicated the content.

        if self.original_content_width > 0 and self.scroll_pos >= self.original_content_width:
             self.scroll_pos -= self.original_content_width

        if self.scroll_pos >= max_val:
            self.scroll_pos = 0

        self.scroll_area.horizontalScrollBar().setValue(int(self.scroll_pos))

    def update_data(self, name, date_str, target_teiler, entries):
        self.name_label.setText(name)
        self.date_label.setText(date_str)
        self.target_teiler_label.setText(f"{target_teiler:.1f}".replace('.', ','))

        self.current_entries = entries
        self.current_target_teiler = target_teiler

        self.rebuild_content()

    def rebuild_content(self):
        # Clear existing
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        sorted_entries = sorted(self.current_entries, key=lambda x: (abs(x['teiler'] - self.current_target_teiler), x['teiler']))

        if not sorted_entries:
            return

        # Determine rows per column based on available height.
        # Use available height minus some padding.
        available_height = self.scroll_area.height()
        if available_height < 200: available_height = 800 # Fallback if window not shown yet

        # Estimate row height more accurately
        row_height = 45
        rows_per_col = max(1, (available_height - 20) // row_height)

        # Chunk entries
        chunks = [sorted_entries[i:i + rows_per_col] for i in range(0, len(sorted_entries), rows_per_col)]

        # Add original columns
        for chunk_index, chunk in enumerate(chunks):
            # Calculate rank correctly for the chunk
            start_rank = chunk_index * rows_per_col + 1
            self.add_column_widget(chunk, start_rank)

        # Force layout update to calculate width
        self.content_widget.adjustSize()
        self.original_content_width = self.content_widget.width() # Store width of original content

        # Duplicate columns for seamless scrolling
        # If we have enough content to warrant scrolling, duplicate ALL columns once.
        if self.original_content_width > self.scroll_area.width() or len(chunks) > 1:
             for chunk_index, chunk in enumerate(chunks):
                 start_rank = chunk_index * rows_per_col + 1
                 self.add_column_widget(chunk, start_rank)

    def add_column_widget(self, entries_chunk, start_rank):
        # Container for column + divider
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Column Content
        col_widget = QWidget()
        col_layout = QVBoxLayout(col_widget)
        col_layout.setContentsMargins(0, 0, 0, 0)
        col_layout.setSpacing(5)
        col_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for i, entry in enumerate(entries_chunk):
            rank = start_rank + i

            entry_widget = QWidget()
            h_layout = QHBoxLayout(entry_widget)
            h_layout.setContentsMargins(10, 5, 10, 5)

            lbl_rank = QLabel(f"{rank}.")
            lbl_rank.setFixedWidth(40)
            lbl_rank.setStyleSheet("color: #888; font-weight: bold; font-size: 14px;")

            lbl_name = QLabel(entry['name'])
            lbl_name.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")

            diff = abs(entry['teiler'] - self.current_target_teiler)
            teiler_color = "#ffffff"
            if diff == 0:
                teiler_color = "#00ff00"
            elif diff <= 1.0:
                teiler_color = "#aaffaa"

            lbl_teiler = QLabel(f"{entry['teiler']:.1f}".replace('.', ','))
            lbl_teiler.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl_teiler.setStyleSheet(f"color: {teiler_color}; font-size: 18px; font-weight: bold;")

            h_layout.addWidget(lbl_rank)
            h_layout.addWidget(lbl_name)
            h_layout.addWidget(lbl_teiler)

            col_layout.addWidget(entry_widget)

        container_layout.addWidget(col_widget)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setStyleSheet("color: #555; background-color: #555;")
        line.setFixedWidth(2)
        container_layout.addWidget(line)

        self.content_layout.addWidget(container)
