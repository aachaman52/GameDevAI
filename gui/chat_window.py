"""
Complete Chat Window - All Features Integrated
Multi-Engine Support, Memory, Asset Search
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, simpledialog
import json
from pathlib import Path
from datetime import datetime
import threading

class ChatWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GameDev AI Assistant - Complete Edition")
        self.root.geometry("1100x750")
        
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        
        self.chat_history = self.load_chat_history()
        self.current_engine = self.config.get('current_engine', 'unity')
        
        self.setup_styles()
        self.create_menu()
        self.create_widgets()
        
        from ai_core.model_interface import AIModel
        from ai_core.memory import ProjectMemory
        from tools.logger import get_logger
        
        self.ai = AIModel(self.config['ai_model'])
        self.memory = ProjectMemory()
        self.logger = get_logger()
        
        self.load_project_context()
    
    def setup_styles(self):
        self.bg_color = "#1e1e1e"
        self.fg_color = "#d4d4d4"
        self.input_bg = "#2d2d2d"
        self.button_bg = "#0e639c"
        self.ai_msg_bg = "#2d3748"
        self.user_msg_bg = "#1a365d"
        self.root.configure(bg=self.bg_color)
    
    def create_menu(self):
        menubar = tk.Menu(self.root, bg=self.bg_color, fg=self.fg_color)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg=self.fg_color)
        file_menu.add_command(label="Open Unity Project", command=lambda: self.select_project('unity'))
        file_menu.add_command(label="Open Godot Project", command=lambda: self.select_project('godot'))
        file_menu.add_command(label="Open Unreal Project", command=lambda: self.select_project('unreal'))
        file_menu.add_separator()
        file_menu.add_command(label="Export Chat", command=self.export_chat)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg=self.fg_color)
        tools_menu.add_command(label="Search Assets", command=self.open_asset_search)
        tools_menu.add_command(label="View System Specs", command=self.show_specs)
        tools_menu.add_command(label="View Logs", command=self.show_logs)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        memory_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg=self.fg_color)
        memory_menu.add_command(label="View Project Memory", command=self.show_memory)
        memory_menu.add_command(label="View TODOs", command=self.show_todos)
        memory_menu.add_command(label="Clear Memory", command=self.clear_memory_confirm)
        menubar.add_cascade(label="Memory", menu=memory_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg=self.fg_color)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_widgets(self):
        toolbar = tk.Frame(self.root, bg=self.bg_color, height=60)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(toolbar, text="Engine:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT, padx=5)
        
        self.engine_var = tk.StringVar(value=self.current_engine)
        engine_combo = ttk.Combobox(toolbar, textvariable=self.engine_var, 
                                    values=['unity', 'godot', 'unreal'], state='readonly', width=10)
        engine_combo.pack(side=tk.LEFT, padx=5)
        engine_combo.bind('<<ComboboxSelected>>', self.on_engine_change)
        
        tk.Label(toolbar, text="Project:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT, padx=5)
        
        self.project_label = tk.Label(toolbar, text=self.get_current_project_path(),
                                      bg=self.bg_color, fg="#888", width=40, anchor='w')
        self.project_label.pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="Browse", command=lambda: self.select_project(self.current_engine),
                 bg=self.button_bg, fg=self.fg_color).pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔍 Assets", command=self.open_asset_search,
                 bg="#059669", fg=self.fg_color).pack(side=tk.LEFT, padx=5)
        
        content_frame = tk.Frame(self.root, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        sidebar = tk.Frame(content_frame, bg=self.input_bg, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text="📋 Context", bg=self.input_bg, 
                fg=self.fg_color, font=("Arial", 10, "bold")).pack(pady=10)
        
        self.context_text = tk.Text(sidebar, bg=self.input_bg, fg=self.fg_color,
                                   font=("Consolas", 8), wrap=tk.WORD, height=20)
        self.context_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.update_context_display()
        
        chat_frame = tk.Frame(content_frame, bg=self.bg_color)
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, bg=self.bg_color, fg=self.fg_color,
            font=("Consolas", 10), wrap=tk.WORD, state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display.tag_config("user", foreground="#60a5fa", font=("Consolas", 10, "bold"))
        self.chat_display.tag_config("ai", foreground="#34d399", font=("Consolas", 10, "bold"))
        self.chat_display.tag_config("system", foreground="#fbbf24", font=("Consolas", 9, "italic"))
        
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        action_frame = tk.Frame(input_frame, bg=self.bg_color)
        action_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Button(action_frame, text="📝 TODO", command=self.quick_add_todo,
                 bg="#0e639c", fg=self.fg_color, width=10).pack(side=tk.LEFT, padx=2)
        tk.Button(action_frame, text="🔍 Find", command=self.find_script,
                 bg="#0e639c", fg=self.fg_color, width=10).pack(side=tk.LEFT, padx=2)
        
        self.input_box = tk.Text(input_frame, bg=self.input_bg, fg=self.fg_color,
                                font=("Consolas", 10), height=3, wrap=tk.WORD)
        self.input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.input_box.bind('<Return>', self.on_enter_key)
        
        button_panel = tk.Frame(input_frame, bg=self.bg_color)
        button_panel.pack(side=tk.RIGHT)
        
        self.send_btn = tk.Button(button_panel, text="Send", command=self.send_message,
                                  bg=self.button_bg, fg=self.fg_color, width=10, height=2)
        self.send_btn.pack(pady=2)
        
        tk.Button(button_panel, text="Clear", command=self.clear_chat,
                 bg="#dc2626", fg=self.fg_color, width=10).pack(pady=2)
        
        self.status_bar = tk.Label(self.root, text="Ready", bg=self.input_bg,
                                  fg=self.fg_color, anchor='w', padx=10)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.display_chat_history()
        self.add_system_message(f"🎮 GameDev AI Assistant Ready | Engine: {self.current_engine.title()}")
    
    def get_current_project_path(self):
        key = f"{self.current_engine}_project_path"
        path = self.config.get(key, "")
        return path if path else "No project selected"
    
    def on_engine_change(self, event):
        self.current_engine = self.engine_var.get()
        self.config['current_engine'] = self.current_engine
        self.save_config()
        self.project_label.config(text=self.get_current_project_path())
        self.add_system_message(f"Switched to {self.current_engine.title()}")
        self.logger.log_action('engine_changed', {'engine': self.current_engine})
    
    def select_project(self, engine_type):
        folder = filedialog.askdirectory(title=f"Select {engine_type.title()} Project")
        
        if folder:
            valid = self.validate_project(folder, engine_type)
            
            if valid:
                key = f"{engine_type}_project_path"
                self.config[key] = folder
                self.save_config()
                self.project_label.config(text=folder, fg=self.fg_color)
                
                self.memory.set_project_info(engine=engine_type)
                self.logger.log_project_opened(folder, engine_type)
                
                self.add_system_message(f"✓ {engine_type.title()} project loaded: {folder}")
                self.update_context_display()
            else:
                self.add_system_message(f"⚠ Not a valid {engine_type.title()} project")
    
    def validate_project(self, path, engine):
        path = Path(path)
        if engine == 'unity':
            return (path / 'Assets').exists()
        elif engine == 'godot':
            return (path / 'project.godot').exists()
        elif engine == 'unreal':
            return any(path.glob('*.uproject'))
        return False
    
    def send_message(self):
        message = self.input_box.get("1.0", tk.END).strip()
        if not message:
            return
        
        self.input_box.delete("1.0", tk.END)
        self.add_message("You", message, "user")
        
        self.send_btn.config(state=tk.DISABLED, text="Thinking...")
        self.update_status("AI processing...")
        
        threading.Thread(target=self.get_ai_response, args=(message,), daemon=True).start()
    
    def get_ai_response(self, message):
        try:
            import time
            start_time = time.time()
            
            context = self.build_full_context()
            response = self.ai.generate_response(message, context, self.chat_history)
            
            elapsed = time.time() - start_time
            
            self.root.after(0, lambda: self.add_message("AI", response, "ai"))
            self.root.after(0, lambda: self.update_status(f"Response time: {elapsed:.1f}s"))
            
            self.logger.log_ai_request(message, elapsed)
            self.auto_update_memory(message, response)
            
        except Exception as e:
            self.root.after(0, lambda: self.add_system_message(f"Error: {str(e)}"))
            self.logger.log_ai_error(str(e), message)
        
        finally:
            self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL, text="Send"))
    
    def build_full_context(self):
        project_path = self.get_current_project_path()
        context = f"Engine: {self.current_engine.title()}\n"
        
        if project_path != "No project selected":
            context += f"Project: {project_path}\n"
        
        if self.config.get('memory_enabled', True):
            context += "\n" + self.memory.build_context_summary()
        
        return context
    
    def auto_update_memory(self, user_msg, ai_response):
        if "script" in user_msg.lower() and (".cs" in ai_response or ".gd" in ai_response or ".cpp" in ai_response):
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
        self.context_text.config(state=tk.NORMAL)
        self.context_text.delete("1.0", tk.END)
        
        info = self.memory.get_project_info()
        scripts = self.memory.list_scripts()
        todos = self.memory.list_todos()
        
        context = f"Project: {info.get('name', 'Unnamed')}\n"
        context += f"Engine: {info.get('engine', 'N/A')}\n\n"
        context += f"Scripts ({len(scripts)}):\n"
        for script in scripts[-5:]:
            context += f"  • {script['name']}\n"
        context += f"\nTODOs ({len(todos)}):\n"
        for todo in todos[:5]:
            context += f"  ☐ {todo['task'][:30]}\n"
        
        self.context_text.insert("1.0", context)
        self.context_text.config(state=tk.DISABLED)
    
    def on_enter_key(self, event):
        if not (event.state & 4):
            self.send_message()
            return "break"
    
    def add_message(self, sender, text, tag):
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"\n[{timestamp}] ", "system")
        self.chat_display.insert(tk.END, f"{sender}:\n", tag)
        self.chat_display.insert(tk.END, f"{text}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        self.chat_history.append({"sender": sender, "text": text, "timestamp": timestamp})
        self.save_chat_history()
    
    def add_system_message(self, text):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"\n{text}\n", "system")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def clear_chat(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_history = []
        self.save_chat_history()
    
    def update_status(self, text):
        self.status_bar.config(text=text)
    
    def display_chat_history(self):
        for msg in self.chat_history[-20:]:
            tag = "user" if msg['sender'] == "You" else "ai"
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"\n[{msg['timestamp']}] ", "system")
            self.chat_display.insert(tk.END, f"{msg['sender']}:\n", tag)
            self.chat_display.insert(tk.END, f"{msg['text']}\n")
            self.chat_display.config(state=tk.DISABLED)
    
    def load_chat_history(self):
        file = Path('data/chat_history.json')
        if file.exists():
            with open(file, 'r') as f:
                return json.load(f)
        return []
    
    def save_chat_history(self):
        with open('data/chat_history.json', 'w') as f:
            json.dump(self.chat_history[-100:], f, indent=2)
    
    # CONTINUATION OF chat_window.py - Menu handlers and helpers
    
    def save_config(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def load_project_context(self):
        for engine in ['unity', 'godot', 'unreal']:
            key = f"{engine}_project_path"
            if self.config.get(key):
                self.memory.set_project_info(engine=engine)
    
    def export_chat(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt",
                                           filetypes=[("Text files", "*.txt")])
        if file:
            with open(file, 'w') as f:
                for msg in self.chat_history:
                    f.write(f"[{msg['timestamp']}] {msg['sender']}: {msg['text']}\n\n")
            messagebox.showinfo("Export", "Chat exported successfully!")
    
    def open_asset_search(self):
        search_query = simpledialog.askstring("Asset Search", "Search for assets:")
        if search_query:
            self.add_system_message(f"🔍 Searching for: {search_query}")
            try:
                from tools.search_assets import search_assets
                results = search_assets(search_query, free_only=False)
                
                total = results.get('total_results', 0)
                if total > 0:
                    self.add_system_message(f"Found {total} results")
                    
                    for source, items in results.get('sources', {}).items():
                        if isinstance(items, list) and items:
                            self.add_system_message(f"\n{source.upper()}:")
                            for item in items[:3]:
                                if isinstance(item, dict):
                                    name = item.get('name', 'Unknown')
                                    url = item.get('url', '#')
                                    self.add_system_message(f"  • {name}\n    {url}")
                else:
                    self.add_system_message("No results found")
                    
            except Exception as e:
                self.add_system_message(f"Search error: {e}")
    
    def show_specs(self):
        specs_file = Path('data/system_specs.json')
        if specs_file.exists():
            with open(specs_file) as f:
                specs = json.load(f)
                tier = specs.get('performance_tier', {})
                cpu = specs.get('cpu', {})
                mem = specs.get('memory', {})
                
                info = f"""SYSTEM SPECIFICATIONS

