# Generator dni treningowych

Aplikacja generuje plan treningowy na podstawie parametrów użytkownika: masy ciała, wzrostu, liczby dni treningowych, poziomu zaawansowania, celu, dostępnego sprzętu i przeciwwskazań do trenowania wybranych partii mięśniowych.

## Architektura

Projekt składa się z dwóch usług:

- `frontend` - Next.js/React eksportowany statycznie i hostowany np. na Cloudflare Pages.
- `backend` - FastAPI z SQLAlchemy, generatorem planów i serwowaniem statycznych materiałów ćwiczeń.

Dane źródłowe ćwiczeń znajdują się w katalogu `cwiczenia/`. Baza SQLite, cache tłumaczeń i wygenerowane słowniki nie są wersjonowane, bo są artefaktami runtime/build. Seed bazy jest odtwarzalny z plików źródłowych i skryptów backendu.

## Konfiguracja środowiskowa

Backend używa zmiennych:

```env
DATABASE_URL=sqlite:///./data/workout_app.db
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
PORT=8000
```

Frontend używa zmiennych build-time:

```env
NEXT_PUBLIC_API_URL=/api
NEXT_PUBLIC_STATIC_URL=/exercises-static
```

Dla Cloudflare Pages z backendem na Render ustaw:

```env
NEXT_PUBLIC_API_URL=https://ztpproj-generator-treningow.onrender.com/api
NEXT_PUBLIC_STATIC_URL=https://ztpproj-generator-treningow.onrender.com/exercises-static
```

## Uruchomienie lokalne przez Docker Compose

```bash
docker compose up --build
```

Po uruchomieniu:

- frontend: `http://localhost:3000`
- backend healthcheck: `http://localhost:3000/api/health`

Kontener backendu wykonuje jawnie:

1. `python migrate.py` - tworzy/aktualizuje schemat bazy,
2. `python seed_data.py --skip-if-populated` - wypełnia pustą bazę danymi ćwiczeń,
3. `uvicorn main:app` - uruchamia API.

Tabele nie są już tworzone podczas importu aplikacji FastAPI.

## Uruchomienie bez Dockera

Backend:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python migrate.py
python seed_data.py --skip-if-populated
uvicorn main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

W trybie lokalnym frontend domyślnie używa `/api`, więc najlepiej uruchamiać go razem z reverse proxy z Dockera albo ustawić `NEXT_PUBLIC_API_URL=http://localhost:8000/api`.

## Testy i kontrola jakości

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

## Deployment

Rekomendowana darmowa konfiguracja:

- Render Free Web Service dla backendu z `backend/Dockerfile`.
- Cloudflare Pages dla statycznego frontendu.

Render:

- Dockerfile path: `backend/Dockerfile`
- Docker build context: `.`
- Health check path: `/api/health`
- Environment: `CORS_ORIGINS=https://ztpproj-generator-treningow.pages.dev`

Cloudflare Pages:

- Root directory: `frontend`
- Build command: `npm run build`
- Build output directory: `out`
- Variables: `NEXT_PUBLIC_API_URL` i `NEXT_PUBLIC_STATIC_URL` wskazujące publiczny backend Render.

## Najważniejsze pliki

- `backend/main.py` - definicja endpointów API, CORS i statycznych plików ćwiczeń.
- `backend/database.py` - konfiguracja SQLAlchemy przez `DATABASE_URL`.
- `backend/migrate.py` - jawne tworzenie schematu bazy.
- `backend/seed_data.py` - idempotentne wypełnianie bazy ćwiczeniami.
- `backend/generator.py` - logika doboru ćwiczeń, objętości treningowej i makroskładników.
- `frontend/src/app/page.tsx` - główny ekran aplikacji.
- `frontend/src/components/ExerciseMedia.tsx` - podgląd zdjęć/GIF-ów ćwiczeń.
- `frontend/src/lib/config.ts` - adresy API i statycznych plików.
- `frontend/src/lib/workoutCopy.ts` - tłumaczenia i mapowania nazw mięśni.
- `frontend/src/types/workout.ts` - typy danych używane przez frontend.
