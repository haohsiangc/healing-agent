# Healing Agent

A full-stack psychological counseling chatbot powered by Anthropic Claude. It offers empathetic conversation, emotion tracking, guided meditation, and generative art therapy — all driven by a **skills-based agent architecture** where each therapeutic technique is a self-contained Markdown file.

## Features

- **Counseling Dialogue** — AI counselor persona grounded in phenomenological psychology; empathetic, concise responses in Traditional Chinese.
- **Emotion Tracking** — Every message is scored for valence and arousal using the CVAW corpus (jieba word segmentation). Rolling history across the session.
- **Agent Skills** — The LLM autonomously invokes therapeutic skills mid-conversation. Skills are plain `.md` files — no code change needed to add new ones.
- **Mindfulness Meditation** — Breathing exercise modal + guided audio triggered when the agent detects sustained anxiety.
- **Generative Art Therapy** — Generates images from conversation context (mock gradient or real SDXL on GPU). Users then reflect on the chosen image in a multimodal follow-up chat.
- **Auth & History** — JWT-based register/login; all conversations and emotion scores are persisted in SQLite.

---

## How the Agent Works

### 1. Counselor Persona
The agent uses a fixed system prompt (`COUNSELOR_SYSTEM_PROMPT`) that instructs Claude to act as a counseling intern specialising in phenomenological psychology — empathetic, present-focused, and concise (≤ 30 characters per reply).

### 2. Emotion Pipeline
Before each LLM call, `EmotionService` segments the user's text with jieba, looks up each word in the CVAW valence-arousal dictionary, and maintains a rolling window of scores. The scores are stored with each message for session-level visualisation.

### 3. Skills-Based Tool Calling
The agent loop in `ChatService` uses Anthropic's tool-use API. Each tool corresponds to a **skill** — a `.md` file in `backend/app/agent/skills/`:

```
backend/app/agent/skills/
├── meditation.md     →  suggest_meditation   (breathing exercise + meditation UI)
├── grounding.md      →  suggest_grounding    (5-4-3-2-1 sensory grounding)
└── affirmation.md    →  give_affirmation     (positive affirmation)
```

Each skill file follows this template:

```markdown
---
name: skill_name
description: When and why the LLM should call this skill.
flags:
  suggest_meditation: true   # or false
---

# Skill Title

Brief description of the therapeutic technique.

## 回應
The exact message returned to the user when this skill fires.

## 適用情境
- When to use this skill (examples)

## 執行準則
- Behavioural guidelines
```

The `loader.py` parses every `.md` at startup, registers them in `SkillRegistry`, and exports a `skill_registry` singleton. `ChatService` queries the registry for tool definitions and dispatches execution — it never references skill names directly.

**Adding a new skill = dropping a `.md` file into the `skills/` directory. Zero Python changes required.**

### 4. Multimodal Image Reflection
After art generation, `ChatService.chat_about_image()` sends the selected image (base64 JPEG) alongside conversation history to Claude's vision API, producing a counselor response that links the image's aesthetic to the user's emotional narrative.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, React Router, Zustand, Axios |
| Backend | FastAPI, Uvicorn, SQLAlchemy, SQLite |
| Auth | JWT (python-jose, passlib + bcrypt 3.x) |
| AI | Anthropic Claude (`claude-haiku-4-5`) |
| NLP | Jieba, Pandas, NumPy, CVAW corpus |
| Image | Pillow (mock); optional SDXL via `diffusers` + GPU |

---

## Project Structure

```
healing-agent/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── base.py          # SkillBase (ABC) + SkillResult dataclass
│   │   │   ├── registry.py      # SkillRegistry — register / dispatch / export
│   │   │   ├── loader.py        # .md parser → MarkdownSkill instances
│   │   │   ├── tools.py         # shim (re-exports skill_registry)
│   │   │   └── skills/
│   │   │       ├── __init__.py  # loads all *.md, builds singleton
│   │   │       ├── meditation.md
│   │   │       ├── grounding.md
│   │   │       └── affirmation.md
│   │   ├── core/                # config, database, JWT security
│   │   ├── models/              # SQLAlchemy ORM models + Pydantic schemas
│   │   ├── routers/             # auth, chat, image, meditation endpoints
│   │   ├── services/
│   │   │   ├── chat_service.py  # agent loop, image reflection, prompt translation
│   │   │   ├── emotion_service.py
│   │   │   └── generation_service.py
│   │   └── main.py              # FastAPI app, CORS, router registration
│   ├── requirements.txt
│   └── tests/
│       ├── test_auth.py
│       ├── test_emotion.py
│       └── test_skills.py       # 31 tests covering loader, skills, registry
└── frontend/
    ├── src/
    │   ├── api/                 # Axios client
    │   ├── components/          # EmotionMeter, MeditationModal, MessageBubble, …
    │   ├── pages/               # ChatPage, LoginPage, MeditationPage
    │   └── stores/              # Zustand: useAuthStore, useChatStore
    ├── package.json
    └── vite.config.js
```

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- Anthropic API Key
- (Optional) CUDA-capable GPU for real SDXL image generation

---

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # fill in ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | — | Claude API key |
| `ANTHROPIC_MODEL` | No | `claude-haiku-4-5` | Model ID |
| `SECRET_KEY` | Yes | (change me) | JWT signing secret |
| `MOCK_IMAGE_GENERATION` | No | `true` | `false` to use real SDXL on GPU |
| `DATABASE_URL` | No | `sqlite:///./healing_bot.db` | SQLAlchemy DB URL |
| `HF_TOKEN` | No | — | HuggingFace token for SDXL download |

---

## Testing

```bash
cd backend
pytest                  # all 34 tests
pytest tests/test_skills.py -v   # skills architecture only
```

---

## Adding a New Skill

1. Create `backend/app/agent/skills/your_skill.md`:

```markdown
---
name: your_skill_name
description: When the LLM should invoke this skill.
flags:
  suggest_meditation: false
---

# Skill Title

## 回應
The message shown to the user.

## 適用情境
- Usage example

## 執行準則
- Guideline
```

2. Restart the backend. The skill is automatically registered and available to the LLM.
