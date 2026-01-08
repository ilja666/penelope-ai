import subprocess
import sys
import os
import re
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Penelope's tools for autonomous debugging
from penelope.tools.file_tools import read_file, write_file, list_dir, replace_text
from penelope.tools.terminal_tools import run_command, grep_search
from penelope.tools.search_tools import search_files
import anthropic

class WindowChecker:
    """Checks if a Windows application is actually open on screen"""
    
    def __init__(self):
        self._win32gui = None
        self._pywinauto = None
        self._init_windows_libs()
    
    def _init_windows_libs(self):
        """Initialize Windows libraries for window detection"""
        try:
            import win32gui
            self._win32gui = win32gui
        except ImportError:
            pass
        
        try:
            from pywinauto import Desktop
            self._pywinauto = Desktop
        except ImportError:
            pass
    
    def check_app_open(self, app_name: str, window_keywords: list = None) -> Tuple[bool, str]:
        """
        Check if an application window is open.
        Returns (is_open, details)
        """
        if window_keywords is None:
            # Default keywords for common apps
            window_keywords_map = {
                "android studio": ["android studio", "studio"],
                "androidstudio": ["android studio", "studio"],
                "chrome": ["chrome", "google chrome"],
                "firefox": ["firefox", "mozilla"],
                "cursor": ["cursor"],
                "code": ["visual studio code", "code"],
                "vscode": ["visual studio code", "code"],
            }
            window_keywords = window_keywords_map.get(app_name.lower(), [app_name])
        
        # Method 1: Check process
        process_running = self._check_process_running(app_name)
        
        # Method 2: Check windows using win32gui
        window_found = False
        window_details = ""
        
        if self._win32gui:
            window_found, window_details = self._check_windows_win32gui(window_keywords)
        
        # Method 3: Check windows using pywinauto (more reliable)
        if not window_found and self._pywinauto:
            window_found, window_details = self._check_windows_pywinauto(window_keywords)
        
        # If process is running but no window found, wait a bit and retry
        if process_running and not window_found:
            time.sleep(2)
            if self._win32gui:
                window_found, window_details = self._check_windows_win32gui(window_keywords)
            if not window_found and self._pywinauto:
                window_found, window_details = self._check_windows_pywinauto(window_keywords)
        
        is_open = process_running and window_found
        
        details = f"Process: {'Running' if process_running else 'Not running'}, "
        details += f"Window: {'Found' if window_found else 'Not found'}"
        if window_details:
            details += f" ({window_details})"
        
        return is_open, details
    
    def _check_process_running(self, app_name: str) -> bool:
        """Check if process is running"""
        try:
            # Map app names to process names
            process_map = {
                "android studio": "studio64.exe",
                "androidstudio": "studio64.exe",
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "cursor": "Cursor.exe",
                "code": "Code.exe",
                "vscode": "Code.exe",
            }
            
            process_name = process_map.get(app_name.lower(), app_name)
            
            # Check if process is running
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {process_name}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return process_name.lower() in result.stdout.lower()
        except Exception as e:
            print(f"[!] Error checking process: {e}")
            return False
    
    def _check_windows_win32gui(self, keywords: list) -> Tuple[bool, str]:
        """Check windows using win32gui"""
        if not self._win32gui:
            return False, ""
        
        try:
            def enum_handler(hwnd, ctx):
                if self._win32gui.IsWindowVisible(hwnd):
                    window_text = self._win32gui.GetWindowText(hwnd)
                    if window_text:
                        for keyword in keywords:
                            if keyword.lower() in window_text.lower():
                                ctx.append(window_text)
                return True
            
            windows = []
            self._win32gui.EnumWindows(enum_handler, windows)
            
            if windows:
                return True, f"Found: {windows[0]}"
            return False, ""
        except Exception as e:
            print(f"[!] Error checking windows (win32gui): {e}")
            return False, ""
    
    def _check_windows_pywinauto(self, keywords: list) -> Tuple[bool, str]:
        """Check windows using pywinauto"""
        if not self._pywinauto:
            return False, ""
        
        try:
            desktop = self._pywinauto(backend="uia")
            for win in desktop.windows():
                try:
                    if win.is_visible():
                        title = win.window_text()
                        if title:
                            for keyword in keywords:
                                if keyword.lower() in title.lower():
                                    return True, f"Found: {title}"
                except Exception:
                    continue
            return False, ""
        except Exception as e:
            print(f"[!] Error checking windows (pywinauto): {e}")
            return False, ""

