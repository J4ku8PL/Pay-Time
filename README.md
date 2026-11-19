# PayTime (Kalkulator Wypłaty)

[Polski](#polski) | [English](#english)

---

## Polski

Aplikacja do wpisywania czasu pracy i liczenia szacowanej wypłaty. Teraz działa jako program desktopowy w Pythonie, a w planach jest wersja mobilna (Flutter) i online. Rozwijam ją jako projekt portfolio (build in public).

### Funkcje (wersja 2.0)

- **Kalendarz miesięczny:** kliknij dzień i wpisz godziny oraz minuty.
- **Podsumowanie:** suma godzin i szacowana wypłata brutto (godziny × stawka).
- **Ustawienia (⚙):** stawka, rodzaj umowy, wymiar etatu, cele.
- **Etat** (pełny, 3/4, 1/2, 1/4): progress bar pokazuje godziny względem normy miesiąca.
- **Zlecenie:** własny cel miesięczny w zł albo w godzinach, pasek pokazuje jedną z tych wartości.
- **Dane lokalne:** `PT_data.json` (godziny) i `settings.json` (ustawienia).

### Uruchomienie

Python 3, testowane na Windows.

```
pip install customtkinter
python pay_time.py
```

### Struktura

```
pay_time.py     # okno główne, kalendarz, obliczenia
settings.py     # ustawienia, motyw, okno ustawień
```

Foldery Fluttera (`android`, `ios`, `web` itd.) są zarezerwowane na przyszłą wersję mobilną.

### Roadmapa

- [x] Panel ustawień, wybór umowy i cele
- [x] Progress bar dopasowany do umowy
- [ ] Tryb wpisywania godziny wejścia i wyjścia
- [ ] 2.1: interfejs i dokumentacja po angielsku
- [ ] Wypłata netto według polskich zasad (ulga dla młodych, status studenta)
- [ ] 3.0: nowy wygląd interfejsu
- [ ] Wersja mobilna (Flutter) 
- [ ] PayTime Online (baza SQL, chmura) w przyszłości

Projekt rozwijam z pomocą asystenta AI. Decyzje o funkcjach i architekturze podejmuję samodzielnie.

---

## English

A tool for logging working hours and estimating pay. It is currently a Python desktop app, with a mobile version (Flutter) and an online version planned. I build it as a portfolio project (build in public).

> **The interface is in Polish** (labels, buttons, messages, month names) and the app follows **Polish work realities**. An English interface is planned for v2.1.

### Polish work realities

- **Etat** = employment contract (*umowa o pracę*), **Zlecenie** = contract of mandate (*umowa zlecenie*).
- **Monthly norm** for Etat = working days (Mon-Fri) × 8 h × employment size. Public holidays are not subtracted yet.
- **Amounts** are in Polish zloty (PLN) and shown **gross**. Polish tax rules (e.g. relief for under 26, student status) are planned.

### Interface glossary

| In the app | Meaning |
|---|---|
| Stawka godzinowa (zł) | Hourly rate (PLN) |
| Godz / Min | Hours / Minutes |
| Zapisz / Wyzeruj | Save / Reset |
| Suma / Wypłata | Total hours / Payout |
| Rodzaj umowy | Contract type |
| Etat / Zlecenie | Employment contract / Contract of mandate |
| Pełny etat, 3/4, 1/2, 1/4 etatu | Full-time, 3/4, 1/2, 1/4 |
| Cel kwoty / Cel czasu pracy | Amount goal / Working time goal |
| Pasek pokazuje: Kwota / Czas pracy | Bar shows: Amount / Working time |

### Features (version 2.0)

- **Monthly calendar:** click a day and enter hours and minutes.
- **Summary:** total hours and estimated gross pay (hours × rate).
- **Settings (⚙):** rate, contract type, employment size, goals.
- **Etat** (full, 3/4, 1/2, 1/4): the progress bar shows hours against the monthly norm.
- **Zlecenie:** your own monthly goal in PLN or in hours, the bar shows one of them.
- **Local data:** `PT_data.json` (hours) and `settings.json` (settings).

### Running

Python 3, tested on Windows.

```
pip install customtkinter
python pay_time.py
```

### Structure

```
pay_time.py     # main window, calendar, calculations
settings.py     # settings, theme, settings window
```

The Flutter folders (`android`, `ios`, `web`, etc.) are reserved for the future mobile version.

### Roadmap

- [x] Settings panel, contract type and goals
- [x] Progress bar adapted to the contract
- [ ] Clock-in / clock-out entry mode
- [ ] 2.1: English interface and documentation
- [ ] Net pay based on Polish rules (relief for under 26, student status)
- [ ] 3.0: redesigned UI
- [ ] Mobile version (Flutter) 
- [ ] PayTime Online (SQL database, cloud) in future 

I develop this project with the help of an AI assistant. I make the decisions about features and architecture myself.