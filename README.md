# TechHelper3

## Jak uruchomić aplikację?

1. **Utwórz i aktywuj wirtualne środowisko (opcjonalnie, zalecane):**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Zainstaluj wymagane pakiety:**

   ```powershell
   pip install -r requirements.txt
   ```

3. **Uruchom serwer FastAPI:**

   ```powershell
   uvicorn techhelper_fastapi.main:app --reload
   ```

   **Alternatywnie:**

   Możesz uruchomić aplikację jednym poleceniem:

   ```powershell
   ./run.ps1
   ```

   Skrypt automatycznie aktywuje wirtualne środowisko i uruchamia serwer FastAPI.

4. **Wejdź w przeglądarce na adres:**
   [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

Aby zatrzymać serwer, naciśnij `Ctrl+C` w terminalu.
