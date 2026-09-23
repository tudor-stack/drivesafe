# 🚗 SafeStart (DriveSafe) — Monorepo

**🥈 2nd Place Winner @ AI Defense Hackathon (Google Developer Groups)**

> **Built in exactly 48 hours (team of 3).** SafeStart is a mobile detection engine designed to identify and prevent aggressive driving behaviors for beginner drivers. It ingests raw smartphone telemetry and processes it through a hybrid kinematic and multi-LLM architecture.

## ✨ Core Features & Architecture

* **Raw Telemetry Ingestion:** Captures and streams real-time accelerometer, gyroscope, and GPS data from the mobile device.
* **Hybrid Classification Engine:** Combines strict kinematic thresholds (hard braking, sharp turns) with a multi-LLM pipeline to evaluate driving aggression contextually.
* **Decoupled Architecture:** The mobile client never communicates directly with the AI models. All traffic is securely routed, validated, and sanitized through the FastAPI backend.

---

## 📂 Project Structure

We utilize a monorepo approach to strictly separate concerns between the API, AI processing, and the client application.

```text
drivesafe/
├── backend/        # ⚙️ API Gateway & Data Integration (Python/FastAPI)
├── ai/             # 🧠 Multi-LLM & Kinematic Pipelines (Python)
├── mobile/         # 📱 Client Application (React Native/TypeScript)
└── docs/           # 📝 API Contracts & Architecture Diagrams
```

---

## 🚀 Development Setup

### 1. Backend API (FastAPI)
Handles request routing, data validation, and connects the mobile app to the AI services.
```bash
cd backend
python -m venv .venv
# On Windows: .venv\Scripts\activate | On Unix: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. AI Processing Pipeline
Contains the LLM integration and kinematic threshold logic.
```bash
cd ai
python -m venv .venv
# On Windows: .venv\Scripts\activate | On Unix: source .venv/bin/activate
pip install -r requirements.txt
python agent.py
```

### 3. Mobile Client (React Native)
Frontend interface guiding beginner drivers with real-time feedback.
```bash
cd mobile
npm install
npx expo start
```

---

## 🤝 Workflow & Branching Strategy

| Team | Branch Pattern | Deployment Target |
|--------|---------------|--------|
| **Backend** | `feature/backend-xxx` | Cloud Run `/backend` |
| **AI** | `feature/ai-xxx` | Cloud Run `/ai-service` |
| **Mobile** | `feature/mobile-xxx` | Expo / App Store |

---

## 👥 The Team

This project was built collaboratively during the 48-hour GDG Hackathon by:

* **[Alexandru Gavriș](https://github.com/alex15g)** — API Gateway & Data Integration (Backend)
* **[Tudor Corbean](https://github.com/tudor-stack)** — Multi-LLM Pipeline & Kinematics (AI)
* **[Roxana Mărginean](https://github.com/Roxiim)** — Client Application (React Native / Mobile)

---

## 📖 API Contract

All endpoints and data structures are strictly documented in [`docs/api-contract.md`](docs/api-contract.md). 

**Architectural Rule:** The Mobile app routes all telemetry strictly through the Backend. Direct calls to the AI service are prohibited to ensure data sanitization.
