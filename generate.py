#!/usr/bin/env python3
# =============================================================================
# PM Solar Dashboard Generator
# =============================================================================
# Generates a Home Assistant dashboard YAML from user config and device
# entity templates.
#
# Usage:  python3 generate.py
# =============================================================================

import os
import sys
import re
import yaml


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.yaml")
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates", "devices")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "dashboard.yaml")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def load_config():
    """Load and validate user configuration from config.yaml."""
    if not os.path.isfile(CONFIG_PATH):
        print(f"[ERROR] Configuration file not found: {CONFIG_PATH}")
        print("        Copy config.example.yaml to config.yaml and edit it.")
        sys.exit(1)

    print("[1/5] Loading config.yaml ...")
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    if not config:
        print("[ERROR] config.yaml is empty or invalid.")
        sys.exit(1)

    # Validate required top-level keys
    for key in ("dashboard", "inverter", "solar", "battery", "grid", "views"):
        if key not in config:
            print(f"[ERROR] Missing required section '{key}' in config.yaml")
            sys.exit(1)

    return config


def _resolve_template_filename(config):
    """Determine which device template file to load based on inverter config."""
    brand = config["inverter"].get("brand", "deye").lower()
    phases = config["inverter"].get("phases", 1)

    # Build candidate filenames in priority order
    candidates = []
    if phases == 3:
        candidates.append(f"{brand}-3phase.yaml")
    else:
        candidates.append(f"{brand}-1phase.yaml")
    candidates.append(f"{brand}.yaml")

    for name in candidates:
        path = os.path.join(TEMPLATES_DIR, name)
        if os.path.isfile(path):
            return path

    print(f"[ERROR] No device template found for brand='{brand}', phases={phases}")
    print(f"        Searched in: {TEMPLATES_DIR}")
    print(f"        Expected one of: {', '.join(candidates)}")
    sys.exit(1)


def load_device_mapping(config):
    """Load entity mapping from the appropriate device template."""
    path = _resolve_template_filename(config)
    print(f"[2/5] Loading device template: {os.path.basename(path)} ...")
    with open(path, "r", encoding="utf-8") as fh:
        mapping = yaml.safe_load(fh)

    if not mapping or "entities" not in mapping:
        print(f"[ERROR] Device template {path} is missing 'entities' section.")
        sys.exit(1)

    return mapping["entities"]


def resolve_entities(raw_entities, config):
    """Replace {{ prefix }} placeholders with the configured entity_prefix."""
    prefix = config["inverter"].get("entity_prefix", "inverter")
    print(f"[3/5] Resolving entities with prefix '{prefix}' ...")

    resolved = {}
    pattern = re.compile(r"\{\{\s*prefix\s*\}\}")
    for key, value in raw_entities.items():
        if isinstance(value, str):
            resolved[key] = pattern.sub(prefix, value)
        else:
            resolved[key] = value

    # Apply user-level entity overrides from config sections
    _apply_overrides(resolved, config)
    return resolved


def _apply_overrides(entities, config):
    """Allow user to override specific entities via config sections."""
    solar_cfg = config.get("solar", {})
    battery_cfg = config.get("battery", {})

    override_map = {
        "pv_power": solar_cfg.get("pv_power_entity"),
        "daily_pv_energy": solar_cfg.get("daily_production_entity"),
        "battery_soc": battery_cfg.get("bms_soc_entity"),
    }
    for key, val in override_map.items():
        if val:
            entities[key] = val


def build_dashboard(config, entities):
    """Assemble the full dashboard structure from enabled views."""
    print("[4/5] Building dashboard views ...")

    dashboard = {
        "title": config["dashboard"].get("title", "Solar"),
        "views": [],
    }

    views_cfg = config.get("views", {})

    view_builders = [
        ("energy_flow", build_energy_flow_view),
        ("overview", build_overview_view),
        ("tou_charging", build_tou_view),
        ("settings", build_settings_view),
        ("home_control", build_home_control_view),
        ("monitoring", build_monitoring_view),
    ]

    for view_key, builder_fn in view_builders:
        if views_cfg.get(view_key, False):
            print(f"       + {view_key}")
            view = builder_fn(config, entities)
            dashboard["views"].append(view)

    if not dashboard["views"]:
        print("[WARNING] No views are enabled in config.yaml / views section.")

    return dashboard


# ---------------------------------------------------------------------------
# View builders
# ---------------------------------------------------------------------------

