#!/usr/bin/env python
"""
Wrapper script to run debug cycle from root directory.
The actual debug cycle is located in debug/run_debug_cycle.py
"""
import sys
from pathlib import Path

# Add debug directory to path
debug_dir = Path(__file__).parent / "debug"
sys.path.insert(0, str(debug_dir))

# Import and run
from run_debug_cycle import run_debug_cycle

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
