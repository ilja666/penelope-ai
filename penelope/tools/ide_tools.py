"""
IDE and Development Tools Control for Penelope
Provides unified interface for controlling various IDEs and development tools
"""
import subprocess
import os
import time
import platform
from typing import Optional, Dict, Any
from pathlib import Path

def _ensure_app_focused(app_name: str) -> bool:
    """Ensure an application window is focused"""
    if platform.system() != "Windows":
        return False
    
    try:
        import win32gui
        import win32con
        
        def find_window(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if app_name.lower() in window_text.lower():
                    ctx.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(find_window, windows)
        
        if windows:
            hwnd = windows[0]
            win32gui.SetForegroundWindow(hwnd)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.5)
            return True
        return False
    except ImportError:
        try:
            import pyautogui
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.5)
            return True
        except:
            return False
    except Exception:
        return False

def _send_key_combination(*keys):
    """Send a key combination using pyautogui"""
    try:
        import pyautogui
        pyautogui.hotkey(*keys)
        time.sleep(0.3)
        return True
    except ImportError:
        return False
    except Exception as e:
        return False

def _type_text(text: str, delay: float = 0.1):
    """Type text using pyautogui"""
    try:
        import pyautogui
        pyautogui.write(text, interval=delay)
        time.sleep(0.3)
        return True
    except ImportError:
        return False
    except Exception as e:
        return False

# ============================================================================
# CURSOR IDE CONTROL
# ============================================================================

def control_cursor(action: str, **kwargs) -> str:
    """
    Control Cursor IDE programmatically.
    
    Available actions:
    - "open_project": Open a project/folder (requires path)
    - "open_file": Open a specific file (requires path)
    - "new_file": Create a new file (requires path, optional content)
    - "open_terminal": Open integrated terminal
    - "open_composer": Open Cursor Composer (AI chat)
    - "send_to_composer": Send message to Composer (requires message)
    - "run_command": Run command in terminal (requires command)
    """
    if platform.system() != "Windows":
        return f"Error: Cursor control only works on Windows"
    
    cursor_path = r"C:\Users\Ilja\AppData\Local\Programs\cursor\Cursor.exe"
    
    try:
        if action == "open_project":
            path = kwargs.get("path", "")
            if not path:
                return "Error: path parameter required"
            subprocess.Popen([cursor_path, path])
            return f"Opened Cursor with project: {path}"
        
        elif action == "open_file":
            path = kwargs.get("path", "")
            if not path:
                return "Error: path parameter required"
            subprocess.Popen([cursor_path, path])
            return f"Opened file in Cursor: {path}"
        
        elif action == "new_file":
            path = kwargs.get("path", "")
            content = kwargs.get("content", "")
            if not path:
                return "Error: path parameter required"
            
            # Create file first, then open in Cursor
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if content:
                p.write_text(content, encoding="utf-8")
            else:
                p.touch()
            
            subprocess.Popen([cursor_path, path])
            return f"Created and opened new file: {path}"
        
        elif action == "open_terminal":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', '`')  # Toggle terminal
            return "Opened terminal in Cursor"
        
        elif action == "open_composer":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            _send_key_combination('ctrl', 'shift', 'i')  # Open Composer
            time.sleep(1)
            return "Opened Cursor Composer"
        
        elif action == "send_to_composer":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            message = kwargs.get("message", "")
            if not message:
                return "Error: message parameter required"
            
            # Open Composer first
            _send_key_combination('ctrl', 'shift', 'i')
            time.sleep(1)
            _type_text(message, delay=0.05)
            time.sleep(0.5)
            _send_key_combination('enter')
            return f"Sent message to Cursor Composer: {message[:50]}..."
        
        elif action == "run_command":
            if not _ensure_app_focused("cursor"):
                return "Error: Cursor is not open or not focused"
            command = kwargs.get("command", "")
            if not command:
                return "Error: command parameter required"
            
            # Open terminal and run command
            _send_key_combination('ctrl', '`')
            time.sleep(0.5)
            _type_text(command, delay=0.05)
            _send_key_combination('enter')
            return f"Ran command in Cursor terminal: {command}"
        
        else:
            return f"Error: Unknown action '{action}'. Available: open_project, open_file, new_file, open_terminal, open_composer, send_to_composer, run_command"
    
    except Exception as e:
        return f"Error executing Cursor action '{action}': {str(e)}"

# ============================================================================
# VS CODE CONTROL
# ============================================================================

def control_vscode(action: str, **kwargs) -> str:
    """
    Control Visual Studio Code programmatically.
    
    Available actions:
    - "open_project": Open a project/folder (requires path)
    - "open_file": Open a specific file (requires path)
    - "open_terminal": Open integrated terminal
    - "run_command": Run command in terminal (requires command)
    """
    if platform.system() != "Windows":
        return f"Error: VS Code control only works on Windows"
    
    try:
        if action == "open_project":
            path = kwargs.get("path", "")
            if not path:
                return "Error: path parameter required"
            subprocess.Popen(["code", path])
            return f"Opened VS Code with project: {path}"
        
        elif action == "open_file":
            path = kwargs.get("path", "")
            if not path:
                return "Error: path parameter required"
            subprocess.Popen(["code", path])
            return f"Opened file in VS Code: {path}"
        
        elif action == "open_terminal":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            _send_key_combination('ctrl', '`')
            return "Opened terminal in VS Code"
        
        elif action == "run_command":
            if not _ensure_app_focused("code"):
                return "Error: VS Code is not open or not focused"
            command = kwargs.get("command", "")
            if not command:
                return "Error: command parameter required"
            
            _send_key_combination('ctrl', '`')
            time.sleep(0.5)
            _type_text(command, delay=0.05)
            _send_key_combination('enter')
            return f"Ran command in VS Code terminal: {command}"
        
        else:
            return f"Error: Unknown action '{action}'. Available: open_project, open_file, open_terminal, run_command"
    
    except Exception as e:
        return f"Error executing VS Code action '{action}': {str(e)}"

