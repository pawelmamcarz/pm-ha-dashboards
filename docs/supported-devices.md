# Wspierane urządzenia

## Falowniki

### W pełni wspierane

| Producent | Model | Fazy | Integracja HA | Plik mapowania |
|-----------|-------|------|---------------|----------------|
| Deye | SUN-xK-SG04LP3 | 3 | [Deye/Sunsynk](https://github.com/StephanJouworst/ha-deye-inverter) | `deye-3phase.yaml` |
| Deye | SUN-xK-SG03LP1 | 1 | Deye/Sunsynk | `deye-1phase.yaml` |

### Podstawowe wsparcie

| Producent | Model | Fazy | Integracja HA | Plik mapowania |
|-----------|-------|------|---------------|----------------|
| Huawei | SUN2000 | 1/3 | [Huawei Solar](https://github.com/wlcrs/huawei_solar) | `huawei-solar.yaml` |

### Planowane

| Producent | Status | ETA |
|-----------|--------|-----|
| Growatt | W przygotowaniu | v1.1 |
| SolarEdge | Planowany | v1.2 |
| Sofar | Planowany | v1.3 |
| GoodWe | Rozważany | - |

## Baterie

| Typ | Wspierane |
|-----|-----------|
| Deye wbudowane (BMS) | Tak |
| Huawei LUNA2000 | Tak |
| Zewnętrzny BMS (EV-BPM, JK-BMS, Daly) | Tak (konfiguracja ręczna) |
| DIY LiFePO4 | Tak (konfiguracja ręczna) |

## Odbiorniki (opcjonalne moduły)

| Urządzenie | Wspierane marki |
|------------|----------------|
| Ładowarka EV | Tesla Wall Connector, Wallbox, OpenEVSE, Easee |
| Pompa ciepła | Panasonic Aquarea, Daikin, Mitsubishi, generyczna |
| Podgrzewacz wody | Dowolny switch w HA |

## Monitoring środowiska (opcjonalny)

| Czujnik | Typ |
|---------|-----|
| Jakość powietrza | PM1, PM2.5, PM10 (dowolny czujnik) |
| CO2 | Dowolny czujnik CO2 w HA |
| Temperatura/wilgotność | Dowolny czujnik w HA |

## Jak dodać własny falownik

1. Skopiuj najbliższy plik z `templates/devices/` jako bazę
2. Dostosuj nazwy encji do swojej integracji HA
3. Zapisz jako `templates/devices/twoj-falownik.yaml`
4. W `config.yaml` ustaw `inverter.brand: twoj-falownik`
5. Uruchom `python3 generate.py`

Zgłoś swoje mapowanie na GitHub - pomóż innym!
