# FAQ - Najczęstsze pytania

## Ogólne

### Czy to działa bez baterii?
Tak. Ustaw `battery.capacity_wh: 0` w config.yaml, a sekcje bateryjne nie zostaną wygenerowane.

### Czy potrzebuję HACS?
Tak. Dashboard korzysta z custom cards, które instaluje się przez HACS. Lista wymaganych kart: [installation.md](installation.md)

### Czy to działa z Home Assistant OS / Container / Core?
Tak, działa ze wszystkimi wariantami Home Assistant. Wymagany jest jedynie dostęp do interfejsu Lovelace.

### W jakim języku jest dashboard?
Dashboard jest domyślnie w języku polskim. Etykiety można łatwo zmienić w wygenerowanym pliku YAML.

## Instalacja

### Generator zgłasza "ModuleNotFoundError: No module named 'yaml'"
Zainstaluj PyYAML:
```bash
pip install pyyaml
# lub
pip3 install pyyaml
```

### Karty wyświetlają się jako "Custom element doesn't exist"
Zainstaluj brakujące karty w HACS:
1. HACS > Frontend
2. Wyszukaj nazwę karty
3. Zainstaluj
4. Wyczyść cache przeglądarki (Ctrl+Shift+R)

### Wykresy Plotly nie działają
Upewnij się, że `plotly-graph-card` jest zainstalowana z HACS (nie z npm).

## Konfiguracja

### Nie znam entity_prefix mojego falownika
1. Otwórz HA > Narzędzia deweloperskie > Stany
2. Wyszukaj "battery" lub "pv" 
3. Znajdź encję falownika, np. `sensor.deye_inverter_battery`
4. Prefix to część przed ostatnim podkreślnikiem: `deye_inverter`

### Mam dwa falowniki
Skonfiguruj drugi falownik w sekcji `secondary_inverter` w config.yaml.

### Mój falownik nie jest na liście wspieranych
Utwórz własny plik mapowania encji - instrukcja w [supported-devices.md](supported-devices.md).

## Problemy

### Dashboard jest pusty / nie wyświetla danych
1. Sprawdź Narzędzia deweloperskie > Stany - czy encje istnieją
2. Sprawdź czy `entity_prefix` jest poprawny
3. Odczekaj kilka minut na zebranie historii

### Wykres SOC baterii pokazuje dziwne wartości
Upewnij się, że encja SOC zwraca wartości 0-100 (procenty), a nie 0-1.

### Dashboard ładuje się wolno
- Zmniejsz `hours_to_show` na wykresach Plotly
- Wyłącz widoki, których nie potrzebujesz w config.yaml
- Rozważ użycie InfluxDB zamiast domyślnej bazy SQLite