Performance: {tier.get('tier', 'unknown').upper()}
Score: {tier.get('score', 0)}/100

CPU: {cpu.get('brand', 'Unknown')}
Cores: {cpu.get('physical_cores', 'N/A')}

Memory: {mem.get('total_gb', 0)} GB
Available: {mem.get('available_gb', 0)} GB

{tier.get('description', '')}
"""
                messagebox.showinfo("System Specs", info)
        else:
            messagebox.showinfo("System Specs", "Run hardware detection first")
    
    def show_logs(self):
        stats = self.logger.get_stats()
        info = f"""USAGE STATISTICS

Total Actions: {stats['total_actions']}
Scripts Created: {stats['scripts_created']}
Scripts Modified: {stats['scripts_modified']}
AI Requests: {stats['ai_requests']}
Errors: {stats['errors']}
"""
        messagebox.showinfo("Logs", info)
    
    def show_memory(self):
        stats = self.memory.get_stats()
        info = f"""PROJECT MEMORY

Scripts: {stats['total_scripts']}
Assets: {stats['total_assets']}
TODOs: {stats['pending_todos']}
Completed: {stats['completed_tasks']}
Days Active: {stats['days_active']}
"""
        messagebox.showinfo("Project Memory", info)
    
    def show_todos(self):
        todos = self.memory.list_todos()
        if todos:
            todo_text = "PENDING TASKS:\n\n"
            for i, todo in enumerate(todos, 1):
                priority = todo.get('priority', 'medium').upper()
                task = todo.get('task', '')
                todo_text += f"{i}. [{priority}] {task}\n"
            messagebox.showinfo("TODOs", todo_text)
        else:
            messagebox.showinfo("TODOs", "No pending tasks")
    
    def clear_memory_confirm(self):
        if messagebox.askyesno("Clear Memory", 
                               "Delete all project memory?\n\n" +
                               "This includes scripts, assets, and TODOs."):
            self.memory.clear_memory()
            self.update_context_display()
            self.add_system_message("✓ Memory cleared")
    
    def show_about(self):
        messagebox.showinfo("About", 
            "GameDev AI Assistant v1.0.0\n\n" +
            "Complete Edition - All Phases\n\n" +
            "Features:\n" +
            "• Unity, Godot, Unreal\n" +
            "• Local AI (Ollama)\n" +
            "• Project Memory\n" +
            "• Asset Search\n" +
            "• Hardware Detection")
    
    def quick_add_todo(self):
        todo = simpledialog.askstring("Add TODO", "Enter task:")
        if todo:
            priority = simpledialog.askstring("Priority", 
                                             "Priority (low/medium/high):", 
                                             initialvalue="medium")
            if priority:
                self.memory.add_todo(todo, priority)
                self.update_context_display()
                self.add_system_message(f"✓ Added TODO: {todo}")
    
    def find_script(self):
        query = simpledialog.askstring("Find Script", "Search for:")
        if query:
            results = self.memory.search_scripts(query)
            if results:
                result_text = f"Found {len(results)} script(s):\n\n"
                for script in results:
                    result_text += f"• {script['name']}\n  {script['purpose']}\n\n"
                messagebox.showinfo("Search Results", result_text)
            else:
                messagebox.showinfo("Search Results", "No scripts found")
    
    def run(self):
        self.root.mainloop()