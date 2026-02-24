import sys
import os
import time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QDoubleSpinBox, QDateEdit,
    QHeaderView, QMessageBox, QFileDialog, QGroupBox, QFormLayout, QComboBox,
    QDialog, QVBoxLayout, QDialogButtonBox, QApplication, QCheckBox, QSlider,
    QSpinBox, QGridLayout, QAbstractItemView
)
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import Qt, QDate, QRect, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from src.core.tournament import Tournament
from src.ui.secondwindow import SecondWindow
from src.core.pdf_exporter import export_to_pdf

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_index=0, current_speed=2, num_lanes=8, show_lanes=False, show_target_teiler=False):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.resize(350, 350)

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

        # Lanes Settings
        layout.addWidget(QLabel("Anzahl Stände:"))
        self.lanes_spin = QSpinBox()
        self.lanes_spin.setRange(1, 100)
        self.lanes_spin.setValue(num_lanes)
        layout.addWidget(self.lanes_spin)

        self.show_lanes_check = QCheckBox("Standzuordnung auf 2. Fenster anzeigen")
        self.show_lanes_check.setChecked(show_lanes)
        layout.addWidget(self.show_lanes_check)

        self.show_target_teiler_check = QCheckBox("Zielteiler auf 2. Fenster anzeigen")
        self.show_target_teiler_check.setChecked(show_target_teiler)
        layout.addWidget(self.show_target_teiler_check)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def get_selected_screen_index(self):
        return self.screen_combo.currentIndex()

    def get_scroll_speed(self):
        return self.speed_slider.value()

    def get_num_lanes(self):
        return self.lanes_spin.value()

    def get_show_lanes(self):
        return self.show_lanes_check.isChecked()

    def get_show_target_teiler(self):
        return self.show_target_teiler_check.isChecked()

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

        # Lane Settings
        self.num_lanes = 8
        self.show_lanes_second_screen = False
        self.show_target_teiler_second_screen = False
        self.lane_assignments = {} # {lane_num: start_nr_str}
        self.lane_timestamps = {}  # {lane_num: timestamp}

        # Filter State
        self.active_filter_names = None

        # Sound Player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        # Path to notice.mp3
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # src
        sound_path = os.path.join(base_dir, "sound", "notice.mp3")
        self.player.setSource(QUrl.fromLocalFile(sound_path))

        # UI Components
        self.init_ui()
        self.setup_lane_inputs()
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
        # Removed validator to allow optional number input
        # self.number_input.setValidator(QIntValidator(1, 999999999))
        self.number_input.setValidator(QIntValidator()) # Allows input but no range restriction, basically any int or empty

        self.schuetze_input = QLineEdit()
        self.schuetze_input.setPlaceholderText("Name des Schützen")

        self.teiler_input = QDoubleSpinBox()
        self.teiler_input.setRange(0.0, 1000000.0)
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
        self.target_teiler_input.setRange(0.0, 1000000.0)
        self.target_teiler_input.setDecimals(1)
        self.target_teiler_input.setSingleStep(0.1)
        self.target_teiler_input.setValue(0.0)
        self.target_teiler_input.valueChanged.connect(self.target_teiler_changed)

        self.sort_combo = QComboBox()
        # Removed "Nr." and added "Eingabereihenfolge" as default
        self.sort_combo.addItems(["Eingabereihenfolge", "Name", "Teiler", "Differenz zum Ziel"])
        self.sort_combo.currentIndexChanged.connect(self.update_table)

        self.sort_mirror_check = QCheckBox("Sortierung anzeigen")
        self.sort_mirror_check.toggled.connect(lambda: self.update_second_window())

        self.filter_btn = QPushButton("Nach markierten Namen filtern")
        self.filter_btn.clicked.connect(self.toggle_filter)

        control_layout.addWidget(QLabel("Zielteiler:"))
        control_layout.addWidget(self.target_teiler_input)
        control_layout.addWidget(self.filter_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.sort_mirror_check)
        control_layout.addWidget(QLabel("Sortierung:"))
        control_layout.addWidget(self.sort_combo)
        main_layout.addLayout(control_layout)

        # --- Table Section ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nr.", "Name", "Teiler", "Abweichung"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemClicked.connect(self.load_entry_into_inputs)
        main_layout.addWidget(self.table)

        # --- Lane Assignments Section ---
        self.lanes_group = QGroupBox("Standzuordnung")
        self.lanes_layout = QGridLayout()
        self.lanes_group.setLayout(self.lanes_layout)
        main_layout.addWidget(self.lanes_group)

        self.update_lanes_btn = QPushButton("Update Stände")
        self.update_lanes_btn.clicked.connect(self.update_lane_assignments)
        main_layout.addWidget(self.update_lanes_btn)

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

    def toggle_filter(self):
        if self.active_filter_names is not None:
            # Clear filter
            self.active_filter_names = None
            self.filter_btn.setText("Nach markierten Namen filtern")
            self.update_table()
        else:
            # Apply filter
            selected_items = self.table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Hinweis", "Bitte wählen Sie mindestens einen Namen aus, nach dem gefiltert werden soll.")
                return

            names = set()
            rows = set()
            for item in selected_items:
                rows.add(item.row())

            for row in rows:
                item = self.table.item(row, 1) # Name column
                if item:
                    names.add(item.text())

            if not names:
                QMessageBox.warning(self, "Hinweis", "Keine Namen in der Auswahl gefunden.")
                return

            self.active_filter_names = names
            self.filter_btn.setText("Filter zurücksetzen")
            self.update_table()

    def target_teiler_changed(self):
        self.tournament.set_target_teiler(self.target_teiler_input.value())
        self.update_table()
        self.update_second_window()

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

        self.current_selected_id = entry_id

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
        if hasattr(self, 'current_selected_id'):
            del self.current_selected_id
            self.table.clearSelection()

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
                "Eingabereihenfolge": "insertion_order",
                "Name": "name",
                "Teiler": "teiler",
                "Differenz zum Ziel": "diff"
            }
            key = key_map.get(sort_mode, "insertion_order")
            entries = self.tournament.get_entries_sorted(key)

            # Apply filter if active
            is_filtered = False
            if self.active_filter_names is not None:
                entries = [e for e in entries if e['name'] in self.active_filter_names]
                is_filtered = True

            # Construct info text
            info_text = f"(Sortierung: {sort_mode}"
            if is_filtered:
                info_text += ", nach ausgewählten Namen gefiltert"
            info_text += ")"

            success = export_to_pdf(
                filepath,
                self.tournament.name,
                self.tournament.date_str,
                entries,
                self.tournament.target_teiler,
                info_text=info_text
            )

            if success:
                QMessageBox.information(self, "Erfolg", "PDF erfolgreich erstellt.")
            else:
                QMessageBox.critical(self, "Fehler", "PDF konnte nicht erstellt werden.")

    def setup_lane_inputs(self):
        # Clear existing
        while self.lanes_layout.count():
            item = self.lanes_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.lane_inputs = [] # List of QLineEdit

        # Grid logic: 5 columns
        cols = 5
        for i in range(self.num_lanes):
            lane_num = i + 1

            # Container for Label + Input
            container = QWidget()
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(0,0,0,0)

            lbl = QLabel(f"{lane_num}:")
            lbl.setFixedWidth(30)
            inp = QLineEdit()
            inp.setPlaceholderText("Startnr.")
            # Restore value if exists
            current_val = self.lane_assignments.get(lane_num, "")
            inp.setText(str(current_val))

            self.lane_inputs.append(inp)

            h_layout.addWidget(lbl)
            h_layout.addWidget(inp)

            row = i // cols
            col = i % cols
            self.lanes_layout.addWidget(container, row, col)

    def apply_lane_assignments(self, play_sound=True):
        new_assignments = {}
        changed_lanes = []
        current_time = time.time()

        for i, inp in enumerate(self.lane_inputs):
            lane_num = i + 1
            text = inp.text().strip()

            val = text if text else ""
            new_assignments[lane_num] = val

            old_val = self.lane_assignments.get(lane_num, "")

            # Logic for timestamps
            if val:
                # If value is present and changed, update timestamp
                if val != old_val:
                    self.lane_timestamps[lane_num] = current_time
                    changed_lanes.append(lane_num)
            else:
                # If value is cleared, remove timestamp
                self.lane_timestamps.pop(lane_num, None)

        self.lane_assignments = new_assignments

        # Play sound only if there are relevant changes (additions/updates)
        if play_sound and changed_lanes and self.show_lanes_second_screen and self.second_window:
             self.player.play()

        self.update_second_window(changed_lanes=changed_lanes)

    def update_lane_assignments(self):
        self.apply_lane_assignments(play_sound=True)

    def open_settings(self):
        dlg = SettingsDialog(
            self,
            self.selected_screen_index,
            self.scroll_speed,
            self.num_lanes,
            self.show_lanes_second_screen,
            self.show_target_teiler_second_screen
        )
        if dlg.exec():
            self.selected_screen_index = dlg.get_selected_screen_index()
            self.scroll_speed = dlg.get_scroll_speed()

            new_num_lanes = dlg.get_num_lanes()
            lanes_changed = (new_num_lanes != self.num_lanes)
            self.num_lanes = new_num_lanes
            self.show_lanes_second_screen = dlg.get_show_lanes()
            self.show_target_teiler_second_screen = dlg.get_show_target_teiler()

            if lanes_changed:
                self.setup_lane_inputs()
                self.apply_lane_assignments(play_sound=False)

            if self.second_window:
                self.second_window.set_scroll_speed(self.scroll_speed)
                self.update_second_window()

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
                lane_timestamps=self.lane_timestamps
            )
