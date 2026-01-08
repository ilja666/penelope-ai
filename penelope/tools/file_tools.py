import os
from pathlib import Path

def read_file(path: str) -> str:
    """Read the content of a file."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(path: str, content: str) -> str:
    """Write content to a file."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def replace_text(path: str, old_text: str, new_text: str) -> str:
    """Replace specific text in a file."""
    try:
        p = Path(path)
        if not p.exists():
            return f"Error: File {path} not found."
        content = p.read_text(encoding="utf-8")
        if old_text not in content:
            return f"Error: Text not found in {path}."
        new_content = content.replace(old_text, new_text)
        p.write_text(new_content, encoding="utf-8")
        return f"Successfully updated {path}"
    except Exception as e:
        return f"Error replacing text: {str(e)}"

def list_dir(path: str = ".") -> str:
    """List contents of a directory with detail (file/dir)."""
    try:
        p = Path(path)
        items = []
        for item in p.iterdir():
            prefix = "[DIR]" if item.is_dir() else "[FILE]"
            items.append(f"{prefix} {item.name}")
        return "\n".join(items) if items else "Directory is empty."
    except Exception as e:
        return f"Error listing directory: {str(e)}"
