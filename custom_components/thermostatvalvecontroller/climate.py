"""Climate platform for the Thermostat Valve Controller integration."""

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_TEMPERATURE_SENSOR_ENTITY_ID, CONF_VALVE_ENTITY_ID


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Initialize test config entry."""
    registry = er.async_get(hass)
    # Validate + resolve entity registry id to entity_id
    entity_id = er.async_validate_entity_id(
        registry, config_entry.options[CONF_VALVE_ENTITY_ID]
    )
    # TODO Optionally validate config entry options before creating entity
    name = config_entry.title
    unique_id = config_entry.entry_id

    async_add_entities([ValveControllerClimate(unique_id, name, entity_id)])


class ValveControllerClimate(ClimateEntity):
    """Representation of a Thermostat Valve Controller."""

    _attr_has_entity_name = True
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_hvac_action = HVACAction.OFF
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_target_temperature_step = 0.5
    _attr_target_temperature = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 0
    _attr_max_temp = 30

    def __init__(self, unique_id: str, name: str, wrapped_entity_id: str) -> None:
        """Initialize the climate entity."""
        super().__init__()
        self._wrapped_entity_id = wrapped_entity_id
        self._attr_name = name
        self._attr_unique_id = unique_id

        self._hvac_mode = HVACMode.OFF
        self._current_temperature: float | None = None
        self._current_valve_position: int | None = None
        # self._attr_device_info = ...  # For automatic device registration
        # self._attr_unique_id = ...

    @property
    def available(self) -> bool:
        """Return climate group availability."""
        return (self._current_temperature is not None) and (
            self._current_valve_position is not None
        )

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._current_temperature

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current running hvac operation if supported."""
        if self._hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        if (
            self._current_valve_position is not None
            and self._current_valve_position > 0
        ):
            return HVACAction.HEATING
        return HVACAction.IDLE

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.HEAT:
            self._attr_hvac_action = HVACAction.HEATING
        elif hvac_mode == HVACMode.OFF:
            self._attr_hvac_action = HVACAction.OFF
        else:
            raise ValueError(f"Unsupported hvac mode: {hvac_mode}")

        # Update the state of the entity
        await self.async_update_ha_state()

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        if "temperature" in kwargs:
            self._attr_target_temperature = kwargs["temperature"]
            # Update the state of the entity
            await self.async_update_ha_state()
        else:
            raise ValueError("Temperature not provided")
