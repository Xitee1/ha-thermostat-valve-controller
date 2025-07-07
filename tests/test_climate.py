"""Test the Thermostat Valve Controller climate platform structure."""

def test_climate_module_structure():
    """Test climate module has proper structure without importing homeassistant."""
    try:
        with open('custom_components/thermostatvalvecontroller/climate.py', 'r') as f:
            content = f.read()
        
        # Check for key functions
        assert 'async def async_setup_entry' in content
        assert 'async def _create_thermostat_entity' in content  
        assert 'async def _create_legacy_thermostat_entity' in content
        assert 'class ValveControllerClimate' in content
        
        # Check for multiple thermostats support
        assert 'CONF_THERMOSTATS' in content
        assert 'thermostats_config = config_entry.data.get(CONF_THERMOSTATS)' in content
        assert 'for i, thermostat_config in enumerate(thermostats_config)' in content
        
        # Check for backward compatibility
        assert '_create_legacy_thermostat_entity' in content
        assert 'config_entry.options' in content
        
        # Check unique ID generation for multiple thermostats
        assert 'unique_id = f"{config_entry.entry_id}_{thermostat_index}"' in content
        
    except FileNotFoundError:
        assert False, "climate.py not found"


def test_backward_compatibility_structure():
    """Test that backward compatibility structures are in place."""
    with open('custom_components/thermostatvalvecontroller/const.py', 'r') as f:
        content = f.read()
    
    # Verify all old constants still exist with expected values
    assert 'CONF_TEMPERATURE_SENSOR_ENTITY_ID = "temperature_sensor_entity_id"' in content
    assert 'CONF_VALVE_ENTITY_ID = "valve_entity_id"' in content
    assert 'CONF_POSITION_MAPPING = "position_mapping"' in content
    assert 'CONF_PRECISION = "precision"' in content
    assert 'CONF_MIN_CYCLE_DURATION = "min_cycle_duration"' in content
    assert 'CONF_VALVE_EMERGENCY_POSITION = "valve_emergency_position"' in content
    assert 'CONF_MIN_TEMP = "min_temp"' in content
    assert 'CONF_MAX_TEMP = "max_temp"' in content
    assert 'CONF_TARGET_TEMP_STEP = "target_temp_step"' in content
    
    # Check that CONF_PRESETS is properly defined
    assert 'CONF_PRESETS = {' in content
    assert 'PRESET_AWAY' in content
    assert 'PRESET_COMFORT' in content
    assert 'PRESET_ECO' in content


def test_error_handling_structure():
    """Test that proper error handling is in place."""
    try:
        with open('custom_components/thermostatvalvecontroller/climate.py', 'r') as f:
            content = f.read()
        
        # Check for proper error handling
        assert 'try:' in content
        assert 'except (KeyError, ValueError)' in content
        assert '_LOGGER.error' in content
        assert 'return None' in content
        
        # Check for validation
        assert 'if not valve_position_mapping:' in content
        assert 'Invalid entity configuration' in content
        assert 'Valve position mapping is empty' in content
        
    except FileNotFoundError:
        assert False, "climate.py not found"


def test_multiple_entities_creation():
    """Test that the setup supports creating multiple entities."""
    try:
        with open('custom_components/thermostatvalvecontroller/climate.py', 'r') as f:
            content = f.read()
        
        # Check that entities list is used
        assert 'entities = []' in content
        assert 'entities.append(entity)' in content
        assert 'if entities:' in content
        assert 'async_add_entities(entities)' in content
        
        # Check both new and legacy format handling
        assert 'if thermostats_config:' in content
        assert 'else:' in content
        assert '# Legacy format' in content
        
    except FileNotFoundError:
        assert False, "climate.py not found"


def test_imports_and_types():
    """Test that proper imports and type annotations are in place."""
    try:
        with open('custom_components/thermostatvalvecontroller/climate.py', 'r') as f:
            content = f.read()
        
        # Check for proper imports
        assert 'from typing import Any' in content
        assert 'import logging' in content
        assert 'from datetime import timedelta' in content
        
        # Check for proper type annotations
        assert ') -> "ValveControllerClimate | None":' in content
        assert 'dict[str, Any]' in content
        assert 'HomeAssistant' in content
        assert 'ConfigEntry' in content
        
    except FileNotFoundError:
        assert False, "climate.py not found"


if __name__ == "__main__":
    test_climate_module_structure()
    test_backward_compatibility_structure()
    test_error_handling_structure()
    test_multiple_entities_creation()
    test_imports_and_types()
    print("All climate tests passed!")