def build_energy_flow_view(config, entities):
    """Main energy-flow view with power-flow card, real-time graph and daily bar chart."""
    solar_cfg = config.get("solar", {})
    battery_cfg = config.get("battery", {})
    grid_cfg = config.get("grid", {})
    inv_cfg = config.get("inverter", {})

    flow_card = {
        "type": "custom:sunsynk-power-flow-card",
        "cardstyle": "full",
        "show_solar": True,
        "show_battery": True,
        "show_grid": True,
        "inverter": {
            "model": inv_cfg.get("model", "deye"),
            "modern": True,
            "auto_scale": True,
        },
        "battery": {
            "energy": battery_cfg.get("capacity_wh", 15960),
            "shutdown_soc": 10,
            "show_daily": True,
            "auto_scale": True,
            "soc": entities.get("battery_soc", "sensor.REPLACE_ME"),
            "voltage": entities.get("battery_voltage", "sensor.REPLACE_ME"),
            "current": entities.get("battery_current", "sensor.REPLACE_ME"),
            "power": entities.get("battery_power", "sensor.REPLACE_ME"),
            "temp": entities.get("battery_temperature", "sensor.REPLACE_ME"),
        },
        "solar": {
            "mppts": solar_cfg.get("mppt_count", 2),
            "show_daily": True,
            "auto_scale": True,
            "pv1_name": solar_cfg.get("pv1_name", "PV1"),
            "pv2_name": solar_cfg.get("pv2_name", "PV2"),
            "pv1_power": entities.get("pv1_power", "sensor.REPLACE_ME"),
            "pv2_power": entities.get("pv2_power", "sensor.REPLACE_ME"),
            "pv1_voltage": entities.get("pv1_voltage", "sensor.REPLACE_ME"),
            "pv2_voltage": entities.get("pv2_voltage", "sensor.REPLACE_ME"),
        },
        "load": {
            "show_daily": True,
            "auto_scale": True,
            "power": entities.get("load_power", "sensor.REPLACE_ME"),
        },
        "grid": {
            "show_daily_buy": True,
            "show_daily_sell": True,
            "auto_scale": True,
            "power": entities.get("grid_power", "sensor.REPLACE_ME"),
            "voltage": entities.get("grid_l1_voltage", "sensor.REPLACE_ME"),
        },
        "entities": {
            "day_pv_energy": entities.get("daily_pv_energy", "sensor.REPLACE_ME"),
            "day_battery_charge": entities.get("daily_battery_charge", "sensor.REPLACE_ME"),
            "day_battery_discharge": entities.get("daily_battery_discharge", "sensor.REPLACE_ME"),
            "day_load_energy": entities.get("daily_load_consumption", "sensor.REPLACE_ME"),
            "day_grid_import": entities.get("daily_energy_bought", "sensor.REPLACE_ME"),
            "day_grid_export": entities.get("daily_energy_sold", "sensor.REPLACE_ME"),
        },
    }

    realtime_graph = {
        "type": "custom:plotly-graph",
        "hours_to_show": 4,
        "refresh_interval": 10,
        "entities": [
            {
                "entity": entities.get("pv_power", "sensor.REPLACE_ME"),
                "name": "Solar",
                "line": {"color": "orange", "width": 2},
                "fill": "tozeroy",
            },
            {
                "entity": entities.get("load_power", "sensor.REPLACE_ME"),
                "name": "Load",
                "line": {"color": "cyan", "width": 2},
            },
            {
                "entity": entities.get("grid_power", "sensor.REPLACE_ME"),
                "name": "Grid",
                "line": {"color": "grey", "width": 2},
            },
            {
                "entity": entities.get("battery_power", "sensor.REPLACE_ME"),
                "name": "Battery",
                "line": {"color": "green", "width": 2},
            },
            {
                "entity": entities.get("battery_soc", "sensor.REPLACE_ME"),
                "name": "SOC",
                "yaxis": "y2",
                "line": {"color": "lime", "dash": "dot", "width": 1},
            },
        ],
        "layout": {
            "yaxis": {"title": "W"},
            "yaxis2": {"title": "SOC %", "overlaying": "y", "side": "right", "range": [0, 100]},
        },
    }

    daily_chart = {
        "type": "custom:plotly-graph",
        "hours_to_show": 120,
        "refresh_interval": 300,
        "entities": [
            {
                "entity": entities.get("daily_pv_energy", "sensor.REPLACE_ME"),
                "name": "Production",
                "type": "bar",
                "marker": {"color": "orange"},
            },
            {
                "entity": entities.get("daily_load_consumption", "sensor.REPLACE_ME"),
                "name": "Consumption",
                "type": "bar",
                "marker": {"color": "cyan"},
            },
            {
                "entity": entities.get("daily_energy_bought", "sensor.REPLACE_ME"),
                "name": "Import",
                "type": "bar",
                "marker": {"color": "red"},
            },
            {
                "entity": entities.get("daily_energy_sold", "sensor.REPLACE_ME"),
                "name": "Export",
                "type": "bar",
                "marker": {"color": "green"},
            },
        ],
        "layout": {
            "barmode": "group",
            "yaxis": {"title": "kWh"},
        },
    }

    return {
        "title": "Energy Flow",
        "path": "energy-flow",
        "icon": "mdi:flash",
        "type": "custom:grid-layout",
        "layout": {
            "grid-template-columns": "2fr 1fr",
            "grid-template-rows": "auto auto",
            "grid-template-areas": '"flow graph" "flow daily"',
        },
        "cards": [
            {"type": "custom:layout-card", "layout_type": "custom:grid-layout",
             "view_layout": {"grid-area": "flow"}, "cards": [flow_card]},
            {"type": "custom:layout-card", "layout_type": "custom:grid-layout",
             "view_layout": {"grid-area": "graph"}, "cards": [realtime_graph]},
            {"type": "custom:layout-card", "layout_type": "custom:grid-layout",
             "view_layout": {"grid-area": "daily"}, "cards": [daily_chart]},
        ],
    }


