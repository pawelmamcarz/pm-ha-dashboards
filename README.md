# PM Solar Dashboard

**Profesjonalny dashboard energetyczny dla Home Assistant**

Kompletny system monitoringu i zarządzania instalacją fotowoltaiczną z magazynem energii. Generowany automatycznie pod Twój falownik i konfigurację.

<!-- TODO: Dodaj screenshoty dashboardu -->
<!-- ![Dashboard Preview](docs/screenshots/preview.png) -->

## Co oferuje

- **Przepływ energii w czasie rzeczywistym** - wizualizacja solar/bateria/sieć/dom z animacjami
- **Zaawansowane wykresy** - moc w czasie, dzienna/miesięczna produkcja, historia 30+ dni
- **Prognoza solarna** - forecast produkcji na dziś, jutro i pojutrze
- **Programowanie TOU** - 6 okien czasowych z kontrolą ładowania z sieci, sprzedaży i SOC
- **Zarządzanie baterią** - SOC, BMS, limity prądowe, napięcia progowe
- **Ustawienia falownika** - tryby pracy, peak shaving, priorytety, generator
- **Sterowanie domem** - pompa ciepła, ładowarka EV, oświetlenie, gniazdka
- **Monitoring środowiska** - jakość powietrza (PM1/PM2.5/PM10), CO2, pogoda

## Wspierane falowniki

| Falownik | Status |
|----------|--------|
| **Deye 3-fazowy** (SUN-xK-SG04LP3) | W pełni wspierany |
| **Deye 1-fazowy** (SUN-xK-SG03LP1) | Wspierany |
| **Huawei Solar** (SUN2000 + LUNA2000) | Podstawowy |
| Growatt | Wkrótce |
| SolarEdge | Planowany |

## Szybki start

```bash
# Sklonuj repozytorium
git clone https://github.com/pawelmamcarz/pm-ha-dashboards.git
cd pm-ha-dashboards

# Skopiuj i edytuj konfigurację
cp config.example.yaml config.yaml
nano config.yaml    # dostosuj pod swój system

# Wygeneruj dashboard
python3 generate.py

# Zaimportuj output/dashboard.yaml do Home Assistant
```

Lub uruchom interaktywny instalator: `bash install.sh`

## Plany cenowe

| | Solar Starter | Solar Pro | Solar Complete |
|---|:---:|:---:|:---:|
| **Cena** | **Darmowy** | **79 PLN** | **199 PLN** |
| Przepływ energii | v | v | v |
| Wykresy mocy i energii | - | v | v |
| Przegląd systemu | - | v | v |
| Programowanie TOU | - | v | v |
| Ustawienia falownika | - | v | v |
| Sterowanie domem | - | - | v |
| Monitoring środowiska | - | - | v |
| Generator konfiguracji | v | v | v |
| Wsparcie email | - | 30 dni | 90 dni |
| Aktualizacje | - | 12 mies. | 12 mies. |

**Solar Starter** jest darmowy i open source (MIT). Idealny do przetestowania przed zakupem.

## Wymagane karty HACS

- [sunsynk-power-flow-card](https://github.com/slipx06/sunsynk-power-flow-card)
- [mushroom](https://github.com/piitaya/lovelace-mushroom)
- [mini-graph-card](https://github.com/kalkih/mini-graph-card)
- [apexcharts-card](https://github.com/RomRider/apexcharts-card)
- [plotly-graph-card](https://github.com/dbuezas/lovelace-plotly-graph-card)
- [power-flow-card-plus](https://github.com/flixlix/power-flow-card-plus)
- [stack-in-card](https://github.com/custom-cards/stack-in-card)

## Dokumentacja

- [Instalacja](docs/installation.md)
- [Konfiguracja](docs/configuration.md)
- [Wspierane urządzenia](docs/supported-devices.md)
- [FAQ](docs/faq.md)

## Struktura projektu

```
pm-ha-dashboards/
├── config.example.yaml      # Szablon konfiguracji
├── generate.py              # Generator dashboardu
├── install.sh               # Interaktywny instalator
├── templates/
│   ├── views/               # Szablony widoków
│   └── devices/             # Mapowania encji falowników
├── docs/                    # Dokumentacja
├── examples/                # Gotowe przykłady
├── free/                    # Darmowy tier (Solar Starter)
└── output/                  # Wygenerowany dashboard (po uruchomieniu generate.py)
```

## Dla instalatorów PV

Oferujemy licencje zbiorcze i white-label dashboardy dla firm instalacyjnych:
- Pakiety 10/50/100 instalacji
- Dashboard z Twoim logo i brandingiem
- Konfiguracja na zamówienie pod konkretny sprzęt

Kontakt: pawel@mamcarz.com

## Licencja

- **Free tier (Solar Starter):** MIT License
- **Paid tiers:** Commercial License - szczegóły w [LICENSE](LICENSE)

## Autor

**Pawel Mamcarz** - pawel@mamcarz.com

Dashboard stworzony na bazie produkcyjnego systemu zarządzania energią (Deye 3-fazowy + 16kWh LiFePO4 + fotowoltaika).
