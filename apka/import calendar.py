import calendar
import datetime
import tkinter as tk
from tkinter import messagebox


class KalkulatorWyplatyApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Kalkulator Wypłaty")
        self.root.geometry("500x600")

        # Pobranie aktualnego roku i miesiąca
        now = datetime.datetime.now()
        self.year = now.year
        self.month = now.month

        # Słownik na przechowywanie godzin: {dzień: godziny}
        self.work_hours = {}

        self._build_ui()

    def _build_ui(self):
        # Sekcja stawki godzinowej
        frame_top = tk.Frame(self.root, padding=10)
        frame_top.pack(fill="x", padx=10, pady=5)

        tk.Label(
            frame_top, text="Stawka godzinowa (zł/h):", font=("Arial", 11)
        ).pack(side="left")

        self.entry_rate = tk.Entry(frame_top, width=10, font=("Arial", 11))
        self.entry_rate.insert(0, "28.10")
        self.entry_rate.pack(side="left", padx=10)
        self.entry_rate.bind("<KeyRelease>", lambda event: self.update_totals())

        # Nagłówek miesiąca
        month_name = calendar.month_name[self.month]
        tk.Label(
            self.root,
            text=f"Miesiąc: {month_name} {self.year}",
            font=("Arial", 14, "bold"),
        ).pack(pady=5)

        # Siatka kalendarza
        self.frame_calendar = tk.Frame(self.root)
        self.frame_calendar.pack(pady=10)

        self._generate_calendar()

        # Podsumowanie na dole
        self.frame_summary = tk.Frame(self.root)
        self.frame_summary.pack(fill="x", side="bottom", pady=15)

        self.label_hours = tk.Label(
            self.frame_summary,
            text="Godziny: 0 h",
            font=("Arial", 11),
            fg="#555555",
        )
        self.label_hours.pack()

        self.label_total = tk.Label(
            self.frame_summary,
            text="Suma do wypłaty: 0.00 zł",
            font=("Arial", 14, "bold"),
            fg="#2e7d32",
        )
        self.label_total.pack(pady=5)

    def _generate_calendar(self):
        # Dni tygodnia
        days_headers = ["Pn", "Wt", "Śr", "Czw", "Pt", "Sob", "Ndz"]
        for col, h in enumerate(days_headers):
            lbl = tk.Label(
                self.frame_calendar,
                text=h,
                font=("Arial", 10, "bold"),
                width=6,
            )
            lbl.grid(row=0, column=col, padx=2, pady=2)

        # Dni miesiąca
        month_cal = calendar.monthcalendar(self.year, self.month)
        self.day_buttons = {}

        for row_idx, week in enumerate(month_cal, start=1):
            for col_idx, day in enumerate(week):
                if day != 0:
                    btn = tk.Button(
                        self.frame_calendar,
                        text=f"{day}\n-",
                        width=6,
                        height=2,
                        bg="#f0f0f0",
                        command=lambda d=day: self.set_hours_dialog(d),
                    )
                    btn.grid(row=row_idx, column=col_idx, padx=2, pady=2)
                    self.day_buttons[day] = btn

    def set_hours_dialog(self, day):
        # Okienko zapytania o godziny dla danego dnia
        current_val = str(self.work_hours.get(day, ""))

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Dzień {day}")
        dialog.geometry("250x130")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog, text=f"Ile godzin przepracowano (dzień {day})?"
        ).pack(pady=10)

        entry = tk.Entry(dialog, width=10)
        entry.insert(0, current_val)
        entry.focus_set()
        entry.pack()

        def save():
            val = entry.get().strip()
            if not val:
                self.work_hours.pop(day, None)
            else:
                try:
                    hours = float(val)
                    if hours > 0:
                        self.work_hours[day] = hours
                    else:
                        self.work_hours.pop(day, None)
                except ValueError:
                    messagebox.showerror(
                        "Błąd", "Wpisz poprawną liczbę godzin."
                    )
                    return
            dialog.destroy()
            self.update_totals()

        tk.Button(dialog, text="Zapisz", command=save).pack(pady=10)

    def update_totals(self):
        try:
            rate = float(self.entry_rate.get())
        except ValueError:
            rate = 0.0

        total_hours = sum(self.work_hours.values())
        total_salary = total_hours * rate

        # Aktualizacja przycisków na kalendarzu
        for day, btn in self.day_buttons.items():
            if day in self.work_hours:
                h = self.work_hours[day]
                earned = h * rate
                btn.config(
                    text=f"{day}\n{earned:.0f} zł",
                    bg="#c8e6c9",
                    activebackground="#a5d6a7",
                )
            else:
                btn.config(text=f"{day}\n-", bg="#f0f0f0")

        # Aktualizacja podsumowania
        self.label_hours.config(text=f"Suma godzin: {total_hours:.1f} h")
        self.label_total.config(
            text=f"Suma do wypłaty: {total_salary:.2f} zł"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = KalkulatorWyplatyApp(root)
    root.mainloop()