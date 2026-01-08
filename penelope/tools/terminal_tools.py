import subprocess
import os
import re
from pathlib import Path

def grep_search(pattern: str, path: str = ".", recursive: bool = True) -> str:
    """Find exact text or regex pattern in files (like ripgrep)."""
    results = []
    try:
        p = Path(path)
        files_to_check = p.rglob("*") if recursive else p.glob("*")
        
        for file_path in files_to_check:
            if file_path.is_dir() or any(part.startswith('.') for part in file_path.parts):
                continue
            if 'node_modules' in file_path.parts or 'venv' in file_path.parts or '__pycache__' in file_path.parts:
                continue
                
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                matches = [line for line in content.splitlines() if re.search(pattern, line, re.IGNORECASE)]
                if matches:
                    results.append(f"--- {file_path} ---\n" + "\n".join(matches[:10]))
            except:
                continue
        
        return "\n\n".join(results) if results else "No matches found."
    except Exception as e:
        return f"Error in grep: {str(e)}"

def run_command(command: str, cwd: str = None) -> str:
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
            timeout=120
        )
        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
        return output or "Command executed successfully."
    except Exception as e:
        return f"Error executing command: {str(e)}"

def open_app(app_name: str) -> str:
    """Open a Windows application by name."""
    import platform
    
    if platform.system() != "Windows":
        return f"Error: open_app only works on Windows. Current system: {platform.system()}"
    
    # Map of app names to their executable paths
    app_paths = {
        "android studio": r"F:\Android\Android Studio\bin\studio64.exe",
        "androidstudio": r"F:\Android\Android Studio\bin\studio64.exe",
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
        "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "notepad": "notepad.exe",
        "calc": "calc.exe",
        "calculator": "calc.exe",
        "explorer": "explorer.exe",
        "cmd": "cmd.exe",
        "powershell": "powershell.exe",
        "cursor": r"C:\Users\Ilja\AppData\Local\Programs\cursor\Cursor.exe",
        "code": "code.cmd",
        "vscode": "code.cmd",
    }
    
    app_name_lower = app_name.lower().strip()
    
    # Check if we have a known path
    if app_name_lower in app_paths:
        app_path = app_paths[app_name_lower]
        try:
            # Try to open the application
            if os.path.exists(app_path):
                subprocess.Popen([app_path], shell=False)
                return f"Successfully opened {app_name}"
            else:
                # If path doesn't exist, try as command
                subprocess.Popen([app_path], shell=True)
                return f"Started {app_name} (as command)"
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"
    
    # If not in known paths, try to run it as a command
    try:
        subprocess.Popen([app_name], shell=True)
        return f"Started {app_name} (as command - may not work if not in PATH)"
    except Exception as e:
        return f"Error opening {app_name}: {str(e)}. Known apps: {', '.join(app_paths.keys())}"
