"""Config flow for the Thermostat Valve Controller integration."""

from __future__ import annotations

from typing import Any
import copy

import voluptuous as vol

from homeassistant.components.input_number import DOMAIN as INPUT_NUMBER_DOMAIN
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.helpers import selector
from homeassistant.config_entries import ConfigFlow, ConfigEntry, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from homeassistant.const import CONF_NAME, DEGREE
from homeassistant.components.climate.const import DEFAULT_MIN_TEMP, DEFAULT_MAX_TEMP

from homeassistant.helpers.selector import (
    ObjectSelector,
    ObjectSelectorConfig,
)

from .const import (
    CONF_MAX_TEMP,
    CONF_MIN_TEMP,
    CONF_POSITION_MAPPING,
    CONF_PRECISION,
    CONF_PRESETS,
    CONF_TARGET_TEMP_STEP,
    CONF_TEMPERATURE_SENSOR_ENTITY_ID,
    CONF_THERMOSTATS,
    CONF_THERMOSTAT_NAME,
    CONF_VALVE_ENTITY_ID,
    CONF_VALVE_EMERGENCY_POSITION,
    CONF_MIN_CYCLE_DURATION,
    DOMAIN,
)

THERMOSTAT_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_THERMOSTAT_NAME): selector.TextSelector(),
        vol.Required(CONF_TEMPERATURE_SENSOR_ENTITY_ID): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=[SENSOR_DOMAIN, NUMBER_DOMAIN, INPUT_NUMBER_DOMAIN]
            )
        ),
        vol.Optional(CONF_PRECISION, default=0.1): selector.NumberSelector(
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
        vol.Optional(CONF_VALVE_EMERGENCY_POSITION, default=25): vol.Coerce(float),
    }
)

VALVE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TEMPERATURE_SENSOR_ENTITY_ID): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=[SENSOR_DOMAIN, NUMBER_DOMAIN, INPUT_NUMBER_DOMAIN]
            )
        ),
        vol.Optional(CONF_PRECISION, default=0.1): selector.NumberSelector(
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
        vol.Optional(CONF_VALVE_EMERGENCY_POSITION, default=25): vol.Coerce(float),
    }
)

VALVE_POSITION_SCHEMA = vol.Schema(
    {
        vol.Optional(
            CONF_POSITION_MAPPING,
            default={
                "-0.2": 0,
                "-0.1": 15,
                "0.0": 25,
                "0.1": 35,
                "0.2": 50,
                "0.4": 80,
                "0.7": 90,
                "1.0": 100,
                "1.3": 120,
                "1.7": 150,
                "2.0": 180,
            },
        ): ObjectSelector(ObjectSelectorConfig()),
    }
)

THERMOSTAT_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_MIN_TEMP, default=DEFAULT_MIN_TEMP): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement=DEGREE,
                step=0.1,
            )
        ),
        vol.Optional(CONF_MAX_TEMP, default=DEFAULT_MAX_TEMP): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement=DEGREE,
                step=0.1,
            )
        ),
        vol.Optional(CONF_TARGET_TEMP_STEP, default=0.5): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement=DEGREE,
                step=0.01,
            )
        ),
    }
)

PRESETS_SCHEMA = vol.Schema(
    {
        vol.Optional(v): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement=DEGREE,
                step=0.1,
            )
        )
        for v in CONF_PRESETS.values()
    }
)

class ThermostatValveControllerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Thermostat Valve Controller."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._name: str | None = None
        self._thermostats: list[dict[str, Any]] = []
        self._current_thermostat: dict[str, Any] = {}
        self._current_thermostat_index: int | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self._name = user_input[CONF_NAME]
            return await self.async_step_manage_thermostats()

        schema = vol.Schema({
            vol.Required(CONF_NAME): selector.TextSelector(),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_manage_thermostats(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage thermostats list."""
        if user_input is not None:
            action = user_input.get("action")
            
            if action == "add":
                self._current_thermostat = {}
                self._current_thermostat_index = None
                return await self.async_step_thermostat_config()
            elif action == "edit" and user_input.get("thermostat_index") is not None:
                index = user_input["thermostat_index"]
                if 0 <= index < len(self._thermostats):
                    self._current_thermostat = copy.deepcopy(self._thermostats[index])
                    self._current_thermostat_index = index
                    return await self.async_step_thermostat_config()
            elif action == "delete" and user_input.get("thermostat_index") is not None:
                index = user_input["thermostat_index"]
                if 0 <= index < len(self._thermostats):
                    self._thermostats.pop(index)
                return await self.async_step_manage_thermostats()
            elif action == "finish":
                if len(self._thermostats) == 0:
                    return self.async_show_form(
                        step_id="manage_thermostats",
                        data_schema=self._get_manage_thermostats_schema(),
                        errors={"base": "no_thermostats"},
                    )
                
                # Create the config entry
                return self.async_create_entry(
                    title=self._name,
                    data={
                        CONF_NAME: self._name,
                        CONF_THERMOSTATS: self._thermostats,
                    },
                )

        return self.async_show_form(
            step_id="manage_thermostats",
            data_schema=self._get_manage_thermostats_schema(),
        )

    def _get_manage_thermostats_schema(self) -> vol.Schema:
        """Get schema for managing thermostats."""
        actions = ["add", "finish"]
        if self._thermostats:
            actions.insert(-1, "edit")
            actions.insert(-1, "delete")

        schema_dict = {
            vol.Required("action"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": "add", "label": "Add thermostat"},
                        {"value": "edit", "label": "Edit thermostat"},
                        {"value": "delete", "label": "Delete thermostat"},
                        {"value": "finish", "label": "Finish configuration"},
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }

        if self._thermostats:
            thermostat_options = [
                {"value": i, "label": f"{i + 1}. {thermostat.get(CONF_THERMOSTAT_NAME, 'Unnamed')}"}
                for i, thermostat in enumerate(self._thermostats)
            ]
            schema_dict[vol.Optional("thermostat_index")] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=thermostat_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )

        return vol.Schema(schema_dict)

    async def async_step_thermostat_config(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure a single thermostat."""
        if user_input is not None:
            self._current_thermostat.update(user_input)
            return await self.async_step_valve_position()

        return self.async_show_form(
            step_id="thermostat_config",
            data_schema=THERMOSTAT_CONFIG_SCHEMA,
        )

    async def async_step_valve_position(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure valve position mapping."""
        if user_input is not None:
            self._current_thermostat.update(user_input)
            return await self.async_step_thermostat_settings()

        return self.async_show_form(
            step_id="valve_position",
            data_schema=VALVE_POSITION_SCHEMA,
        )

    async def async_step_thermostat_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure thermostat settings."""
        if user_input is not None:
            self._current_thermostat.update(user_input)
            return await self.async_step_presets()

        return self.async_show_form(
            step_id="thermostat_settings",
            data_schema=THERMOSTAT_SCHEMA,
        )

    async def async_step_presets(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure presets."""
        if user_input is not None:
            self._current_thermostat.update(user_input)
            
            # Save the thermostat
            if self._current_thermostat_index is not None:
                # Edit existing
                self._thermostats[self._current_thermostat_index] = self._current_thermostat
            else:
                # Add new
                self._thermostats.append(self._current_thermostat)
            
            return await self.async_step_manage_thermostats()

        return self.async_show_form(
            step_id="presets",
            data_schema=PRESETS_SCHEMA,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return ThermostatValveControllerOptionsFlow(config_entry)


class ThermostatValveControllerOptionsFlow(OptionsFlow):
    """Handle options flow for Thermostat Valve Controller."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._thermostats: list[dict[str, Any]] = config_entry.data.get(CONF_THERMOSTATS, [])
        self._current_thermostat: dict[str, Any] = {}
        self._current_thermostat_index: int | None = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        return await self.async_step_manage_thermostats()

    async def async_step_manage_thermostats(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage thermostats list."""
        if user_input is not None:
            action = user_input.get("action")
            
            if action == "add":
                self._current_thermostat = {}
                self._current_thermostat_index = None
                return await self.async_step_thermostat_config()
            elif action == "edit" and user_input.get("thermostat_index") is not None:
                index = user_input["thermostat_index"]
                if 0 <= index < len(self._thermostats):
                    self._current_thermostat = copy.deepcopy(self._thermostats[index])
                    self._current_thermostat_index = index
                    return await self.async_step_thermostat_config()
            elif action == "delete" and user_input.get("thermostat_index") is not None:
                index = user_input["thermostat_index"]
                if 0 <= index < len(self._thermostats):
                    self._thermostats.pop(index)
                return await self.async_step_manage_thermostats()
            elif action == "finish":
                if len(self._thermostats) == 0:
                    return self.async_show_form(
                        step_id="manage_thermostats",
                        data_schema=self._get_manage_thermostats_schema(),
                        errors={"base": "no_thermostats"},
                    )
                
                # Update the config entry
                return self.async_create_entry(
                    title="",
                    data={CONF_THERMOSTATS: self._thermostats},
                )

        return self.async_show_form(
            step_id="manage_thermostats",
            data_schema=self._get_manage_thermostats_schema(),
        )

    def _get_manage_thermostats_schema(self) -> vol.Schema:
        """Get schema for managing thermostats."""
        actions = ["add", "finish"]
        if self._thermostats:
            actions.insert(-1, "edit")
            actions.insert(-1, "delete")

        schema_dict = {
            vol.Required("action"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": "add", "label": "Add thermostat"},
                        {"value": "edit", "label": "Edit thermostat"},
                        {"value": "delete", "label": "Delete thermostat"},
                        {"value": "finish", "label": "Finish configuration"},
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }

        if self._thermostats:
            thermostat_options = [
                {"value": i, "label": f"{i + 1}. {thermostat.get(CONF_THERMOSTAT_NAME, 'Unnamed')}"}
                for i, thermostat in enumerate(self._thermostats)
            ]
            schema_dict[vol.Optional("thermostat_index")] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=thermostat_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )

        return vol.Schema(schema_dict)

    async def async_step_thermostat_config(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure a single thermostat."""
        if user_input is not None:
            self._current_thermostat.update(user_input)
            return await self.async_step_valve_position()

        return self.async_show_form(
            step_id="thermostat_config",
            data_schema=THERMOSTAT_CONFIG_SCHEMA,
        )

    async def async_step_valve_position(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure valve position mapping."""
        if user_input is not None:
            self._current_thermostat.update(user_input)
            return await self.async_step_thermostat_settings()

        return self.async_show_form(
            step_id="valve_position",
            data_schema=VALVE_POSITION_SCHEMA,
        )

    async def async_step_thermostat_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure thermostat settings."""
        if user_input is not None:
            self._current_thermostat.update(user_input)
            return await self.async_step_presets()

        return self.async_show_form(
            step_id="thermostat_settings",
            data_schema=THERMOSTAT_SCHEMA,
        )

    async def async_step_presets(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure presets."""
        if user_input is not None:
            self._current_thermostat.update(user_input)
            
            # Save the thermostat
            if self._current_thermostat_index is not None:
                # Edit existing
                self._thermostats[self._current_thermostat_index] = self._current_thermostat
            else:
                # Add new
                self._thermostats.append(self._current_thermostat)
            
            return await self.async_step_manage_thermostats()

        return self.async_show_form(
            step_id="presets",
            data_schema=PRESETS_SCHEMA,
        )
