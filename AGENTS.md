# 🤖 AGENTS.md — TechHelper: Moduł Kalkulatorów i Bazy Narzędzi

## 🏗️ Architektura projektu

**Technologie:**
| Element | Technologia | Rola | Ocena |
|----------|--------------|------|--------|
| Backend | 🐍 FastAPI | API + logika backendu | ✅ Nowoczesny, szybki, prosty w użyciu i doskonały dla prototypów |
| Frontend | ⚡ HTMX | Dynamiczne aktualizacje HTML bez JS | ✅ Świetny do prostych, interaktywnych UI bez frameworków JS |
| Styling | 🎨 TailwindCSS (CDN) | Stylowanie | ✅ Minimalna konfiguracja, bardzo szybkie tworzenie ładnego UI |
| Database | 🗄️ SQLite | Baza danych | ✅ Zero konfiguracji, idealna dla MVP, łatwa do przeniesienia |
| ORM | 🗃️ SQLModel | ORM + Pydantic | ✅ Spójny z FastAPI, prosty model danych, wygodny dla CRUD |
| Szablony | 🧩 Jinja2 | Widoki HTML | ✅ Klasyczne rozwiązanie, dobrze współgra z HTMX i FastAPI |

---

## 🎯 Scope MVP

### ✅ Co MUSI być w MVP:

1. **Kalkulator prędkości i posuwu** - pełna funkcjonalność
2. **Kalkulator kosztu obróbki** - pełna funkcjonalność (max 10 operacji)
3. **Baza narzędzi** - wszystkie 3 typy (Głowice, Frezy, Wiertła)
   - CRUD (Create, Read, Update, Delete) przez UI
   - Filtrowanie i wyszukiwanie
4. **UI/UX:**
   - Osobne podstrony dla każdego modułu
   - Nawigacja między modułami
   - Desktop only (nie musi być responsywne na telefon)
   - Praca przez przeglądarkę

### 🚀 Do zrobienia PO MVP:

- **Deployment na Railway.app** (po zakończeniu lokalnego MVP i testów)
- Opcjonalnie: migracja na Azure (w przyszłości)

---

## 🧮 Moduły kalkulatorów

### 1. Kalkulator prędkości i posuwu - Frezowanie

**Cel:** automatyczne rozpoznanie typu obliczenia i wyłączenie niepotrzebnych pól.  
**Funkcje:**

- Użytkownik wprowadza dane: Vc, S, Fz, F, D, z (liczba ostrzy).
- Jeśli wpisane jest Vc → pole S jest nieaktywne (i odwrotnie).
- Jeśli wpisane jest Fz → pole F jest nieaktywne (i odwrotnie).
- Wynik pojawia się na tej samej stronie po pełnym odświeżeniu.
- Logika obliczeń w osobnym pliku Pythona (np. `calculations/feed_speed.py`).
- Przycisk „CLEAR" — reset wszystkich pól.

**Wzory:**

```
Vc = (π × D × n) / 1000
n = (1000 × Vc) / (π × D)
F = Fz × z × n
Fz = F / (z × n)
```

**Podstrona:** `/calculators/speed-feed`

---

### 2. Kalkulator prędkości i posuwu - Frezowanie

🎯 Zakres funkcjonalny

Kalkulator powinien umożliwiać obliczenia parametrów skrawania dla wiercenia, z logiką odmienną od frezowania.

📌 Parametry wejściowe

Średnica wiertła D (mm)

Prędkość skrawania Vc (m/min) lub obroty n (obr/min) — wzajemnie zależne

Posuw na obrót fn (mm/obr) lub posuw F (mm/min) — wzajemnie zależne

(opcjonalnie) Rodzaj wiertła – może wpływać na domyślne zakresy, ale na etapie MVP nie wymaga dodatkowej logiki

🧮 Wzory obliczeń (wiercenie)
Vc = (π × D × n) / 1000
n = (1000 × Vc) / (π × D)
F = fn × n
fn = F / n
🔧 Zasady działania

Jeśli użytkownik wpisze Vc, pole n staje się nieaktywne (i odwrotnie).

