"""Climate platform for the Thermostat Valve Controller integration."""

import asyncio
import logging
import math
from datetime import timedelta, datetime

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
    PRESET_NONE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature,
    EVENT_HOMEASSISTANT_START,
    ATTR_TEMPERATURE,
)
from homeassistant.core import (
    HomeAssistant,
    callback,
    State,
    Event,
    EventStateChangedData,
    CoreState,
)
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.device import async_device_info_to_link_from_entity
from homeassistant.helpers.event import (
    async_track_state_change_event,
)
from homeassistant.exceptions import ConditionError
from homeassistant.helpers import condition
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CONF_MAX_TEMP,
    CONF_MIN_TEMP,
    CONF_POSITION_MAPPING,
    CONF_PRECISION,
    CONF_PRESETS,
    CONF_TARGET_TEMP_STEP,
    CONF_TEMPERATURE_SENSOR_ENTITY_ID,
    CONF_VALVE_ENTITY_ID,
    CONF_ADDITIONAL_VALVE_ENTITY_IDS,
    CONF_MIN_CYCLE_DURATION,
    CONF_VALVE_EMERGENCY_POSITION,
    CONF_MIN_TEMP_CHANGE_STEP,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Initialize test config entry."""
    registry = er.async_get(hass)

    name: str = config_entry.title
    unique_id: str = config_entry.entry_id
    valve_entity_id: str = er.async_validate_entity_id(
        registry, config_entry.options[CONF_VALVE_ENTITY_ID]
    )

    # Handle additional valve entities
    additional_valve_entity_ids: list[str] = []
    if CONF_ADDITIONAL_VALVE_ENTITY_IDS in config_entry.options:
        additional_valve_ids = config_entry.options[CONF_ADDITIONAL_VALVE_ENTITY_IDS]
        if additional_valve_ids:
            # Handle both list and single entity ID formats
            if isinstance(additional_valve_ids, list):
                additional_valve_entity_ids = [
                    er.async_validate_entity_id(registry, entity_id)
                    for entity_id in additional_valve_ids
                ]
            else:
                # Single entity ID provided
                additional_valve_entity_ids = [
                    er.async_validate_entity_id(registry, additional_valve_ids)
                ]

    valve_position_mapping: dict[str, float] = config_entry.options.get(
        CONF_POSITION_MAPPING, {}
    )
    temp_sensor_entity_id: str = er.async_validate_entity_id(
        registry, config_entry.options[CONF_TEMPERATURE_SENSOR_ENTITY_ID]
    )
    min_temp: float | None = config_entry.options.get(CONF_MIN_TEMP)
    max_temp: float | None = config_entry.options.get(CONF_MAX_TEMP)
    precision: float | None = config_entry.options.get(CONF_PRECISION)
    min_cycle_duration: timedelta | None = (
        timedelta(**min_cycle_duration_dict)
        if (
            min_cycle_duration_dict := config_entry.options.get(CONF_MIN_CYCLE_DURATION)
        )
        else None
    )
    valve_emergency_position: float | None = config_entry.options.get(
        CONF_VALVE_EMERGENCY_POSITION
    )
    target_temp_step: float | None = config_entry.options.get(CONF_TARGET_TEMP_STEP)
    min_temp_change_step: float = config_entry.options.get(CONF_MIN_TEMP_CHANGE_STEP, 0)
    unit = hass.config.units.temperature_unit
    presets: dict[str, float] = {
        key: config_entry.options[value]
        for key, value in CONF_PRESETS.items()
        if value in config_entry.options
    }

    # TODO add more and better validation

    # Validate valve position mapping
    if len(valve_position_mapping) == 0:
        _LOGGER.error(
            "Valve position mapping is empty! Please add your valve mappings."
        )
        return

    # convert mapping keys to float and values to float
    converted_valve_position_mapping = {
        float(k): float(v) for k, v in valve_position_mapping.items()
    }

    async_add_entities(
        [
            ValveControllerClimate(
                hass=hass,
                name=name,
                unique_id=unique_id,
                valve_entity_id=valve_entity_id,
                additional_valve_entity_ids=additional_valve_entity_ids,
                valve_position_mapping=converted_valve_position_mapping,
                temp_sensor_entity_id=temp_sensor_entity_id,
                min_temp=min_temp,
                max_temp=max_temp,
                precision=precision,
                min_cycle_duration=min_cycle_duration,
                valve_emergency_position=valve_emergency_position,
                target_temp_step=target_temp_step,
                min_temp_change_step=min_temp_change_step,
                unit=unit,
                presets=presets,
            )
        ]
    )


class ValveControllerClimate(ClimateEntity, RestoreEntity):
    """Representation of a Thermostat Valve Controller."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        unique_id: str,
        valve_entity_id: str,
        additional_valve_entity_ids: list[str],
        valve_position_mapping: dict[float, float],
        temp_sensor_entity_id: str,
        min_temp: float | None,
        max_temp: float | None,
        precision: float | None,
        min_cycle_duration: timedelta | None,
        valve_emergency_position: float | None,
        target_temp_step: float | None,
        min_temp_change_step: float,
        unit: UnitOfTemperature,
        presets: dict[str, float],
    ) -> None:
        """Initialize the climate entity."""
        # super().__init__()

        # Entity Attributes
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        if len(presets):
            self._attr_supported_features |= ClimateEntityFeature.PRESET_MODE
            self._attr_preset_modes = [PRESET_NONE, *presets.keys()]
        else:
            self._attr_preset_modes = [PRESET_NONE]

        self._attr_preset_mode = PRESET_NONE

        self._attr_device_info = async_device_info_to_link_from_entity(
            hass,
            valve_entity_id,
        )
        self._attr_name = name
        self._attr_unique_id = unique_id

        if min_temp is not None:
            self._attr_min_temp = min_temp

        if max_temp is not None:
            self._attr_max_temp = max_temp

        if precision is not None:
            self._attr_precision = precision

        self._attr_target_temperature_step = (
            target_temp_step if target_temp_step is not None else precision
        )
        self._attr_temperature_unit = unit

        # Other values
        self._valve_entity_id = valve_entity_id
        self._additional_valve_entity_ids = additional_valve_entity_ids
        self._all_valve_entity_ids = [valve_entity_id] + additional_valve_entity_ids
        self._temp_sensor_entity_id = temp_sensor_entity_id
        self._min_cycle_duration = min_cycle_duration
        self._valve_emergency_position = valve_emergency_position
        self._target_temp = next(iter(presets.values()), None)
        self._saved_target_temp = next(iter(presets.values()), None)
        self._current_temp: float | None = None
        self._hvac_mode: HVACMode | None = None
        self._pending_update_task: asyncio.Task | None = None
        self._min_temp_change_step = min_temp_change_step
        self._last_valve_update_temp: float | None = None

        self._valve_position_mapping = valve_position_mapping
        self._sorted_valve_mapping_keys = sorted(self._valve_position_mapping.keys())
        self._min_valve_position = min(self._valve_position_mapping.values())
        self._max_valve_position = max(self._valve_position_mapping.values())

        self._presets = presets
        self._presets_inv = {v: k for k, v in presets.items()}

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        # Add listener
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._temp_sensor_entity_id], self._async_sensor_changed
            )
        )
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, self._all_valve_entity_ids, self._async_valve_changed
            )
        )

        @callback
        def _async_startup(_: Event | None = None) -> None:
            """Init on startup."""
            sensor_state = self.hass.states.get(self._temp_sensor_entity_id)
            if sensor_state and sensor_state.state not in (
                STATE_UNAVAILABLE,
                STATE_UNKNOWN,
            ):
                self._async_update_temp(sensor_state)

            valve_state = self.hass.states.get(self._valve_entity_id)
            if valve_state and valve_state.state not in (
                STATE_UNAVAILABLE,
                STATE_UNKNOWN,
            ):
                self.hass.async_create_task(
                    self._check_valve_initial_state(), eager_start=True
                )

        if self.hass.state is CoreState.running:
            _async_startup()
        else:
            self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, _async_startup)

        # Restore previous state if available
        if (last_state := await self.async_get_last_state()) is not None:
            # Restore target temperature
            if last_state.attributes.get(ATTR_TEMPERATURE) is not None:
                self._target_temp = float(last_state.attributes[ATTR_TEMPERATURE])

            # Restore HVAC mode
            if last_state.state is not None and last_state.state != STATE_UNKNOWN:
                if last_state.state in [mode.value for mode in HVACMode]:
                    self._hvac_mode = HVACMode(last_state.state)
                else:
                    self._hvac_mode = HVACMode.OFF

            # Restore preset mode
            if (preset_mode := last_state.attributes.get("preset_mode")) is not None:
                self._attr_preset_mode = preset_mode
                if preset_mode != PRESET_NONE and preset_mode in self._presets:
                    self._target_temp = self._presets[preset_mode]
            else:
                self._attr_preset_mode = None

        # Set default target temperature if still None
        if self._target_temp is None:
            self._target_temp = self.min_temp

        # Set default hvac mode to off if still None
        if self._hvac_mode not in self.hvac_modes:
            self._hvac_mode = HVACMode.OFF

        self.async_write_ha_state()

    async def _async_sensor_changed(self, event: Event[EventStateChangedData]) -> None:
        """Handle temperature changes."""
        new_state = event.data["new_state"]
        if new_state is None or new_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return

        self._async_update_temp(new_state)
        await self._async_control_heating()
        self.async_write_ha_state()

    @callback
    def _async_valve_changed(self, event: Event[EventStateChangedData]) -> None:
        """Handle valve position state changes."""
        new_state = event.data["new_state"]
        # old_state = event.data["old_state"]
        if new_state is None:
            return
        # if old_state is None:
        #     self.hass.async_create_task(
        #         self._check_switch_initial_state(), eager_start=True
        #     )
        self.async_write_ha_state()

    async def _check_valve_initial_state(self) -> None:
        """Sets the valve to the correct position on startup."""
        await self._async_control_heating(force=True)

    @property
    def available(self) -> bool:
        """Return climate group availability."""
        return self.hass.states.get(self._valve_entity_id) is not None

    # HVAC Mode
    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return the current hvac mode."""
        return self._hvac_mode

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode not in self.hvac_modes:
            raise ValueError(
                f"Got unsupported hvac_mode {hvac_mode}. Must be one of {self.hvac_modes}"
            )

        self._hvac_mode = hvac_mode
        await self._async_control_heating(force=True)

        # Update the state of the entity
        self.async_write_ha_state()

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current hvac operation."""
        if self._is_device_active:
            return HVACAction.HEATING

        if self._hvac_mode == HVACMode.OFF:
            return HVACAction.OFF

        return HVACAction.IDLE

    @property
    def _is_device_active(self) -> bool | None:
        """If any valve is currently active/open."""
        # Check all valves - if ANY is active, consider the device active
        any_valve_available = False

        for valve_entity_id in self._all_valve_entity_ids:
            valve_state = self.hass.states.get(valve_entity_id)
            if not valve_state:
                continue

            any_valve_available = True

            try:
                if float(valve_state.state) > float(self._min_valve_position):
                    return True
            except (ValueError, TypeError):
                _LOGGER.error(
                    "Failed to parse valve state for %s: %s",
                    valve_entity_id,
                    valve_state.state,
                )
                continue

        # If no valve was available, return None
        if not any_valve_available:
            return None

        # All valves checked and none are active
        return False

    # Current temperature
    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._current_temp

    @callback
    def _async_update_temp(self, state: State) -> None:
        """Update thermostat with latest state from sensor."""
        try:
            current_temp = float(state.state)
            if not math.isfinite(current_temp):
                raise ValueError(f"Sensor has illegal state {state.state}")
            self._current_temp = current_temp
        except ValueError as e:
            self._current_temp = None
            _LOGGER.error("Unable to update from sensor: %s", e)

    # Presets
    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        if preset_mode not in (self.preset_modes or []):
            raise ValueError(
                f"Got unsupported preset_mode {preset_mode}. Must be one of"
                f" {self.preset_modes}"
            )
        if preset_mode == self._attr_preset_mode:
            # I don't think we need to call async_write_ha_state if we didn't change the state
            return
        if preset_mode == PRESET_NONE:
            self._attr_preset_mode = PRESET_NONE
            self._target_temp = self._saved_target_temp
            await self._async_control_heating(force=True)
        else:
            if self._attr_preset_mode == PRESET_NONE:
                self._saved_target_temp = self._target_temp
            self._attr_preset_mode = preset_mode
            self._target_temp = self._presets[preset_mode]
            await self._async_control_heating(force=True)

        self.async_write_ha_state()

    # Target temperature
    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self._target_temp

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        self._attr_preset_mode = self._presets_inv.get(temperature, PRESET_NONE)
        self._target_temp = temperature
        await self._async_control_heating(force=True)
        self.async_write_ha_state()

    # Valve control
    async def _async_control_heating(self, force: bool = False) -> None:
        """Control the valve position."""
        current_valve_state = self.hass.states.get(self._valve_entity_id)

        if current_valve_state is None:
            _LOGGER.error(
                "Failed to update the valve position because entity %s is not available",
                self._valve_entity_id,
            )
            return

        try:
            current_valve_position = float(current_valve_state.state)
        except (ValueError, TypeError):
            _LOGGER.error(
                "Failed to update the valve position because parsing of the current state has failed: %s",
                current_valve_state.state,
            )
            return

        # Check if we are in the min cycle duration, skip updating valve if so.
        if not force and self._min_cycle_duration:
            try:
                # TODO ignore unavailable/unkown states
                # Check if the valve has been in its current state for the minimum duration
                long_enough = condition.state(
                    hass=self.hass,
                    entity=self._valve_entity_id,
                    req_state=current_valve_state.state,  # Use the actual state string
                    for_period=self._min_cycle_duration,
                )

            except ConditionError:
                long_enough = False

            if not long_enough:
                _LOGGER.debug(
                    "Valve update blocked - minimum cycle duration not met, scheduling deferred update"
                )
                if self._pending_update_task and not self._pending_update_task.done():
                    _LOGGER.debug(
                        "A deferred update is already scheduled, not scheduling another"
                    )
                else:
                    self._schedule_deferred_update()
                return

        # Check if temperature changed enough to allow valve position update
        if (
            not force
            and self._min_temp_change_step > 0
            and self._current_temp is not None
            and self._last_valve_update_temp is not None
        ):
            temp_difference = abs(self._current_temp - self._last_valve_update_temp)

            if temp_difference < self._min_temp_change_step:
                _LOGGER.debug(
                    "Temperature change (%.2f°C) is below threshold (%.2f°C), skipping valve update",
                    temp_difference,
                    self._min_temp_change_step,
                )
                return

        # Cancel any pending deferred update since we're updating now
        if self._pending_update_task and not self._pending_update_task.done():
            self._pending_update_task.cancel()
            _LOGGER.debug(
                "Cancelled pending deferred update - executing immediate update"
            )

        if self._hvac_mode == HVACMode.OFF:
            # Close valve if the hvac mode is off.
            # To allow manual changes to the valve position while the thermostat is turned off
            #   (and not keep resetting it on temp changes), we only close it when force is True, which is the case when changing the hvac mode
            if force:
                await self._set_valve_position(self._min_valve_position)

            # ...and do not perform further actions
            return

        def calculate_valve_position(
            current_temp: float | None, target_temp: float | None
        ) -> float:
            """Calculate the valve position based on the current and target temperature."""
            if not current_temp or not target_temp:
                _LOGGER.warning(
                    "Current or target temperature is None, setting valve %s to emergency position",
                    self._valve_entity_id,
                )
                return self._valve_emergency_position or self._min_valve_position

            temp_difference = round(target_temp - current_temp, 1)

            # Handle cases outside the defined range
            if temp_difference <= self._sorted_valve_mapping_keys[0]:
                # Return minimum value
                return self._min_valve_position

            if temp_difference >= self._sorted_valve_mapping_keys[-1]:
                # Return maximum value
                return self._valve_position_mapping[self._sorted_valve_mapping_keys[-1]]

            # Find the appropriate valve position
            for i, mapping_diff in enumerate(self._sorted_valve_mapping_keys):
                if temp_difference <= mapping_diff:
                    # Return the position from the previous threshold
                    return self._valve_position_mapping[
                        self._sorted_valve_mapping_keys[i - 1]
                    ]

            # Temp diff is higher than the highest threshold, fall back to max
            return self._max_valve_position

        # Get new valve position
        new_valve_position = calculate_valve_position(
            current_temp=self._current_temp, target_temp=self._target_temp
        )
        if new_valve_position == current_valve_position:
            # No need to update the valve position if it is already the same
            # TODO maybe add an option to force update it no matter the current state
            #       (in case the thermostat did not report a state update and the actual value is different).
            #       Need to check if that would even work or if HA would ignore it if we set the same state again
            #       (maybe this check here isn't even neccessary in this case).
            return

        # Set the new valve position and set the last update temp
        await self._set_valve_position(new_valve_position)
        self._last_valve_update_temp = self._current_temp

    async def _set_valve_position(self, position: float) -> None:
        """Set the valve position using number.set_value service."""
        _LOGGER.debug("Setting valve position to %s", position)

        # Set position for all valves (main + additional)
        for valve_entity_id in self._all_valve_entity_ids:
            domain = valve_entity_id.split(".", 1)[0]

            await self.hass.services.async_call(
                domain,
                "set_value",
                {"entity_id": valve_entity_id, "value": position},
                blocking=True,
            )

    def _schedule_deferred_update(self) -> None:
        """Schedule a deferred valve update after the minimum cycle duration."""
        # Calculate delay - get time since valve last changed
        if self._min_cycle_duration:
            valve_state = self.hass.states.get(self._valve_entity_id)

            if valve_state and valve_state.last_changed:
                # Calculate time elapsed since valve last changed
                time_elapsed = (
                    datetime.now(valve_state.last_changed.tzinfo)
                    - valve_state.last_changed
                )
                time_remaining = self._min_cycle_duration - time_elapsed

                # If there's still time remaining, schedule for that time
                if time_remaining.total_seconds() > 0:
                    delay = time_remaining.total_seconds()
                else:
                    # If time has already passed, schedule immediately
                    delay = 0.1
            else:
                # Fallback to full cycle duration if we can't determine last change time
                delay = self._min_cycle_duration.total_seconds()

            self._pending_update_task = self.hass.async_create_task(
                self._execute_deferred_update(delay)
            )
            _LOGGER.debug("Scheduled deferred valve update in %s seconds", delay)

    async def _execute_deferred_update(self, delay: float) -> None:
        """Execute the deferred valve update after waiting for the delay."""
        try:
            await asyncio.sleep(delay)
            _LOGGER.debug("Executing deferred valve update")
            await self._async_control_heating()
        except asyncio.CancelledError:
            _LOGGER.debug("Deferred valve update was cancelled")
        finally:
            self._pending_update_task = None

    async def async_will_remove_from_hass(self) -> None:
        """Cancel any pending deferred updates when entity is removed."""
        if self._pending_update_task and not self._pending_update_task.done():
            self._pending_update_task.cancel()
        await super().async_will_remove_from_hass()
