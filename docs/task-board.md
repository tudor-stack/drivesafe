# DriveSafe — Task Board

## 👤 Persoana 1 — Backend (Python / FastAPI)

### Sprint 1 — Setup (azi)
- [ ] `git clone` repo, `cd backend`, setup venv, `pip install -r requirements.txt`
- [ ] Copiază `serviceAccountKey.json` în `backend/`
- [ ] `cp .env.example .env` și completează valorile
- [ ] Rulează `uvicorn main:app --reload` → verifică `/health`

### Sprint 2 — Implementare
- [ ] `app/api/users.py` — endpoint GET `/api/users/me`
- [ ] `app/api/health.py` — endpoint GET `/health`
- [ ] `app/api/__init__.py` — empty init
- [ ] Testează toate endpoint-urile cu Postman sau curl
- [ ] Scrie `tests/test_trips.py` cu pytest

### Sprint 3 — Integrare
- [ ] Conectare reală cu Firestore (înlocuiește mock)
- [ ] Testează flow complet: POST /process → Firestore → GET /history

---

## 👤 Persoana 2 — AI (Python / ADK)

### Sprint 1 — Setup (azi)
- [ ] `cd ai`, setup venv, `pip install -r requirements.txt`
- [ ] Copiază `serviceAccountKey.json` în `ai/`
- [ ] `cp .env.example .env` (GOOGLE_GENAI_USE_VERTEXAI=FALSE + GOOGLE_API_KEY)
- [ ] Mută fișierele din `drivesafe-backend/drivesafe_agent/` în `ai/drivesafe_agent/`
- [ ] Rulează `adk web .` din `ai/` → testează în browser

### Sprint 2 — Implementare
- [ ] Înlocuiește mock `get_road_context` cu Google Roads API
- [ ] Înlocuiește mock `save_trip_to_firestore` cu Firebase Admin SDK real
- [ ] Rafinează prompturile din `prompts.py` — testează în ADK web UI
- [ ] Rulează `pytest tests/ -v` — toate testele verzi

### Sprint 3 — Expunere ca serviciu
- [ ] Testează `uvicorn main:app --port 8001 --reload`
- [ ] Testează POST `/analyze` cu date din `tests/fixtures/sample_trip.json`
- [ ] Coordonează cu Persoana 1 pentru conectarea backend → AI service

---

## 👤 Persoana 3 — Mobile (React Native / Expo)

### Sprint 1 — Setup (azi)
- [ ] `cd mobile`, `npm install`
- [ ] `npx expo start` → scanează QR cu Expo Go pe telefon
- [ ] Creează proiect Firebase → descarcă `google-services.json` (Android) / `GoogleService-Info.plist` (iOS)

### Sprint 2 — Implementare de bază
- [ ] `src/screens/HomeScreen.tsx` — dashboard cu scor și buton "Începe cursa"
- [ ] `src/screens/TripScreen.tsx` — ecran activ în timpul cursei (cronometru, viteza)
- [ ] `src/services/sensorService.ts` — deja generat, testează pe telefon real
- [ ] Firebase Auth — login cu Google

### Sprint 3 — Trip History + Hartă
- [ ] `src/screens/HistoryScreen.tsx` — lista de curse
- [ ] `src/screens/TripDetailScreen.tsx` — hartă cu polyline colorat
- [ ] Conectează `src/services/api.ts` la backend-ul real (înlocuiește localhost cu URL Cloud Run)

---

## 🔗 Puncte de sincronizare echipă

| Moment | Ce se verifică |
|--------|---------------|
| Zilnic 5 min | Fiecare spune ce a făcut și ce e blocat |
| PR review | Minim 1 aprobare înainte de merge în develop |
| Înainte de demo | Test end-to-end: Mobile → Backend → AI → Firestore → hartă |

## 📋 Resurse necesare (o singură persoană le creează și le împărtășește)

| Resursă | Cine o creează | Unde se pune |
|---------|---------------|-------------|
| `serviceAccountKey.json` | Persoana 1 | Trimis prin WhatsApp/Drive (NU în Git) |
| Firebase `google-services.json` | Persoana 1 | Trimis la Persoana 3 direct |
| Gemini API Key | Persoana 2 | Fiecare îi face unul separat pe AI Studio (gratuit) |
| GCP project ID | Persoana 1 | Scris în `.env.example` din repo |
| Cloud Run URL (după deploy) | Persoana 1 | Actualizează `mobile/src/services/api.ts` |
