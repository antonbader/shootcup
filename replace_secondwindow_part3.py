import re

with open("src/ui/secondwindow.py", "r") as f:
    content = f.read()

diff_text = """<<<<<<< SEARCH
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
=======
    def rebuild_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.current_entries:
            return

        # Transform entries for display: Insert class headers and calculate ranks
        display_entries = []
        has_classes = any(e.get('klasse') for e in self.current_entries)

        current_class = object() # dummy object for first iteration
        rank = 1

        if has_classes:
            for entry in self.current_entries:
                cls = entry.get('klasse')
                if cls != current_class:
                    current_class = cls
                    header_name = cls if cls else "Nicht zugeordnet"
                    display_entries.append({"is_header": True, "name": header_name})
                    rank = 1 # Reset rank for new class

                entry_copy = entry.copy()
                entry_copy['display_rank'] = rank
                display_entries.append(entry_copy)
                rank += 1
        else:
            for entry in self.current_entries:
                entry_copy = entry.copy()
                entry_copy['display_rank'] = rank
                display_entries.append(entry_copy)
                rank += 1

        # REAL height
        available_height = self.scroll_area.viewport().height()
        if available_height < 200:
            available_height = 800

        row_height = 30
        # Headers take a bit more space, but we approximate
        rows_per_col = max(1, available_height // row_height)

        chunks = [display_entries[i:i + rows_per_col] for i in range(0, len(display_entries), rows_per_col)]
>>>>>>> REPLACE
"""

import sys

def apply_patch():
    with open("replace_secondwindow_part3.diff", "w") as f:
        f.write(diff_text)

apply_patch()
