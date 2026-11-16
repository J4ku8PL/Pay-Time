import calendar
import datetime
import json
import os
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from settings import (
    ETATY,
    load_settings,
    save_settings,
    open_settings_window,
    THEME_BG,
    THEME_FG,
    THEME_ACCENT,
    THEME_ACCENT_FG,
    THEME_FIELD_BG,
    THEME_FONT_FAMILY,
    THEME_FONT_SIZE,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "PT_data.json")

HOURS_PER_DAY = 8  # godzin na dzień przy pełnym etacie

MIESIACE_PL = [
    "",
    "Styczeń",
    "Luty",
    "Marzec",
    "Kwiecień",
    "Maj",
    "Czerwiec",
    "Lipiec",
    "Sierpień",
    "Wrzesień",
    "Październik",
    "Listopad",
    "Grudzień",
]


class Application:

    def __init__(self, root):
        self.root = root
        root.title("$ Pay Time $")
        root.geometry("560x600")
        root.minsize(480, 560)  # Minimalny rozmiar okna
        root.configure(fg_color=THEME_BG)

        root.update_idletasks()
        root.geometry(
            f"+{(root.winfo_screenwidth() - 560) // 2}+{(root.winfo_screenheight() - 600) // 2}"
        )

        # Konfiguracja skalowania kolumn i wierszy okna głównego
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(
            2, weight=1
        )  # Kalendarz rozciąga się w pionie

        now = datetime.datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        self.data_store = {}
        self.settings = load_settings()

        # ---------------- 1. Górna sekcja: informacja o stawce + ustawienia ----------------
        self.frame_top = ctk.CTkFrame(root, fg_color=THEME_BG)
        self.frame_top.grid(
            row=0, column=0, padx=20, pady=(15, 5), sticky="ew"
        )
        self.frame_top.grid_columnconfigure(0, weight=1)

        self.lbl_info = ctk.CTkLabel(
            self.frame_top,
            text="",
            text_color=THEME_FG,
            font=ctk.CTkFont(family=THEME_FONT_FAMILY, size=THEME_FONT_SIZE),
        )
        self.lbl_info.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.btn_settings = ctk.CTkButton(
            self.frame_top,
            text="⚙",
            width=32,
            height=30,
            fg_color=THEME_FIELD_BG,
            hover_color=THEME_ACCENT,
            command=lambda: open_settings_window(
                self.root, self.settings, on_save=self._update_totals
            ),
        )
        self.btn_settings.grid(row=0, column=1, padx=(0, 10), pady=5)

        # ---------------- 2. Nawigacja miesięcy ----------------
        self.frame_nav = ctk.CTkFrame(root, fg_color=THEME_BG)
        self.frame_nav.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.frame_nav.grid_columnconfigure(1, weight=1)

        self.btn_prev = ctk.CTkButton(
            self.frame_nav,
            text="<",
            command=self.poprzedni_miesiac,
            fg_color=THEME_ACCENT,
            text_color=THEME_ACCENT_FG,
            font=ctk.CTkFont(
                family=THEME_FONT_FAMILY, size=12, weight="bold"
            ),
            width=40,
            height=32,
        )
        self.btn_prev.grid(row=0, column=0, padx=5)

        self.miesiace = ctk.CTkFrame(
            self.frame_nav, border_width=1, fg_color=THEME_BG, height=32
        )
        self.miesiace.grid(row=0, column=1, padx=5, sticky="ew")
        self.miesiace.grid_columnconfigure(0, weight=1)

        self.lbl_nazwa_miesiaca = ctk.CTkLabel(
            self.miesiace,
            text="",
            text_color=THEME_FG,
            font=ctk.CTkFont(
                family=THEME_FONT_FAMILY, size=12, weight="bold"
            ),
        )
        self.lbl_nazwa_miesiaca.grid(row=0, column=0, pady=2, sticky="nsew")

        self.btn_next = ctk.CTkButton(
            self.frame_nav,
            text=">",
            command=self.nastepny_miesiac,
            fg_color=THEME_ACCENT,
            text_color=THEME_ACCENT_FG,
            font=ctk.CTkFont(
                family=THEME_FONT_FAMILY, size=12, weight="bold"
            ),
            width=40,
            height=32,
        )
        self.btn_next.grid(row=0, column=2, padx=5)

        # ---------------- 3. Kontener na kalendarz ----------------
        self.frame_kalendarz = ctk.CTkFrame(
            root, border_width=1, fg_color=THEME_BG
        )
        self.frame_kalendarz.grid(
            row=2, column=0, padx=20, pady=10, sticky="nsew"
        )

        # Konfiguracja równomiernego skalowania 7 kolumn kalendarza (Pn-Nd)
        for col in range(7):
            self.frame_kalendarz.grid_columnconfigure(col, weight=1)

        # ---------------- 4. Progress bar ----------------
        self.frame_progress = ctk.CTkFrame(
            root, border_width=1, fg_color=THEME_BG
        )
        self.frame_progress.grid(
            row=3, column=0, padx=20, pady=(5, 5), sticky="ew"
        )
        self.frame_progress.grid_columnconfigure(0, weight=1)

        self.lbl_progress = ctk.CTkLabel(
            self.frame_progress,
            text="",
            text_color=THEME_FG,
            font=ctk.CTkFont(
                family=THEME_FONT_FAMILY, size=THEME_FONT_SIZE, weight="bold"
            ),
        )
        self.lbl_progress.grid(row=0, column=0, padx=10, pady=(8, 4))

        self.progress = ctk.CTkProgressBar(
            self.frame_progress,
            height=14,
            fg_color=THEME_FIELD_BG,
            progress_color=THEME_ACCENT,
        )
        self.progress.grid(row=1, column=0, padx=15, pady=(0, 4), sticky="ew")
        self.progress.set(0)

        self.lbl_progress_info = ctk.CTkLabel(
            self.frame_progress,
            text="",
            text_color="#9a9a9a",
            font=ctk.CTkFont(family=THEME_FONT_FAMILY, size=10),
        )
        self.lbl_progress_info.grid(row=2, column=0, padx=10, pady=(0, 8))

        # ---------------- 5. Podsumowanie na dole ----------------
        self.frame4 = ctk.CTkFrame(root, border_width=1, fg_color=THEME_BG)
        self.frame4.grid(row=4, column=0, padx=20, pady=(5, 15), sticky="ew")
        self.frame4.grid_columnconfigure((0, 1), weight=1)

        self.lbl_suma_godzin = ctk.CTkLabel(
            self.frame4,
            text="Suma godzin: 0 h",
            text_color=THEME_FG,
            font=ctk.CTkFont(family=THEME_FONT_FAMILY, size=THEME_FONT_SIZE),
        )
        self.lbl_suma_godzin.grid(row=0, column=0, padx=10, pady=10)

        self.lbl_suma_wyplaty = ctk.CTkLabel(
            self.frame4,
            text="Szacowana wypłata: 0.00 zł",
            text_color="#50fa7b",
            font=ctk.CTkFont(
                family=THEME_FONT_FAMILY, size=THEME_FONT_SIZE, weight="bold"
            ),
        )
        self.lbl_suma_wyplaty.grid(row=0, column=1, padx=10, pady=10)

        self._load_data()
        self._render_calendar()

    def _render_calendar(self):
        for widget in self.frame_kalendarz.winfo_children():
            widget.destroy()

        month_name = MIESIACE_PL[self.current_month]
        self.lbl_nazwa_miesiaca.configure(
            text=f"{month_name} {self.current_year}"
        )

        headers = ["Pn", "Wt", "Śr", "Cz", "Pt", "So", "Nd"]
        for col, h in enumerate(headers):
            lbl = ctk.CTkLabel(
                self.frame_kalendarz,
                text=h,
                text_color="#8be9fd",
                font=ctk.CTkFont(
                    family=THEME_FONT_FAMILY, size=10, weight="bold"
                ),
            )
            lbl.grid(row=0, column=col, padx=2, pady=5, sticky="ew")

        month_matrix = calendar.monthcalendar(
            self.current_year, self.current_month
        )
        self.day_buttons = {}

        # Skalowanie wierszy dni w kalendarzu
        for r in range(1, len(month_matrix) + 1):
            self.frame_kalendarz.grid_rowconfigure(r, weight=1)

        for row_idx, week in enumerate(month_matrix, start=1):
            for col_idx, day in enumerate(week):
                if day != 0:
                    btn = ctk.CTkButton(
                        self.frame_kalendarz,
                        text=f"{day}\n-",
                        font=ctk.CTkFont(family=THEME_FONT_FAMILY, size=9),
                        fg_color=THEME_FIELD_BG,
                        text_color=THEME_FG,
                        command=lambda d=day: self._open_day_dialog(d),
                    )
                    btn.grid(
                        row=row_idx, column=col_idx, padx=2, pady=2, sticky="nsew"
                    )
                    self.day_buttons[day] = btn

        self._update_totals()

    def _open_day_dialog(self, day):
        month_key = (self.current_year, self.current_month)
        month_data = self.data_store.get(month_key, {})
        curr_h, curr_m = month_data.get(day, (0, 0))

        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Dzień {day}")
        dialog.geometry("260x170")
        dialog.configure(fg_color=THEME_BG)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        month_name = MIESIACE_PL[self.current_month]
        ctk.CTkLabel(
            dialog,
            text=f"Czas pracy: {day} {month_name}",
            font=ctk.CTkFont(
                family=THEME_FONT_FAMILY, size=11, weight="bold"
            ),
            text_color=THEME_FG,
        ).pack(pady=(12, 8))

        frame_in = ctk.CTkFrame(dialog, fg_color=THEME_BG)
        frame_in.pack(pady=5)

        ctk.CTkLabel(
            frame_in,
            text="Godz:",
            font=ctk.CTkFont(family=THEME_FONT_FAMILY, size=10),
            text_color=THEME_FG,
        ).grid(row=0, column=0, padx=4)
        entry_h = ctk.CTkEntry(
            frame_in,
            width=50,
            fg_color=THEME_FIELD_BG,
            text_color=THEME_FG,
            justify="center",
        )
        entry_h.insert(0, str(curr_h) if curr_h > 0 else "")
        entry_h.grid(row=0, column=1, padx=(0, 8))

        ctk.CTkLabel(
            frame_in,
            text="Min:",
            font=ctk.CTkFont(family=THEME_FONT_FAMILY, size=10),
            text_color=THEME_FG,
        ).grid(row=0, column=2, padx=4)
        entry_m = ctk.CTkEntry(
            frame_in,
            width=50,
            fg_color=THEME_FIELD_BG,
            text_color=THEME_FG,
            justify="center",
        )
        entry_m.insert(0, str(curr_m) if curr_m > 0 else "")
        entry_m.grid(row=0, column=3)
        entry_h.focus_set()

        def save(event=None):
            h_raw = entry_h.get().strip()
            m_raw = entry_m.get().strip()

            if not h_raw and not m_raw:
                if month_key in self.data_store:
                    self.data_store[month_key].pop(day, None)
            else:
                try:
                    h = int(h_raw) if h_raw else 0
                    m = int(m_raw) if m_raw else 0

                    if h < 0 or m < 0 or m >= 60:
                        raise ValueError

                    if month_key not in self.data_store:
                        self.data_store[month_key] = {}

                    if h == 0 and m == 0:
                        self.data_store[month_key].pop(day, None)
                    else:
                        self.data_store[month_key][day] = (h, m)

                except ValueError:
                    messagebox.showerror(
                        "Błąd", "Wpisz poprawne godziny i minuty (0-59)."
                    )
                    return

            dialog.destroy()
            self._update_totals()
            self._save_data()

        entry_h.bind("<Return>", save)
        entry_h.bind("<KP_Enter>", save)
        entry_m.bind("<Return>", save)
        entry_m.bind("<KP_Enter>", save)
        dialog.bind("<Return>", save)
        dialog.bind("<KP_Enter>", save)

        # Funkcje przełączające fokus między polami
        def focus_m(event):
            entry_m.focus_set()
            entry_m.select_range(0, tk.END)
            return "break"

        def focus_h(event):
            entry_h.focus_set()
            entry_h.select_range(0, tk.END)
            return "break"

        # Podpięcie zdarzeń klawiatury
        entry_h.bind("<Right>", focus_m)  # Strzałka w prawo w godzinach -> minuty
        entry_h.bind("<Tab>", focus_m)  # Tab w godzinach -> minuty
        entry_m.bind("<Left>", focus_h)  # Strzałka w lewo w minutach -> godziny

        # Funkcja wyzerowania wpisu dla danego dnia
        def clear_day():
            if month_key in self.data_store:
                self.data_store[month_key].pop(day, None)
            dialog.destroy()
            self._update_totals()
            self._save_data()

        # Kontener na przyciski obok siebie
        frame_btns = ctk.CTkFrame(dialog, fg_color=THEME_BG)
        frame_btns.pack(pady=12)

        # Czerwony przycisk Wyzeruj
        btn_clear_day = ctk.CTkButton(
            frame_btns,
            text="Wyzeruj",
            fg_color="#ff5555",
            hover_color="#ff3333",
            text_color="#ffffff",
            width=80,
            command=clear_day,
        )
        btn_clear_day.grid(row=0, column=0, padx=5)

        # Niebieski przycisk Zapisz
        btn_save = ctk.CTkButton(
            frame_btns,
            text="Zapisz",
            fg_color=THEME_ACCENT,
            text_color=THEME_ACCENT_FG,
            width=100,
            command=save,
        )
        btn_save.grid(row=0, column=1, padx=5)

        dialog.focus_force()

    def _workdays_in_month(self):
        """Liczba dni roboczych (Pn-Pt) w wyświetlanym miesiącu.
        Święta nie są uwzględniane."""
        weeks = calendar.monthcalendar(self.current_year, self.current_month)
        return sum(
            1
            for week in weeks
            for col, day in enumerate(week)
            if day != 0 and col < 5
        )

    def _contract_name(self):
        """Nazwa do wyświetlenia: wymiar etatu albo 'Zlecenie'."""
        if self.settings["contract"] == "zlecenie":
            return "Zlecenie"
        etat = self.settings["employment"]
        return next(
            (n for n, v in ETATY.items() if v == etat), f"{etat:g} etatu"
        )

    def _update_progress(self, hours, salary):
        s = self.settings
        if s["contract"] == "etat":
            # Etat: pasek = przepracowany czas względem normy etatu
            workdays = self._workdays_in_month()
            target = workdays * HOURS_PER_DAY * s["employment"]
            ratio = hours / target if target > 0 else 0
            title = f"{hours:.1f} / {target:.0f} h"
            info = (
                f"{ratio * 100:.0f}% normy "
                f"({self._contract_name()}, {workdays} dni roboczych)"
            )
        elif s["bar_mode"] == "kwota":
            # Zlecenie, pasek kwoty
            goal = s["monthly_goal"]
            ratio = salary / goal if goal > 0 else 0
            title = (
                f"{salary:.0f} / {goal:.0f} zł"
                if goal > 0
                else f"{salary:.0f} zł"
            )
            info = (
                f"{ratio * 100:.0f}% celu: {goal:.0f} zł"
                if goal > 0
                else "Ustaw cel kwoty w ustawieniach (⚙)"
            )
        else:
            # Zlecenie, pasek czasu pracy
            goal_h = s["goal_hours"]
            ratio = hours / goal_h if goal_h > 0 else 0
            title = (
                f"{hours:.1f} / {goal_h:g} h"
                if goal_h > 0
                else f"{hours:.1f} h"
            )
            info = (
                f"{ratio * 100:.0f}% celu: {goal_h:g} h"
                if goal_h > 0
                else "Ustaw cel czasu pracy w ustawieniach (⚙)"
            )

        self.lbl_progress.configure(text=title)
        self.lbl_progress_info.configure(text=info)
        self.progress.set(min(ratio, 1.0))
        self.progress.configure(
            progress_color="#50fa7b" if ratio >= 1.0 else THEME_ACCENT
        )

    def _update_totals(self):
        rate = self.settings["hourly_rate"]

        if rate > 0:
            self.lbl_info.configure(
                text=f"Stawka: {rate:.2f} zł/h  ·  {self._contract_name()}"
            )
        else:
            self.lbl_info.configure(text="Ustaw stawkę w ustawieniach (⚙)")

        month_key = (self.current_year, self.current_month)
        month_data = self.data_store.get(month_key, {})

        total_dec_hours = 0.0
        total_minutes_raw = 0
        total_hours_raw = 0

        for day, btn in self.day_buttons.items():
            if day in month_data:
                h, m = month_data[day]
                dec_h = h + (m / 60.0)

                total_dec_hours += dec_h
                total_hours_raw += h
                total_minutes_raw += m

                earned = dec_h * rate
                btn.configure(
                    text=f"{day}\n{earned:.0f}zł ({dec_h:.1f}h)",
                    fg_color="#2d4f3e",
                    text_color="#50fa7b",
                )
            else:
                btn.configure(
                    text=f"{day}\n-",
                    fg_color=THEME_FIELD_BG,
                    text_color=THEME_FG,
                )

        total_salary = total_dec_hours * rate
        extra_h, final_m = divmod(total_minutes_raw, 60)
        final_h = total_hours_raw + extra_h

        self.lbl_suma_godzin.configure(
            text=f"Suma: {final_h}h {final_m}m ({total_dec_hours:.2f}h)"
        )
        self.lbl_suma_wyplaty.configure(
            text=f"Wypłata: {total_salary:.2f} zł"
        )
        self._update_progress(total_dec_hours, total_salary)

    def poprzedni_miesiac(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._render_calendar()

    def nastepny_miesiac(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._render_calendar()

    def _save_data(self):
        serialized_data = {
            f"{rok}-{msc}": {str(dzien): h_m for dzien, h_m in dni.items()}
            for (rok, msc), dni in self.data_store.items()
        }
        payload = {"schedule": serialized_data}

        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=4)
        except Exception as e:
            print(f"Błąd zapisu: {e}")

    def _load_data(self):
        if not os.path.exists(DATA_FILE):
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                payload = json.load(f)

            # Migracja: stawka ze starego pliku danych -> settings.json
            old_rate = payload.get("rate")
            if old_rate and not self.settings["hourly_rate"]:
                try:
                    self.settings["hourly_rate"] = float(
                        str(old_rate).replace(",", ".")
                    )
                    save_settings(self.settings)
                except ValueError:
                    pass

            schedule = payload.get("schedule", {})
            for key, dni in schedule.items():
                rok, msc = map(int, key.split("-"))
                self.data_store[(rok, msc)] = {
                    int(dzien): tuple(h_m) for dzien, h_m in dni.items()
                }
        except Exception as e:
            print(f"Błąd odczytu: {e}")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    app = Application(root)
    root.mainloop()