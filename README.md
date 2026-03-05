# Healing Chatbot (Bot Agent)

A full-stack web application designed to provide psychological counseling dialogue, emotion detection, mindfulness meditation, and generative art therapy. The project features a React frontend and a FastAPI backend.

## Features

- **Psychological Counseling Dialogue**: AI-driven empathetic conversation.
- **Emotion Detection**: NLP-based emotion analysis during chat.
- **Mindfulness Meditation**: Guided meditation sessions and resources.
- **Generative Art Therapy**: Image generation (mock or via local Stable Diffusion/GPU).
- **User System**: JWT-based authentication for user registration and login.
- **Conversation History**: Save and retrieve past chat sessions safely.

## How the Agent Works

The conversational brain of the Healing Chatbot is powered by Anthropic's Claude (`claude-3-5-sonnet-latest`) and is orchestrated via a custom FastAPI backend architecture. Here is a breakdown of its inner workings:

1. **System Prompt & Persona Formulation**: 
   The agent adopts the persona of a counseling intern who specializes in phenomenological psychology. It is guided by a tailored system prompt (`COUNSELOR_SYSTEM_PROMPT`) to ensure responses are highly empathetic, centered on the user's immediate perceptions, and kept engagingly concise.

2. **Emotion Tracking Pipeline**:
   Before the agent generates a response, every user input is processed by an NLP-based `EmotionService`. This module evaluates the text for "valence" and "arousal" scores, keeping a rolling history across the session.

3. **Autonomous Tool Calling**:
   The agent utilizes Anthropic's tool-use framework.
   - **`AgentTools`**: It holds a registry of functions, such as `suggest_meditation`.
   - When the LLM detects that a user is highly anxious, stressed, or explicitly asks for relaxation, it autonomously decides to invoke this tool.
   - The `ChatService` handles an internal execution loop: intercepting the agent's tool requests, executing the local Python function, and appending the tool results back if needed, allowing for a seamless transition into offering breathing exercises mid-chat.

4. **Multimodal Image Reflection**:
   In the generative art therapy flow, the agent engages its multimodal capabilities (`chat_about_image`). Using a specialized image counselor prompt, it analyzes the base64-encoded image chosen by the user alongside the conversation history, helping users deeply explore the psychological link between their lived experiences and the aesthetic of the generated art.

## Tech Stack

### Frontend
- **Framework**: React 19 + Vite
- **State Management**: Zustand
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **Styling**: Vanilla CSS

### Backend
- **Framework**: FastAPI + Uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (python-jose, passlib)
- **AI / NLP**: Anthropic API (Claude), Jieba, Pandas, Numpy
- **Image Generation**: Pillow (optional integration with `torch` and `diffusers`)

## Project Structure

```text
bot_agent/
├── backend/
│   ├── app/
│   │   ├── agent/       # Chat and AI agents (Tools definitions)
│   │   ├── core/        # Config, database setup, security
│   │   ├── models/      # SQLAlchemy database models
│   │   ├── routers/     # API endpoints (auth, chat, image, meditation)
│   │   ├── services/    # Business logic (ChatService, EmotionService)
│   │   └── main.py      # FastAPI application entry point
│   ├── requirements.txt # Python dependencies
│   └── tests/           # Pytest suite
└── frontend/
    ├── src/
    │   ├── api/         # Axios API clients
    │   ├── assets/      # Static assets
    │   ├── components/  # Reusable React components
    │   ├── pages/       # React route components
    │   └── stores/      # Zustand state stores
    ├── package.json     # Node.js dependencies
    └── vite.config.js   # Vite configuration
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- Anthropic API Key for full AI chatbot capabilities
- (Optional) Compatible GPU for local Stable Diffusion image generation

## Installation & Setup

### 1. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Set up environment variables:

```bash
cp .env.example .env
```
Edit `.env` and fill in your generic configuration and `ANTHROPIC_API_KEY`.

Start the backend server:

```bash
# Optional: Ensure database is initialized
# uvicorn app.main:app --reload
fastapi dev app/main.py # or python -m uvicorn app.main:app --reload
```
The FastAPI backend will run at `http://localhost:8000`. API documentation is available at `http://localhost:8000/docs`.

### 2. Frontend Setup

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install the Node.js dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```
The React frontend will be accessible at `http://localhost:5173`.

## Testing

**Backend Tests:**
Run the test suite using `pytest` from the `backend` directory:
```bash
cd backend
pytest
```