def build_overview_view(config, entities):
    """Overview of PV, battery, grid with statistics."""
    solar_cfg = config.get("solar", {})
    battery_cfg = config.get("battery", {})
    grid_cfg = config.get("grid", {})

    status_chips = {
        "type": "custom:mushroom-chips-card",
        "chips": [
            {"type": "entity", "entity": entities.get("running_status", "sensor.REPLACE_ME")},
            {"type": "entity", "entity": entities.get("battery_soc", "sensor.REPLACE_ME"),
             "icon": "mdi:battery"},
            {"type": "entity", "entity": entities.get("grid_connected_status", "sensor.REPLACE_ME"),
             "icon": "mdi:transmission-tower"},
            {"type": "entity", "entity": entities.get("ac_temperature", "sensor.REPLACE_ME"),
             "icon": "mdi:thermometer"},
        ],
    }

    power_flow = {
        "type": "custom:power-flow-card-plus",
        "watt_threshold": 0,
        "entities": {
            "solar": {
                "entity": entities.get("pv_power", "sensor.REPLACE_ME"),
                "display_zero_state": True,
                "color": {"icon_color": "orange"},
            },
            "battery": {
                "entity": entities.get("battery_power", "sensor.REPLACE_ME"),
                "state_of_charge": entities.get("battery_soc", "sensor.REPLACE_ME"),
            },
            "grid": {
                "entity": entities.get("grid_power", "sensor.REPLACE_ME"),
            },
            "home": {
                "entity": entities.get("load_power", "sensor.REPLACE_ME"),
            },
        },
    }

    pv_graph = {
        "type": "custom:mini-graph-card",
        "name": "PV Power",
        "entities": [
            {"entity": entities.get("pv1_power", "sensor.REPLACE_ME"),
             "name": solar_cfg.get("pv1_name", "PV1"), "color": "orange"},
            {"entity": entities.get("pv2_power", "sensor.REPLACE_ME"),
             "name": solar_cfg.get("pv2_name", "PV2"), "color": "darkorange"},
        ],
        "hours_to_show": 24,
        "line_width": 2,
        "show": {"labels": True, "points": False, "legend": True},
    }

    battery_chart = {
        "type": "custom:apexcharts-card",
        "header": {"title": "Battery", "show": True},
        "graph_span": "24h",
        "series": [
            {"entity": entities.get("battery_power", "sensor.REPLACE_ME"),
             "name": "Power", "type": "area", "color": "green"},
            {"entity": entities.get("battery_soc", "sensor.REPLACE_ME"),
             "name": "SOC", "type": "line", "color": "lime",
             "group_by": {"func": "last", "duration": "5min"}},
        ],
    }

    energy_stats = {
        "type": "entities",
        "title": "Daily Energy",
        "entities": [
            {"entity": entities.get("daily_pv_energy", "sensor.REPLACE_ME"),
             "name": "PV Production", "icon": "mdi:solar-power"},
            {"entity": entities.get("daily_load_consumption", "sensor.REPLACE_ME"),
             "name": "Consumption", "icon": "mdi:home-lightning-bolt"},
            {"entity": entities.get("daily_energy_bought", "sensor.REPLACE_ME"),
             "name": "Grid Import", "icon": "mdi:transmission-tower-import"},
            {"entity": entities.get("daily_energy_sold", "sensor.REPLACE_ME"),
             "name": "Grid Export", "icon": "mdi:transmission-tower-export"},
            {"entity": entities.get("daily_battery_charge", "sensor.REPLACE_ME"),
             "name": "Battery Charge", "icon": "mdi:battery-charging"},
            {"entity": entities.get("daily_battery_discharge", "sensor.REPLACE_ME"),
             "name": "Battery Discharge", "icon": "mdi:battery-minus"},
        ],
    }

    return {
        "title": "Overview",
        "path": "overview",
        "icon": "mdi:view-dashboard",
        "type": "sections",
        "max_columns": 3,
        "sections": [
            {"type": "grid", "cards": [status_chips, power_flow]},
            {"type": "grid", "cards": [pv_graph]},
            {"type": "grid", "cards": [battery_chart, energy_stats]},
        ],
    }


