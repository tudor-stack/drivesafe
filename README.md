# DriveSafe — Monorepo

Aplicație mobilă pentru detectarea și prevenirea condusului agresiv la șoferii începători.

## Structura proiectului

```
drivesafe/
├── backend/        # 👤 Persoana 1 — FastAPI REST API (Python)
├── ai/             # 👤 Persoana 2 — ADK Agent Pipeline (Python)
├── mobile/         # 👤 Persoana 3 — React Native App (TypeScript)
└── docs/           # Contract API + diagrame arhitectură
```

## Cum lucrăm împreună

| Echipă | Branch pattern | Deploy |
|--------|---------------|--------|
| Backend | `feature/backend-xxx` | Cloud Run `/backend` |
| AI | `feature/ai-xxx` | Cloud Run `/ai-service` |
| Mobile | `feature/mobile-xxx` | Expo / App Store |

### Setup rapid per echipă

```bash
# Clonează repo
git clone https://github.com/ECHIPA/drivesafe.git
cd drivesafe

# Backend
cd backend && python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# AI
cd ai && python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# Mobile
cd mobile && npm install && npx expo start
```

## Contractul API

Toate endpoint-urile sunt documentate în [`docs/api-contract.md`](docs/api-contract.md).
Mobile nu apelează niciodată direct AI — **tot trece prin Backend**.
