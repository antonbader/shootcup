import json
import uuid
from datetime import datetime
from operator import itemgetter

class Tournament:
    def __init__(self, name="Neues Turnier", date_str=None):
        self.name = name
        self.date_str = date_str if date_str else datetime.now().strftime("%d.%m.%Y")
        self.target_teiler = 0.0
        self.mode = "teiler" # "teiler" or "ringzahl"
        self.entries = []  # List of dicts: {'id': str, 'number': int|None, 'name': str, 'teiler': float, 'klasse': str|None}
        self.entries_ringzahl = [] # List of dicts: {'id': str, 'number': int|None, 'name': str, 'ringzahl': float, 'klasse': str|None}

    def set_mode(self, mode):
        self.mode = mode if mode in ["teiler", "ringzahl"] else "teiler"

    def set_name(self, name):
        self.name = name

    def set_date(self, date_str):
        self.date_str = date_str

    def set_target_teiler(self, target):
        self.target_teiler = round(float(target), 1)

    def add_entry(self, number, name, score, klasse=None):
        """Adds a new entry. Returns True if successful. No uniqueness check for number."""
        entry = {
            'id': uuid.uuid4().hex,
            'number': int(number) if number is not None and str(number).strip() != "" else None,
            'name': name,
            'klasse': klasse.strip() if klasse and klasse.strip() else None
        }
        if self.mode == "teiler":
            entry['teiler'] = round(float(score), 1)
            self.entries.append(entry)
        else:
            entry['ringzahl'] = round(float(score), 1)
            self.entries_ringzahl.append(entry)
        return True

    def remove_entry(self, entry_id):
        """Removes an entry by ID."""
        if self.mode == "teiler":
            self.entries = [e for e in self.entries if e.get('id') != entry_id]
        else:
            self.entries_ringzahl = [e for e in self.entries_ringzahl if e.get('id') != entry_id]

    def update_entry(self, entry_id, new_number, new_name, new_score, new_klasse=None):
        """
        Updates an entry by ID.
        Returns True if successful, False if ID not found.
        """
        target_list = self.entries if self.mode == "teiler" else self.entries_ringzahl
        score_key = 'teiler' if self.mode == "teiler" else 'ringzahl'

        for entry in target_list:
            if entry.get('id') == entry_id:
                entry['number'] = int(new_number) if new_number is not None and str(new_number).strip() != "" else None
                entry['name'] = new_name
                entry[score_key] = round(float(new_score), 1)
                entry['klasse'] = new_klasse.strip() if new_klasse and new_klasse.strip() else None
                return True
        return False

    def get_entries_sorted(self, sort_key='insertion_order', sort_by_class=True):
        """
        Returns a sorted list of entries based on the key.
        sort_key can be: 'insertion_order', 'name', 'teiler', 'diff' or 'ringzahl'.
        """
        target_list = self.entries if self.mode == "teiler" else self.entries_ringzahl

        # Sort by primary key
        if sort_key == 'diff' and self.mode == "teiler":
            sorted_list = sorted(target_list, key=lambda x: (abs(x['teiler'] - self.target_teiler), x['teiler']))
        elif sort_key == 'name':
             sorted_list = sorted(target_list, key=lambda x: x['name'].lower())
        elif sort_key == 'teiler' and self.mode == "teiler":
             sorted_list = sorted(target_list, key=itemgetter('teiler'))
        elif sort_key == 'ringzahl' and self.mode == "ringzahl":
             # Ringzahl highest first
             sorted_list = sorted(target_list, key=itemgetter('ringzahl'), reverse=True)
        else:
            # Default: insertion order
            sorted_list = target_list.copy()

        # Check if we need class sorting
        if sort_by_class:
            has_classes = any(e.get('klasse') for e in target_list)
            if has_classes:
                # Sort by class primary, then maintain the current sorted order
                # "nicht zugeordnet" goes to the end
                sorted_list.sort(key=lambda x: (x.get('klasse') is None, x.get('klasse', '').lower() if x.get('klasse') else ''))

        return sorted_list

    def get_all_classes(self):
        """Returns a sorted list of all unique classes used in the current mode."""
        target_list = self.entries if self.mode == "teiler" else self.entries_ringzahl
        classes = {e.get('klasse') for e in target_list if e.get('klasse')}
        return sorted(list(classes), key=lambda x: x.lower())

    def to_dict(self):
        return {
            'name': self.name,
            'date': self.date_str,
            'target_teiler': self.target_teiler,
            'mode': self.mode,
            'entries': self.entries,
            'entries_ringzahl': self.entries_ringzahl
        }

    def save_to_json(self, filepath):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False

    def load_from_json(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.name = data.get('name', "Unbenannt")
            self.date_str = data.get('date', datetime.now().strftime("%d.%m.%Y"))
            self.target_teiler = data.get('target_teiler', 0.0)
            self.mode = data.get('mode', "teiler")
            self.entries = data.get('entries', [])
            self.entries_ringzahl = data.get('entries_ringzahl', [])

            # Backfill IDs and optional fields for existing entries if missing
            for entry in self.entries:
                if 'id' not in entry:
                    entry['id'] = uuid.uuid4().hex
                if 'klasse' not in entry:
                    entry['klasse'] = None

            for entry in self.entries_ringzahl:
                if 'id' not in entry:
                    entry['id'] = uuid.uuid4().hex
                if 'klasse' not in entry:
                    entry['klasse'] = None

            return True
        except Exception as e:
            print(f"Error loading from JSON: {e}")
            return False
