import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont


class SecondWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShootCup - Anzeige")
        self.resize(1200, 800)

        # ================= STYLE =================
        self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")

        # ================= MAIN LAYOUT =================
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 10)
        self.layout.setSpacing(0)

        # =========================================================
        # ================= HEADER =================
        # =========================================================
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ---- Left: Tournament Info ----
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(0)

        self.name_label = QLabel("Turniername")
        self.name_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))

        self.date_label = QLabel("Datum")
        self.date_label.setFont(QFont("Arial", 16))
        self.date_label.setStyleSheet("color: #aaaaaa;")

        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.date_label)
        header_layout.addLayout(info_layout)

        header_layout.addStretch()

        # ---- Right: Target Teiler ----
        target_layout = QVBoxLayout()
        target_layout.setContentsMargins(0, 0, 0, 0)
        target_layout.setSpacing(0)

        target_title = QLabel("Zielteiler")
        target_title.setFont(QFont("Arial", 14))
        target_title.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.target_teiler_label = QLabel("0,0")
        self.target_teiler_label.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        self.target_teiler_label.setStyleSheet("color: #4CAF50;")
        self.target_teiler_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        target_layout.addWidget(target_title)
        target_layout.addWidget(self.target_teiler_label)
        header_layout.addLayout(target_layout)

        # ---- Close Button (NO STRETCH BUG!) ----
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
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
        close_container.setContentsMargins(0, 0, 0, 0)
        close_container.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignTop)
        header_layout.addLayout(close_container)

        self.layout.addLayout(header_layout)

        # =========================================================
        # ================= LANES =================
        # =========================================================
        self.lanes_container = QWidget()
        self.lanes_layout = QGridLayout(self.lanes_container)
        self.lanes_layout.setContentsMargins(0, 5, 0, 5)
        self.lanes_layout.setSpacing(10)
        self.layout.addWidget(self.lanes_container)
        self.lanes_container.hide()

        # =========================================================
        # ================= SCROLL AREA =================
        # =========================================================
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("background-color: transparent; border: none;")

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: transparent;")

        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(40)

        self.scroll_area.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll_area)

        # Scroll stretch rules
        self.layout.setStretch(0, 0)  # header
        self.layout.setStretch(1, 0)  # lanes
        self.layout.setStretch(2, 1)  # scroll area takes rest

        # =========================================================
        # ================= SCROLL LOGIC =================
        # =========================================================
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.scroll_step)
        self.scroll_speed = 2
        self.is_scrolling = False
        self.scroll_pos = 0.0

        # Data storage
        self.current_entries = []
        self.current_target_teiler = 0.0
        self.current_assignments = {}
        self.show_assignments = False
        self.changed_lanes = []
        self.use_provided_order = False
        self.loop_threshold = 0

    # =========================================================
    # WINDOW EVENTS
    # =========================================================
    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    # =========================================================
    # SCROLL
    # =========================================================
    def set_scroll_active(self, active: bool):
        self.is_scrolling = active
        if active:
            self.scroll_timer.start(50)
        else:
            self.scroll_timer.stop()
            self.scroll_pos = 0
            self.scroll_area.horizontalScrollBar().setValue(0)

    def set_scroll_speed(self, speed: int):
        self.scroll_speed = max(1, speed)

    def scroll_step(self):
        if not self.is_scrolling:
            return

        max_val = self.scroll_area.horizontalScrollBar().maximum()
        self.scroll_pos += self.scroll_speed

        if self.loop_threshold > 0 and self.scroll_pos >= self.loop_threshold:
            self.scroll_pos -= self.loop_threshold

        if self.scroll_pos >= max_val:
            self.scroll_pos = 0

        self.scroll_area.horizontalScrollBar().setValue(int(self.scroll_pos))

    # =========================================================
    # UPDATE DATA
    # =========================================================
    def update_data(self, name, date_str, target_teiler, entries, lane_assignments=None, show_lanes=False, changed_lanes=None, use_provided_order=False):
        self.name_label.setText(name)
        self.date_label.setText(date_str)
        self.target_teiler_label.setText(f"{target_teiler:.1f}".replace('.', ','))

        self.current_entries = entries
        self.current_target_teiler = target_teiler
        self.current_assignments = lane_assignments if lane_assignments else {}
        self.show_assignments = show_lanes
        self.changed_lanes = changed_lanes if changed_lanes else []
        self.use_provided_order = use_provided_order

        self.rebuild_lanes_display()
        QTimer.singleShot(50, self.rebuild_content)  # wait for layout size

    # =========================================================
    # LANES DISPLAY
    # =========================================================
    def rebuild_lanes_display(self):
        while self.lanes_layout.count():
            item = self.lanes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.show_assignments:
            self.lanes_container.hide()
            return

        self.lanes_container.show()

        cols = 6
        for idx, lane in enumerate(sorted(self.current_assignments.keys())):
            val = self.current_assignments[lane] or "frei"
            lbl = QLabel(f"Stand {lane}: {val}")

            # Determine style based on whether this lane changed
            if lane in self.changed_lanes:
                # Changed: Green and Bold
                style = (
                    "font-size: 18px; font-weight: bold; color: #00ff00; "
                    "padding: 5px; border: 2px solid #00ff00; border-radius: 4px;"
                )
            else:
                # Default: Yellow
                style = (
                    "font-size: 18px; font-weight: bold; color: #ffeb3b; "
                    "padding: 5px; border: 1px solid #444; border-radius: 4px;"
                )

            lbl.setStyleSheet(style)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            row = idx // cols
            col = idx % cols
            self.lanes_layout.addWidget(lbl, row, col)

    # =========================================================
    # CONTENT
    # =========================================================
    def rebuild_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if self.use_provided_order:
            sorted_entries = self.current_entries
        else:
            sorted_entries = sorted(
                self.current_entries,
                key=lambda x: (abs(x["teiler"] - self.current_target_teiler), x["teiler"])
            )

        if not sorted_entries:
            return

        # REAL height
        available_height = self.scroll_area.viewport().height()
        if available_height < 200:
            available_height = 800

        row_height = 30
        rows_per_col = max(1, available_height // row_height)

        chunks = [sorted_entries[i:i + rows_per_col] for i in range(0, len(sorted_entries), rows_per_col)]

        for ci, chunk in enumerate(chunks):
            self.add_column_widget(chunk, ci * rows_per_col + 1)

        self.content_widget.adjustSize()
        spacing = self.content_layout.spacing()
        self.loop_threshold = self.content_widget.width() + spacing

        # duplicate for seamless scroll
        if self.content_widget.width() > self.scroll_area.width() or len(chunks) > 1:
            for ci, chunk in enumerate(chunks):
                self.add_column_widget(chunk, ci * rows_per_col + 1)

    # =========================================================
    # COLUMN BUILDER
    # =========================================================
    def add_column_widget(self, entries_chunk, start_rank):
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        col_widget = QWidget()
        col_layout = QVBoxLayout(col_widget)
        col_layout.setContentsMargins(0, 0, 0, 0)
        col_layout.setSpacing(2)
        col_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for i, entry in enumerate(entries_chunk):
            rank = start_rank + i

            entry_widget = QWidget()
            h_layout = QHBoxLayout(entry_widget)
            h_layout.setContentsMargins(10, 1, 10, 1)

            lbl_rank = QLabel(f"{rank}.")
            lbl_rank.setFixedWidth(40)
            lbl_rank.setStyleSheet("color: #888; font-size: 14px;")

            lbl_name = QLabel(entry["name"])
            lbl_name.setStyleSheet("font-size: 16px; font-weight: bold;")

            diff = abs(entry["teiler"] - self.current_target_teiler)
            teiler_color = "#ffffff"
            if diff == 0:
                teiler_color = "#00ff00"
            elif diff <= 1.0:
                teiler_color = "#aaffaa"

            lbl_teiler = QLabel(f"{entry['teiler']:.1f}".replace('.', ','))
            lbl_teiler.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl_teiler.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {teiler_color};")

            h_layout.addWidget(lbl_rank)
            h_layout.addWidget(lbl_name)
            h_layout.addWidget(lbl_teiler)

            col_layout.addWidget(entry_widget)

        container_layout.addWidget(col_widget)

        # divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setStyleSheet("background-color: #555;")
        line.setFixedWidth(2)
        container_layout.addWidget(line)

        self.content_layout.addWidget(container)


# =========================================================
# TEST MAIN
# =========================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SecondWindow()
    w.show()

    # Dummy Testdaten
    entries = [
        {"name": "Müller", "teiler": 38.5},
        {"name": "Schmidt", "teiler": 47.5},
        {"name": "Huber", "teiler": 39.2},
        {"name": "Meier", "teiler": 40.1},
        {"name": "Bauer", "teiler": 41.0},
        {"name": "Klein", "teiler": 42.7},
        {"name": "Fischer", "teiler": 44.3},
        {"name": "Weber", "teiler": 45.8},
        {"name": "Wolf", "teiler": 50.0},
        {"name": "Lang", "teiler": 55.2},
    ]

    lanes = {1: "22", 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None}

    w.update_data("Neues Turnier", "22.02.2026", 0.0, entries, lanes, show_lanes=True)
    w.set_scroll_active(True)

    sys.exit(app.exec())