Jeśli użytkownik wpisze fn, pole F jest nieaktywne (i odwrotnie).

Wyniki wyświetlane po pełnym odświeżeniu sekcji (HTMX).

Wszystkie pola mają walidację (wartości dodatnie, liczby, D > 0).

🖥️ UI i szablony

Osobny template HTML: drilling_speed_feed.html

Pola ułożone w takiej samej kolejności jak w kalkulatorze frezowania, ale z nazwami właściwymi dla wiercenia (fn zamiast fz).

Przycisk CLEAR resetuje cały formularz.

🛣️ Routing

Endpoint GET: /calculators/drilling-speed-feed

Endpoint POST (przeliczenia): /calculators/drilling-speed-feed/calculate

🧠 Logika Pythona

Plik: calculations/drilling_feed_speed.py

Zawiera:

funkcje do obliczeń n, Vc, F, fn

funkcję wykrywającą, które pola podał użytkownik

zwracanie błędów wejściowych (np. brak wystarczających danych)

✔ Testy

Przeliczenia Vc ↔ n

Przeliczenia fn ↔ F

Walidacja danych błędnych (np. D = 0, fn < 0)

Test HTMX: poprawne odświeżanie tabeli wyników

### 3. Kalkulator kosztu obróbki

**Cel:** obliczenie kosztu operacji na podstawie czasu i typu maszyny.

**Parametry wejściowe (dla każdej z max. 10 operacji):**

- Grupa maszyny (wybór z listy dropdown)
- Czas przygotowawczo-zakończeniowy `Tpz` (min)
- Czas jednostkowy `Tj` (min)

**Obliczenia:**

- Koszt Tpz = (Tpz / 60) × stawka
- Koszt Tj = (Tj / 60) × stawka
- Suma: Σ (Koszt Tpz + Koszt Tj) dla wszystkich operacji

**Domyślne stawki (PLN/h):**
| Grupa | Opis | Stawka |
|--------|------|---------|
| 1 | Frezarka konwencjonalna do 600 mm | 110 |
| 2 | Frezarka konwencjonalna powyżej 600 mm | 120 |
| 4 | Tokarka CNC | 120 |
| 5 | Frezarka CNC stara | 120 |
| 6 | Frezarka CNC nowa | 140 |
| 7 | Frezarka CNC z głowicą skrętną | 180 |
| 9 | Frezarka CNC nowa pozioma | 140 |
| 10 | Wytaczarka CNC ponad 2000 mm | 220 |
| 16 | Frezarka bramowa CNC | 220 |
| 17 | Obróbka ślusarska | 90 |

**UI:**

- Możliwość dynamicznego dodawania kolejnych operacji (do 10)
- Przycisk "Dodaj operację"
- Przycisk "Usuń operację"
- Suma kosztów na dole
- Przycisk "CLEAR" - reset wszystkich pól

**Uwagi:**

- Na razie stawki są stałe (zakodowane w aplikacji, bez edycji w UI).
- W przyszłości można dodać możliwość ich modyfikacji.

**Podstrona:** `/calculators/cost`

---

## 🧰 Baza narzędzi

### 🎯 Wymagania ogólne dla wszystkich baz:

- **CRUD:** Create, Read, Update, Delete przez UI
- **Filtrowanie:** po średnicy i symbolu narzędzia (minimum)
- **Wyszukiwanie:** live search (HTMX)
- **Tabela:** sortowanie kolumn
- **Formularze:** walidacja danych
- **UI:** przyciski "Dodaj", "Edytuj", "Usuń"

---

### 1. Głowice frezarskie (Milling_Heads)

