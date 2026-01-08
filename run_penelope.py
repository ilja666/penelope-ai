"""
Penelope Entry Point
Supports both CLI mode and interactive chat mode
"""
import sys
from pathlib import Path

# Check if CLI command is used
if len(sys.argv) > 1 and sys.argv[1] in ['ide', 'android', 'dev', 'system', 'tools', 'info', 'chat']:
    # Use new CLI
    from penelope.cli import main
    main()
else:
    # Use old interactive mode
    from penelope.main import main
    main()

