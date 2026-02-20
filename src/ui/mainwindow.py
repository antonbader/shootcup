import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QDoubleSpinBox, QDateEdit,
    QHeaderView, QMessageBox, QFileDialog, QGroupBox, QFormLayout, QComboBox,
    QDialog, QVBoxLayout, QDialogButtonBox, QApplication, QCheckBox, QSlider
)
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import Qt, QDate, QRect
from src.core.tournament import Tournament
from src.ui.secondwindow import SecondWindow
from src.core.pdf_exporter import export_to_pdf

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_index=0, current_speed=2):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.resize(300, 250)

        layout = QVBoxLayout(self)

        # Screen Selection
        layout.addWidget(QLabel("Bildschirm für Vollbild-Anzeige auswählen:"))
        self.screen_combo = QComboBox()
        screens = QApplication.screens()
        for i, screen in enumerate(screens):
            self.screen_combo.addItem(f"Bildschirm {i+1}: {screen.name()} ({screen.geometry().width()}x{screen.geometry().height()})")

        if current_index < len(screens):
            self.screen_combo.setCurrentIndex(current_index)
        layout.addWidget(self.screen_combo)

        # Scroll Speed
        layout.addWidget(QLabel("Scroll-Geschwindigkeit:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(current_speed)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(1)
        layout.addWidget(self.speed_slider)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def get_selected_screen_index(self):
        return self.screen_combo.currentIndex()

    def get_scroll_speed(self):
        return self.speed_slider.value()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShootCup Tournament Manager")
        self.resize(1000, 700)

        # Initialize Tournament Logic
        self.tournament = Tournament()

        # Second Window State
        self.second_window = None
        self.selected_screen_index = 0 # Default to primary
        self.scroll_speed = 2

        # UI Components
        self.init_ui()
        self.update_table()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Tournament Info Section ---
        info_group = QGroupBox("Turnier Informationen")
        info_layout = QHBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Turnier Name")
        self.name_input.setText(self.tournament.name)
        self.name_input.textChanged.connect(self.update_tournament_info)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("dd.MM.yyyy")
        self.date_input.dateChanged.connect(self.update_tournament_info)

        info_layout.addWidget(QLabel("Name:"))
        info_layout.addWidget(self.name_input)
        info_layout.addWidget(QLabel("Datum:"))
        info_layout.addWidget(self.date_input)
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # --- Data Entry Section ---
        entry_group = QGroupBox("Eintrag hinzufügen / bearbeiten")
        entry_layout = QHBoxLayout()

        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Nr.")
        self.number_input.setValidator(QIntValidator(1, 9999))

        self.schuetze_input = QLineEdit()
        self.schuetze_input.setPlaceholderText("Name des Schützen")

        self.teiler_input = QDoubleSpinBox()
        self.teiler_input.setRange(0.0, 1999.9)
        self.teiler_input.setDecimals(1)
        self.teiler_input.setSingleStep(0.1)

        self.add_btn = QPushButton("Hinzufügen")
        self.add_btn.clicked.connect(self.add_entry)

        self.update_btn = QPushButton("Aktualisieren")
        self.update_btn.setEnabled(False)
        self.update_btn.clicked.connect(self.update_entry)

        self.delete_btn = QPushButton("Löschen")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_entry)

        self.clear_btn = QPushButton("Felder leeren")
        self.clear_btn.clicked.connect(self.clear_inputs)

        entry_layout.addWidget(QLabel("Nr.:"))
        entry_layout.addWidget(self.number_input)
        entry_layout.addWidget(QLabel("Name:"))
        entry_layout.addWidget(self.schuetze_input)
        entry_layout.addWidget(QLabel("Teiler:"))
        entry_layout.addWidget(self.teiler_input)
        entry_layout.addWidget(self.add_btn)
        entry_layout.addWidget(self.update_btn)
        entry_layout.addWidget(self.delete_btn)
        entry_layout.addWidget(self.clear_btn)
        entry_group.setLayout(entry_layout)
        main_layout.addWidget(entry_group)

        # --- Target Teiler & Sorting ---
        control_layout = QHBoxLayout()

        self.target_teiler_input = QDoubleSpinBox()
        self.target_teiler_input.setRange(0.0, 1999.9)
        self.target_teiler_input.setDecimals(1)
        self.target_teiler_input.setSingleStep(0.1)
        self.target_teiler_input.setValue(0.0)
        self.target_teiler_input.valueChanged.connect(self.target_teiler_changed)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Nr.", "Name", "Teiler", "Differenz zum Ziel"])
        self.sort_combo.currentIndexChanged.connect(self.update_table)

        control_layout.addWidget(QLabel("Zielteiler:"))
        control_layout.addWidget(self.target_teiler_input)
        control_layout.addStretch()
        control_layout.addWidget(QLabel("Sortierung:"))
        control_layout.addWidget(self.sort_combo)
        main_layout.addLayout(control_layout)

        # --- Table Section ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nr.", "Name", "Teiler", "Abweichung"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemClicked.connect(self.load_entry_into_inputs)
        main_layout.addWidget(self.table)

        # --- Footer Buttons ---
        footer_layout = QHBoxLayout()

        self.save_btn = QPushButton("Speichern (JSON)")
        self.save_btn.clicked.connect(self.save_json)

        self.load_btn = QPushButton("Laden (JSON)")
        self.load_btn.clicked.connect(self.load_json)

        self.export_btn = QPushButton("PDF Export")
        self.export_btn.clicked.connect(self.export_pdf) # Placeholder

        self.scroll_check = QCheckBox("Automatisches Scrollen (2. Bildschirm)")
        self.scroll_check.clicked.connect(self.toggle_scrolling)

        self.settings_btn = QPushButton("Einstellungen")
        self.settings_btn.clicked.connect(self.open_settings)

        self.second_screen_btn = QPushButton("2. Bildschirm öffnen")
        self.second_screen_btn.clicked.connect(self.toggle_second_screen)

        footer_layout.addWidget(self.save_btn)
        footer_layout.addWidget(self.load_btn)
        footer_layout.addStretch()
        footer_layout.addWidget(self.scroll_check)
        footer_layout.addWidget(self.settings_btn)
        footer_layout.addWidget(self.export_btn)
        footer_layout.addWidget(self.second_screen_btn)
        main_layout.addLayout(footer_layout)

    # --- Logic ---

    def update_tournament_info(self):
        self.tournament.set_name(self.name_input.text())
        self.tournament.set_date(self.date_input.text())
        self.update_second_window()

    def target_teiler_changed(self):
        self.tournament.set_target_teiler(self.target_teiler_input.value())
        self.update_table()
        self.update_second_window()

    def add_entry(self):
        try:
            txt_num = self.number_input.text()
            if not txt_num:
                 QMessageBox.warning(self, "Fehler", "Bitte eine Nummer eingeben.")
                 return
            number = int(txt_num)
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
                QMessageBox.warning(self, "Fehler", f"Nummer {number} existiert bereits.")
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Bitte eine gültige Nummer eingeben.")

    def update_entry(self):
        # We need to know which entry was originally selected.
        # For now, we assume the user hasn't changed the number field to something else unless intended.
        # But wait, if they change the number, we need to know the OLD number to update correctly.
        # So we need to store the currently selected number.
        if not hasattr(self, 'current_selected_number'):
            return

        try:
            new_number = int(self.number_input.text())
            name = self.schuetze_input.text()
            teiler = self.teiler_input.value()

            if self.tournament.update_entry(self.current_selected_number, new_number, name, teiler):
                self.update_table()
                self.clear_inputs()
                self.update_second_window()
            else:
                 QMessageBox.warning(self, "Fehler", f"Nummer {new_number} kann nicht verwendet werden (existiert bereits).")
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Ungültige Eingabe.")

    def delete_entry(self):
        if not hasattr(self, 'current_selected_number'):
            return

        self.tournament.remove_entry(self.current_selected_number)
        self.update_table()
        self.clear_inputs()
        self.update_second_window()

    def load_entry_into_inputs(self, item):
        row = item.row()
        # Ensure we are getting the items from the correct columns regardless of which cell was clicked
        number_item = self.table.item(row, 0)
        name_item = self.table.item(row, 1)
        teiler_item = self.table.item(row, 2)

        if not (number_item and name_item and teiler_item):
            return

        number = int(number_item.text())
        name = name_item.text()
        teiler = float(teiler_item.text().replace(',', '.'))

        self.number_input.setText(str(number))
        self.schuetze_input.setText(name)
        self.teiler_input.setValue(teiler)

        self.current_selected_number = number

        self.add_btn.setEnabled(False)
        self.update_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def clear_inputs(self):
        self.number_input.clear()
        self.schuetze_input.clear()
        self.teiler_input.setValue(0.0)

        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        if hasattr(self, 'current_selected_number'):
            del self.current_selected_number
            self.table.clearSelection()

    def update_table(self):
        sort_mode = self.sort_combo.currentText()
        key_map = {
            "Nr.": "number",
            "Name": "name",
            "Teiler": "teiler",
            "Differenz zum Ziel": "diff"
        }
        key = key_map.get(sort_mode, "number")

        entries = self.tournament.get_entries_sorted(key)

        self.table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            self.table.setItem(row, 0, QTableWidgetItem(str(entry['number'])))
            self.table.setItem(row, 1, QTableWidgetItem(entry['name']))
            self.table.setItem(row, 2, QTableWidgetItem(f"{entry['teiler']:.1f}".replace('.', ',')))

            diff = abs(entry['teiler'] - self.tournament.target_teiler)
            self.table.setItem(row, 3, QTableWidgetItem(f"{diff:.1f}".replace('.', ',')))

    def save_json(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Turnier speichern", "", "JSON Files (*.json)")
        if filepath:
            if self.tournament.save_to_json(filepath):
                QMessageBox.information(self, "Erfolg", "Turnier gespeichert.")
            else:
                QMessageBox.critical(self, "Fehler", "Speichern fehlgeschlagen.")

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

    def export_pdf(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "PDF Exportieren", "", "PDF Files (*.pdf)")
        if filepath:
            if not filepath.endswith('.pdf'):
                filepath += '.pdf'

            # Get sorted entries based on current sort mode
            sort_mode = self.sort_combo.currentText()
            key_map = {
                "Nr.": "number",
                "Name": "name",
                "Teiler": "teiler",
                "Differenz zum Ziel": "diff"
            }
            key = key_map.get(sort_mode, "number")
            entries = self.tournament.get_entries_sorted(key)

            success = export_to_pdf(
                filepath,
                self.tournament.name,
                self.tournament.date_str,
                entries,
                self.tournament.target_teiler
            )

            if success:
                QMessageBox.information(self, "Erfolg", "PDF erfolgreich erstellt.")
            else:
                QMessageBox.critical(self, "Fehler", "PDF konnte nicht erstellt werden.")

    def open_settings(self):
        dlg = SettingsDialog(self, self.selected_screen_index, self.scroll_speed)
        if dlg.exec():
            self.selected_screen_index = dlg.get_selected_screen_index()
            self.scroll_speed = dlg.get_scroll_speed()
            if self.second_window:
                self.second_window.set_scroll_speed(self.scroll_speed)

    def toggle_scrolling(self):
        if self.second_window:
            self.second_window.set_scroll_active(self.scroll_check.isChecked())

    def toggle_second_screen(self):
        if self.second_window is None:
            self.second_window = SecondWindow()
            self.second_window.closed.connect(self.on_second_window_closed)

            # Move to selected screen
            screens = QApplication.screens()
            if self.selected_screen_index < len(screens):
                screen = screens[self.selected_screen_index]
                geo = screen.geometry()
                self.second_window.move(geo.x(), geo.y())
                self.second_window.showFullScreen()
            else:
                self.second_window.show() # Fallback

            # Apply settings
            self.second_window.set_scroll_speed(self.scroll_speed)
            self.second_window.set_scroll_active(self.scroll_check.isChecked())

            self.second_screen_btn.setText("2. Bildschirm schließen")
            self.update_second_window()
        else:
            self.second_window.close() # Will trigger on_second_window_closed

    def on_second_window_closed(self):
        self.second_window = None
        self.second_screen_btn.setText("2. Bildschirm öffnen")

    def update_second_window(self):
        if self.second_window:
            # Always pass entries sorted by DIFF regardless of table sort
            # Actually, SecondWindow sorts them by diff itself in update_data.
            # So we can just pass raw entries or whatever list.
            # But wait, logic in SecondWindow is: `sorted_entries = sorted(entries, key=lambda x: (abs(x['teiler'] - target_teiler), x['teiler']))`
            # So we just pass current entries.
            self.second_window.update_data(
                self.tournament.name,
                self.tournament.date_str,
                self.tournament.target_teiler,
                self.tournament.entries
            )