**Model SQLModel:**
| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| id | int | Auto | Primary Key |
| średnica_D_mm | float | ✅ | Średnica narzędzia |
| symbol_narzędzia | str | ✅ | Symbol katalogowy |
| producent | str | ❌ | Producent narzędzia |
| symbol_płytki | str | ❌ | Symbol i gatunek płytki |
| liczba_ostrzy | int | ✅ | Ilość ostrzy (z) |
| materiał | str | ❌ | Obrabiany materiał |
| posuw_na_ząb_min | float | ❌ | Minimalny fz |
| posuw_na_ząb_max | float | ❌ | Maksymalny fz |
| prędkość_skrawania_min | float | ❌ | Minimalna Vc |
| prędkość_skrawania_max | float | ❌ | Maksymalna Vc |
| obroty | float | ❌ | n (obr/min) |
| posuw | float | ❌ | F (mm/min) |
| głębokość_skrawania_ap | float | ❌ | ap (mm) |
| uwagi | str | ❌ | Dodatkowe informacje |

**Filtrowanie:** po `średnica_D_mm`, `symbol_narzędzia`, `producent`

**Podstrona:** `/tools/milling-heads`

---

### 2. Frezy (Milling_Cutters)

**Model SQLModel:**
| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| id | int | Auto | Primary Key |
| średnica_D_mm | float | ✅ | Średnica narzędzia |
| symbol_narzędzia | str | ✅ | Symbol katalogowy |
| producent | str | ❌ | Producent narzędzia |
| liczba_ostrzy | int | ✅ | Ilość ostrzy (z) |
| materiał | str | ❌ | Obrabiany materiał |
| posuw_na_ząb_min | float | ❌ | Minimalny fz |
| posuw_na_ząb_max | float | ❌ | Maksymalny fz |
| prędkość_skrawania_min | float | ❌ | Minimalna Vc |
| prędkość_skrawania_max | float | ❌ | Maksymalna Vc |
| obroty | float | ❌ | n (obr/min) |
| posuw | float | ❌ | F (mm/min) |
| głębokość_skrawania_ap | float | ❌ | ap (mm) |
| szerokość_skrawania_ae_procent | float | ❌ | ae (% średnicy D) |
| uwagi | str | ❌ | Dodatkowe informacje |

**Filtrowanie:** po `średnica_D_mm`, `symbol_narzędzia`, `producent`

**Podstrona:** `/tools/milling-cutters`

---

### 3. Wiertła (Drills)

**Model SQLModel:**
| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| id | int | Auto | Primary Key |
| średnica_D_mm | float | ✅ | Średnica narzędzia |
| symbol_narzędzia | str | ✅ | Symbol katalogowy |
| producent | str | ❌ | Producent narzędzia |
| rodzaj_wiertła | str | ✅ | HSS / VHM / na 1 płytkę / na 2 płytki |
| symbol_płytki | str | ❌ | (opcjonalnie) Symbol płytki |
| długość_robocza_mm | float | ❌ | Długość robocza |
| liczba_ostrzy | int | ❌ | Ilość ostrzy |
| posuw_fn_min | float | ❌ | Minimalny fn (mm/obr) |
| posuw_fn_max | float | ❌ | Maksymalny fn (mm/obr) |
| prędkość_skrawania_min | float | ❌ | Minimalna Vc |
| prędkość_skrawania_max | float | ❌ | Maksymalna Vc |
| obroty | float | ❌ | n (obr/min) |
| posuw | float | ❌ | F (mm/min) |
| uwagi | str | ❌ | Dodatkowe informacje |

**Filtrowanie:** po `średnica_D_mm`, `symbol_narzędzia`, `rodzaj_wiertła`, `producent`

**Podstrona:** `/tools/drills`

---

---

## 🔐 System użytkowników (POST-MVP)

**Cel:**  
Zabezpieczenie bazy danych i kalkulatorów przed nieautoryzowanymi zmianami.

**Założenia:**

- **Etap 1:** tylko 1 użytkownik (`admin`), dane logowania zapisane w `.env`.
- **Etap 2:** system wielu użytkowników z poziomami uprawnień:
  - `admin` – pełny dostęp (CRUD, kalkulatory)
  - `viewer` – tylko odczyt danych
- Uwierzytelnianie przez **FastAPI Security** (`OAuth2PasswordBearer` + JWT).
- Hasła szyfrowane przy użyciu `bcrypt`.
- Middleware sprawdzające token JWT przed każdą operacją modyfikującą dane.
- Endpointy:
  - `/auth/login` – zwraca token JWT
  - `/auth/logout` – unieważnia token (opcjonalnie)
  - `/auth/me` – zwraca dane zalogowanego użytkownika