def build_tou_view(config, entities):
    """Time-of-Use programming view."""
    grid_cfg = config.get("grid", {})
    prefix = config["inverter"].get("entity_prefix", "inverter")
    tou_slots = grid_cfg.get("tou_slots", 6)

    # Status chips + SOC mini graph
    status_chips = {
        "type": "custom:mushroom-chips-card",
        "chips": [
            {"type": "entity", "entity": entities.get("time_of_use", "sensor.REPLACE_ME"),
             "icon": "mdi:clock-outline"},
            {"type": "entity", "entity": entities.get("battery_soc", "sensor.REPLACE_ME")},
        ],
    }

    soc_graph = {
        "type": "custom:mini-graph-card",
        "name": "SOC",
        "entities": [entities.get("battery_soc", "sensor.REPLACE_ME")],
        "hours_to_show": 24,
        "line_width": 2,
        "color_thresholds": [
            {"value": 20, "color": "red"},
            {"value": 50, "color": "orange"},
            {"value": 80, "color": "green"},
        ],
    }

    # Charge current parameters
    charge_params = {
        "type": "vertical-stack",
        "title": "Charge Parameters",
        "cards": [
            {
                "type": "custom:mushroom-number-card",
                "entity": entities.get("max_battery_charge_current", "sensor.REPLACE_ME"),
                "name": "Max Charge Current",
                "icon": "mdi:current-ac",
            },
            {
                "type": "custom:mushroom-number-card",
                "entity": entities.get("max_battery_discharge_current", "sensor.REPLACE_ME"),
                "name": "Max Discharge Current",
                "icon": "mdi:current-ac",
            },
            {
                "type": "custom:mushroom-number-card",
                "entity": entities.get("max_battery_grid_charge_current", "sensor.REPLACE_ME"),
                "name": "Max Grid Charge Current",
                "icon": "mdi:current-ac",
            },
        ],
    }

    # TOU window cards
    tou_window_cards = []
    for slot in range(1, tou_slots + 1):
        grid_toggle_entity = f"switch.{prefix}_time_of_use_slot_{slot}_grid"
        sell_toggle_entity = f"switch.{prefix}_time_of_use_slot_{slot}_solar_sell"
        gen_toggle_entity = f"switch.{prefix}_time_of_use_slot_{slot}_generator"
        soc_entity = f"number.{prefix}_time_of_use_slot_{slot}_soc"
        power_entity = f"number.{prefix}_time_of_use_slot_{slot}_power"
        start_entity = f"time.{prefix}_time_of_use_slot_{slot}_start"
        end_entity = f"time.{prefix}_time_of_use_slot_{slot}_end"

        window_card = {
            "type": "custom:stack-in-card",
            "mode": "vertical",
            "cards": [
                {
                    "type": "custom:mushroom-template-card",
                    "primary": f"TOU Window {slot}",
                    "secondary": "{{ states('" + start_entity + "') }} - {{ states('" + end_entity + "') }}",
                    "icon": "mdi:clock-time-four-outline",
                    "icon_color": "amber",
                },
                {
                    "type": "custom:mushroom-chips-card",
                    "chips": [
                        {"type": "entity", "entity": grid_toggle_entity,
                         "icon": "mdi:transmission-tower", "name": "Grid"},
                        {"type": "entity", "entity": sell_toggle_entity,
                         "icon": "mdi:cash", "name": "Sell"},
                        {"type": "entity", "entity": gen_toggle_entity,
                         "icon": "mdi:engine", "name": "Gen"},
                    ],
                },
                {
                    "type": "custom:mushroom-number-card",
                    "entity": soc_entity,
                    "name": "Target SOC",
                    "icon": "mdi:battery-charging-medium",
                },
                {
                    "type": "custom:mushroom-number-card",
                    "entity": power_entity,
                    "name": "Power Limit",
                    "icon": "mdi:flash",
                },
            ],
        }
        tou_window_cards.append(window_card)

    # Day-of-week toggles
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_toggles = {
        "type": "custom:mushroom-chips-card",
        "chips": [
            {"type": "entity",
             "entity": f"switch.{prefix}_time_of_use_{day.lower()}",
             "name": day[:3]}
            for day in days
        ],
    }

    # TOU start times
    tou_times = {
        "type": "entities",
        "title": "TOU Start/End Times",
        "entities": [],
    }
    for slot in range(1, tou_slots + 1):
        tou_times["entities"].append({
            "entity": f"time.{prefix}_time_of_use_slot_{slot}_start",
            "name": f"Slot {slot} Start",
        })
        tou_times["entities"].append({
            "entity": f"time.{prefix}_time_of_use_slot_{slot}_end",
            "name": f"Slot {slot} End",
        })

    sections = [
        {"type": "grid", "cards": [status_chips, soc_graph]},
        {"type": "grid", "cards": [charge_params]},
    ]
    # Add TOU windows in pairs (2 per section row)
    for i in range(0, len(tou_window_cards), 2):
        row_cards = tou_window_cards[i:i + 2]
        sections.append({"type": "grid", "cards": row_cards})

    sections.append({"type": "grid", "cards": [day_toggles]})
    sections.append({"type": "grid", "cards": [tou_times]})

    return {
        "title": "TOU Charging",
        "path": "tou",
        "icon": "mdi:clock-check-outline",
        "type": "sections",
        "max_columns": 2,
        "sections": sections,
    }


