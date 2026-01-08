import subprocess
import sys
import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Penelope's tools for autonomous debugging
from penelope.tools.file_tools import read_file, write_file, list_dir, replace_text
from penelope.tools.terminal_tools import run_command, grep_search
from penelope.tools.search_tools import search_files
import anthropic

class AutonomousDebugger:
    """Completely autonomous debugger that uses AI to analyze and fix bugs"""
    
    def __init__(self, penelope_dir: Path):
        self.penelope_dir = penelope_dir
        self.crash_dir = penelope_dir / "debug" / "crashes"
        self.crash_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize AI client for autonomous debugging
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
    
    def get_latest_crash(self) -> Optional[Path]:
        """Gets the most recent crash log"""
        crash_files = sorted(self.crash_dir.glob("crash_*.log"), reverse=True)
        return crash_files[0] if crash_files else None
    
    def analyze_and_fix_crash(self) -> bool:
        """Uses AI to autonomously analyze crash and implement fixes"""
        crash_file = self.get_latest_crash()
        if not crash_file:
            print("[!] No crash file found")
            return False
        
        print(f"[*] Analyzing crash: {crash_file.name}")
        
        # Read crash log
        crash_content = read_file(str(crash_file))
        
        # Read relevant source files to understand context
        source_files = self._identify_relevant_files(crash_content)
        codebase_context = self._gather_codebase_context(source_files)
        
        # Create prompt for autonomous debugging
        debug_prompt = f"""You are an autonomous debugging AI. Your task is to analyze a crash and fix it completely independently.

CRASH LOG:
{crash_content}

CODEBASE CONTEXT:
{codebase_context}

Your task:
1. Analyze the crash to understand the root cause
2. Identify which files need to be modified
3. Implement the fix using the available tools
4. Be thorough and make sure the fix addresses the root cause

Available tools (use JSON format with "action" and "params"):
- read_file: {"action": "read_file", "params": {"path": "file_path"}}
- write_file: {"action": "write_file", "params": {"path": "file_path", "content": "file_content"}}
- replace_text: {"action": "replace_text", "params": {"path": "file_path", "old_text": "old", "new_text": "new"}}
- grep_search: {"action": "grep_search", "params": {"pattern": "pattern", "path": "path"}}
- list_dir: {"action": "list_dir", "params": {"path": "path"}}
- search_files: {"action": "search_files", "params": {"pattern": "pattern", "directory": "dir"}}

You MUST use tools to:
1. First, read the relevant source files to understand the code
2. Then, apply fixes using write_file or replace_text
3. Verify your changes make sense

Start by reading the relevant files mentioned in the crash log, then implement the fix."""
        
        # Use AI to autonomously debug
        print("[*] AI is analyzing and fixing the bug autonomously...")
        
        history = [
            {"role": "user", "content": debug_prompt}
        ]
        
        max_iterations = 15
        for iteration in range(max_iterations):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    system="""You are an autonomous debugging AI. You analyze crashes and fix bugs completely independently.
You have access to file manipulation tools. Use them to read code, understand the problem, and implement fixes.
Always be thorough - read the relevant files first, then make precise fixes.""",
                    messages=history,
                    max_tokens=4000
                )
            except (anthropic.RateLimitError, anthropic.AuthenticationError):
                if self._switch_key():
                    continue
                raise
            
            ai_content = response.content[0].text
            history.append({"role": "assistant", "content": ai_content})
            
            print(f"[*] AI Response (iteration {iteration + 1}):")
            print(ai_content[:500] + "..." if len(ai_content) > 500 else ai_content)
            
            # Try to extract and execute tool calls
            tool_called = False
            try:
                if "{" in ai_content and "}" in ai_content:
                    start = ai_content.find("{")
                    end = ai_content.rfind("}") + 1
                    data = json.loads(ai_content[start:end])
                    
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
        
        print("[+] Autonomous debugging cycle complete")
        return True
    
    def _identify_relevant_files(self, crash_content: str) -> list:
        """Identifies relevant source files from crash log"""
        files = []
        
        # Extract file paths from traceback
        file_pattern = r'File "([^"]+)"'
        matches = re.findall(file_pattern, crash_content)
        for match in matches:
            # Convert to relative path if needed
            if "penelope" in match:
                rel_path = match.split("penelope")[-1].lstrip("\\/")
                if rel_path and rel_path.endswith(".py"):
                    files.append(rel_path)
        
        # Also check for common source files
        common_files = [
            "penelope/core/agent.py",
            "penelope/main.py",
            "run_penelope.py"
        ]
        files.extend(common_files)
        
        return list(set(files))  # Remove duplicates
    
    def _gather_codebase_context(self, files: list) -> str:
        """Gathers codebase context by reading relevant files"""
        context = []
        for file_path in files[:5]:  # Limit to 5 files to avoid token limits
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
    
    # Save output for inspection
    debug_dir = penelope_dir / "debug"
    debug_dir.mkdir(exist_ok=True)
    
    with open(debug_dir / "last_run_stdout.log", "w", encoding="utf-8") as f:
        f.write(stdout)
    with open(debug_dir / "last_run_stderr.log", "w", encoding="utf-8") as f:
        f.write(stderr)
    
    success = process.returncode == 0
    return success, stdout, stderr