- W UI: ukrycie przycisków „Dodaj / Edytuj / Usuń”, jeśli użytkownik ma rolę `viewer`.

**Struktura (propozycja katalogów):**

```
├── routers/
│   ├── auth.py               # logowanie, generowanie tokenów
│   └── tools.py              # CRUD narzędzi (z zabezpieczeniem JWT)
│
├── models/
│   ├── user.py               # model użytkownika SQLModel
│   ├── milling_heads.py
│   ├── milling_cutters.py
│   └── drills.py
```

**Dodatkowe kroki w Roadmapie (POST-MVP):**

- [ ] Dodać model `User` w SQLModel
- [ ] Zaimplementować JWT i middleware autoryzacji
- [ ] Przygotować prosty formularz logowania (HTML + HTMX)
- [ ] Testy uprawnień i poprawności logowania
- [ ] Aktualizacja dokumentacji

---

## 🌐 Deployment Strategy

### 🎯 POST-MVP: Railway.app

**⚠️ UWAGA: Deployment dopiero PO zakończeniu i przetestowaniu lokalnego MVP!**

**Dlaczego Railway:**

- ✅ Prosty deployment (git push = auto deploy)
- ✅ Darmowy tier: 500h/miesiąc + $5 creditu
- ✅ Obsługuje SQLite z persistent volume
- ✅ Automatyczne SSL i domena
- ✅ Idealne dla FastAPI

**Kroki (do wykonania PO MVP):**

1. Przygotować `requirements.txt`
2. Dodać `Procfile` lub `railway.toml`
3. Stworzyć konto na Railway.app
4. Podłączyć repo GitHub
5. Skonfigurować persistent volume dla SQLite
6. Deploy!

**Koszt:**

- Free tier na start
- ~$5-10/miesiąc przy intensywnym użyciu

**URL docelowy:** `https://techhelper-production.up.railway.app`

### 🔷 Opcjonalnie w przyszłości: Azure App Service

- Migracja gdy aplikacja urośnie
- Azure SQL Database zamiast SQLite
- CI/CD przez GitHub Actions
- Koszt: ~$15-30/miesiąc

---

## 🚀 Roadmap MVP

### Etap 1: Setup projektu (2-3h)

- [x] Struktura katalogów
- [x] Konfiguracja FastAPI
- [x] Setup SQLite + SQLModel
- [x] Podstawowe szablony Jinja2
- [x] Routing (strona główna + nawigacja)
- [x] TailwindCSS CDN

### Etap 2: Kalkulator obrotów i posuwu - Frezowanie (3-4h)

- [x] Model danych (jeśli potrzebny)
- [x] Logika obliczeń (`calculations/feed_speed.py`)
- [x] Template HTML + HTMX
- [x] Routing i endpointy
- [x] Walidacja inputów
- [x] Testy funkcjonalności

### Etap 2.5: Kalkulator obrotów i posuwu - Wiercenie (2-3h)

- [x] Model danych/specyfikacja różnic dla wiercenia
- [x] Logika obliczeń (`calculations/drilling_feed_speed.py`)
- [x] Template HTML + HTMX (wariant wiercenia)
- [x] Routing i endpointy (`/calculators/drilling-speed-feed`)
- [x] Walidacja inputów
- [x] Testy funkcjonalności

### Etap 3: Kalkulator kosztu obróbki (3-4h)

- [x] Model danych (operacje)
- [x] Logika obliczeń (`calculations/cost.py`)
- [x] Template HTML + HTMX (dynamiczne operacje)
- [x] Routing i endpointy
- [x] Walidacja inputów
- [x] Testy funkcjonalności

### Etap 4: Baza Głowic Frezarskich (4-5h)

