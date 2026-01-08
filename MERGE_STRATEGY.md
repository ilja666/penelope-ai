# Merge Strategie: Penelope + Fara-7B

**Datum:** 8 januari 2026

## Belangrijk: Fara-7B is Extern Project

**Fara-7B** is een Microsoft project dat al op GitHub staat:
- Repository: https://github.com/microsoft/fara
- Licentie: MIT (open source)
- **Niet committen:** De `fara/` directory in Penelope is alleen voor referentie

## Merge Aanpak

### Optie 1: Fara als Dependency (Aanbevolen)
- Fara installeren via pip: `pip install fara` (als package beschikbaar)
- Of Fara als Git submodule toevoegen (voor development)
- **Voordeel:** Schone scheiding, makkelijke updates

### Optie 2: Fara Code Integreren
- Alleen de benodigde Fara componenten kopiëren naar Penelope
- Aanpassen aan Penelope's architectuur
- **Voordeel:** Volledige controle, geen externe dependencies

### Optie 3: Unified Repository
- Beide projecten in één repo (niet aanbevolen)
- **Nadeel:** Grote repo, moeilijk te onderhouden

## Aanbevolen Strategie: Dependency + Selectieve Integratie

1. **Fara als Git Submodule** (voor development/referentie)
   ```bash
   git submodule add https://github.com/microsoft/fara.git fara
   ```

2. **Alleen benodigde componenten integreren:**
   - Browser management (PlaywrightController)
   - Vision processing (screenshot handling)
   - Action execution (web automation tools)

3. **Penelope architectuur behouden:**
   - Tool-based systeem
   - CLI interface
   - Development workflows

## Wat NIET te committen

- ❌ `fara/` directory (volledige Fara codebase)
- ❌ `jarvis_archive/` (oude versies)
- ✅ Alleen geïntegreerde componenten
- ✅ Nieuwe unified agent code

## Volgende Stappen

1. ✅ `fara/` toegevoegd aan `.gitignore`
2. ⬜ Fara componenten identificeren die nodig zijn
3. ⬜ Selectieve integratie van Fara code
4. ⬜ Unified agent development
5. ⬜ Testing en documentatie
