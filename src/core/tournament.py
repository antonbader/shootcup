import json
import uuid
from datetime import datetime
from operator import itemgetter

class Tournament:
    def __init__(self, name="Neues Turnier", date_str=None):
        self.name = name
        self.date_str = date_str if date_str else datetime.now().strftime("%d.%m.%Y")
        self.target_teiler = 0.0
        self.entries = []  # List of dicts: {'id': str, 'number': int|None, 'name': str, 'teiler': float}

    def set_name(self, name):
        self.name = name

    def set_date(self, date_str):
        self.date_str = date_str

    def set_target_teiler(self, target):
        self.target_teiler = round(float(target), 1)

    def add_entry(self, number, name, teiler):
        """Adds a new entry. Returns True if successful. No uniqueness check for number."""
        entry = {
            'id': uuid.uuid4().hex,
            'number': int(number) if number is not None and str(number).strip() != "" else None,
            'name': name,
            'teiler': round(float(teiler), 1)
        }
        self.entries.append(entry)
        return True

    def remove_entry(self, entry_id):
        """Removes an entry by ID."""
        self.entries = [e for e in self.entries if e.get('id') != entry_id]

    def update_entry(self, entry_id, new_number, new_name, new_teiler):
        """
        Updates an entry by ID.
        Returns True if successful, False if ID not found.
        """
        for entry in self.entries:
            if entry.get('id') == entry_id:
                entry['number'] = int(new_number) if new_number is not None and str(new_number).strip() != "" else None
                entry['name'] = new_name
                entry['teiler'] = round(float(new_teiler), 1)
                return True
        return False

    def get_entries_sorted(self, sort_key='insertion_order'):
        """
        Returns a sorted list of entries based on the key.
        sort_key can be: 'insertion_order', 'name', 'teiler', 'diff'.
        'diff' sorts by the absolute difference to target_teiler.
        """
        if sort_key == 'diff':
            # Sort by difference, then by teiler (ascending) as secondary
            return sorted(self.entries, key=lambda x: (abs(x['teiler'] - self.target_teiler), x['teiler']))
        elif sort_key == 'name':
             return sorted(self.entries, key=lambda x: x['name'].lower())
        elif sort_key == 'teiler':
             return sorted(self.entries, key=itemgetter('teiler'))
        else:
            # Default: insertion order (as is in list)
            return self.entries

    def to_dict(self):
        return {
            'name': self.name,
            'date': self.date_str,
            'target_teiler': self.target_teiler,
            'entries': self.entries
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
            self.entries = data.get('entries', [])

            # Backfill IDs for existing entries if missing
            for entry in self.entries:
                if 'id' not in entry:
                    entry['id'] = uuid.uuid4().hex

            return True
        except Exception as e:
            print(f"Error loading from JSON: {e}")
            return False
