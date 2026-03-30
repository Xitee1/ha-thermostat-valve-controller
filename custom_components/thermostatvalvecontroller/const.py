"""Constants for the Thermostat Valve Controller integration."""

from homeassistant.components.climate.const import (
    PRESET_ACTIVITY,
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_HOME,
    PRESET_SLEEP,
)

DOMAIN = "thermostatvalvecontroller"

# Valve
CONF_TEMPERATURE_SENSOR_ENTITY_ID = "temperature_sensor_entity_id"
CONF_PRECISION = "precision"
CONF_VALVE_ENTITY_ID = "valve_entity_id"
CONF_ADDITIONAL_VALVE_ENTITY_IDS = "additional_valve_entity_ids"
CONF_MIN_CYCLE_DURATION = "min_cycle_duration"
CONF_VALVE_EMERGENCY_POSITION = "valve_emergency_position"
CONF_MIN_TEMP_CHANGE_STEP = "min_temp_change_step"

# Valve Positions
CONF_POSITION_MAPPING = "position_mapping"

# Thermostat
CONF_MIN_TEMP = "min_temp"
CONF_MAX_TEMP = "max_temp"
CONF_TARGET_TEMP_STEP = "target_temp_step"

# Presets
CONF_PRESETS = {
    p: f"{p}_temp"
    for p in (
        PRESET_AWAY,
        PRESET_COMFORT,
        PRESET_ECO,
        PRESET_HOME,
        PRESET_SLEEP,
        PRESET_ACTIVITY,
    )
}
