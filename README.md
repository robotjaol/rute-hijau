# RuteHijau

heheheh

## run (mode demo)

```bash
# Terminal 1 — engine
cd engine
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

# Terminal 2 — web
cd web
npm install
echo "NEXT_PUBLIC_ENGINE_URL=http://localhost:8000" > .env.local
npm run dev
# buka http://localhost:3000
```

## test

```bash
pip install -r engine/requirements.txt
pytest -q
```

## Struktur

```
engine/   Python FastAPI + CVRP OR-Tools
web/      Next.js + react-leaflet
tests/    Uji unit dan integrasi
plan/     Dokumen perencanaan
```
