# Penelope CLI Guide

## Overzicht

Penelope heeft nu een uitgebreide Command Line Interface met subcommands voor verschillende operaties.

## Basis Gebruik

### Interactive Chat Mode (standaard)
```bash
penelope
# of
penelope chat --interactive
# of
penelope chat -i
```

### Single Query
```bash
penelope chat "open android studio"
# of
penelope --query "open android studio"
```

## CLI Commands Overzicht

### Chat Commands
- `penelope chat [QUERY]` - Chat met Penelope
- `penelope chat --interactive` - Start interactive mode

### IDE Commands
- `penelope ide cursor <action> [options]` - Control Cursor IDE
- `penelope ide vscode <action> [options]` - Control VS Code
- `penelope ide git <action> [options]` - Git operations

### Android Studio Commands
- `penelope android studio <action> [options]` - Control Android Studio
- `penelope android gemini <message>` - Send message to Gemini

### Development Tools Commands
- `penelope dev python <action> [options]` - Python tools
- `penelope dev npm <action> [options]` - npm/Node.js operations

### System Commands
- `penelope system open <app_name>` - Open application
- `penelope system run <command>` - Run system command

### Info Commands
- `penelope tools` - List all available tools
- `penelope info` - Show Penelope information
- `penelope --version` - Show version

## Voorbeelden

### Cursor IDE
```bash
# Open project in Cursor
penelope ide cursor open_project --path "F:/myproject"

# Open file
penelope ide cursor open_file --path "F:/myproject/main.py"

# Send message to Composer
penelope ide cursor send_to_composer --message "help me with this code"
```

### Git Operations
```bash
# Check status
penelope ide git status --path "F:/myproject"

# Add files
penelope ide git add --path "F:/myproject" --files "*.py"

# Commit
penelope ide git commit --path "F:/myproject" --message "Initial commit"

# Push
penelope ide git push --path "F:/myproject"
```

### Android Studio
```bash
# Open Gemini
penelope android studio open_gemini

# Send message to Gemini
penelope android gemini "create a new activity"

# Build project
penelope android studio build
```

### Python Development
```bash
# Run script
penelope dev python run_script --path "script.py"

# Install package
penelope dev python install_package --package "requests"

# Run tests
penelope dev python run_tests --path "tests/"
```

### npm Operations
```bash
# Initialize project
penelope dev npm init --path "F:/myproject"

# Install packages
penelope dev npm install --path "F:/myproject" --package "express"

# Run script
penelope dev npm run_script --path "F:/myproject" --script "start"
```

## CLI Features

✅ **Subcommands** - Georganiseerde command structuur
✅ **Options** - Flexibele parameters per command
✅ **Help System** - Automatische help via `--help`
✅ **Rich Output** - Mooie formatted output met Rich library
✅ **Error Handling** - Goede error messages
✅ **Interactive Mode** - Chat interface met styled prompt

## Toekomstige Uitbreidingen

- Auto-completion voor commands
- Command history
- Aliases voor veel gebruikte commands
- Config file voor default paths
- Plugin system voor custom commands