def build_settings_view(config, entities):
    """Inverter settings and controls."""

    # Operating mode switches
    operating_mode = {
        "type": "vertical-stack",
        "title": "Operating Mode",
        "cards": [
            {
                "type": "custom:mushroom-entity-card",
                "entity": entities.get("power_switch", "sensor.REPLACE_ME"),
                "name": "Inverter Power",
                "icon": "mdi:power",
            },
            {
                "type": "custom:mushroom-entity-card",
                "entity": entities.get("solar_sell", "sensor.REPLACE_ME"),
                "name": "Solar Sell",
                "icon": "mdi:cash-plus",
            },
            {
                "type": "custom:mushroom-entity-card",
                "entity": entities.get("energy_priority", "sensor.REPLACE_ME"),
                "name": "Energy Priority",
                "icon": "mdi:priority-high",
            },
            {
                "type": "custom:mushroom-entity-card",
                "entity": entities.get("force_off_grid", "sensor.REPLACE_ME"),
                "name": "Force Off-Grid",
                "icon": "mdi:transmission-tower-off",
            },
        ],
    }

    # Battery section
    battery_settings = {
        "type": "vertical-stack",
        "title": "Battery",
        "cards": [
            {
                "type": "custom:mushroom-entity-card",
                "entity": entities.get("battery_grid_charging", "sensor.REPLACE_ME"),
                "name": "Grid Charging",
                "icon": "mdi:battery-charging",
            },
            {
                "type": "custom:mushroom-entity-card",
                "entity": entities.get("battery_generator_charging", "sensor.REPLACE_ME"),
                "name": "Generator Charging",
                "icon": "mdi:engine",
            },
            {
                "type": "custom:mushroom-entity-card",
                "entity": entities.get("battery_wake_up", "sensor.REPLACE_ME"),
                "name": "Battery Wake Up",
                "icon": "mdi:alarm",
            },
            {
                "type": "custom:mushroom-number-card",
                "entity": entities.get("max_battery_charge_current", "sensor.REPLACE_ME"),
                "name": "Max Charge Current",
            },
            {
                "type": "custom:mushroom-number-card",
                "entity": entities.get("max_battery_discharge_current", "sensor.REPLACE_ME"),
                "name": "Max Discharge Current",
            },
            {
                "type": "custom:mushroom-number-card",
                "entity": entities.get("battery_shutdown_soc", "sensor.REPLACE_ME"),
                "name": "Shutdown SOC",
                "icon": "mdi:battery-alert",
            },
            {
                "type": "custom:mushroom-number-card",
                "entity": entities.get("battery_shutdown_voltage", "sensor.REPLACE_ME"),
                "name": "Shutdown Voltage",
                "icon": "mdi:flash-alert",
            },
        ],
    }

    # Grid & Generator section
    grid_generator = {
        "type": "vertical-stack",
        "title": "Grid & Generator",
        "cards": [
            {
                "type": "custom:mushroom-entity-card",
                "entity": entities.get("grid_peak_shaving_enable", "sensor.REPLACE_ME"),
                "name": "Peak Shaving",
                "icon": "mdi:chart-bell-curve-cumulative",
            },
            {
                "type": "custom:mushroom-number-card",
                "entity": entities.get("grid_peak_shaving_power", "sensor.REPLACE_ME"),
                "name": "Peak Shaving Power",
            },
            {
                "type": "custom:mushroom-number-card",
                "entity": entities.get("max_sell_power", "sensor.REPLACE_ME"),
                "name": "Max Sell Power",
                "icon": "mdi:flash",
            },
            {
                "type": "custom:mushroom-entity-card",
                "entity": entities.get("generator", "sensor.REPLACE_ME"),
                "name": "Generator",
                "icon": "mdi:engine",
            },
            {
                "type": "custom:mushroom-entity-card",
                "entity": entities.get("generator_always_on", "sensor.REPLACE_ME"),
                "name": "Generator Always On",
                "icon": "mdi:engine-outline",
            },
        ],
    }

    # SmartLoad section
    smartload = {
        "type": "vertical-stack",
        "title": "SmartLoad",
        "cards": [
            {
                "type": "custom:mushroom-number-card",
                "entity": entities.get("smartload_on_soc", "sensor.REPLACE_ME"),
                "name": "SmartLoad ON SOC",
                "icon": "mdi:battery-arrow-up",
            },
            {
                "type": "custom:mushroom-number-card",
                "entity": entities.get("smartload_off_soc", "sensor.REPLACE_ME"),
                "name": "SmartLoad OFF SOC",
                "icon": "mdi:battery-arrow-down",
            },
            {
                "type": "custom:mushroom-number-card",
                "entity": entities.get("smartload_on_voltage", "sensor.REPLACE_ME"),
                "name": "SmartLoad ON Voltage",
                "icon": "mdi:flash",
            },
            {
                "type": "custom:mushroom-number-card",
                "entity": entities.get("smartload_off_voltage", "sensor.REPLACE_ME"),
                "name": "SmartLoad OFF Voltage",
                "icon": "mdi:flash-off",
            },
        ],
    }

    return {
        "title": "Settings",
        "path": "settings",
        "icon": "mdi:cog",
        "type": "sections",
        "max_columns": 2,
        "sections": [
            {"type": "grid", "cards": [operating_mode]},
            {"type": "grid", "cards": [battery_settings]},
            {"type": "grid", "cards": [grid_generator]},
            {"type": "grid", "cards": [smartload]},
        ],
    }


