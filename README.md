# 🎮 GameDev AI Assistant - Complete Edition

**All-in-one AI assistant for game development with Unity, Godot, and Unreal Engine**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)

---

## ✨ Features

### 🎯 Multi-Engine Support
- **Unity** - Full C# script generation
- **Godot** - GDScript support
- **Unreal** - C++ class generation

### 🤖 Local AI
- Runs completely offline using Ollama
- Llama 3.2 3B model (or your choice)
- No internet required for AI features

### 💾 Project Memory
- Tracks created scripts automatically
- Maintains TODO lists
- Remembers project context
- Context-aware conversations

### 🔍 Asset Search
- Search across itch.io
- Unity Asset Store links
- Filter by free/paid
- Hardware-aware recommendations

### 📊 Hardware Detection
- Automatic system specs detection
- Performance tier calculation
- Smart asset recommendations

### 🎨 Modern GUI
- Dark theme interface
- Sidebar with project context
- Multi-engine switching
- Real-time status updates

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- 8GB+ RAM (16GB recommended)
- Windows 10/11, macOS, or Linux

### Installation

**1. Install Ollama**
```bash
# Download from: https://ollama.ai
# After installation:
ollama pull llama3.2:3b
```

**2. Setup Project**
```bash
cd GameDevAI
python setup.py
```

**3. Launch**
```bash
python main.py
# Or on Windows: run.bat
```

---

## 📖 Usage

### Select Engine
Choose Unity, Godot, or Unreal from the dropdown

### Open Project
Click Browse and select your project folder

### Start Creating
```
"Create a 3D player controller with WASD movement"
"Add a health system with UI"
"Find free character models"
```

---

## 🗂️ Project Structure

```
GameDevAI/
├── main.py                 # Entry point
├── gui/                    # User interface
├── ai_core/                # AI integration
├── connectors/             # Engine connectors
├── tools/                  # Utilities
├── data/                   # Your data
└── logs/                   # Activity logs
```

---

## ⚙️ Configuration

Edit `config.json`:
```json
{
  "ai_model": "llama3.2:3b",
  "current_engine": "unity",
  "theme": "dark",
  "memory_enabled": true
}
```

---

## 🆘 Troubleshooting

### "Ollama connection failed"
```bash
ollama serve
# Then restart app
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### Slow responses
- Normal: 5-15 seconds on CPU
- Try smaller model: `ollama pull gemma2:2b`

---

## 📚 Documentation

- **QUICKSTART.md** - 5-minute setup
- **EXAMPLE_PROMPTS.md** - Usage examples
- **TROUBLESHOOTING.md** - Common issues
- **DEVELOPMENT_GUIDE.md** - Implementation details

---

## 🎯 System Requirements

**Minimum:**
- Python 3.8+
- 8GB RAM
- 5GB disk space

**Recommended:**
- Python 3.11+
- 16GB RAM
- 10GB disk space

---

## 📄 License

MIT License - Free to use, modify, and distribute

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM inference
- **Meta AI** - Llama models
- **Unity, Godot, Unreal** - Game engines

---

**Version 1.0.0 - Complete Edition**
**All Phases Integrated - Ready to Use**