import json
import os

import customtkinter as ctk
from tkinter import messagebox

# ---------------- Wygląd ----------------
THEME_BG = "#2b2b2b"
THEME_FG = "#e8e8e8"
THEME_ACCENT = "#4a9eff"
THEME_ACCENT_FG = "#ffffff"
THEME_FIELD_BG = "#3c3c3c"
THEME_FONT_FAMILY = "Segoe UI"
THEME_FONT_SIZE = 11
THEME_DISABLED_FG = "#777777"

# ---------------- Dane ustawień ----------------
SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "settings.json"
)
VERSION = 2

DEFAULTS = {
    "version": VERSION,
    "hourly_rate": 0.0,
    "contract": "etat",  # "etat" albo "zlecenie"
    "employment": 1.0,  # wymiar etatu: 1.0 = pełny, 0.5 = 1/2 itd.
    "monthly_goal": 0.0,  # cel kwoty (zł), tylko zlecenie
    "goal_hours": 0.0,  # cel czasu pracy (h), tylko zlecenie
    "bar_mode": "kwota",  # "kwota" albo "czas", tylko zlecenie
    "language": "pl",
}

ETATY = {
    "Pełny etat": 1.0,
    "3/4 etatu": 0.75,
    "1/2 etatu": 0.5,
    "1/4 etatu": 0.25,
}

CONTRACTS = {"Etat": "etat", "Zlecenie": "zlecenie"}
BAR_MODES = {"Kwota": "kwota", "Czas pracy": "czas"}


def load_settings():
    settings = dict(DEFAULTS)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                settings.update(json.load(f))
        except (json.JSONDecodeError, OSError):
            pass
    settings["version"] = VERSION
    return settings


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)


def _key_for(mapping, value, default):
    """Etykieta (klucz słownika) dla zapisanej wartości."""
    return next((k for k, v in mapping.items() if v == value), default)


def _parse_number(text):
    """Zamienia tekst z pola na liczbę >= 0. Puste pole = 0."""
    value = float(text.replace(",", ".").strip() or 0)
    if value < 0:
        raise ValueError
    return value


# ---------------- Okno ustawień ----------------
def open_settings_window(root, settings, on_save=None):
    win = ctk.CTkToplevel(root)
    win.title("Ustawienia")
    win.geometry("420x420")
    win.configure(fg_color=THEME_BG)
    win.resizable(False, False)
    win.transient(root)
    win.after(100, win.grab_set)

    def label(text, row):
        ctk.CTkLabel(win, text=text, text_color=THEME_FG).grid(
            row=row, column=0, padx=15, pady=10, sticky="w"
        )

    def entry(value, row):
        e = ctk.CTkEntry(
            win,
            width=170,
            fg_color=THEME_FIELD_BG,
            text_color=THEME_FG,
            justify="center",
        )
        e.insert(0, str(value) if value else "")
        e.grid(row=row, column=1, padx=15, pady=10)
        return e

    def segmented(values, current, row):
        s = ctk.CTkSegmentedButton(
            win,
            values=values,
            width=170,
            selected_color=THEME_ACCENT,
            unselected_color=THEME_FIELD_BG,
            text_color_disabled=THEME_DISABLED_FG,
            command=lambda v: update_states(),
        )
        s.set(current)
        s.grid(row=row, column=1, padx=15, pady=10)
        return s

    # --- Pola wspólne ---
    label("Stawka godzinowa (zł):", 0)
    entry_rate = entry(settings["hourly_rate"], 0)

    label("Rodzaj umowy:", 1)
    contract = segmented(
        list(CONTRACTS), _key_for(CONTRACTS, settings["contract"], "Etat"), 1
    )

    # --- Tylko etat ---
    label("Wymiar etatu:", 2)
    menu = ctk.CTkOptionMenu(
        win,
        values=list(ETATY),
        width=170,
        fg_color=THEME_FIELD_BG,
        button_color=THEME_ACCENT,
        text_color_disabled=THEME_DISABLED_FG,
    )
    menu.set(_key_for(ETATY, settings["employment"], "Pełny etat"))
    menu.grid(row=2, column=1, padx=15, pady=10)

    # --- Tylko zlecenie ---
    label("Cel kwoty (zł):", 3)
    entry_goal = entry(settings["monthly_goal"], 3)

    label("Cel czasu pracy (h):", 4)
    entry_hours = entry(settings["goal_hours"], 4)

    label("Pasek pokazuje:", 5)
    bar_mode = segmented(
        list(BAR_MODES), _key_for(BAR_MODES, settings["bar_mode"], "Kwota"), 5
    )

    def set_entry_active(e, active):
        e.configure(
            state="normal" if active else "disabled",
            text_color=THEME_FG if active else THEME_DISABLED_FG,
        )

    def update_states():
        """Etat: blokuje cele i wybór paska.
        Zlecenie: blokuje wymiar etatu oraz cel, którego pasek nie używa."""
        is_etat = CONTRACTS[contract.get()] == "etat"
        mode = BAR_MODES[bar_mode.get()]

        menu.configure(state="normal" if is_etat else "disabled")
        bar_mode.configure(state="disabled" if is_etat else "normal")
        set_entry_active(entry_goal, not is_etat and mode == "kwota")
        set_entry_active(entry_hours, not is_etat and mode == "czas")

    update_states()
    entry_rate.focus_set()

    def save(event=None):
        is_etat = CONTRACTS[contract.get()] == "etat"
        try:
            rate = _parse_number(entry_rate.get())
            goal = settings["monthly_goal"]
            goal_h = settings["goal_hours"]
            if not is_etat:
                if BAR_MODES[bar_mode.get()] == "kwota":
                    goal = _parse_number(entry_goal.get())
                else:
                    goal_h = _parse_number(entry_hours.get())
        except ValueError:
            messagebox.showerror(
                "Błąd", "Stawka i cele muszą być liczbami (np. 31.40 i 3000)."
            )
            return

        settings["hourly_rate"] = rate
        settings["contract"] = CONTRACTS[contract.get()]
        settings["monthly_goal"] = goal
        settings["goal_hours"] = goal_h
        settings["bar_mode"] = BAR_MODES[bar_mode.get()]
        if is_etat:
            settings["employment"] = ETATY[menu.get()]
        save_settings(settings)
        win.destroy()
        if on_save:
            on_save()

    ctk.CTkButton(
        win,
        text="Zapisz",
        command=save,
        fg_color=THEME_ACCENT,
        text_color=THEME_ACCENT_FG,
    ).grid(row=6, column=0, columnspan=2, pady=20)
    win.bind("<Return>", save)