import json
import os

class JsonManager:
    def __init__(self, filepath):
        self.filepath = filepath

    def read_json(self):
        # ❗ Soubor neexistuje → vrať prázdný list
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
            return []

        # ❗ Soubor existuje → pokus o načtení
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # Pokud je to dict → obal do listu
                if isinstance(data, dict):
                    return [data]
                return data
        except json.JSONDecodeError:
            return []  # poškozený JSON → vracíme prázdný list

    def write_json(self, new_entry):
        import json, os

        # 🔹 Načti data (ať už jsou to {} nebo [])
        data = []
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as file:
                try:
                    loaded = json.load(file)
                    # Pokud je to slovník, obal ho do seznamu
                    if isinstance(loaded, dict):
                        data = [loaded]
                    else:
                        data = loaded
                except json.JSONDecodeError:
                    data = []

        # 🔹 Přidej nový záznam
        data.append(new_entry)

        # 🔹 Ulož zpět jako seznam
        with open(self.filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    
    def delete_by_id(self, entry_id):
        data = self.read_json()
        # Filtruj záznamy, které nemají dané ID
        data = [entry for entry in data if entry.get("id") != entry_id]
        # Ulož zpět upravená data
        with open(self.filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def update_by_pin(self, pin, new_value):
        data = self.read_json()
        for entry in data:
            if entry.get("pin") == pin:
                entry["value"] = new_value
        with open(self.filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)