# Konfiguracja PM Solar Dashboard

## Plik config.yaml

Skopiuj `config.example.yaml` jako `config.yaml` i dostosuj parametry.

## Sekcje konfiguracji

### dashboard
```yaml
dashboard:
  title: "Dom"        # Tytuł dashboardu w HA
  language: pl         # pl | en
```

### inverter - Falownik główny
```yaml
inverter:
  brand: deye              # deye | huawei | growatt | solaredge
  phases: 3                # 1 (jednofazowy) | 3 (trójfazowy)
  model: deye              # model do karty sunsynk-power-flow-card
  entity_prefix: "deye_inverter"  # prefix encji w Home Assistant
```

**Jak znaleźć entity_prefix:**
1. Otwórz HA > Narzędzia deweloperskie > Stany
2. Wyszukaj encje swojego falownika
3. Jeśli encja to `sensor.deye_inverter_battery`, prefix to `deye_inverter`

### solar - Panele PV
```yaml
solar:
  mppt_count: 2            # Liczba wejść MPPT
  total_max_power: 11000   # Moc szczytowa całej instalacji [W]
  pv1_name: "PV1"          # Nazwa pierwszego stringa
  pv2_name: "PV2"          # Nazwa drugiego stringa
  pv1_max_power: 5500      # Moc szczytowa PV1 [W]
  pv2_max_power: 5500      # Moc szczytowa PV2 [W]
```

### battery - Magazyn energii
```yaml
battery:
  capacity_wh: 10000       # Pojemność nominalna [Wh]
  count: 1                 # Liczba modułów bateryjnych
  max_power: 5000          # Max moc ładowania/rozładowania [W]
  has_bms: false            # Czy masz zewnętrzny system BMS?
```

### grid - Sieć elektryczna
```yaml
grid:
  provider_name: "PGE"     # Nazwa dostawcy (wyświetlana na dashboardzie)
  max_power: 11000         # Moc przyłączeniowa [W]
  has_tou: true            # Czy używasz taryfy wielostrefowej?
  tou_slots: 6             # Liczba okien czasowych TOU (1-6)
```

### loads - Odbiorniki (opcjonalne)
```yaml
loads:
  ev_charger:
    enabled: true           # Włącz moduł ładowarki EV
    name: "Tesla"
    icon: "mdi:car-electric"
    power_entity: "sensor.tesla_wall_connector_power"
    soc_entity: "sensor.tesla_battery_level"

  heat_pump:
    enabled: true
    name: "Pompa ciepła"
    brand: panasonic        # panasonic | daikin | mitsubishi | generic
    power_entity: "sensor.heat_pump_power_consumption"

  water_heater:
    enabled: true
    entity: "switch.water_heater"
```

### views - Widoki do wygenerowania
```yaml
views:
  energy_flow: true        # Główny widok przepływu energii
  overview: true           # Przegląd systemu
  tou_charging: true       # Programowanie TOU
  settings: true           # Ustawienia falownika
  home_control: false      # Sterowanie domem
  monitoring: false        # Monitoring środowiska
```

## Niestandardowe encje

Jeśli Twoje encje HA mają inne nazwy niż domyślne, możesz je nadpisać:

```yaml
solar:
  pv_power_entity: "sensor.my_custom_pv_power"
  daily_production_entity: "sensor.my_daily_solar"

battery:
  bms_soc_entity: "sensor.my_bms_soc"
  bms_soh_entity: "sensor.my_bms_soh"
```

## Przykładowe konfiguracje

### Deye SUN-12K-SG04LP3 (3-fazowy, z baterią)
```yaml
inverter:
  brand: deye
  phases: 3
  entity_prefix: "deye_inverter"
solar:
  mppt_count: 2
  total_max_power: 12000
battery:
  capacity_wh: 15000
  max_power: 12000
grid:
  provider_name: "PGE"
  has_tou: true
```

### Deye SUN-5K-SG03LP1 (1-fazowy)
```yaml
inverter:
  brand: deye
  phases: 1
  entity_prefix: "deye_inverter"
solar:
  mppt_count: 2
  total_max_power: 5000
battery:
  capacity_wh: 5120
  max_power: 5000
grid:
  provider_name: "Tauron"
  has_tou: false
```

### Huawei SUN2000 + LUNA2000
```yaml
inverter:
  brand: huawei
  phases: 3
  entity_prefix: "inverter"
solar:
  mppt_count: 2
  total_max_power: 10000
battery:
  capacity_wh: 10000
  max_power: 5000
grid:
  provider_name: "Enea"
```
