import json, os

SETTINGS_FILE = "settings.json"
VERSION = 1

DEFAULTS = {
    "version": VERSION,
    "hourly_rate": 0.0,
    "monthly_goal": 0.0,
    "employment": 1.0,     # 1.0 = pełny etat, 0.5 = 1/2 itd.
    "language": "pl",
}

def load_settings():
    settings = dict(DEFAULTS)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                settings.update(json.load(f))
        except (json.JSONDecodeError, OSError):
            pass  # uszkodzony plik -> wartości domyślne
    return settings

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)