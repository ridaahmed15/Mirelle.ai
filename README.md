# Mirelle.ai

**Your personal AI companion that runs entirely on your own machine.**

Mirelle is a desktop AI assistant built with Python, PySide6 and [Ollama](https://ollama.com). It chats using a local language model, remembers important things about you across sessions, and never sends your conversations to the cloud.

> **Status:** early development (v0.3). Chat and long-term memory work today. Voice, automation, tools and agents are planned. See the [Roadmap](#roadmap).

---

## Features

- **Local-first AI**: all inference runs through Ollama on `localhost`. No API keys, no cloud.
- **Desktop chat interface**: a dark-themed PySide6 (Qt) window with a sidebar, chat history and a non-blocking "Thinking..." state, so the UI never freezes while the model responds.
- **Persistent chat history**: conversations are stored in SQLite, and the last 20 messages are reloaded on startup.
- **Smart Memory**: after each message, Mirelle extracts long-term personal facts (as key/value pairs) and injects them into future prompts.
- **Memory viewer**: open the **Smart Memory** panel from the sidebar to see everything Mirelle remembers, refresh it, or delete individual facts.
- **Configurable personality**: Mirelle's tone and response rules are defined in a single system prompt in `ai/ollama_client.py`.
- **Terminal mode**: `ai/ollama_client.py` can also be run directly for a quick command-line chat.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3 |
| GUI | PySide6 (Qt for Python) |
| LLM runtime | Ollama (default model: `qwen3:4b`) |
| HTTP client | `requests` |
| Storage | SQLite (`sqlite3`, standard library) |

---

## Project Structure

```
Mirelle.ai/
├── main.py                  # Application entry point (launches the GUI)
├── config.py                # Central configuration (placeholder)
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
│
├── ai/
│   └── ollama_client.py     # MirelleAI: chat, system prompt, memory extraction
│
├── interface/
│   └── main_window.py       # PySide6 main window, worker thread, memory viewer
│
├── memory/
│   ├── memory_manager.py    # SQLite layer for chat history and user facts
│   └── storage/
│       └── mirelle.db       # Local SQLite database
│
├── agents/                  # Planned: autonomous agents
├── automation/              # Planned: desktop / task automation
├── core/                    # Planned: core services
├── security/                # Planned: permissions and safety
├── tools/                   # Planned: tool integrations
└── voice/                   # Planned: speech input / output
```

---

## How It Works

1. You send a message from the GUI. It runs on a background `QThread` (`AIWorker`) so the window stays responsive.
2. `MirelleAI.chat()` saves the message to SQLite.
3. A second, low-temperature Ollama call extracts any important long-term facts from the message as JSON (e.g. `{"key": "favorite_language", "value": "Python"}`) and upserts them into the `user_facts` table.
4. Saved facts are appended to the system prompt as `IMPORTANT USER MEMORY`, followed by the recent conversation history.
5. The request goes to Ollama's `/api/chat` endpoint at `http://localhost:11434`, and the reply is shown in the UI and saved to history.

### Database schema

| Table | Columns |
|-------|---------|
| `chat_history` | `id`, `role`, `content`, `created_at` |
| `user_facts` | `id`, `fact_key` (unique), `fact_value`, `updated_at` |

---

## Getting Started

### Prerequisites

- Python 3.10 or newer
- [Ollama](https://ollama.com/download) installed and running
- A machine that can run a small local model (the default `qwen3:4b` is lightweight)

### 1. Clone the repository

```bash
git clone https://github.com/ridaahmed15/Mirelle.ai.git
cd Mirelle.ai
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install PySide6 requests
```

### 4. Pull the model and start Ollama

```bash
ollama pull qwen3:4b
ollama serve
```

Ollama listens on `http://localhost:11434` by default. If it is already running as a background service, you can skip `ollama serve`.

### 5. Run Mirelle

```bash
python main.py
```

To chat from the terminal instead of the GUI:

```bash
python -m ai.ollama_client
```

---

## Configuration

| Setting | Where | Default |
|---------|-------|---------|
| Model | `MirelleAI(model=...)` in `ai/ollama_client.py` | `qwen3:4b` |
| Ollama URL | `self.api_url` in `ai/ollama_client.py` | `http://localhost:11434/api/chat` |
| Personality and rules | `self.system_prompt` in `ai/ollama_client.py` | English-only, short, friendly answers |
| History loaded on start | `load_recent_messages(limit=20)` | 20 messages |
| Response length | `num_predict` in `chat()` | 200 tokens |
| Context window | `num_ctx` | 4096 tokens |

To use a different model, pull it with Ollama (for example `ollama pull llama3.2`) and change the `model` argument.

---

## Privacy

Everything stays on your device. Conversations and memories live in a local SQLite file (`memory/storage/mirelle.db`), and the only network traffic is between the app and your local Ollama server. You can delete individual memories from the Smart Memory panel at any time, or call `MirelleAI.clear_memory()` to wipe chat history.

---

## Roadmap

- [ ] Voice input and spoken replies (`voice/`)
- [ ] Tool use: file search, web lookup, system info (`tools/`)
- [ ] Task and desktop automation (`automation/`)
- [ ] Multi-agent workflows (`agents/`)
- [ ] Permission and safety layer for tools (`security/`)
- [ ] Settings screen (model picker, personality, theme)
- [ ] Streaming responses in the chat window
- [ ] Centralised config via `config.py` and `.env`
- [ ] Packaged installer for Windows

---

## Troubleshooting

**"I am having trouble connecting to my AI model."**
Make sure Ollama is running (`ollama serve`) and that the model is installed (`ollama list`).

**The first reply is slow.**
Ollama loads the model into memory on the first request. Later replies are faster.

**Memory extraction seems to be skipped.**
Small models sometimes return invalid JSON. Mirelle skips that extraction silently and carries on chatting.

---

## Contributing

Contributions, ideas and bug reports are welcome. Fork the repo, create a feature branch, and open a pull request.

---

## Author

Built by **Rida Ahmed**. GitHub: [@ridaahmed15](https://github.com/ridaahmed15)

---

## License

No license has been specified yet. Add a `LICENSE` file (for example MIT) to make the terms of use clear.
