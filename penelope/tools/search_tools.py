import os
import re
from pathlib import Path

def search_files(pattern: str, directory: str = ".", extension: str = None) -> str:
    """Search for a regex pattern in files within a directory."""
    results = []
    try:
        path = Path(directory)
        for root, dirs, files in os.walk(path):
            # Skip common hidden/build dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', '.git']]
            
            for file in files:
                if extension and not file.endswith(extension):
                    continue
                
                file_path = Path(root) / file
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                    
                    file_matches = []
                    for i, match in enumerate(matches):
                        if i >= 5: # Limit matches per file
                            file_matches.append("... more matches ...")
                            break
                        
                        # Find line number
                        line_no = content.count('\n', 0, match.start()) + 1
                        line_content = content.splitlines()[line_no-1].strip()
                        file_matches.append(f"Line {line_no}: {line_content}")
                    
                    if file_matches:
                        results.append(f"--- {file_path} ---\n" + "\n".join(file_matches))
                except Exception:
                    continue # Skip binary/unreadable files
                    
        return "\n\n".join(results) if results else "No matches found."
    except Exception as e:
        return f"Error during search: {str(e)}"

