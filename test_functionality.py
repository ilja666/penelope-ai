#!/usr/bin/env python
"""
Wrapper to run functionality test cycle
"""
import sys
from pathlib import Path

# Add debug directory to path
debug_dir = Path(__file__).parent / "debug"
sys.path.insert(0, str(debug_dir))

from functionality_test_cycle import run_test_cycle

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Penelope Functionality Test Cycle")
    parser.add_argument("--max-iterations", type=int, default=3, help="Maximum iterations")
    
    args = parser.parse_args()
    
    success = run_test_cycle(max_iterations=args.max_iterations)
    sys.exit(0 if success else 1)
