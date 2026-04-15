import re

with open("src/ui/secondwindow.py", "r") as f:
    content = f.read()

diff_text = """<<<<<<< SEARCH
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
=======
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
            if "is_header" in entry:
                # It's a class header
                header_widget = QWidget()
                h_layout = QHBoxLayout(header_widget)
                h_layout.setContentsMargins(5, 10, 5, 2)

                lbl_header = QLabel(entry["name"])
                lbl_header.setStyleSheet("color: #ff9800; font-size: 20px; font-weight: bold; text-decoration: underline;")
                lbl_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
                h_layout.addWidget(lbl_header)
                col_layout.addWidget(header_widget)
                continue

            rank = entry.get("display_rank", start_rank + i)

            entry_widget = QWidget()
            h_layout = QHBoxLayout(entry_widget)
            h_layout.setContentsMargins(10, 1, 10, 1)

            lbl_rank = QLabel(f"{rank}.")
            lbl_rank.setFixedWidth(40)
            lbl_rank.setStyleSheet("color: #888; font-size: 14px;")

            lbl_name = QLabel(entry["name"])
            lbl_name.setStyleSheet("font-size: 16px; font-weight: bold;")

            score_key = "teiler" if getattr(self, "current_mode", "teiler") == "teiler" else "ringzahl"
            score_val = entry.get(score_key, 0.0)

            score_color = "#ffffff"
            if score_key == "teiler":
                diff = abs(score_val - self.current_target_teiler)
                if diff == 0:
                    score_color = "#00ff00"
                elif diff <= 1.0:
                    score_color = "#aaffaa"

            lbl_score = QLabel(f"{score_val:.1f}".replace('.', ','))
            lbl_score.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl_score.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {score_color};")

            h_layout.addWidget(lbl_rank)
            h_layout.addWidget(lbl_name)
            h_layout.addWidget(lbl_score)

            col_layout.addWidget(entry_widget)

        container_layout.addWidget(col_widget)

        # divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setStyleSheet("background-color: #555;")
        line.setFixedWidth(2)
        container_layout.addWidget(line)

        self.content_layout.addWidget(container)
>>>>>>> REPLACE
"""

import sys

def apply_patch():
    with open("replace_secondwindow_part2.diff", "w") as f:
        f.write(diff_text)

apply_patch()
