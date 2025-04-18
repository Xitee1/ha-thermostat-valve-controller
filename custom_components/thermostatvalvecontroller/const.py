"""Constants for the Thermostat Valve Controller integration."""

from homeassistant.components.climate import (
    PRESET_ACTIVITY,
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_HOME,
    PRESET_SLEEP,
)

DOMAIN = "thermostatvalvecontroller"

CONF_TEMPERATURE_SENSOR_ENTITY_ID = "temperature_sensor_entity_id"
CONF_VALVE_ENTITY_ID = "valve_entity_id"
CONF_VALVE_MAX_POSITION = "valve_max_position"
CONF_VALVE_MIN_POSITION = "valve_min_position"
CONF_MIN_TEMP = "min_temp"
CONF_MAX_TEMP = "max_temp"
CONF_PRECISION = "precision"
CONF_TARGET_TEMP = "target_temp"
CONF_TARGET_TEMP_STEP = "target_temp_step"
CONF_INITIAL_HVAC_MODE = "initial_hvac_mode"
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
CONF_SENSOR = "target_sensor"
CONF_TARGET_TEMP = "target_temp"
CONF_TARGET_TEMP_STEP = "target_temp_step"
CONF_INITIAL_HVAC_MODE = "initial_hvac_mode"
