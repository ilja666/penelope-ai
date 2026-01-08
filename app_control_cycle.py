#!/usr/bin/env python
"""
Wrapper script to run app control cycle from root directory.
The actual app control cycle is located in debug/app_control_cycle.py
"""
import sys
from pathlib import Path

# Add debug directory to path
debug_dir = Path(__file__).parent / "debug"
sys.path.insert(0, str(debug_dir))

# Import and run
from app_control_cycle import run_app_control_cycle

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
