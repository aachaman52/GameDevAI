# 🔧 Troubleshooting Guide

Quick solutions to common problems with GameDev AI Assistant.

---

## 🚨 Installation Issues

### "Python not found"
**Symptom:** `python: command not found` or `python is not recognized`

**Solution:**
1. Install Python from [python.org](https://python.org)
2. During installation, **check "Add Python to PATH"**
3. Restart terminal/command prompt
4. Test: `python --version`

---

### "pip install fails"
**Symptom:** `ERROR: Could not install packages` or permission errors

**Solutions:**
```bash
# Try with user flag
pip install -r requirements.txt --user

# Or upgrade pip first
python -m pip install --upgrade pip
pip install -r requirements.txt

# Windows: Run as Administrator
# Linux/Mac: Use sudo
sudo pip install -r requirements.txt
```

---

## 🤖 Ollama Connection Issues

### "Ollama connection failed"
**Symptom:** App starts but AI doesn't respond, shows connection error

**Check:**
```bash
# Is Ollama installed?
ollama --version

# Is Ollama running?
# Windows/Mac: Check system tray for Ollama icon
# Linux: Check process
ps aux | grep ollama

# Test API directly
curl http://localhost:11434/api/tags
```

**Solutions:**
```bash
# Start Ollama
ollama serve

# In another terminal, pull model
ollama pull llama3.2:3b

# Verify model downloaded
ollama list
```

**Still not working?**
- Check firewall isn't blocking port 11434
- Restart Ollama completely
- Try different port: Edit `ai_core/model_interface.py`, change `11434` to `11435`

---

### "Model not found"
**Symptom:** `Model llama3.2:3b not found in Ollama`

**Solution:**
```bash
# Pull the model
ollama pull llama3.2:3b

# Alternative models if that fails
ollama pull llama3.2
ollama pull phi3
ollama pull gemma2:2b

# Update config.json with the model you downloaded
```

---

## 🎮 Unity Integration Issues

### "Not a valid Unity project"
**Symptom:** Error when selecting project folder

**Check:**
- Did you select the **root** Unity folder?
- Does it have an `Assets` folder inside?

**Correct structure:**
```
MyUnityProject/          ← Select THIS folder
├── Assets/              ← Must exist
├── Library/
├── ProjectSettings/
└── Packages/
```

---

### "Script not saving"
**Symptom:** AI generates script but file doesn't appear in Unity

**Solutions:**
1. Check file permissions on Assets folder
2. Close Unity before creating scripts
3. Check logs: `logs/unity_actions.json`
4. Try manual path: Check if script is in `Assets/Scripts/`

**Verify manually:**
```bash
# Check if file was created
ls Assets/Scripts/

# Check logs
cat logs/unity_actions.json
```

---

### "Unity doesn't recognize script"
**Symptom:** Script appears in folder but Unity shows errors

**Common causes:**
1. **Class name doesn't match filename**
   ```csharp
   // ❌ Wrong
   // File: PlayerController.cs
   public class Player : MonoBehaviour { }
   
   // ✅ Correct
   // File: PlayerController.cs
   public class PlayerController : MonoBehaviour { }
   ```

2. **Syntax errors in generated code**
   - Copy error message
   - Ask AI: "Fix this error: [paste error]"

3. **Missing using statements**
   ```csharp
   // Add at top of file:
   using UnityEngine;
   using System.Collections;
   ```

---

## 💬 GUI/Chat Issues

### "GUI won't launch"
**Symptom:** Error when running `python main.py`

**Check Python version:**
```bash
python --version
# Need 3.8 or higher
```

**Check Tkinter:**
```python
# Test Tkinter
python -c "import tkinter; print('OK')"

# If error on Linux:
sudo apt-get install python3-tk
```

---

### "Chat freezes when sending message"
**Symptom:** GUI becomes unresponsive, can't click anything

**Cause:** AI is processing (normal for CPU-only)

**Wait time:**
- First message: 10-20 seconds
- Later messages: 5-15 seconds

**If truly frozen (> 2 minutes):**
1. Force quit the app
2. Check Ollama is running: `ollama serve`
3. Restart app
4. Try simpler prompt first: "Hello"

---

### "Chat history disappeared"
**Symptom:** Previous conversations not showing

**Check:**
```bash
# History file exists?
ls data/chat_history.json

# If missing, recreate folder
mkdir -p data
```

**Manual recovery:**
```python
# Create empty history
echo "[]" > data/chat_history.json
```

---

## 🐌 Performance Issues

### "AI responses too slow"
**Symptom:** 30+ seconds per response

**Solutions:**

1. **Use smaller model:**
   ```bash
   ollama pull gemma2:2b  # Faster, less accurate
   # Update config.json: "ai_model": "gemma2:2b"
   ```

2. **Close other programs:**
   - Close browser tabs
   - Close IDE if not needed
   - Free up RAM

3. **Reduce context:**
   Edit `config.json`:
   ```json
   {
     "max_chat_history": 50  // Reduce from 100
   }
   ```

4. **Check CPU usage:**
   ```bash
   # Windows
   taskmgr
   
   # Linux/Mac
   top
   
   # Look for 'ollama' process using 100% CPU (normal during generation)
   ```

---

### "High RAM usage"
**Symptom:** Computer slows down, 90%+ RAM used

**Model RAM requirements:**
- llama3.2:3b → ~4GB RAM
- phi3:3.8b → ~5GB RAM
- llama3.2:7b → ~8GB RAM

**Solutions:**
- Use 2B parameter models
- Close other applications
- Restart Ollama: `ollama serve`
- Upgrade RAM (if possible)

---

## 📝 Code Generation Issues

### "Generated code has errors"
**Symptom:** Unity shows compilation errors

**Common AI mistakes:**
1. Hallucinated API methods (methods that don't exist)
2. Wrong Unity version syntax
3. Missing semicolons or brackets

**Solution:**
1. Copy full error message
2. Ask AI: "Fix this compilation error: [paste error]"
3. Or manually debug: Check Unity docs

---

### "Code works but not as expected"
**Symptom:** No errors, but behavior is wrong

**Debug steps:**
1. Add `Debug.Log()` statements
   ```csharp
   void Start() {
       Debug.Log("Script started!");
   }
   ```

2. Check Inspector values
   - Are serialized fields set correctly?
   - Is component enabled?

3. Ask AI for debugging help:
   ```
   "This code compiles but doesn't [expected behavior].
   Here's the script: [paste code]
   Here's what happens: [describe actual behavior]"
   ```

---

## 🔒 Permission/Access Issues

### "Permission denied" saving script
**Windows:**
```bash
# Run app as Administrator
# Right-click → Run as administrator
```

**Linux/Mac:**
```bash
# Fix folder permissions
chmod -R 755 Assets/Scripts/
```

---

### "Can't read Unity project"
**Symptom:** `PermissionError: [Errno 13]`

**Solution:**
- Close Unity editor
- Check antivirus isn't blocking access
- Move project to non-system folder (not C:\Program Files)

---

## 🌐 Network Issues (Phase 4+)

### "Asset search not working"
**Symptom:** "Connection error" when searching assets

**Check:**
```bash
# Test internet connection
ping google.com

# Test specific site
ping itch.io
```

**Firewall:**
- Allow Python.exe through firewall
- Allow outbound connections on ports 80/443

---

## 🗂️ Data/Config Issues

### "Config file corrupted"
**Symptom:** App won't start, JSON errors

**Fix:**
```bash
# Delete corrupt config
rm config.json

# App will recreate default on next launch
python main.py
```

---

### "Lost all my scripts!"
**Symptom:** Scripts disappeared from Unity project

**Recovery:**
1. Check for `.bak` backup files:
   ```bash
   find Assets/Scripts/ -name "*.bak"
   ```

2. Check action log:
   ```bash
   cat logs/unity_actions.json
   # Shows all file operations
   ```

3. Restore from backup:
   ```bash
   cp PlayerController.cs.bak PlayerController.cs
   ```

---

## 🧪 Advanced Debugging

### Enable debug mode

Edit `main.py`:
```python
import logging

# Add at top of main()
logging.basicConfig(level=logging.DEBUG)
```

### Check all logs
```bash
# Unity actions
cat logs/unity_actions.json

# Chat history
cat data/chat_history.json

# System specs
cat data/system_specs.json
```

### Test individual components
```python
# Test Unity connector
python -c "from connectors.unity_connector import UnityConnector; print('OK')"

# Test AI model
python -c "from ai_core.model_interface