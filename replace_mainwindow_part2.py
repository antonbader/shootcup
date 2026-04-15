import re

with open("src/ui/mainwindow.py", "r") as f:
    content = f.read()

# Replace methods to support the mode toggle and class
diff_text = """<<<<<<< SEARCH
    # --- Logic ---

    def update_tournament_info(self):
=======
    # --- Logic ---

    def set_mode(self, mode):
        self.tournament.set_mode(mode)

        # Update buttons
        if mode == "teiler":
            self.mode_teiler_btn.setChecked(True)
            self.mode_ringzahl_btn.setChecked(False)

            # UI Updates for Teiler
            self.teiler_label.setText("Teiler:")
            self.target_teiler_label.show()
            self.target_teiler_input.show()
            self.table.setHorizontalHeaderLabels(["Nr.", "Name", "Klasse", "Teiler", "Abweichung"])
            self.table.setColumnHidden(4, False) # Show Abweichung

            # Update combo box
            current_sort = self.sort_combo.currentText()
            self.sort_combo.clear()
            self.sort_combo.addItems(["Eingabereihenfolge", "Name", "Teiler", "Differenz zum Ziel"])
            if current_sort in ["Eingabereihenfolge", "Name", "Teiler"]:
                self.sort_combo.setCurrentText(current_sort)
        else:
            self.mode_teiler_btn.setChecked(False)
            self.mode_ringzahl_btn.setChecked(True)

            # UI Updates for Ringzahl
            self.teiler_label.setText("Ringzahl:")
            self.target_teiler_label.hide()
            self.target_teiler_input.hide()
            self.table.setHorizontalHeaderLabels(["Nr.", "Name", "Klasse", "Ringzahl", "Abweichung"])
            self.table.setColumnHidden(4, True) # Hide Abweichung

            # Update combo box
            current_sort = self.sort_combo.currentText()
            self.sort_combo.clear()
            self.sort_combo.addItems(["Eingabereihenfolge", "Name", "Ringzahl"])
            if current_sort in ["Eingabereihenfolge", "Name"]:
                self.sort_combo.setCurrentText(current_sort)
            elif current_sort == "Teiler":
                self.sort_combo.setCurrentText("Ringzahl")

        self.update_classes_completer()
        self.update_table()
        self.update_second_window()

    def update_classes_completer(self):
        classes = self.tournament.get_all_classes()
        self.klasse_completer.model().setStringList(classes)

    def update_tournament_info(self):
>>>>>>> REPLACE
<<<<<<< SEARCH
    def add_entry(self):
        try:
            number_text = self.number_input.text().strip()
            number = int(number_text) if number_text else None

            name = self.schuetze_input.text()
            teiler = self.teiler_input.value()

            if not name:
                QMessageBox.warning(self, "Fehler", "Bitte einen Namen eingeben.")
                return

            if self.tournament.add_entry(number, name, teiler):
                self.update_table()
                self.clear_inputs()
                self.update_second_window()
            else:
                QMessageBox.warning(self, "Fehler", "Fehler beim Hinzufügen des Eintrags.")
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Bitte eine gültige Nummer eingeben oder leer lassen.")

    def update_entry(self):
        if not hasattr(self, 'current_selected_id'):
            return

        try:
            number_text = self.number_input.text().strip()
            new_number = int(number_text) if number_text else None

            name = self.schuetze_input.text()
            teiler = self.teiler_input.value()

            if self.tournament.update_entry(self.current_selected_id, new_number, name, teiler):
                self.update_table()
                self.clear_inputs()
                self.update_second_window()
            else:
                 QMessageBox.warning(self, "Fehler", "Eintrag konnte nicht aktualisiert werden.")
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Ungültige Eingabe.")

    def delete_entry(self):
        if not hasattr(self, 'current_selected_id'):
            return

        self.tournament.remove_entry(self.current_selected_id)
        self.update_table()
        self.clear_inputs()
        self.update_second_window()
=======
    def add_entry(self):
        try:
            number_text = self.number_input.text().strip()
            number = int(number_text) if number_text else None

            name = self.schuetze_input.text()
            score = self.teiler_input.value()
            klasse = self.klasse_input.text()

            if not name:
                QMessageBox.warning(self, "Fehler", "Bitte einen Namen eingeben.")
                return

            if self.tournament.add_entry(number, name, score, klasse):
                self.update_classes_completer()
                self.update_table()
                self.clear_inputs()
                self.update_second_window()
            else:
                QMessageBox.warning(self, "Fehler", "Fehler beim Hinzufügen des Eintrags.")
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Bitte eine gültige Nummer eingeben oder leer lassen.")

    def update_entry(self):
        if not hasattr(self, 'current_selected_id'):
            return

        try:
            number_text = self.number_input.text().strip()
            new_number = int(number_text) if number_text else None

            name = self.schuetze_input.text()
            score = self.teiler_input.value()
            klasse = self.klasse_input.text()

            if self.tournament.update_entry(self.current_selected_id, new_number, name, score, klasse):
                self.update_classes_completer()
                self.update_table()
                self.clear_inputs()
                self.update_second_window()
            else:
                 QMessageBox.warning(self, "Fehler", "Eintrag konnte nicht aktualisiert werden.")
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Ungültige Eingabe.")

    def delete_entry(self):
        if not hasattr(self, 'current_selected_id'):
            return

        self.tournament.remove_entry(self.current_selected_id)
        self.update_classes_completer()
        self.update_table()
        self.clear_inputs()
        self.update_second_window()
>>>>>>> REPLACE
<<<<<<< SEARCH
    def load_entry_into_inputs(self, item):
        row = item.row()
        # Retrieve ID from the first column item
        id_item = self.table.item(row, 0)
        entry_id = id_item.data(Qt.ItemDataRole.UserRole)

        # Ensure we are getting the items from the correct columns regardless of which cell was clicked
        number_item = self.table.item(row, 0)
        name_item = self.table.item(row, 1)
        teiler_item = self.table.item(row, 2)

        if not (number_item and name_item and teiler_item):
            return

        number_text = number_item.text()
        name = name_item.text()
        teiler = float(teiler_item.text().replace(',', '.'))

        self.number_input.setText(number_text)
        self.schuetze_input.setText(name)
        self.teiler_input.setValue(teiler)
=======
    def load_entry_into_inputs(self, item):
        row = item.row()
        # Retrieve ID from the first column item
        id_item = self.table.item(row, 0)
        entry_id = id_item.data(Qt.ItemDataRole.UserRole)

        # Ensure we are getting the items from the correct columns regardless of which cell was clicked
        number_item = self.table.item(row, 0)
        name_item = self.table.item(row, 1)
        klasse_item = self.table.item(row, 2)
        score_item = self.table.item(row, 3)

        if not (number_item and name_item and score_item):
            return

        number_text = number_item.text()
        name = name_item.text()
        klasse = klasse_item.text() if klasse_item else ""
        score = float(score_item.text().replace(',', '.'))

        self.number_input.setText(number_text)
        self.schuetze_input.setText(name)
        self.klasse_input.setText(klasse)
        self.teiler_input.setValue(score)
>>>>>>> REPLACE
<<<<<<< SEARCH
    def clear_inputs(self):
        self.number_input.clear()
        self.schuetze_input.clear()
        self.teiler_input.setValue(0.0)

        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
=======
    def clear_inputs(self):
        self.number_input.clear()
        self.schuetze_input.clear()
        self.klasse_input.clear()
        self.teiler_input.setValue(0.0)

        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
>>>>>>> REPLACE
<<<<<<< SEARCH
    def update_table(self):
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

        self.table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            number_val = str(entry['number']) if entry['number'] is not None else ""
            item_number = QTableWidgetItem(number_val)
            item_number.setData(Qt.ItemDataRole.UserRole, entry['id'])

            self.table.setItem(row, 0, item_number)
            self.table.setItem(row, 1, QTableWidgetItem(entry['name']))
            self.table.setItem(row, 2, QTableWidgetItem(f"{entry['teiler']:.1f}".replace('.', ',')))

            diff = abs(entry['teiler'] - self.tournament.target_teiler)
            self.table.setItem(row, 3, QTableWidgetItem(f"{diff:.1f}".replace('.', ',')))

        if self.second_window and self.sort_mirror_check.isChecked():
            self.update_second_window()
=======
    def update_table(self):
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

        self.table.setRowCount(len(entries))
        score_key = 'teiler' if self.tournament.mode == "teiler" else 'ringzahl'

        for row, entry in enumerate(entries):
            number_val = str(entry['number']) if entry['number'] is not None else ""
            item_number = QTableWidgetItem(number_val)
            item_number.setData(Qt.ItemDataRole.UserRole, entry['id'])

            self.table.setItem(row, 0, item_number)
            self.table.setItem(row, 1, QTableWidgetItem(entry['name']))

            klasse_val = entry.get('klasse') or ""
            self.table.setItem(row, 2, QTableWidgetItem(klasse_val))

            self.table.setItem(row, 3, QTableWidgetItem(f"{entry[score_key]:.1f}".replace('.', ',')))

            if self.tournament.mode == "teiler":
                diff = abs(entry['teiler'] - self.tournament.target_teiler)
                self.table.setItem(row, 4, QTableWidgetItem(f"{diff:.1f}".replace('.', ',')))
            else:
                self.table.setItem(row, 4, QTableWidgetItem("")) # Hidden column anyway

        if self.second_window and self.sort_mirror_check.isChecked():
            self.update_second_window()
>>>>>>> REPLACE
"""

import sys

def apply_patch():
    with open("replace_mainwindow_part2.diff", "w") as f:
        f.write(diff_text)

apply_patch()