- [x] Model SQLModel
- [x] CRUD endpoints
- [x] Template: lista + tabela
- [x] Template: formularz add/edit
- [x] Template: strona szczegółów
- [x] Filtrowanie i wyszukiwanie (HTMX)
- [x] Delete functionality
- [x] Sortowanie po średnicy (domyślnie rosnąco)
- [x] Endpoint szczegółów narzędzia
- [x] Przycisk "Szczegóły" w tabeli
- [x] Testy CRUD + testy dla szczegółów (26 testów)
- [x] Nawigacja między modułami

### Etap 5: Baza Frezów (3-4h)

- [x] Model SQLModel (15 fields: 3 required + 12 optional + ae_percent)
- [x] CRUD endpoints (9 total: list, filter, add_form, edit_form, details, create, update, delete, home)
- [x] Templates (4: list, form, details, table partial)
- [x] Filtrowanie (symbol, manufacturer, diameter)
- [x] Testy CRUD (26 tests - CREATE:6, READ:4, UPDATE:2, DELETE:1, DETAILS:2, FILTER:5, INTEGRATION:1, EDGE:5)
- [x] Sorting by diameter (default ascending)
- [x] HTMX integration
- [x] Validation (required fields, positive numerics)
- [x] Database registration (SQLModel metadata)
- [x] UI activation (Frezy button in tools/index.html)

### Etap 6: Baza Wierteł (3-4h)

- [x] Model SQLModel (13 fields: 3 required + 10 optional)
- [x] CRUD endpoints (9 total: list, filter, add_form, edit_form, details, create, update, delete, home)
- [x] Templates (4: list, form, details, table partial)
- [x] Filtrowanie (symbol, manufacturer, drill type)
- [x] Testy CRUD (26 tests - CREATE:6, READ:4, UPDATE:2, DELETE:1, DETAILS:2, FILTER:5, INTEGRATION:1, EDGE:5)
- [x] Sorting by diameter (default ascending)
- [x] HTMX integration
- [x] Validation (required fields, positive numerics)
- [x] Database registration (SQLModel metadata)
- [x] UI activation (Wiertła button in tools/index.html)

### Etap 7: Integracja i testy końcowe (2-3h)

- [ ] Poprawki UI/UX
- [ ] Testy wszystkich modułów
- [ ] Sprawdzenie nawigacji
- [ ] Walidacja danych we wszystkich formularzach
- [ ] Bug fixing

### Etap 7.5: 🔐 Basic Auth (1-2h)

**⚠️ WYMAGANE przed deploymentem!**

- [ ] Implementacja Basic Auth w FastAPI
- [ ] Zabezpieczenie wszystkich endpointów (kalkulatory + bazy narzędzi)
- [ ] Login/hasło w zmiennych środowiskowych (.env)
- [ ] Middleware autoryzacji
- [ ] Testy dostępu (z i bez autoryzacji)
- [ ] Dokumentacja credentials dla Railway deployment

**Cel:** Zabezpieczenie aplikacji przed nieautoryzowanym dostępem po wdrożeniu na Railway.

### Etap 8: 🌐 Deployment (2-3h)

**⚠️ Dopiero po zakończeniu Etapu 7 i 7.5!**

- [ ] Przygotowanie `requirements.txt`
- [ ] Konfiguracja Railway
- [ ] Deploy na Railway.app
- [ ] Testy produkcyjne
- [ ] Dokumentacja (README)

**Szacowany czas: 22-30h** (rozłożone na ~2 tygodnie przy 1-2h/dzień)

**Status aktualny:**

- ✅ Etapy 1-6 ukończone (Setup, 2 Kalkulatory, Kalkulator kosztów, Baza Głowic, Baza Frezów, Baza Wierteł)
- 🔄 Etapy 7-8 pozostałe (Integracja i testy końcowe, Deployment)
- ✅ Wszystkie testy przechodzą (77/77 testów CRUD - Heads: 26, Cutters: 26, Drills: 25+)
- ✅ UI w pełni funkcjonalne

---

## 📂 Struktura katalogów