def run_debug_cycle(max_iterations: int = 10, test_query: str = None):
    """Main autonomous debug cycle loop"""
    # Get penelope directory (parent of debug/)
    penelope_dir = Path(__file__).parent.parent
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(penelope_dir / ".env")
    
    debugger = AutonomousDebugger(penelope_dir)
    
    if test_query is None:
        test_query = "List the files in the current directory and then tell me what is in README.md"
    
    print("=" * 70)
    print("[*] AUTONOMOUS PENELOPE DEBUG CYCLE")
    print("=" * 70)
    print(f"[*] Test query: {test_query}")
    print(f"[*] Max iterations: {max_iterations}")
    print("[*] This will run completely autonomously - AI will analyze and fix bugs")
    print("-" * 70)
    
    iteration = 0
    consecutive_successes = 0
    max_consecutive_successes = 3
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'=' * 70}")
        print(f"[=== ITERATION {iteration}/{max_iterations} ===]")
        print(f"{'=' * 70}\n")
        
        # Step 1: Start Penelope and give her a task
        success, stdout, stderr = run_penelope(test_query, penelope_dir)
        
        if success:
            print(f"\n[+] Penelope finished successfully!")
            print(f"[*] Output preview: {stdout[:300]}...")
            consecutive_successes += 1
            
            if consecutive_successes >= max_consecutive_successes:
                print(f"\n{'=' * 70}")
                print(f"[+] SUCCESS! Penelope ran successfully {consecutive_successes} times in a row!")
                print("[+] Debug cycle complete - Penelope is stable!")
                print(f"{'=' * 70}")
                return True
        else:
            consecutive_successes = 0
            print(f"\n[!] Penelope CRASHED")
            if stderr:
                print(f"[!] Error preview: {stderr[:300]}...")
            
            # Step 2 & 3: Autonomous analysis and fixing
            print(f"\n{'=' * 70}")
            print("[*] AUTONOMOUS DEBUGGING MODE")
            print("[*] AI is analyzing the crash and implementing fixes...")
            print(f"{'=' * 70}\n")
            
            if debugger.analyze_and_fix_crash():
                print("\n[+] Autonomous debugging completed")
                print("[*] Restarting Penelope to test the fix...")
            else:
                print("\n[!] Autonomous debugging failed")
                print("[!] Manual intervention may be required")
                return False
        
        # Small delay between iterations
        import time
        time.sleep(2)
    
    print(f"\n{'=' * 70}")
    print(f"[!] Reached max iterations ({max_iterations})")
    print(f"{'=' * 70}")
    return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Autonomous Penelope Debug Cycle")
    parser.add_argument("--query", help="Test query to give Penelope", default=None)
    parser.add_argument("--max-iterations", type=int, default=10, help="Maximum iterations")
    
    args = parser.parse_args()
    
    success = run_debug_cycle(
        max_iterations=args.max_iterations,
        test_query=args.query
    )
    
    sys.exit(0 if success else 1)
