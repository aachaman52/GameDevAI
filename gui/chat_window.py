"""
Modern GameDev AI Chat Window
Complete Edition with Beautiful UI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, simpledialog
import json
from pathlib import Path
from datetime import datetime
import threading


class ChatWindow:
    def __init__(self):
        # Load config
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except:
            self.config = {
                "ai_model": "llama3.2:3b",
                "current_engine": "unity",
                "memory_enabled": True,
                "unity_project_path": "",
                "godot_project_path": "",
                "unreal_project_path": ""
            }
            self.save_config()

        # Initialize subsystems
        self.init_subsystems()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("GameDev AI Assistant")
        self.root.geometry("1200x800")
        
        self.chat_history = self.load_chat_history()
        self.current_engine = self.config.get('current_engine', 'unity')
        
        self.setup_modern_styles()
        self.create_ui()
        
        # Load project context
        self.load_project_context()
    
    def init_subsystems(self):
        """Initialize AI, Memory, and Logger"""
        # AI Model
        try:
            from ai_core.model_interface import AIModel
            self.ai = AIModel(self.config.get('ai_model', 'llama3.2:3b'))
        except:
            class DummyAI:
                def generate_response(self, *args, **kwargs):
                    return "⚠️ AI module not available"
                def check_ollama_status(self): return False
            self.ai = DummyAI()
        
        # Memory
        try:
            from ai_core.memory import ProjectMemory
            self.memory = ProjectMemory()
        except:
            class DummyMemory:
                def get_project_info(self): 
                    return {'name': 'Unnamed', 'engine': 'N/A'}
                def list_scripts(self): return []
                def list_todos(self): return []
                def build_context_summary(self): return ""
                def add_script(self, *a, **k): pass
                def add_todo(self, *a, **k): pass
                def clear_memory(self): pass
                def set_project_info(self, **k): pass
                def get_stats(self): return {
                    "total_scripts": 0, "total_assets": 0,
                    "pending_todos": 0, "completed_tasks": 0, "days_active": 0
                }
                def search_scripts(self, q): return []
            self.memory = DummyMemory()
        
        # Logger
        try:
            from tools.logger import get_logger
            self.logger = get_logger()
        except:
            import logging
            self.logger = logging.getLogger("GameDevAI")
    
    def setup_modern_styles(self):
        """Modern color scheme and fonts"""
        # Dark theme colors
        self.colors = {
            'bg': '#0d1117',           # Main background
            'surface': '#161b22',      # Surface elements
            'surface_alt': '#21262d',  # Alternate surface
            'border': '#30363d',       # Borders
            'accent': '#58a6ff',       # Accent color (blue)
            'accent_hover': '#79c0ff', # Accent hover
            'success': '#3fb950',      # Success (green)
            'warning': '#d29922',      # Warning (yellow)
            'danger': '#f85149',       # Danger (red)
            'text': '#c9d1d9',         # Primary text
            'text_secondary': '#8b949e', # Secondary text
            'user_msg': '#1f6feb',     # User messages
            'ai_msg': '#238636',       # AI messages
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Modern.TCombobox',
                       fieldbackground=self.colors['surface'],
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       bordercolor=self.colors['border'],
                       arrowcolor=self.colors['text'])
    
    def create_ui(self):
        """Create modern UI layout"""
        # Header
        self.create_header()
        
        # Main content area
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Sidebar
        self.create_sidebar(main_frame)
        
        # Chat area
        self.create_chat_area(main_frame)
        
        # Input area
        self.create_input_area()
        
        # Status bar
        self.create_status_bar()
        
        # Display history and welcome
        self.display_chat_history()
        self.add_system_message("🎮 Welcome to GameDev AI Assistant!")
        
        # Check AI status
        if hasattr(self.ai, 'check_ollama_status'):
            if not self.ai.check_ollama_status():
                self.add_system_message("⚠️ Ollama not detected. Check connection in Tools menu.")
    
    def create_header(self):
        """Modern header with toolbar"""
        header = tk.Frame(self.root, bg=self.colors['surface'], height=60)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        # Left side - Title and Engine selector
        left_frame = tk.Frame(header, bg=self.colors['surface'])
        left_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        # App title
        title_label = tk.Label(left_frame, text="🎮 GameDev AI",
                              bg=self.colors['surface'],
                              fg=self.colors['text'],
                              font=("Segoe UI", 14, "bold"))
        title_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Engine selector
        tk.Label(left_frame, text="Engine:",
                bg=self.colors['surface'],
                fg=self.colors['text_secondary'],
                font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.engine_var = tk.StringVar(value=self.current_engine)
        engine_combo = ttk.Combobox(left_frame, textvariable=self.engine_var,
                                    values=['unity', 'godot', 'unreal'],
                                    state='readonly', width=10,
                                    style='Modern.TCombobox')
        engine_combo.pack(side=tk.LEFT, padx=(0, 10))
        engine_combo.bind('<<ComboboxSelected>>', self.on_engine_change)
        
        # Right side - Action buttons
        right_frame = tk.Frame(header, bg=self.colors['surface'])
        right_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Modern buttons
        self.create_modern_button(right_frame, "📁 Open Project",
                                 lambda: self.select_project(self.current_engine),
                                 self.colors['accent']).pack(side=tk.LEFT, padx=5)
        
        self.create_modern_button(right_frame, "🔍 Assets",
                                 self.open_asset_search,
                                 self.colors['success']).pack(side=tk.LEFT, padx=5)
        
        self.create_modern_button(right_frame, "⚙️ Settings",
                                 self.show_settings,
                                 self.colors['surface_alt']).pack(side=tk.LEFT, padx=5)
    
    def create_modern_button(self, parent, text, command, bg_color):
        """Create a modern styled button"""
        btn = tk.Button(parent, text=text, command=command,
                       bg=bg_color, fg=self.colors['text'],
                       font=("Segoe UI", 9),
                       relief=tk.FLAT, cursor="hand2",
                       padx=15, pady=8,
                       activebackground=self.colors['accent_hover'],
                       activeforeground=self.colors['text'])
        
        # Hover effects
        def on_enter(e):
            btn['bg'] = self.colors['accent_hover']
        def on_leave(e):
            btn['bg'] = bg_color
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def create_sidebar(self, parent):
        """Modern sidebar with context info"""
        sidebar = tk.Frame(parent, bg=self.colors['surface'], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        sidebar.pack_propagate(False)
        
        # Sidebar header
        sidebar_header = tk.Frame(sidebar, bg=self.colors['surface_alt'], height=50)
        sidebar_header.pack(fill=tk.X)
        sidebar_header.pack_propagate(False)
        
        tk.Label(sidebar_header, text="📊 Project Context",
                bg=self.colors['surface_alt'],
                fg=self.colors['text'],
                font=("Segoe UI", 11, "bold")).pack(pady=15, padx=15, anchor='w')
        
        # Context text area
        context_frame = tk.Frame(sidebar, bg=self.colors['surface'])
        context_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.context_text = tk.Text(context_frame,
                                   bg=self.colors['surface_alt'],
                                   fg=self.colors['text'],
                                   font=("Consolas", 9),
                                   wrap=tk.WORD,
                                   relief=tk.FLAT,
                                   padx=10, pady=10,
                                   cursor="arrow")
        self.context_text.pack(fill=tk.BOTH, expand=True)
        
        # Quick actions
        actions_frame = tk.Frame(sidebar, bg=self.colors['surface'])
        actions_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.create_modern_button(actions_frame, "➕ Add TODO",
                                 self.quick_add_todo,
                                 self.colors['surface_alt']).pack(fill=tk.X, pady=2)
        
        self.create_modern_button(actions_frame, "🔍 Find Script",
                                 self.find_script,
                                 self.colors['surface_alt']).pack(fill=tk.X, pady=2)
        
        self.create_modern_button(actions_frame, "📋 View Memory",
                                 self.show_memory,
                                 self.colors['surface_alt']).pack(fill=tk.X, pady=2)
        
        self.update_context_display()
    
    def create_chat_area(self, parent):
        """Modern chat display area"""
        chat_container = tk.Frame(parent, bg=self.colors['bg'])
        chat_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=("Segoe UI", 10),
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=20, pady=20,
            cursor="arrow",
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for modern message styling
        self.chat_display.tag_config("user",
                                    foreground=self.colors['user_msg'],
                                    font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("ai",
                                    foreground=self.colors['ai_msg'],
                                    font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("system",
                                    foreground=self.colors['text_secondary'],
                                    font=("Segoe UI", 9, "italic"))
        self.chat_display.tag_config("timestamp",
                                    foreground=self.colors['text_secondary'],
                                    font=("Segoe UI", 8))
    
    def create_input_area(self):
        """Modern input area with enhanced controls"""
        input_container = tk.Frame(self.root, bg=self.colors['surface'], height=120)
        input_container.pack(fill=tk.X, padx=0, pady=0)
        input_container.pack_propagate(False)
        
        # Input frame with padding
        input_frame = tk.Frame(input_container, bg=self.colors['surface'])
        input_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Text input
        self.input_box = tk.Text(input_frame,
                                bg=self.colors['surface_alt'],
                                fg=self.colors['text'],
                                font=("Segoe UI", 10),
                                height=3,
                                wrap=tk.WORD,
                                relief=tk.FLAT,
                                padx=15, pady=10,
                                insertbackground=self.colors['accent'])
        self.input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.input_box.bind('<Return>', self.on_enter_key)
        self.input_box.bind('<Shift-Return>', lambda e: None)  # Allow Shift+Enter for newline
        
        # Button panel
        button_frame = tk.Frame(input_frame, bg=self.colors['surface'])
        button_frame.pack(side=tk.RIGHT)
        
        self.send_btn = self.create_modern_button(button_frame, "▶ Send",
                                                  self.send_message,
                                                  self.colors['accent'])
        self.send_btn.pack(pady=2)
        
        self.create_modern_button(button_frame, "🗑️ Clear",
                                 self.clear_chat,
                                 self.colors['danger']).pack(pady=2)
    
    def create_status_bar(self):
        """Modern status bar"""
        self.status_bar = tk.Label(self.root,
                                  text="● Ready",
                                  bg=self.colors['surface_alt'],
                                  fg=self.colors['text_secondary'],
                                  font=("Segoe UI", 9),
                                  anchor='w',
                                  padx=20, pady=8)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    # ========== Message Handling ==========
    
    def send_message(self):
        """Send user message"""
        message = self.input_box.get("1.0", tk.END).strip()
        if not message:
            return
        
        self.input_box.delete("1.0", tk.END)
        self.add_message("You", message, "user")
        
        self.send_btn.config(state=tk.DISABLED, text="⏳ Thinking...")
        self.update_status("● AI processing...")
        
        threading.Thread(target=self.get_ai_response, args=(message,), daemon=True).start()
    
    def get_ai_response(self, message):
        """Get AI response in background thread"""
        try:
            import time
            start = time.time()
            
            context = self.build_context()
            response = self.ai.generate_response(message, context, self.chat_history)
            
            elapsed = time.time() - start
            
            self.root.after(0, lambda: self.add_message("AI", response, "ai"))
            self.root.after(0, lambda: self.update_status(f"● Ready ({elapsed:.1f}s)"))
            
            self.auto_update_memory(message, response)
            
        except Exception as e:
            self.root.after(0, lambda: self.add_system_message(f"❌ Error: {e}"))
        finally:
            self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL, text="▶ Send"))
    
    def add_message(self, sender, text, tag):
        """Add message to chat with modern styling"""
        timestamp = datetime.now().strftime("%H:%M")
        
        self.chat_display.config(state=tk.NORMAL)
        
        # Add spacing
        self.chat_display.insert(tk.END, "\n")
        
        # Add timestamp
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add sender
        self.chat_display.insert(tk.END, f"{sender}:\n", tag)
        
        # Add message text
        self.chat_display.insert(tk.END, f"{text}\n")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Save to history
        self.chat_history.append({"sender": sender, "text": text, "timestamp": timestamp})
        self.save_chat_history()
    
    def add_system_message(self, text):
        """Add system message"""
        if not hasattr(self, 'chat_display'):
            return
        
        try:
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"\n{text}\n", "system")
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
        except:
            pass
    
    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_history = []
        self.save_chat_history()
        self.add_system_message("🗑️ Chat cleared")
    
    # ========== Helper Methods ==========
    
    def on_enter_key(self, event):
        """Handle Enter key"""
        if not (event.state & 1):  # No Shift
            self.send_message()
            return "break"
    
    def build_context(self):
        """Build AI context"""
        context = f"Engine: {self.current_engine.title()}\n"
        
        project_path = self.get_current_project_path()
        if project_path != "No project":
            context += f"Project: {project_path}\n"
        
        if self.config.get('memory_enabled', True):
            context += "\n" + self.memory.build_context_summary()
        
        return context
    
    def auto_update_memory(self, user_msg, ai_response):
        """Auto-update memory from conversation"""
        if "script" in user_msg.lower():
            import re
            match = re.search(r'class\s+(\w+)', ai_response)
            if match:
                script_name = match.group(1)
                if ".cs" in ai_response:
                    script_name += ".cs"
                elif ".gd" in ai_response:
                    script_name += ".gd"
                elif ".cpp" in ai_response:
                    script_name += ".cpp"
                self.memory.add_script(script_name, user_msg[:100], [])
                self.update_context_display()
    
    def update_context_display(self):
        """Update sidebar context"""
        if not hasattr(self, 'context_text'):
            return
        
        try:
            self.context_text.config(state=tk.NORMAL)
            self.context_text.delete("1.0", tk.END)
            
            info = self.memory.get_project_info()
            scripts = self.memory.list_scripts()
            todos = self.memory.list_todos()
            
            context = f"📦 Project: {info.get('name', 'Unnamed')}\n"
            context += f"🎮 Engine: {info.get('engine', 'N/A')}\n\n"
            
            context += f"📝 Scripts ({len(scripts)}):\n"
            for script in scripts[-5:]:
                context += f"  • {script['name']}\n"
            
            context += f"\n✅ TODOs ({len(todos)}):\n"
            for todo in todos[:5]:
                task = todo['task'][:30]
                context += f"  ☐ {task}...\n" if len(todo['task']) > 30 else f"  ☐ {task}\n"
            
            self.context_text.insert("1.0", context)
            self.context_text.config(state=tk.DISABLED)
        except:
            pass
    
    def update_status(self, text):
        """Update status bar"""
        self.status_bar.config(text=text)
    
    def display_chat_history(self):
        """Display saved chat history"""
        for msg in self.chat_history[-20:]:
            tag = "user" if msg['sender'] == "You" else "ai"
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"\n[{msg['timestamp']}] ", "timestamp")
            self.chat_display.insert(tk.END, f"{msg['sender']}:\n", tag)
            self.chat_display.insert(tk.END, f"{msg['text']}\n")
            self.chat_display.config(state=tk.DISABLED)
    
    # ========== File Operations ==========
    
    def load_chat_history(self):
        """Load chat history"""
        file = Path('data/chat_history.json')
        file.parent.mkdir(exist_ok=True)
        if file.exists():
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_chat_history(self):
        """Save chat history"""
        try:
            Path('data').mkdir(exist_ok=True)
            with open('data/chat_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.chat_history[-100:], f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def save_config(self):
        """Save configuration"""
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def load_project_context(self):
        """Load project context on startup"""
        for engine in ['unity', 'godot', 'unreal']:
            key = f"{engine}_project_path"
            if self.config.get(key):
                self.memory.set_project_info(engine=engine)
    
    # ========== Menu Actions ==========
    
    def on_engine_change(self, event):
        """Handle engine change"""
        self.current_engine = self.engine_var.get()
        self.config['current_engine'] = self.current_engine
        self.save_config()
        self.add_system_message(f"🎯 Switched to {self.current_engine.title()}")
        self.update_context_display()
    
    def select_project(self, engine_type):
        """Select project folder"""
        folder = filedialog.askdirectory(title=f"Select {engine_type.title()} Project")
        
        if folder:
            valid = self.validate_project(folder, engine_type)
            
            if valid:
                key = f"{engine_type}_project_path"
                self.config[key] = folder
                self.save_config()
                self.memory.set_project_info(engine=engine_type)
                
                self.add_system_message(f"✓ {engine_type.title()} project loaded")
                self.update_context_display()
            else:
                self.add_system_message(f"⚠ Not a valid {engine_type.title()} project")
    
    def validate_project(self, path, engine):
        """Validate project folder"""
        path = Path(path)
        if engine == 'unity':
            return (path / 'Assets').exists()
        elif engine == 'godot':
            return (path / 'project.godot').exists()
        elif engine == 'unreal':
            return any(path.glob('*.uproject'))
        return False
    
    def get_current_project_path(self):
        """Get current project path"""
        key = f"{self.current_engine}_project_path"
        return self.config.get(key, "No project")
    
    def open_asset_search(self):
        """Open asset search dialog"""
        query = simpledialog.askstring("Asset Search", "Search for assets:")
        if query:
            self.add_system_message(f"🔍 Searching for: {query}")
            # TODO: Implement actual search
            self.add_system_message("Asset search coming soon!")
    
    def show_settings(self):
        """Show settings dialog"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("500x400")
        settings_win.configure(bg=self.colors['surface'])
        
        # Settings content
        tk.Label(settings_win, text="⚙️ Settings",
                bg=self.colors['surface'],
                fg=self.colors['text'],
                font=("Segoe UI", 14, "bold")).pack(pady=20)
        
        # AI Model setting
        frame = tk.Frame(settings_win, bg=self.colors['surface'])
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame, text="AI Model:",
                bg=self.colors['surface'],
                fg=self.colors['text']).pack(anchor='w')
        
        model_var = tk.StringVar(value=self.config.get('ai_model', 'llama3.2:3b'))
        model_entry = tk.Entry(frame, textvariable=model_var,
                              bg=self.colors['surface_alt'],
                              fg=self.colors['text'],
                              font=("Segoe UI", 10),
                              relief=tk.FLAT)
        model_entry.pack(fill=tk.X, pady=5)
        
        def save_settings():
            self.config['ai_model'] = model_var.get()
            self.save_config()
            messagebox.showinfo("Settings", "Restart app for changes to take effect")
            settings_win.destroy()
        
        self.create_modern_button(settings_win, "💾 Save Settings",
                                 save_settings,
                                 self.colors['accent']).pack(pady=20)
    
    def quick_add_todo(self):
        """Quick add TODO"""
        todo = simpledialog.askstring("Add TODO", "Enter task:")
        if todo:
            self.memory.add_todo(todo, "medium")
            self.update_context_display()
            self.add_system_message(f"✓ Added: {todo}")
    
    def find_script(self):
        """Find script in memory"""
        query = simpledialog.askstring("Find Script", "Search for:")
        if query:
            results = self.memory.search_scripts(query)
            if results:
                msg = f"Found {len(results)} script(s):\n"
                for s in results:
                    msg += f"• {s['name']}\n"
                messagebox.showinfo("Search Results", msg)
            else:
                messagebox.showinfo("Search Results", "No scripts found")
    
    def show_memory(self):
        """Show project memory stats"""
        try:
            stats = self.memory.get_stats()
            info = f"""📊 Project Memory

Scripts: {stats['total_scripts']}
Assets: {stats['total_assets']}
TODOs: {stats['pending_todos']}
Completed: {stats['completed_tasks']}
Days Active: {stats['days_active']}
"""
            messagebox.showinfo("Project Memory", info)
        except:
            messagebox.showinfo("Project Memory", "No memory data available")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


# Allow direct execution
if __name__ == "__main__":
    app = ChatWindow()
    app.run()