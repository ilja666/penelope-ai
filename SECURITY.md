# Security Guidelines

## API Keys & Secrets

**⚠️ BELANGRIJK: Nooit API keys of secrets committen naar Git!**

### Veilige Praktijken

1. **Gebruik altijd `.env` bestanden** voor API keys
2. **`.env` staat in `.gitignore`** - wordt nooit gecommit
3. **Gebruik `env_example.txt`** als template voor andere developers
4. **Nooit hardcode** API keys in source code

### Environment Variables

De volgende environment variables worden gebruikt:

- `ANTHROPIC_API_KEY` - Anthropic Claude API key
- `ANTHROPIC_API_KEY_1` tot `ANTHROPIC_API_KEY_5` - Extra API keys voor fallback
- `OPENAI_API_KEY` - OpenAI API key (optioneel)
- `WORKING_DIRECTORY` - Working directory path

### Pre-commit Checklist

Voordat je commit, controleer:

- [ ] Geen `.env` bestanden in staging area
- [ ] Geen hardcoded API keys in code
- [ ] Geen secrets in log files
- [ ] Geen credentials in comments
- [ ] `.gitignore` bevat alle gevoelige bestanden

### Als je per ongeluk een key hebt gecommit

1. **Onmiddellijk de key roteren** bij de provider
2. **Verwijder uit Git history:**
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (alleen als je zeker weet wat je doet!)

### Best Practices

- Gebruik altijd environment variables
- Gebruik `.env.example` als template
- Documenteer welke keys nodig zijn in README
- Review code voor hardcoded secrets
- Gebruik secret management tools voor productie
