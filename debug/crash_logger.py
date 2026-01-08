import traceback
import os
from datetime import datetime
from pathlib import Path

def log_crash(exception: Exception, context: str = "General"):
    """Logs a crash with full traceback to a file."""
    # Get penelope directory (parent of debug/)
    penelope_dir = Path(__file__).parent.parent
    log_dir = penelope_dir / "debug" / "crashes"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"crash_{timestamp}.log"
    
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Context: {context}\n")
        f.write(f"Exception: {type(exception).__name__}: {str(exception)}\n")
        f.write("-" * 50 + "\n")
        f.write(traceback.format_exc())
        f.write("-" * 50 + "\n")
        
    return log_file
