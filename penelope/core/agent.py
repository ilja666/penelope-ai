import os
import json
import anthropic
from typing import Dict, Any, List
from penelope.tools.file_tools import read_file, write_file, list_dir, replace_text
from penelope.tools.terminal_tools import run_command, grep_search, open_app
from penelope.tools.search_tools import search_files
from penelope.tools.android_studio_tools import control_android_studio, new_android_project, open_gemini_agent, send_message_to_gemini, type_in_gemini_chat
from penelope.tools.ide_tools import control_cursor, control_vscode, control_git, control_python, control_npm

class PenelopeAgent:
    def __init__(self):
        self.api_keys = self._load_keys()
        if not self.api_keys:
            raise ValueError("No valid ANTHROPIC_API_KEYs found in .env")
        
        self.current_key_index = 0
        self.client = anthropic.Anthropic(api_key=self.api_keys[self.current_key_index])
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        self.history = []
        self.tools = {
            "read_file": read_file,
            "write_file": write_file,
            "replace_text": replace_text,
            "list_dir": list_dir,
            "run_command": run_command,
            "grep_search": grep_search,
            "search_files": search_files,
            "open_app": open_app,
            "control_android_studio": control_android_studio,
            "new_android_project": new_android_project,
            "open_gemini_agent": open_gemini_agent,
            "send_message_to_gemini": send_message_to_gemini,
            "type_in_gemini_chat": type_in_gemini_chat,
            "control_cursor": control_cursor,
            "control_vscode": control_vscode,
            "control_git": control_git,
            "control_python": control_python,
            "control_npm": control_npm
        }

    def _load_keys(self) -> List[str]:
        keys = []
        for i in range(1, 6):
            key = os.getenv(f"ANTHROPIC_API_KEY_{i}")
            if key:
                if not key.startswith("sk-"):
                    key = f"sk-ant-{key}" if len(key) < 100 else f"sk-{key}"
                keys.append(key)
        standard_key = os.getenv("ANTHROPIC_API_KEY")
        if standard_key and standard_key not in keys:
            if not standard_key.startswith("sk-"): standard_key = f"sk-ant-{standard_key}"
            keys.append(standard_key)
        return keys

    def _switch_key(self):
        if len(self.api_keys) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            self.client = anthropic.Anthropic(api_key=self.api_keys[self.current_key_index])
            return True
        return False

    def get_system_prompt(self):
        return """You are Penelope, an AI agent inspired by Cursor's agentic flow. 
You act as a pair programmer with full system access.

CORE WORKFLOW:
1. EXPLORE: Use 'list_dir', 'grep_search', and 'read_file' to understand the codebase.
2. PLAN: Explain your thought process to the user.
3. EXECUTE: Use 'write_file' to apply changes and 'run_command' to test or run code.
4. ITERATE: If a command fails or a file isn't what you expected, adjust your approach.

TOOLS:
- read_file(path) -> str
- write_file(path, content) -> str
- replace_text(path, old_text, new_text) -> str
- list_dir(path=".") -> str
- run_command(command) -> str
- grep_search(pattern, path=".") -> str (Finds text in files)
- search_files(pattern) -> str (Regex search across files)
- open_app(app_name) -> str (Opens Windows applications like "android studio", "chrome", etc.)
- control_android_studio(action, **kwargs) -> str (Controls Android Studio: "new_project", "open_gemini", "build", "run", "sync_gradle", etc.)
- new_android_project(project_name, template) -> str (Creates a new Android project)
- open_gemini_agent() -> str (Opens Gemini AI assistant in Android Studio)
- send_message_to_gemini(message) -> str (Types and sends a message in Gemini's chat window)
- type_in_gemini_chat(message) -> str (Types text in Gemini's chat input without sending)
- control_cursor(action, **kwargs) -> str (Control Cursor IDE: "open_project", "open_file", "new_file", "open_composer", "send_to_composer", etc.)
- control_vscode(action, **kwargs) -> str (Control VS Code: "open_project", "open_file", "open_terminal", "run_command")
- control_git(action, **kwargs) -> str (Git operations: "init", "status", "add", "commit", "push", "pull", "branch", "log")
- control_python(action, **kwargs) -> str (Python tools: "run_script", "install_package", "run_tests", "create_venv")
- control_npm(action, **kwargs) -> str (npm operations: "init", "install", "run_script", "build")

RESPONSE FORMAT:
To use a tool, you MUST output a single JSON object:
{
  "thought": "Why you are doing this",
  "action": "tool_name",
  "params": { ... }
}

Wait for the result. If you are done, simply talk to the user.
"""

    def chat(self, user_input: str):
        if not self.history or self.history[-1]["role"] != "user":
            self.history.append({"role": "user", "content": user_input})
        
        # Max iteration to prevent infinite loops
        for _ in range(10):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    system=self.get_system_prompt(),
                    messages=self.history,
                    max_tokens=4000
                )
            except (anthropic.RateLimitError, anthropic.AuthenticationError):
                if self._switch_key(): continue
                raise

            ai_content = response.content[0].text
            self.history.append({"role": "assistant", "content": ai_content})

            # Try to extract JSON for tool call
            try:
                if "{" in ai_content and "}" in ai_content:
                    start = ai_content.find("{")
                    end = ai_content.rfind("}") + 1
                    data = json.loads(ai_content[start:end])
                    
                    if "action" in data:
                        tool_name = data["action"]
                        params = data.get("params", {})
                        if tool_name in self.tools:
                            print(f"[*] Tool: {tool_name} | {data.get('thought', '')}")
                            result = self.tools[tool_name](**params)
                            self.history.append({"role": "user", "content": f"Tool Result ({tool_name}):\n{result}"})
                            continue
            except:
                pass

            return ai_content
        return "I've reached my iteration limit. How should we proceed?"
