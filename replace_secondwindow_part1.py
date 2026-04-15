import re

with open("src/ui/secondwindow.py", "r") as f:
    content = f.read()

diff_text = """<<<<<<< SEARCH
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
=======
    # =========================================================
    # UPDATE DATA
    # =========================================================
    def update_data(self, name, date_str, target_teiler, entries, lane_assignments=None, show_lanes=False, changed_lanes=None, show_target_teiler=False, lane_timestamps=None, lane_display_duration_seconds=300, mode="teiler"):
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
        self.current_mode = mode

        self.rebuild_lanes_display()
        QTimer.singleShot(50, self.rebuild_content)  # wait for layout size
>>>>>>> REPLACE
"""

import sys

def apply_patch():
    with open("replace_secondwindow_part1.diff", "w") as f:
        f.write(diff_text)

apply_patch()
