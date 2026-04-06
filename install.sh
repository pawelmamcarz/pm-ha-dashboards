#!/bin/bash
# =============================================================================
# PM Solar Dashboard - Skrypt instalacyjny
# =============================================================================
# Użycie: bash install.sh
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.yaml"
CONFIG_EXAMPLE="$SCRIPT_DIR/config.example.yaml"
OUTPUT_DIR="$SCRIPT_DIR/output"

# Kolory
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║           PM Solar Dashboard - Instalator               ║"
echo "║     Dashboard energetyczny dla Home Assistant            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# --- Krok 1: Sprawdź Python ---
echo -e "${YELLOW}[1/5] Sprawdzanie wymagań...${NC}"

if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo -e "${RED}BŁĄD: Python 3 nie jest zainstalowany.${NC}"
    echo "Zainstaluj Python 3: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$($PYTHON --version 2>&1)
echo -e "  Python: ${GREEN}$PYTHON_VERSION${NC}"

# Sprawdź PyYAML
if $PYTHON -c "import yaml" 2>/dev/null; then
    echo -e "  PyYAML: ${GREEN}zainstalowany${NC}"
else
    echo -e "  PyYAML: ${RED}brak${NC}"
    echo -e "${YELLOW}Instaluję PyYAML...${NC}"
    $PYTHON -m pip install pyyaml --quiet 2>/dev/null || {
        echo -e "${RED}BŁĄD: Nie udało się zainstalować PyYAML.${NC}"
        echo "Zainstaluj ręcznie: pip install pyyaml"
        exit 1
    }
    echo -e "  PyYAML: ${GREEN}zainstalowany${NC}"
fi

# --- Krok 2: Konfiguracja ---
echo ""
echo -e "${YELLOW}[2/5] Konfiguracja...${NC}"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "  Plik config.yaml nie istnieje."
    echo -e "  Tworzę z szablonu config.example.yaml..."
    cp "$CONFIG_EXAMPLE" "$CONFIG_FILE"
    echo ""
    echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  WAŻNE: Edytuj plik config.yaml przed kontynuacją!${NC}"
    echo ""
    echo "  Dostosuj następujące parametry:"
    echo "  - inverter.brand (deye/huawei/growatt)"
    echo "  - inverter.phases (1/3)"
    echo "  - inverter.entity_prefix (prefix encji w HA)"
    echo "  - battery.capacity_wh"
    echo "  - solar.mppt_count, solar.pv1_max_power"
    echo "  - grid.provider_name"
    echo "  - views.* (które widoki wygenerować)"
    echo ""
    echo -e "  Plik: ${GREEN}$CONFIG_FILE${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
    echo ""
    read -p "Naciśnij Enter gdy config.yaml będzie gotowy (lub Ctrl+C aby przerwać)..."
fi

echo -e "  Używam: ${GREEN}$CONFIG_FILE${NC}"

# --- Krok 3: Sprawdź wymagane HACS cards ---
echo ""
echo -e "${YELLOW}[3/5] Wymagane komponenty HACS...${NC}"
echo ""
echo "  Upewnij się, że masz zainstalowane w HACS:"
echo -e "  ${GREEN}✓${NC} sunsynk-power-flow-card"
echo -e "  ${GREEN}✓${NC} mushroom (mushroom-entity-card, mushroom-template-card, itp.)"
echo -e "  ${GREEN}✓${NC} mini-graph-card"
echo -e "  ${GREEN}✓${NC} apexcharts-card"
echo -e "  ${GREEN}✓${NC} plotly-graph-card"
echo -e "  ${GREEN}✓${NC} power-flow-card-plus"
echo -e "  ${GREEN}✓${NC} stack-in-card"
echo ""
echo "  Opcjonalne (w zależności od widoków):"
echo -e "  ${BLUE}○${NC} flex-horseshoe-card (widok energy_flow)"
echo -e "  ${BLUE}○${NC} gauge-card-pro (widok monitoring)"
echo -e "  ${BLUE}○${NC} scheduler-card (widok monitoring)"
echo -e "  ${BLUE}○${NC} grid-layout (widok energy_flow)"
echo ""

# --- Krok 4: Generuj dashboard ---
echo -e "${YELLOW}[4/5] Generowanie dashboardu...${NC}"

$PYTHON "$SCRIPT_DIR/generate.py"

if [ $? -ne 0 ]; then
    echo -e "${RED}BŁĄD: Generowanie nie powiodło się.${NC}"
    exit 1
fi

# --- Krok 5: Instrukcje importu ---
echo ""
echo -e "${YELLOW}[5/5] Import do Home Assistant${NC}"
echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo -e "  Wygenerowany dashboard: ${GREEN}$OUTPUT_DIR/dashboard.yaml${NC}"
echo ""
echo "  Jak zaimportować do Home Assistant:"
echo ""
echo "  Metoda 1 - Przez UI:"
echo "    1. Otwórz HA → Ustawienia → Dashboardy"
echo "    2. Kliknij + Dodaj dashboard"
echo "    3. Wybierz 'Nowy dashboard od zera'"
echo "    4. Przejdź do edycji dashboardu (3 kropki → Edytuj)"
echo "    5. Kliknij 3 kropki → Edytor YAML"
echo "    6. Wklej zawartość pliku dashboard.yaml"
echo "    7. Zapisz"
echo ""
echo "  Metoda 2 - Przez API:"
echo "    curl -X POST http://YOUR_HA:8123/api/config/dashboard \\"
echo "      -H 'Authorization: Bearer YOUR_TOKEN' \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d @$OUTPUT_DIR/dashboard.json"
echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Gotowe! Dashboard został wygenerowany.${NC}"
