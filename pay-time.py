import calendar
import datetime
import json
import os
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "wyplaty_data.json")

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

THEME_BG = "#2b2b2b"
THEME_FG = "#e8e8e8"
THEME_ACCENT = "#4a9eff"
THEME_ACCENT_FG = "#ffffff"
THEME_FIELD_BG = "#3c3c3c"
THEME_FONT_FAMILY = "Segoe UI"
THEME_FONT_SIZE = 11


class Application:

    def __init__(self, root):
        self.root = root
        root.title("Kalkulator Wypłaty")
        root.geometry("560x520")
        root.minsize(480, 480)  # Minimalny rozmiar okna
        root.configure(fg_color=THEME_BG)

        root.update_idletasks()
        root.geometry(
            f"+{(root.winfo_screenwidth() - 560) // 2}+{(root.winfo_screenheight() - 520) // 2}"
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

        # ---------------- 1. Górna sekcja: Stawka ----------------
        self.frame_rate = ctk.CTkFrame(root, fg_color=THEME_BG)
        self.frame_rate.grid(
            row=0, column=0, padx=20, pady=(15, 5), sticky="ew"
        )
        self.frame_rate.grid_columnconfigure(0, weight=1)

        self.label1 = ctk.CTkLabel(
            self.frame_rate,
            text="Wpisz godzinową stawkę (zł):",
            text_color=THEME_FG,
            font=ctk.CTkFont(family=THEME_FONT_FAMILY, size=THEME_FONT_SIZE),
        )
        self.label1.grid(row=0, column=0, padx=(10, 10), pady=5, sticky="e")

        self.stawka = ctk.CTkEntry(
            self.frame_rate,
            fg_color=THEME_FIELD_BG,
            text_color=THEME_FG,
            font=ctk.CTkFont(
                family=THEME_FONT_FAMILY, size=THEME_FONT_SIZE, weight="bold"
            ),
            width=120,
            height=30,
            justify="center",
        )
        self.stawka.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="e")
        self.stawka.insert(0, "28.10")
        self.stawka.bind("<KeyRelease>", lambda e: self._on_rate_change())

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

        # ---------------- 4. Podsumowanie na dole ----------------
        self.frame4 = ctk.CTkFrame(root, border_width=1, fg_color=THEME_BG)
        self.frame4.grid(row=3, column=0, padx=20, pady=(5, 15), sticky="ew")
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

        # Przechwytywanie Entera dla okienka dialogowego
        dialog.focus_force()
        dialog.bind("<Return>", lambda e: save())
        dialog.bind("<KP_Enter>", lambda e: save())

    def _update_totals(self):
        try:
            rate_val = self.stawka.get().replace(",", ".")
            rate = float(rate_val) if rate_val else 0.0
        except ValueError:
            rate = 0.0

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

    def _on_rate_change(self):
        self._update_totals()
        self._save_data()

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
        payload = {"rate": self.stawka.get(), "schedule": serialized_data}

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

            raw_rate = payload.get("rate", "28.10")
            self.stawka.delete(0, tk.END)
            self.stawka.insert(0, raw_rate)

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