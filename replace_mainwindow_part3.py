import re

with open("src/ui/mainwindow.py", "r") as f:
    content = f.read()

# Replace methods to support mode logic in load_json and update_second_window

diff_text = """<<<<<<< SEARCH
    def load_json(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Turnier laden", "", "JSON Files (*.json)")
        if filepath:
            if self.tournament.load_from_json(filepath):
                self.name_input.setText(self.tournament.name)
                # Parse date string back to QDate
                try:
                    day, month, year = map(int, self.tournament.date_str.split('.'))
                    self.date_input.setDate(QDate(year, month, day))
                except:
                    pass
                self.target_teiler_input.setValue(self.tournament.target_teiler)
                self.update_table()
                QMessageBox.information(self, "Erfolg", "Turnier geladen.")
            else:
                QMessageBox.critical(self, "Fehler", "Laden fehlgeschlagen.")
=======
    def load_json(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Turnier laden", "", "JSON Files (*.json)")
        if filepath:
            if self.tournament.load_from_json(filepath):
                self.name_input.setText(self.tournament.name)
                # Parse date string back to QDate
                try:
                    day, month, year = map(int, self.tournament.date_str.split('.'))
                    self.date_input.setDate(QDate(year, month, day))
                except:
                    pass
                self.target_teiler_input.setValue(self.tournament.target_teiler)
                self.set_mode(self.tournament.mode) # This handles updating table and combobox
                QMessageBox.information(self, "Erfolg", "Turnier geladen.")
            else:
                QMessageBox.critical(self, "Fehler", "Laden fehlgeschlagen.")
>>>>>>> REPLACE
<<<<<<< SEARCH
    def update_second_window(self, changed_lanes=None):
        if self.second_window:
            if changed_lanes is None:
                changed_lanes = []

            entries_to_send = self.tournament.entries

            if self.sort_mirror_check.isChecked():
                sort_mode = self.sort_combo.currentText()
                key_map = {
                    "Eingabereihenfolge": "insertion_order",
                    "Name": "name",
                    "Teiler": "teiler",
                    "Differenz zum Ziel": "diff"
                }
                key = key_map.get(sort_mode, "insertion_order")
                entries = self.tournament.get_entries_sorted(key)

                if self.active_filter_names is not None:
                    entries = [e for e in entries if e['name'] in self.active_filter_names]
                entries_to_send = entries

            self.second_window.update_data(
                self.tournament.name,
                self.tournament.date_str,
                self.tournament.target_teiler,
                entries_to_send,
                self.lane_assignments,
                self.show_lanes_second_screen,
                changed_lanes=changed_lanes,
                show_target_teiler=self.show_target_teiler_second_screen,
                lane_timestamps=self.lane_timestamps,
                lane_display_duration_seconds=self.lane_display_duration_minutes * 60
            )
=======
    def update_second_window(self, changed_lanes=None):
        if self.second_window:
            if changed_lanes is None:
                changed_lanes = []

            entries_to_send = self.tournament.entries if self.tournament.mode == "teiler" else self.tournament.entries_ringzahl

            if self.sort_mirror_check.isChecked():
                sort_mode = self.sort_combo.currentText()
                key_map = {
                    "Eingabereihenfolge": "insertion_order",
                    "Name": "name",
                    "Teiler": "teiler",
                    "Ringzahl": "ringzahl",
                    "Differenz zum Ziel": "diff"
                }
                key = key_map.get(sort_mode, "insertion_order")
                entries = self.tournament.get_entries_sorted(key)

                if self.active_filter_names is not None:
                    entries = [e for e in entries if e['name'] in self.active_filter_names]
                entries_to_send = entries

            self.second_window.update_data(
                self.tournament.name,
                self.tournament.date_str,
                self.tournament.target_teiler,
                entries_to_send,
                self.lane_assignments,
                self.show_lanes_second_screen,
                changed_lanes=changed_lanes,
                show_target_teiler=self.show_target_teiler_second_screen and self.tournament.mode == "teiler",
                lane_timestamps=self.lane_timestamps,
                lane_display_duration_seconds=self.lane_display_duration_minutes * 60,
                mode=self.tournament.mode
            )
>>>>>>> REPLACE
"""

import sys

def apply_patch():
    with open("replace_mainwindow_part3.diff", "w") as f:
        f.write(diff_text)

apply_patch()
