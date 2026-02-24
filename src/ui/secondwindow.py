import sys
import time
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
        self.target_teiler_container = QWidget()
        target_layout = QVBoxLayout(self.target_teiler_container)
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
        header_layout.addWidget(self.target_teiler_container)

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
        self.lanes_header_label = QLabel("Standbelegung (Zuordnung Startnummer zu Stand)")
        self.lanes_header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.lanes_header_label.setStyleSheet("color: #ffffff; margin-top: 5px; margin-bottom: 2px;")
        self.lanes_header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.lanes_header_label)
        self.lanes_header_label.hide()

        self.lanes_container = QWidget()
        self.lanes_layout = QGridLayout(self.lanes_container)
        self.lanes_layout.setContentsMargins(0, 2, 0, 2)
        self.lanes_layout.setSpacing(5)
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
        self.current_timestamps = {}
        self.show_assignments = False
        self.changed_lanes = []
        self.loop_threshold = 0
        self.lane_labels = {}
        self.display_duration_seconds = 300 # Default 5 min

        # Lane color timer
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.update_lane_colors)
        self.color_timer.start(1000)

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
        self.rebuild_content()

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
    def update_data(self, name, date_str, target_teiler, entries, lane_assignments=None, show_lanes=False, changed_lanes=None, show_target_teiler=False, lane_timestamps=None, lane_display_duration_seconds=300):
        self.name_label.setText(name)
        self.date_label.setText(date_str)
        self.target_teiler_label.setText(f"{target_teiler:.1f}".replace('.', ','))
        self.target_teiler_container.setVisible(show_target_teiler)

        self.current_entries = entries
        self.current_target_teiler = target_teiler
        self.current_assignments = lane_assignments if lane_assignments else {}
        self.current_timestamps = lane_timestamps if lane_timestamps else {}
        self.show_assignments = show_lanes
        self.changed_lanes = changed_lanes if changed_lanes else []
        self.display_duration_seconds = lane_display_duration_seconds

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

        self.lane_labels.clear()

        if not self.show_assignments:
            self.lanes_container.hide()
            self.lanes_header_label.hide()
            return

        self.lanes_container.show()
        self.lanes_header_label.show()

        # Reset container layout alignment
        self.lanes_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        cols = 8
        lanes = sorted(self.current_assignments.keys())
        for idx, lane in enumerate(lanes):
            val = self.current_assignments[lane] or "frei"
            lbl = QLabel(f"Stand {lane}: {val}")
            lbl.setFixedHeight(50)
            lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            row = idx // cols
            col = idx % cols
            self.lanes_layout.addWidget(lbl, row, col)

            self.lane_labels[lane] = lbl

        # Initial Color Update
        self.update_lane_colors()

        # Calculate and set fixed height for container to prevent vertical expansion
        num_rows = (len(lanes) + cols - 1) // cols
        if num_rows > 0:
            # 50px per row + spacing (5) * (rows-1) + margins (2*2)
            spacing = self.lanes_layout.spacing()
            margins = self.lanes_layout.contentsMargins()
            total_height = (num_rows * 50) + (max(0, num_rows - 1) * spacing) + margins.top() + margins.bottom()
            self.lanes_container.setFixedHeight(total_height)
        else:
            self.lanes_container.setFixedHeight(0)

    def update_lane_colors(self):
        current_time = time.time()
        for lane, lbl in self.lane_labels.items():
            val = self.current_assignments.get(lane, "")

            # Default style base
            base_style = "padding: 2px; border-radius: 4px; border: 1px solid #444;"

            if not val:
                # Empty -> Green
                # "Wenn er nicht belegt ist grün."
                style = base_style + "color: #00ff00; font-size: 14px;"
            else:
                # Occupied
                timestamp = self.current_timestamps.get(lane)
                is_new = False
                if timestamp:
                    diff = current_time - timestamp
                    # "für maximal 5 Minuten ... gelb und Fett"
                    # Wenn display_duration_seconds 0 ist, wird dies immer False sein, wenn diff > 0
                    if diff < self.display_duration_seconds:
                        is_new = True

                if is_new:
                    # Yellow and Bold
                    style = base_style + "color: #ffeb3b; font-size: 14px; font-weight: bold; border: 2px solid #ffeb3b;"
                else:
                    # Older than 5 min -> Red
                    # "wenn er weiterhin belegt ist rot"
                    style = base_style + "color: #ff0000; font-size: 14px;"

            lbl.setStyleSheet(style)

    # =========================================================
    # CONTENT
    # =========================================================
    def rebuild_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Always use the order provided by the main window.
        # This defaults to insertion order (unless "Sortierung anzeigen" is checked and modified in main window).
        sorted_entries = self.current_entries

        if not sorted_entries:
            return

        # REAL height
        available_height = self.scroll_area.viewport().height()
        if available_height < 200:
            available_height = 800

        row_height = 30
        rows_per_col = max(1, available_height // row_height)

        chunks = [sorted_entries[i:i + rows_per_col] for i in range(0, len(sorted_entries), rows_per_col)]

        # --- Build FIRST set to measure it ---
        for ci, chunk in enumerate(chunks):
            self.add_column_widget(chunk, ci * rows_per_col + 1)

        self.content_widget.adjustSize()
        spacing = self.content_layout.spacing()

        # Measure real width by summing children hints (ignoring resize behavior)
        single_set_width = 0
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item.widget():
                single_set_width += item.widget().sizeHint().width()

        # Add spacing (N-1 gaps for N items)
        if self.content_layout.count() > 1:
            single_set_width += (self.content_layout.count() - 1) * spacing

        # If something went wrong and width is 0, fallback
        if single_set_width <= 0:
            single_set_width = self.content_widget.width()

        self.loop_threshold = single_set_width + spacing

        viewport_width = self.scroll_area.viewport().width()

        # Decide if we should scroll and duplicate
        # Condition: Scrolling enabled AND content wider than viewport
        should_scroll = self.is_scrolling and (single_set_width > viewport_width)

        if should_scroll:
            # --- Duplicate until we have enough content ---
            # We need to scroll up to loop_threshold.
            # At that point, the view resets to 0.
            # But visually, at loop_threshold, we are looking at the START of the NEXT set.
            # We must ensure that there is enough content visible AFTER that point to fill the screen.

            target_width = self.loop_threshold + viewport_width
            current_width = single_set_width

            # Safety: avoid infinite loop
            if self.loop_threshold > 0:
                while current_width < target_width:
                    for ci, chunk in enumerate(chunks):
                        self.add_column_widget(chunk, ci * rows_per_col + 1)

                    current_width += self.loop_threshold

            if not self.scroll_timer.isActive():
                self.scroll_timer.start(50)
        else:
            self.scroll_timer.stop()
            self.scroll_pos = 0
            self.scroll_area.horizontalScrollBar().setValue(0)

        self.content_widget.adjustSize()

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
