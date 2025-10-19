"""
AI Model Interface - Ollama Integration
Handles all AI communication
"""

import requests
import json
from pathlib import Path

class AIModel:
    def __init__(self, model_name="llama3.2:3b"):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/generate"
        self.system_prompt = self.load_system_prompt()
        self.check_connection()
    
    def check_connection(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                print(f"✓ Connected to Ollama")
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                if self.model_name not in model_names:
                    print(f"⚠ Model {self.model_name} not found")
                    if model_names:
                        self.model_name = model_names[0]
                        print(f"→ Using {self.model_name}")
            else:
                raise Exception("Ollama not responding")
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            print("Install Ollama from: https://ollama.ai")
            raise
    
    def load_system_prompt(self):
        prompt_file = Path('ai_core/prompt_templates/system_prompt.txt')
        
        if prompt_file.exists():
            return prompt_file.read_text()
        
        default_prompt = """You are a game development AI assistant.

Capabilities:
- Write C# scripts for Unity
- Write GDScript for Godot
- Write C++ for Unreal Engine
- Explain game development concepts
- Debug code and fix errors
- Suggest game architecture

Guidelines:
- Keep code clean and well-commented
- Follow engine-specific conventions
- Provide complete, working code
- Explain complex logic
- Be concise but thorough

User System: Windows, 16GB RAM, CPU-only
Recommend performance-conscious solutions."""

        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(default_prompt)
        return default_prompt
    
    def generate_response(self, user_message, context="", chat_history=None):
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        
        if chat_history:
            for msg in chat_history[-10:]:
                role = "user" if msg['sender'] == "You" else "assistant"
                messages.append({"role": role, "content": msg['text']})
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": self.format_prompt(messages),
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 2048
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['response'].strip()
            else:
                return f"Error: API returned status {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "Request timed out. Model may be slow on this hardware."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def format_prompt(self, messages):
        prompt = ""
        for msg in messages:
            role = msg['role'].upper()
            content = msg['content']
            prompt += f"{role}:\n{content}\n\n"
        
        prompt += "ASSISTANT:\n"
        return prompt