# 🛠️ Development Guide - GameDev AI Assistant

Complete roadmap for building and extending the project.

---

## 🎯 Phase 1: Core + GUI Chat ✅ (CURRENT)

**Status:** MVP Ready
**Time Estimate:** 2-3 weeks
**Difficulty:** ⭐⭐☆☆☆

### What's Included
- [x] Tkinter GUI with dark theme
- [x] Ollama integration for local AI
- [x] Basic Unity project detection
- [x] Script generation and saving
- [x] Chat history persistence
- [x] Action logging

### Testing Phase 1

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Ollama
ollama serve

# 3. Pull model
ollama pull llama3.2:3b

# 4. Run app
python main.py

# 5. Test checklist:
□ GUI launches without errors
□ Can select Unity project folder
□ Chat sends/receives messages
□ AI responds within 15 seconds
□ Scripts save to Assets/Scripts/
□ Chat history persists after restart
```

### Known Limitations
- AI may hallucinate Unity API methods
- Slow on CPU-only systems (5-15s response)
- No syntax validation before saving
- No code execution/testing

### Next Steps Before Phase 2
- [ ] Add error handling for malformed scripts
- [ ] Implement script preview before saving
- [ ] Add "Undo last change" feature
- [ ] Create more prompt templates

---

## 🔧 Phase 2: Extended Unity Integration

**Status:** Not Started
**Time Estimate:** 3-4 weeks
**Difficulty:** ⭐⭐⭐☆☆

### New Features to Implement

#### 2.1: Scene Analysis
```python
# File: connectors/scene_analyzer.py

class SceneAnalyzer:
    def parse_scene_file(self, scene_path):
        """Parse .unity scene files (YAML format)"""
        # Unity scenes are YAML - use PyYAML
        pass
    
    def get_scene_objects(self):
        """List all GameObjects in scene"""
        pass
    
    def find_missing_components(self):
        """Detect GameObjects missing required components"""
        pass
```

**Dependencies:** `pyyaml`

#### 2.2: Component Suggestions
```python
# AI prompt addition
"""When suggesting scripts, also recommend:
1. Required components (Rigidbody, Collider, etc.)
2. Which GameObject to attach to
3. Inspector settings to configure
"""
```

#### 2.3: Multi-File Generation
```python
# File: connectors/project_generator.py

class ProjectGenerator:
    def create_system(self, system_name, files):
        """Generate multiple related scripts"""
        # Example: Create Player system with:
        # - PlayerController.cs
        # - PlayerHealth.cs
        # - PlayerInput.cs
        pass
```

### Implementation Order
1. ✅ Scene file parser (read-only)
2. ✅ Component dependency detection
3. ✅ Multi-script generation
4. ✅ Smart GameObject recommendations

### Testing Phase 2
```
Test Cases:
1. Parse a simple scene with 5 GameObjects
2. Detect missing Rigidbody on physics-based script
3. Generate complete "Player System" (3 scripts)
4. Recommend correct GameObject for script attachment
```

---

## 📊 Phase 3: Hardware Detection

**Status:** Partially Implemented
**Time Estimate:** 1-2 weeks
**Difficulty:** ⭐⭐☆☆☆

### Implementation Plan

#### 3.1: Integrate Specs Checker
```python
# In main.py, add:
from tools.check_specs import SpecsChecker

def on_first_run():
    checker = SpecsChecker()
    checker.detect_all()
    checker.save_report()
    
    # Show user their performance tier
    show_specs_dialog()
```

#### 3.2: Performance-Aware Recommendations
```python
# In ai_core/model_interface.py, modify system prompt:

def load_system_prompt(self):
    # Load specs
    with open('data/system_specs.json') as f:
        specs = json.load(f)
    
    tier = specs['performance_tier']['tier']
    
    # Add to system prompt
    if tier == 'low':
        return base_prompt + """
        IMPORTANT: User has limited hardware.
        - Recommend 2D solutions over 3D
        - Suggest baked lighting only
        - Avoid heavy particle effects
        - Focus on optimization
        """