class AutonomousAppController:
    """Completely autonomous app controller that uses AI to fix app opening issues"""
    
    def __init__(self, penelope_dir: Path):
        self.penelope_dir = penelope_dir
        self.window_checker = WindowChecker()
        
        # Initialize AI client for autonomous fixing
        self.api_keys = self._load_keys()
        if not self.api_keys:
            raise ValueError("No valid ANTHROPIC_API_KEYs found in .env")
        self.current_key_index = 0
        self.client = anthropic.Anthropic(api_key=self.api_keys[self.current_key_index])
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
    
    def _load_keys(self):
        keys = []
        for i in range(1, 6):
            key = os.getenv(f"ANTHROPIC_API_KEY_{i}")
            if key:
                if not key.startswith("sk-"):
                    key = f"sk-ant-{key}" if len(key) < 100 else f"sk-{key}"
                keys.append(key)
        standard_key = os.getenv("ANTHROPIC_API_KEY")
        if standard_key and standard_key not in keys:
            if not standard_key.startswith("sk-"): 
                standard_key = f"sk-ant-{standard_key}"
            keys.append(standard_key)
        return keys
    
    def _switch_key(self):
        if len(self.api_keys) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            self.client = anthropic.Anthropic(api_key=self.api_keys[self.current_key_index])
            return True
        return False
    
    def analyze_and_fix_app_issue(self, app_name: str, penelope_output: str, check_result: Tuple[bool, str]) -> bool:
        """Uses AI to autonomously analyze why app didn't open and fix it"""
        is_open, details = check_result
        
        if is_open:
            print("[+] App is open, no fix needed")
            return True
        
        print(f"[*] App '{app_name}' is not open. Analyzing issue...")
        print(f"[*] Check result: {details}")
        
        # Gather context about Penelope's code
        source_files = [
            "penelope/core/agent.py",
            "penelope/main.py",
            "penelope/tools/terminal_tools.py",
        ]
        
        codebase_context = self._gather_codebase_context(source_files)
        
        # Create prompt for autonomous fixing
        fix_prompt = f"""You are an autonomous AI that fixes application opening issues. Your task is to analyze why an app didn't open and fix it completely independently.

APP TO OPEN: {app_name}
PENELOPE OUTPUT: {penelope_output}
CHECK RESULT: {details}

CODEBASE CONTEXT:
{codebase_context}

CRITICAL ISSUE: Penelope is trying to use macOS commands ("open -a") on Windows. This won't work!

Your task:
1. Analyze why the app didn't open - Penelope doesn't have a Windows app-opening tool
2. Add a new tool function to penelope/tools/terminal_tools.py called "open_app" that:
   - Takes an app_name parameter
   - Uses Windows-specific commands (subprocess.Popen or os.startfile)
   - For Android Studio, use: r"F:\\Android\\Android Studio\\bin\\studio64.exe" or find it via registry/start menu
3. Add this tool to PenelopeAgent's tools dictionary in penelope/core/agent.py
4. Update the system prompt to mention the open_app tool

Available tools (use JSON format with "action" and "params"):
- read_file: {{"action": "read_file", "params": {{"path": "file_path"}}}}
- write_file: {{"action": "write_file", "params": {{"path": "file_path", "content": "file_content"}}}}
- replace_text: {{"action": "replace_text", "params": {{"path": "file_path", "old_text": "old", "new_text": "new"}}}}
- grep_search: {{"action": "grep_search", "params": {{"pattern": "pattern", "path": "path"}}}}
- list_dir: {{"action": "list_dir", "params": {{"path": "path"}}}}
- search_files: {{"action": "search_files", "params": {{"pattern": "pattern", "directory": "dir"}}}}
- run_command: {{"action": "run_command", "params": {{"command": "command"}}}}

You MUST:
1. Read penelope/tools/terminal_tools.py to see the current tools
2. Read penelope/core/agent.py to see how tools are registered
3. Add an open_app function to terminal_tools.py that works on Windows
4. Register open_app in the PenelopeAgent tools dictionary
5. Update the system prompt to include open_app

IMPORTANT: Use Windows paths and commands. For Android Studio, the path is typically: F:\\Android\\Android Studio\\bin\\studio64.exe"""
        
        # Use AI to autonomously fix
        print("[*] AI is analyzing and fixing the app opening issue...")
        
        history = [
            {"role": "user", "content": fix_prompt}
        ]
        
        max_iterations = 15
        for iteration in range(max_iterations):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    system="""You are an autonomous AI that fixes application opening issues. You analyze why apps don't open and implement fixes completely independently.
You have access to file manipulation tools. Use them to read code, understand the problem, and implement fixes.
Always be thorough - read the relevant files first, then make precise fixes.""",
                    messages=history,
                    max_tokens=4000
                )
            except (anthropic.RateLimitError, anthropic.AuthenticationError):
                if self._switch_key():
                    continue
                raise
            
            # Handle response content
            if not response.content:
                print("[!] Empty response from AI")
                break
            
            # Get text content from response
            ai_content = ""
            if hasattr(response.content[0], 'text'):
                ai_content = response.content[0].text
            elif isinstance(response.content[0], str):
                ai_content = response.content[0]
            else:
                ai_content = str(response.content[0])
            
            history.append({"role": "assistant", "content": ai_content})
            
            print(f"[*] AI Response (iteration {iteration + 1}):")
            print(ai_content[:500] + "..." if len(ai_content) > 500 else ai_content)
            
            # Try to extract and execute tool calls
            tool_called = False
            try:
                # Try to find JSON in the response (handle markdown code blocks)
                json_str = None
                
                # Look for JSON in markdown code blocks first
                if "```json" in ai_content:
                    start = ai_content.find("```json") + 7
                    end = ai_content.find("```", start)
                    if end != -1:
                        json_str = ai_content[start:end].strip()
                elif "```" in ai_content:
                    # Try regular code block
                    start = ai_content.find("```") + 3
                    end = ai_content.find("```", start)
                    if end != -1:
                        potential_json = ai_content[start:end].strip()
                        if potential_json.startswith("{"):
                            json_str = potential_json
                
                # If no code block, try to find JSON directly
                if not json_str and "{" in ai_content and "}" in ai_content:
                    start = ai_content.find("{")
                    # Find the matching closing brace
                    brace_count = 0
                    end = start
                    for i in range(start, len(ai_content)):
                        if ai_content[i] == '{':
                            brace_count += 1
                        elif ai_content[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end = i + 1
                                break
                    json_str = ai_content[start:end]
                
                if json_str:
                    # Clean up JSON string
                    json_str = json_str.strip()
                    # Remove any leading/trailing whitespace or newlines
                    json_str = json_str.strip('`').strip()
                    data = json.loads(json_str)
                    
                    if "action" in data:
                        tool_name = data["action"]
                        params = data.get("params", {})
                        result = self._execute_tool(tool_name, params)
                        
                        print(f"[*] Tool executed: {tool_name}")
                        if result:
                            print(f"[*] Result: {result[:200]}...")
                        
                        history.append({
                            "role": "user", 
                            "content": f"Tool Result ({tool_name}):\n{result}"
                        })
                        tool_called = True
            except Exception as e:
                print(f"[!] Error parsing tool call: {e}")
            
            # If no tool was called and AI says it's done, break
            if not tool_called:
                if any(word in ai_content.lower() for word in ["done", "fixed", "complete", "finished"]):
                    print("[+] AI indicates fix is complete")
                    break
        
        print("[+] Autonomous fixing cycle complete")
        return True
    
    def _gather_codebase_context(self, files: list) -> str:
        """Gathers codebase context by reading relevant files"""
        context = []
        for file_path in files[:5]:  # Limit to 5 files
            full_path = self.penelope_dir / file_path
            if full_path.exists():
                try:
                    content = read_file(str(full_path))
                    context.append(f"\n=== {file_path} ===\n{content[:2000]}")  # Limit file size
                except:
                    pass
        return "\n".join(context)
    
    def _execute_tool(self, tool_name: str, params: dict) -> str:
        """Executes a tool call"""
        # Change to penelope directory for tool execution
        original_cwd = os.getcwd()
        try:
            os.chdir(str(self.penelope_dir))
            
            tools = {
                "read_file": lambda: read_file(params.get("path", "")),
                "write_file": lambda: write_file(params.get("path", ""), params.get("content", "")),
                "replace_text": lambda: replace_text(
                    params.get("path", ""), 
                    params.get("old_text", ""), 
                    params.get("new_text", "")
                ),
                "grep_search": lambda: grep_search(params.get("pattern", ""), params.get("path", ".")),
                "list_dir": lambda: list_dir(params.get("path", ".")),
                "search_files": lambda: search_files(params.get("pattern", ""), params.get("directory", ".")),
                "run_command": lambda: run_command(params.get("command", "")),
            }
            
            if tool_name in tools:
                try:
                    return tools[tool_name]()
                except Exception as e:
                    return f"Error executing {tool_name}: {str(e)}"
            return f"Unknown tool: {tool_name}"
        finally:
            os.chdir(original_cwd)

def run_penelope(query: str, penelope_dir: Path) -> tuple[bool, str, str]:
    """Runs Penelope with a query and returns success status and output"""
    print(f"[*] Starting Penelope with query: {query}")
    
    cmd = [
        sys.executable,
        "run_penelope.py",
        "--query",
        query
    ]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(penelope_dir)
    )
    
    stdout, stderr = process.communicate()
    
    success = process.returncode == 0
    return success, stdout, stderr

