"""Config flow for the Thermostat Valve Controller integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol

from homeassistant.components.input_number import DOMAIN as INPUT_NUMBER_DOMAIN
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
)

from homeassistant.const import CONF_NAME, DEGREE
from homeassistant.components.climate.const import DEFAULT_MIN_TEMP, DEFAULT_MAX_TEMP


from .const import (
    CONF_MAX_TEMP,
    CONF_MIN_TEMP,
    CONF_PRECISION,
    CONF_PRESETS,
    CONF_TARGET_TEMP_STEP,
    CONF_TEMPERATURE_SENSOR_ENTITY_ID,
    CONF_VALVE_ENTITY_ID,
    CONF_VALVE_MAX_POSITION,
    CONF_VALVE_MIN_POSITION,
    CONF_MIN_CYCLE_DURATION,
    DOMAIN,
)

VALVE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TEMPERATURE_SENSOR_ENTITY_ID): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=[SENSOR_DOMAIN, NUMBER_DOMAIN, INPUT_NUMBER_DOMAIN]
            )
        ),
        vol.Optional(CONF_PRECISION, default=0.5): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX, step=0.01
            )
        ),
        vol.Required(CONF_VALVE_ENTITY_ID): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=[NUMBER_DOMAIN, INPUT_NUMBER_DOMAIN])
        ),
        vol.Optional(CONF_MIN_CYCLE_DURATION): selector.DurationSelector(
            selector.DurationSelectorConfig(allow_negative=False)
        ),
        vol.Required(CONF_VALVE_MIN_POSITION, default=0): int,
        vol.Required(CONF_VALVE_MAX_POSITION, default=100): int,
    }
)

THERMOSTAT_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_MIN_TEMP, default=DEFAULT_MIN_TEMP): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX, unit_of_measurement=DEGREE, step=0.1
            )
        ),
        vol.Optional(CONF_MAX_TEMP, default=DEFAULT_MAX_TEMP): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX, unit_of_measurement=DEGREE, step=0.1
            )
        ),
        vol.Optional(CONF_TARGET_TEMP_STEP, default=0.1): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX, unit_of_measurement=DEGREE, step=0.01
            )
        ),
    }
)

PRESETS_SCHEMA = vol.Schema(
    {
        vol.Optional(v): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX, unit_of_measurement=DEGREE, step=0.1
            )
        )
        for v in CONF_PRESETS.values()
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): selector.TextSelector(),
    }
).extend(VALVE_SCHEMA.schema)

CONFIG_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "user": SchemaFlowFormStep(CONFIG_SCHEMA, next_step="thermostat"),
    "thermostat": SchemaFlowFormStep(THERMOSTAT_SCHEMA, next_step="presets"),
    "presets": SchemaFlowFormStep(PRESETS_SCHEMA),
}

OPTIONS_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "init": SchemaFlowMenuStep(
        options=["valve", "thermostat", "presets"]
    ),
    "valve": SchemaFlowFormStep(VALVE_SCHEMA),
    "thermostat": SchemaFlowFormStep(THERMOSTAT_SCHEMA),
    "presets": SchemaFlowFormStep(PRESETS_SCHEMA),
}


class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow for Thermostat Valve Controller."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""
        return cast(str, options[CONF_NAME]) if CONF_NAME in options else ""
