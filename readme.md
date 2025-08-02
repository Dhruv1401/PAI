# 🧠 RPI-Assisted AI Assistant (formerly TARS 3.0)

A modular, plugin-driven AI assistant designed for Raspberry Pi and desktop environments. Inspired by real-world robotics and space exploration, this assistant supports both voice and text interfaces, dynamic plugin management, and powerful LLM-based conversation capabilities.

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
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
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

## 🛤️ Roadmap

- [ ] Hardware integration (robotics movement)
- [ ] Auto plugin updates and sync

---

## 🤝 Contributing

Have ideas or improvements? Feel free to fork the repo and open a pull request or issue. All contributions are welcome!

---

## 📜 License

MIT License. Use freely with attribution.

---

## 🙌 Credits

- Mistral-7B (via Hugging Face)
- Project architecture and vision: You (and your futuristic brain)
- Inspiration: *TARS* from Interstellar, Raspberry Pi robotics, voice automation.
- Made with ❤️, 🧠,ChatGPT(by openai) and lots of dedication.
```

---