```

#### 3.3: Asset Compatibility Filter
```python
# For Phase 4 asset search
def filter_by_specs(assets, user_specs):
    tier = user_specs['performance_tier']['tier']
    
    if tier == 'low':
        # Filter out high-poly models
        # Remove "requires GPU" assets
        pass
```

### Testing Phase 3
```
Test Cases:
1. Run on high-end PC → Tier: high
2. Run on 16GB laptop → Tier: medium
3. AI suggests 2D game for low-tier system
4. AI recommends 3D for high-tier system
```

---

## 🔍 Phase 4: Asset Finder

**Status:** Not Started
**Time Estimate:** 4-5 weeks
**Difficulty:** ⭐⭐⭐⭐☆

### Architecture

```
tools/search_assets.py
├── UnityAssetStoreSearcher
├── ItchIOSearcher
├── SketchfabSearcher
└── AssetAggregator
```

### 4.1: itch.io API Integration
```python
import requests

class ItchIOSearcher:
    API_BASE = "https://itch.io/api/1/KEY"
    
    def search(self, query, filters):
        """Search itch.io game assets"""
        params = {
            'query': query,
            'classification': 'assets',
            'format': 'json'
        }
        # itch.io has official API
        response = requests.get(f"{self.API_BASE}/search/games", params=params)
        return self.parse_results(response.json())
```

### 4.2: Unity Asset Store (No Official API)
```python
class UnityAssetStoreSearcher:
    """Scraping-based search (unofficial)"""
    
    def search(self, query):
        # Use DuckDuckGo with site: operator
        search_url = f"https://duckduckgo.com/?q=site:assetstore.unity.com+{query}"
        
        # Alternative: Direct search on asset store page
        store_url = "https://assetstore.unity.com/packages"
        # Parse HTML results (use BeautifulSoup)
```

**Note:** Unity may block scraping. Consider alternatives:
- Manual curated lists
- Community-maintained database
- User can paste asset store links

### 4.3: GUI Integration
```python
# Add to chat_window.py

class AssetSearchDialog:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Asset Search")
        
        # Search controls
        self.query_entry = tk.Entry()
        self.filter_free = tk.Checkbutton(text="Free Only")
        self.filter_type = ttk.Combobox(values=['3D Models', 'Textures', 'Audio'])
        
        # Results list
        self.results_list = ttk.Treeview()
```

### 4.4: AI-Assisted Asset Finding
```python
# User prompt example:
# "Find free low-poly character models for Unity"

# AI response:
"""
I'll search for free low-poly character assets...

Found 5 results:

1. **Polygon Adventure Pack** (Free)
   - Platform: Unity Asset Store
   - Poly count: ~500 per model
   - Link: [url]
   
2. **Simple Character Models** (Free)
   - Platform: itch.io
   - Includes: 10 characters
   - Link: [url]

Based on your system specs (medium tier), these assets should run smoothly.
"""
```

### Implementation Order
1. itch.io integration (has API)
2. Sketchfab integration (has API)
3. GUI asset browser
4. DuckDuckGo fallback for Unity Store
5. Asset recommendations in AI responses

### Testing Phase 4
```
Test Cases:
1. Search "low poly tree" → Returns 10+ results
2. Filter "Free only" → Shows only free assets
3. Click link → Opens in browser
4. AI suggests assets matching user's specs tier
```

---

## 🧠 Phase 5: Project Memory & Context

**Status:** Not Started
**Time Estimate:** 3-4 weeks
**Difficulty:** ⭐⭐⭐⭐☆

### Architecture Decision

**Option A: ChromaDB (Vector Database)**
```python
import chromadb

class ProjectMemory:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("project_memory")
    
    def remember(self, text, metadata):
        """Store information with semantic search"""
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[generate_id()]
        )
    
    def recall(self, query, n_results=5):
        """Retrieve relevant memories"""
        return self.collection.query(query_texts=[query], n_results=n_results)