def run_app_control_cycle(app_name: str = "android studio", max_iterations: int = 10):
    """Main autonomous app control cycle loop"""
    # Get penelope directory (parent of debug/)
    penelope_dir = Path(__file__).parent.parent
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(penelope_dir / ".env")
    
    controller = AutonomousAppController(penelope_dir)
    window_checker = WindowChecker()
    
    query = f"open {app_name}"
    
    print("=" * 70)
    print("[*] AUTONOMOUS APP CONTROL CYCLE")
    print("=" * 70)
    print(f"[*] App to open: {app_name}")
    print(f"[*] Query: {query}")
    print(f"[*] Max iterations: {max_iterations}")
    print("[*] This will run completely autonomously - AI will fix app opening issues")
    print("-" * 70)
    
    iteration = 0
    consecutive_successes = 0
    max_consecutive_successes = 3
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'=' * 70}")
        print(f"[=== ITERATION {iteration}/{max_iterations} ===]")
        print(f"{'=' * 70}\n")
        
        # Step 1: Start Penelope and give her the task
        success, stdout, stderr = run_penelope(query, penelope_dir)
        
        print(f"\n[*] Penelope response:")
        print(stdout[:500] + "..." if len(stdout) > 500 else stdout)
        
        # Step 2: Wait a bit for app to start
        print("\n[*] Waiting for app to start...")
        time.sleep(3)
        
        # Step 3: Check if app is actually open
        print(f"[*] Checking if {app_name} is open...")
        is_open, details = window_checker.check_app_open(app_name)
        
        if is_open:
            print(f"\n[+] SUCCESS! {app_name} is open!")
            print(f"[*] Details: {details}")
            consecutive_successes += 1
            
            if consecutive_successes >= max_consecutive_successes:
                print(f"\n{'=' * 70}")
                print(f"[+] SUCCESS! {app_name} opened successfully {consecutive_successes} times in a row!")
                print("[+] App control cycle complete - Penelope can open apps!")
                print(f"{'=' * 70}")
                return True
        else:
            consecutive_successes = 0
            print(f"\n[!] FAILED! {app_name} is NOT open")
            print(f"[!] Details: {details}")
            
            # Step 4: Autonomous analysis and fixing
            print(f"\n{'=' * 70}")
            print("[*] AUTONOMOUS FIXING MODE")
            print("[*] AI is analyzing why the app didn't open and fixing it...")
            print(f"{'=' * 70}\n")
            
            if controller.analyze_and_fix_app_issue(app_name, stdout, (is_open, details)):
                print("\n[+] Autonomous fixing completed")
                print("[*] Restarting Penelope to test the fix...")
            else:
                print("\n[!] Autonomous fixing failed")
                print("[!] Manual intervention may be required")
                return False
        
        # Small delay between iterations
        time.sleep(2)
    
    print(f"\n{'=' * 70}")
    print(f"[!] Reached max iterations ({max_iterations})")
    print(f"{'=' * 70}")
    return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Autonomous App Control Cycle")
    parser.add_argument("--app", help="App name to open", default="android studio")
    parser.add_argument("--max-iterations", type=int, default=10, help="Maximum iterations")
    
    args = parser.parse_args()
    
    success = run_app_control_cycle(
        app_name=args.app,
        max_iterations=args.max_iterations
    )
    
    sys.exit(0 if success else 1)