```
TechHelper3/                           # ROOT projektu (tu git init)
│
├── README.md                          # Dokumentacja projektu
├── requirements.txt                   # Zależności Python
├── .gitignore                         # Pliki ignorowane przez git
├── AGENTS.md                          # Ten dokument - specyfikacja techniczna
├── .env                               # (opcjonalnie) Zmienne środowiskowe
│
├── techhelper_fastapi/               # Główny folder aplikacji
│   ├── main.py                       # Entry point FastAPI
│   ├── database.py                   # SQLite connection
│   │
│   ├── templates/                    # Szablony Jinja2
│   │   ├── base.html                # Base template z nawigacją
│   │   ├── index.html               # Strona główna
│   │   │
│   │   ├── calculators/
│   │   │   ├── speed_feed.html      # Kalkulator prędkości
│   │   │   └── cost.html            # Kalkulator kosztu
│   │   │
│   │   └── tools/
│   │       ├── milling_heads_list.html      # Lista głowic
│   │       ├── milling_heads_form.html      # Formularz głowic
│   │       ├── milling_cutters_list.html    # Lista frezów
│   │       ├── milling_cutters_form.html    # Formularz frezów
│   │       ├── drills_list.html             # Lista wierteł
│   │       └── drills_form.html             # Formularz wierteł
│   │
│   ├── static/                       # Pliki statyczne
│   │   └── styles.css               # (opcjonalnie) Custom CSS
│   │
│   ├── routers/                      # FastAPI routers
│   │   ├── __init__.py
│   │   ├── calculators.py           # Routing kalkulatorów
│   │   └── tools.py                 # Routing bazy narzędzi
│   │
│   ├── calculations/                 # Logika obliczeń
│   │   ├── __init__.py
│   │   ├── feed_speed.py            # Logika kalkulatora prędkości
│   │   └── cost.py                  # Logika kalkulatora kosztu
│   │
│   └── models/                       # SQLModel modele
│       ├── __init__.py
│       ├── milling_heads.py         # Model SQLModel głowic
│       ├── milling_cutters.py       # Model SQLModel frezów
│       └── drills.py                # Model SQLModel wierteł
│
└── techhelper.db                     # SQLite database (dodane do .gitignore)
```

---

## ✅ Definition of Done (MVP)

MVP jest ukończone gdy:

1. ✅ Oba kalkulatory działają poprawnie (obliczenia + UI)
2. ✅ Wszystkie 3 bazy narzędzi mają pełny CRUD przez UI
3. ✅ Filtrowanie i wyszukiwanie działa
4. ✅ Nawigacja między modułami działa płynnie
5. ✅ Aplikacja jest przetestowana lokalnie
6. ✅ Brak krytycznych bugów
7. ✅ Kod jest czytelny i zorganizowany

**Po spełnieniu powyższych → można przejść do deploymentu na Railway!**

---

## 📝 Notatki techniczne

### SQLite Setup

```python
# database.py
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./techhelper.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

### HTMX Przykład (filtrowanie)

```html
<input
  type="text"
  name="search"
  hx-get="/tools/milling-heads/filter"
  hx-trigger="keyup changed delay:500ms"
  hx-target="#results-table"
  placeholder="Szukaj..."
/>
```

### Stawki maszynowe (do zakodowania w `calculations/cost.py`)

```python
MACHINE_RATES = {
    1: {"name": "Frezarka konwencjonalna do 600 mm", "rate": 110},
    2: {"name": "Frezarka konwencjonalna powyżej 600 mm", "rate": 120},
    4: {"name": "Tokarka CNC", "rate": 120},
    5: {"name": "Frezarka CNC stara", "rate": 120},
    6: {"name": "Frezarka CNC nowa", "rate": 140},
    7: {"name": "Frezarka CNC z głowicą skrętną", "rate": 180},
    9: {"name": "Frezarka CNC nowa pozioma", "rate": 140},
    10: {"name": "Wytaczarka CNC ponad 2000 mm", "rate": 220},
    16: {"name": "Frezarka bramowa CNC", "rate": 220},
    17: {"name": "Obróbka ślusarska", "rate": 90},
}
```

---

**Dokument zaktualizowany:** 2025-11-09  
**Wersja:** 2.0 (z deployment strategy)
