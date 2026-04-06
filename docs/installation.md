# Instalacja PM Solar Dashboard

## Wymagania

### Home Assistant
- Home Assistant 2024.1 lub nowszy
- HACS (Home Assistant Community Store)

### Wymagane karty HACS (zainstaluj przed importem dashboardu)

| Karta | Wymagana | Opis |
|-------|----------|------|
| [sunsynk-power-flow-card](https://github.com/slipx06/sunsynk-power-flow-card) | Tak | Wizualizacja przepływu energii |
| [mushroom](https://github.com/piitaya/lovelace-mushroom) | Tak | Nowoczesne karty UI |
| [mini-graph-card](https://github.com/kalkih/mini-graph-card) | Tak | Miniaturowe wykresy |
| [apexcharts-card](https://github.com/RomRider/apexcharts-card) | Tak | Zaawansowane wykresy |
| [plotly-graph-card](https://github.com/dbuezas/lovelace-plotly-graph-card) | Tak | Interaktywne wykresy Plotly |
| [power-flow-card-plus](https://github.com/flixlix/power-flow-card-plus) | Tak | Karta przepływu mocy |
| [stack-in-card](https://github.com/custom-cards/stack-in-card) | Tak | Grupowanie kart |
| [flex-horseshoe-card](https://github.com/AmoebeLabs/flex-horseshoe-card) | Opcja | Wskaźniki podkowowe |
| [gauge-card-pro](https://github.com/benjamin-music/gauge-card-pro) | Opcja | Zaawansowane wskaźniki |
| [grid-layout](https://github.com/AmoebeLabs/grid-layout) | Opcja | Layout gridowy |
| [scheduler-card](https://github.com/nielsfaber/scheduler-card) | Opcja | Harmonogram |

### Oprogramowanie
- Python 3.8+ (do generatora)
- PyYAML (`pip install pyyaml`)

## Szybki start

```bash
# 1. Sklonuj repozytorium
git clone https://github.com/pawelmamcarz/pm-ha-dashboards.git
cd pm-ha-dashboards

# 2. Skopiuj konfigurację
cp config.example.yaml config.yaml

# 3. Edytuj config.yaml - dostosuj do swojego systemu
nano config.yaml

# 4. Uruchom generator
python3 generate.py

# 5. Zaimportuj output/dashboard.yaml do Home Assistant
```

Lub użyj skryptu instalacyjnego:

```bash
bash install.sh
```

## Konfiguracja

Szczegóły konfiguracji: [configuration.md](configuration.md)

## Wspierane falowniki

| Falownik | Status | Plik mapowania |
|----------|--------|----------------|
| Deye 3-fazowy | W pełni wspierany | `templates/devices/deye-3phase.yaml` |
| Deye 1-fazowy | Wspierany | `templates/devices/deye-1phase.yaml` |
| Huawei Solar | Podstawowy | `templates/devices/huawei-solar.yaml` |
| Growatt | Planowany | - |
| SolarEdge | Planowany | - |

## Import do Home Assistant

### Metoda 1: Przez UI (zalecana)

1. Otwórz Home Assistant
2. Przejdz do **Ustawienia** > **Dashboardy**
3. Kliknij **+ Dodaj dashboard**
4. Wybierz **Nowy dashboard od zera**
5. Nadaj nazwę (np. "Solar Dashboard")
6. Otwórz nowy dashboard
7. Kliknij **3 kropki** (menu) > **Edytuj dashboard**
8. Kliknij ponownie **3 kropki** > **Edytor surowego kodu**
9. Wklej zawartość pliku `output/dashboard.yaml`
10. Kliknij **Zapisz**

### Metoda 2: Przez API

```bash
# Zastąp YOUR_HA adresem HA i YOUR_TOKEN tokenem dostępu
curl -X POST "http://YOUR_HA:8123/api/config/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Solar Dashboard", "config": '$(cat output/dashboard.yaml | python3 -c "import sys,yaml,json; print(json.dumps(yaml.safe_load(sys.stdin)))")'}'
```

## Rozwiązywanie problemów

### Karty nie wyświetlają się
- Upewnij się, że wszystkie wymagane karty HACS są zainstalowane
- Wyczyść cache przeglądarki (Ctrl+Shift+R)
- Sprawdź konsolę przeglądarki (F12) pod kątem błędów

### Brak danych na wykresach
- Sprawdź czy encje falownika są dostępne w HA (Narzędzia deweloperskie > Stany)
- Upewnij się, że `entity_prefix` w config.yaml jest poprawny
- Poczekaj kilka minut na zebranie danych historycznych

### Generator zgłasza błędy
- Sprawdź czy config.yaml jest poprawnym YAML (np. na yamlvalidator.com)
- Upewnij się, że wybrany brand falownika ma odpowiedni plik w `templates/devices/`