# ============================================================================
# GIT CONTROL
# ============================================================================

def control_git(action: str, **kwargs) -> str:
    """
    Control Git operations programmatically.
    
    Available actions:
    - "init": Initialize a new repository (requires path)
    - "status": Check repository status (requires path)
    - "add": Add files to staging (requires path, optional files)
    - "commit": Make a commit (requires path, message)
    - "push": Push to remote (requires path)
    - "pull": Pull from remote (requires path)
    - "branch": List/create branches (requires path, optional branch_name)
    - "log": Show commit log (requires path)
    """
    try:
        path = kwargs.get("path", ".")
        cwd = Path(path).resolve() if path else Path.cwd()
        
        if action == "init":
            result = subprocess.run(
                ["git", "init"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout or "Repository initialized"
        
        elif action == "status":
            result = subprocess.run(
                ["git", "status"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout or result.stderr or "Status checked"
        
        elif action == "add":
            files = kwargs.get("files", ".")
            result = subprocess.run(
                ["git", "add", files] if files != "." else ["git", "add", "."],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout or f"Added {files} to staging"
        
        elif action == "commit":
            message = kwargs.get("message", "")
            if not message:
                return "Error: message parameter required for commit"
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout or f"Committed: {message}"
        
        elif action == "push":
            result = subprocess.run(
                ["git", "push"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout or result.stderr or "Pushed to remote"
        
        elif action == "pull":
            result = subprocess.run(
                ["git", "pull"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout or result.stderr or "Pulled from remote"
        
        elif action == "branch":
            branch_name = kwargs.get("branch_name", "")
            if branch_name:
                result = subprocess.run(
                    ["git", "checkout", "-b", branch_name],
                    cwd=str(cwd),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.stdout or f"Created and switched to branch: {branch_name}"
            else:
                result = subprocess.run(
                    ["git", "branch"],
                    cwd=str(cwd),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.stdout or "Listed branches"
        
        elif action == "log":
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout or "No commits found"
        
        else:
            return f"Error: Unknown action '{action}'. Available: init, status, add, commit, push, pull, branch, log"
    
    except Exception as e:
        return f"Error executing Git action '{action}': {str(e)}"

# ============================================================================
# PYTHON DEVELOPMENT TOOLS
# ============================================================================

def control_python(action: str, **kwargs) -> str:
    """
    Control Python development operations.
    
    Available actions:
    - "run_script": Run a Python script (requires path)
    - "install_package": Install a package via pip (requires package)
    - "run_tests": Run pytest tests (requires path)
    - "create_venv": Create virtual environment (requires path)
    """
    try:
        if action == "run_script":
            script_path = kwargs.get("path", "")
            if not script_path:
                return "Error: path parameter required"
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout or result.stderr or "Script executed"
        
        elif action == "install_package":
            package = kwargs.get("package", "")
            if not package:
                return "Error: package parameter required"
            result = subprocess.run(
                ["pip", "install", package],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout or result.stderr or f"Installed {package}"
        
        elif action == "run_tests":
            test_path = kwargs.get("path", ".")
            result = subprocess.run(
                ["pytest", test_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout or result.stderr or "Tests executed"
        
        elif action == "create_venv":
            venv_path = kwargs.get("path", "venv")
            result = subprocess.run(
                ["python", "-m", "venv", venv_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout or f"Created virtual environment: {venv_path}"
        
        else:
            return f"Error: Unknown action '{action}'. Available: run_script, install_package, run_tests, create_venv"
    
    except Exception as e:
        return f"Error executing Python action '{action}': {str(e)}"

# ============================================================================
# NODE.JS / NPM CONTROL
# ============================================================================

def control_npm(action: str, **kwargs) -> str:
    """
    Control Node.js/npm operations.
    
    Available actions:
    - "init": Initialize npm project (requires path)
    - "install": Install packages (requires path, optional package)
    - "run_script": Run npm script (requires path, script_name)
    - "build": Run build script (requires path)
    """
    try:
        path = kwargs.get("path", ".")
        cwd = Path(path).resolve() if path else Path.cwd()
        
        if action == "init":
            result = subprocess.run(
                ["npm", "init", "-y"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout or "Initialized npm project"
        
        elif action == "install":
            package = kwargs.get("package", "")
            if package:
                result = subprocess.run(
                    ["npm", "install", package],
                    cwd=str(cwd),
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            else:
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=str(cwd),
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            return result.stdout or result.stderr or "Packages installed"
        
        elif action == "run_script":
            script_name = kwargs.get("script_name", "")
            if not script_name:
                return "Error: script_name parameter required"
            result = subprocess.run(
                ["npm", "run", script_name],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout or result.stderr or f"Ran script: {script_name}"
        
        elif action == "build":
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout or result.stderr or "Build completed"
        
        else:
            return f"Error: Unknown action '{action}'. Available: init, install, run_script, build"
    
    except Exception as e:
        return f"Error executing npm action '{action}': {str(e)}"
