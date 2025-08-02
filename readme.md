# 🧠 Personal AI assistant.

 A modular, AI assistant designed for Raspberry Pi and desktop environments. Inspired by real-world robotics and fantasies, this assistant supports both voice and text interfaces and mediocre LLM-based conversation capabilities.
---

## 🚀 Features

- ⚙️ **Plugin System** — Enable/disable features live via chat commands
- 🧠 **LLM-Powered Brain** — Uses Mistral 7B via Hugging Face API
- 🎙️/⌨️ **Voice & Text Interfaces** — Only one interface active at a time
- 📝 **Memory System** — Logs sessions by date/time for later reference
- 🔍 **Self-Diagnostics** — Reports internal plugin states and errors
- 🌤️ **Real Weather Plugin** — Fetches live weather using your location
- 🗃️ **Modular Codebase** — Easy to extend, modify, and debug

---

## 🛠️ Installation

```bash
git clone https://github.com/Dhruv1401/PAI.git
cd PAI
pip install -r requirements.txt
```

## 🧩 Plugin Commands

Inside the assistant chat, use:

```
plugin list
plugin enable <plugin_name>
plugin disable <plugin_name>
```

---

## 📁 Folder Structure

```
project_root/
│
├── main.py                 # Entry point
├── plugins/                # Modular plugin system
├── interface/              # Voice/Text input-output
├── core/                   # Brain logic and async handler
├── memory/                 # Memory management system
├── logs/                   # Session-based logs
└── requirements.txt        # Python dependencies
```

---

## 🧠 Current Plugins

| Plugin Name       | Description                            |
|-------------------|----------------------------------------|
| `sample_greet`    | Friendly startup greeting              |
| `weather`         | Reports current weather                |
| `self_diagnostics`| System health check                    |
| `voice_interface` | Voice input/output                     |
| `text_interface`  | CLI-based interaction                  |
| `scheduler`       | (Planned) Task and reminder module     |
| `debug_logger`    | Logs plugin startup/runtime activity   |

---

## 🛣️ Roadmap

### ✅ **Completed**
- Added some basic functionalities
- 🔧 Plugin architecture with dynamic loading
- ✅ Chat-based command system for plugin control
- 🔀 Voice ↔ Text interface toggling via commands
- 🧠 Memory system storing session logs by date/time
- 🧪 Self-diagnostics plugin for system checks
- 🌤️ Weather plugin with real-world data
- 🗓️ Scheduler plugin for timed tasks
- 🐞 Debug plugin for runtime logs
- 📃 Plugin failsafe: prevents enabling nonexistent plugins
- 📝 Auto-list all enabled plugins at startup
- 💬 Added error handling and feedback for invalid plugin actions

### 🏗️ **Upcoming**
- 🛞 Hardware Integration
- 💾 Memory persistence & context injection on restart
- 📊 Dashboard for plugin performance and logs


---

## 🤝 Contributing

Have ideas or improvements? Feel free to fork the repo and open a pull request or issue. All contributions are welcome!

---

## 📜 License

MIT License.
(Use freely, but dont forget the credits!)

---

## 🙌 Credits

- Mistral-7B (via Hugging Face)
- Project architecture and vision: You (and your futuristic brain)
- Inspiration: *TARS* from Interstellar, Raspberry Pi robotics, voice automation.
- Made with ❤️, 🧠,ChatGPT(by openai) and lots of dedication.
