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

from .const import (
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

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("name"): selector.TextSelector(),
    }
).extend(VALVE_SCHEMA.schema)

CONFIG_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "user": SchemaFlowFormStep(CONFIG_SCHEMA)
}

OPTIONS_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "init": SchemaFlowFormStep(VALVE_SCHEMA)
}


class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow for Thermostat Valve Controller."""

    config_flow = CONFIG_FLOW
    # TODO remove the options_flow if the integration does not have an options flow
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""
        return cast(str, options["name"]) if "name" in options else ""