def build_home_control_view(config, entities):
    """Home device control view based on configured loads."""
    loads_cfg = config.get("loads", {})
    cards = []

    for load_key, load_def in loads_cfg.items():
        if not isinstance(load_def, dict):
            continue
        if not load_def.get("enabled", False):
            continue

        entity_id = load_def.get("entity") or load_def.get("power_entity")
        if not entity_id:
            # Build a default entity name from key
            entity_id = f"switch.{load_key}"

        card = {
            "type": "custom:mushroom-entity-card",
            "entity": entity_id,
            "name": load_def.get("name", load_key.replace("_", " ").title()),
            "icon": load_def.get("icon", "mdi:lightning-bolt"),
            "tap_action": {"action": "toggle"},
        }

        # Add SOC sub-entity if available (e.g. EV charger)
        if load_def.get("soc_entity"):
            card["secondary_info"] = "state"

        cards.append(card)

    if not cards:
        cards.append({
            "type": "markdown",
            "content": "No loads are enabled in `config.yaml` under the `loads:` section.",
        })

    return {
        "title": "Home Control",
        "path": "home-control",
        "icon": "mdi:home-automation",
        "type": "sections",
        "max_columns": 3,
        "sections": [
            {"type": "grid", "cards": cards},
        ],
    }


def build_monitoring_view(config, entities):
    """System monitoring, weather, air quality."""
    env_cfg = config.get("environment", {})
    air_cfg = env_cfg.get("air_quality", {})
    indoor_cfg = env_cfg.get("indoor_air", {})

    cards = []

    # Weather card
    cards.append({
        "type": "weather-forecast",
        "entity": "weather.home",
        "show_forecast": True,
    })

    # System monitoring entities
    system_entities = [
        {"entity": entities.get("ac_temperature", "sensor.REPLACE_ME"),
         "name": "AC Temperature", "icon": "mdi:thermometer"},
        {"entity": entities.get("dc_transformer_temp", "sensor.REPLACE_ME"),
         "name": "DC Temperature", "icon": "mdi:thermometer-high"},
        {"entity": entities.get("running_status", "sensor.REPLACE_ME"),
         "name": "Running Status", "icon": "mdi:information-outline"},
    ]

    # Add firmware if available
    if entities.get("firmware_version"):
        system_entities.append({
            "entity": entities.get("firmware_version", "sensor.REPLACE_ME"),
            "name": "Firmware", "icon": "mdi:chip",
        })
    if entities.get("hardware_version"):
        system_entities.append({
            "entity": entities.get("hardware_version", "sensor.REPLACE_ME"),
            "name": "Hardware", "icon": "mdi:circuit-board",
        })

    # Add alarm entities if present
    for alarm_key in ("battery_alarm", "battery_fault", "time_error"):
        if entities.get(alarm_key):
            system_entities.append({
                "entity": entities[alarm_key],
                "name": alarm_key.replace("_", " ").title(),
                "icon": "mdi:alert-circle",
            })

    cards.append({
        "type": "entities",
        "title": "System Monitoring",
        "entities": system_entities,
    })

    # Air quality markdown
    if air_cfg.get("enabled", False):
        pm25 = air_cfg.get("pm25_entity", "sensor.air_pm25")
        pm10 = air_cfg.get("pm10_entity", "sensor.air_pm10")
        pm1 = air_cfg.get("pm1_entity", "sensor.air_pm1")
        air_md = (
            f"## Air Quality\n"
            f"| Metric | Value |\n"
            f"|--------|-------|\n"
            f"| PM1.0 | {{{{ states('{pm1}') }}}} ug/m3 |\n"
            f"| PM2.5 | {{{{ states('{pm25}') }}}} ug/m3 |\n"
            f"| PM10 | {{{{ states('{pm10}') }}}} ug/m3 |"
        )
        if indoor_cfg.get("enabled", False):
            co2 = indoor_cfg.get("co2_entity", "sensor.indoor_co2")
            air_md += f"\n| CO2 | {{{{ states('{co2}') }}}} ppm |"

        cards.append({
            "type": "markdown",
            "title": "Air Quality",
            "content": air_md,
        })
    else:
        cards.append({
            "type": "markdown",
            "content": "*Air quality monitoring not enabled.*",
        })

    return {
        "title": "Monitoring",
        "path": "monitoring",
        "icon": "mdi:chart-line",
        "type": "sections",
        "max_columns": 2,
        "sections": [
            {"type": "grid", "cards": cards},
        ],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  PM Solar Dashboard Generator")
    print("=" * 60)
    print()

    config = load_config()
    raw_entities = load_device_mapping(config)
    entities = resolve_entities(raw_entities, config)
    dashboard = build_dashboard(config, entities)

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"[5/5] Writing dashboard to {OUTPUT_PATH} ...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        yaml.dump(
            dashboard,
            fh,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

    view_count = len(dashboard.get("views", []))
    entity_count = len(entities)
    print()
    print(f"  Done!  {view_count} view(s), {entity_count} entities resolved.")
    print(f"  Output: {OUTPUT_PATH}")
    print()
    print("  Copy the contents of output/dashboard.yaml into your")
    print("  Home Assistant dashboard YAML editor.")
    print("=" * 60)


if __name__ == "__main__":
    main()