```

**Option B: Simple JSON (Simpler, no ML)**
```python
class ProjectMemory:
    def __init__(self):
        self.memory = {
            'scripts_created': [],
            'user_preferences': {},
            'game_type': '',
            'features_requested': [],
            'common_tasks': []
        }
    
    def remember_script(self, script_name, purpose):
        self.memory['scripts_created'].append({
            'name': script_name,
            'purpose': purpose,
            'created_at': datetime.now().isoformat()
        })
```

**Recommendation:** Start with Option B (JSON), upgrade to ChromaDB later

### 5.1: What to Remember
```python
{
    "project_info": {
        "name": "My Platformer Game",
        "genre": "2D Platformer",
        "target_platform": "PC/Mobile",
        "art_style": "Pixel Art"
    },
    "scripts": [
        {
            "name": "PlayerController.cs",
            "purpose": "Main player movement and input",
            "features": ["double jump", "wall slide"],
            "created": "2025-01-15",
            "last_modified": "2025-01-16"
        }
    ],
    "todos": [
        "Add enemy AI",
        "Create level system",
        "Implement save/load"
    ],
    "preferences": {
        "coding_style": "verbose comments",
        "architecture": "component-based",
        "naming_convention": "camelCase"
    }
}
```

### 5.2: Context-Aware Conversations
```python
# AI prompt enhancement:

def build_context_prompt(user_message, project_memory):
    context = f"""
PROJECT CONTEXT:
- Game Type: {project_memory['project_info']['genre']}
- Scripts Created: {', '.join([s['name'] for s in project_memory['scripts']])}
- Current Goals: {', '.join(project_memory['todos'])}
- Last worked on: {get_recent_activity()}

USER MESSAGE: {user_message}
"""
    return context
```

### 5.3: Smart Suggestions
```python
# AI can now say things like:
"""
I notice you already have PlayerController.cs with movement.
Would you like me to:
1. Add a new feature to PlayerController
2. Create a separate PlayerCombat.cs
3. Create an enemy that interacts with the player
"""
```

### Implementation Order
1. JSON-based memory system
2. Automatic script tracking
3. Context injection in AI prompts
4. User preferences learning
5. TODO list management
6. (Optional) Upgrade to ChromaDB

### Testing Phase 5
```
Test Cases:
1. Create script → Memory tracks it
2. Ask "What scripts do I have?" → Lists all scripts
3. Ask "Add health to player" → AI knows PlayerController exists
4. Restart app → Memory persists
5. Ask "What should I work on next?" → AI suggests from TODOs
```

---

## 📦 Phase 6: Packaging & Distribution

**Status:** Not Started
**Time Estimate:** 2-3 weeks
**Difficulty:** ⭐⭐⭐☆☆

### 6.1: PyInstaller Configuration

```python
# File: build.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gui/assets', 'gui/assets'),
        ('ai_core/prompt_templates', 'ai_core/prompt_templates'),
        ('config.json', '.')
    ],
    hiddenimports=['tkinter', 'requests', 'psutil'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GameDevAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='gui/assets/icon.ico'  # Add app icon
)
```

### 6.2: Build Process

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller build.spec

# Output will be in dist/GameDevAI.exe
```

### 6.3: File Size Optimization

```bash
# Typical sizes:
- Unoptimized: ~150-200 MB
- With UPX compression: ~80-100 MB
- Excluding unnecessary libraries: ~60-80 MB
```

**Optimization techniques:**
```python
# In build.spec, exclude heavy unused libraries:
excludes=[
    'matplotlib',
    'numpy',  # If not used
    'pandas',  # If not used
    'scipy'
]
```

### 6.4: Installer Creation (Optional)

Use **Inno Setup** (Windows):

