import re

with open("src/ui/mainwindow.py", "r") as f:
    content = f.read()

diff_text = """<<<<<<< SEARCH
            success = export_to_pdf(
                filepath,
                self.tournament.name,
                self.tournament.date_str,
                entries,
                self.tournament.target_teiler,
                info_text=info_text
            )
=======
            success = export_to_pdf(
                filepath,
                self.tournament.name,
                self.tournament.date_str,
                entries,
                self.tournament.target_teiler,
                info_text=info_text,
                mode=self.tournament.mode
            )
>>>>>>> REPLACE
"""

import sys

def apply_patch():
    with open("replace_mainwindow_pdf.diff", "w") as f:
        f.write(diff_text)

apply_patch()
