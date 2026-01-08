# Pre-commit Security Setup

## Automatische Security Checks

Een pre-commit hook is aangemaakt om te voorkomen dat gevoelige bestanden worden gecommit.

### Wat wordt gecontroleerd:

1. **`.env` bestanden** - Worden geblokkeerd
2. **Hardcoded API keys** - Worden gedetecteerd en geblokkeerd
3. **Pattern matching** - Zoekt naar API key patterns in code

### Setup (na git init):

```bash
# Maak hook executable (Linux/Mac)
chmod +x .git/hooks/pre-commit

# Op Windows met Git Bash:
# De hook werkt automatisch
```

### Test de hook:

```bash
# Probeer .env te committen (zou moeten falen)
git add .env
git commit -m "test"
# Output: ❌ ERROR: Attempting to commit .env
```

### Handmatige Check:

Voordat je commit, controleer altijd:

```bash
# Check welke bestanden worden gecommit
git status

# Check of .env wordt gecommit (zou leeg moeten zijn)
git status --porcelain | grep ".env"
```

### Als de hook faalt:

1. **Verwijder gevoelige bestanden uit staging:**
   ```bash
   git reset HEAD .env
   ```

2. **Zorg dat .env in .gitignore staat:**
   ```bash
   echo ".env" >> .gitignore
   ```

3. **Commit opnieuw**