```iss
; File: installer.iss

[Setup]
AppName=GameDev AI Assistant
AppVersion=0.1.0
DefaultDirName={pf}\GameDevAI
DefaultGroupName=GameDev AI
OutputDir=output
OutputBaseFilename=GameDevAI_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\GameDevAI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\GameDev AI Assistant"; Filename: "{app}\GameDevAI.exe"
Name: "{commondesktop}\GameDev AI"; Filename: "{app}\GameDevAI.exe"

[Run]
Filename: "{app}\GameDevAI.exe"; Description: "Launch GameDev AI"; Flags: postinstall nowait skipifsilent
```

### 6.5: Auto-Update System

```python
# File: tools/updater.py

import requests
from packaging import version

class AutoUpdater:
    GITHUB_API = "https://api.github.com/repos/user/gamedev-ai/releases/latest"
    
    def check_for_updates(self):
        """Check GitHub releases for newer version"""
        response = requests.get(self.GITHUB_API)
        latest = response.json()['tag_name']
        current = self.get_current_version()
        
        if version.parse(latest) > version.parse(current):
            return {
                'update_available': True,
                'latest_version': latest,
                'download_url': latest['assets'][0]['browser_download_url']
            }
        return {'update_available': False}
    
    def download_update(self, url):
        """Download and install update"""
        # Download new .exe
        # Replace current executable
        # Restart application
        pass
```

### Testing Phase 6
```
Test Cases:
1. Build .exe → Runs without errors
2. .exe size < 100 MB
3. Double-click launches GUI
4. No console window appears
5. Installer creates Start Menu shortcut
6. Uninstaller removes all files
7. Update check works (mock server)
```

---

## 🚀 Post-Launch Features (Phase 7+)

### Ideas for Future Versions

#### Godot Integration
```python
# File: connectors/godot_connector.py
# GDScript generation instead of C#
# Parse .tscn scene files
```

#### Unreal Engine Integration
```python
# File: connectors/unreal_connector.py
# Blueprint visual scripting
# C++ code generation
```

#### Collaborative Features
- Share project configs
- Export/import prompt templates
- Community script library

#### Advanced AI Features
- Code review and suggestions
- Performance profiling
- Bug prediction
- Auto-documentation generation

#### Plugin System
```python
# Allow users to create custom connectors
class CustomEngine(EngineConnector):
    def generate_script(self, ...):
        pass
```

---

## 🎓 Development Best Practices

### Code Organization
```
✅ DO:
- Keep files under 500 lines
- One class per file
- Use type hints
- Write docstrings

❌ DON'T:
- Put everything in main.py
- Use global variables
- Ignore error handling
```

### Testing Strategy
```python
# File: tests/test_unity_connector.py

import unittest
from connectors.unity_connector import UnityConnector

class TestUnityConnector(unittest.TestCase):
    def setUp(self):
        self.connector = UnityConnector('test_project/')
    
    def test_create_script(self):
        result = self.connector.create_script('TestScript.cs', 'content')
        self.assertTrue(result['success'])
```

### Version Control
```bash
# .gitignore
data/
logs/
*.bak
__pycache__/
dist/
build/
*.spec
config.json
```

### Documentation
- Update README.md with each phase
- Document API changes in CHANGELOG.md
- Add inline comments for complex logic
- Create video tutorials for users

---

## 📊 Success Metrics

### Phase 1
- [ ] 100+ lines of generated code without errors
- [ ] Chat response time < 15s average
- [ ] 95% script save success rate

### Phase 2-6
- [ ] Support 3 game engines
- [ ] Find 1000+ searchable assets
- [ ] .exe size < 100 MB
- [ ] User retention > 50% after 1 week

---

## 🤝 Community & Support

### GitHub Repository Structure
```
README.md
CONTRIBUTING.md
CODE_OF_CONDUCT.md
LICENSE
docs/
├── installation.md
├── usage.md
└── api.md
examples/
├── example_scripts/
└── example_prompts.md
```

### Issue Templates
```markdown
**Bug Report Template:**
- OS Version:
- Python Version:
- AI Model:
- Steps to reproduce:
- Expected behavior:
- Actual behavior:
```

---

**Next Steps:** Start with Phase 1 testing, then move to Phase 2 scene analysis! 🚀