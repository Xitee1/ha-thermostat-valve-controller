"""Test the Thermostat Valve Controller constants and basic structure."""

def test_constants_file():
    """Test that constants file has proper values."""
    with open('custom_components/thermostatvalvecontroller/const.py', 'r') as f:
        content = f.read()
    
    # Test new constants
    assert 'CONF_THERMOSTATS = "thermostats"' in content
    assert 'CONF_THERMOSTAT_NAME = "thermostat_name"' in content
    
    # Test backward compatibility
    assert 'CONF_TEMPERATURE_SENSOR_ENTITY_ID = "temperature_sensor_entity_id"' in content
    assert 'CONF_VALVE_ENTITY_ID = "valve_entity_id"' in content
    assert 'CONF_POSITION_MAPPING = "position_mapping"' in content
    assert 'CONF_PRECISION = "precision"' in content
    assert 'CONF_MIN_CYCLE_DURATION = "min_cycle_duration"' in content
    assert 'CONF_VALVE_EMERGENCY_POSITION = "valve_emergency_position"' in content
    assert 'CONF_MIN_TEMP = "min_temp"' in content
    assert 'CONF_MAX_TEMP = "max_temp"' in content
    assert 'CONF_TARGET_TEMP_STEP = "target_temp_step"' in content
    assert 'DOMAIN = "thermostatvalvecontroller"' in content


def test_config_flow_structure():
    """Test that config flow classes are properly defined."""
    try:
        with open('custom_components/thermostatvalvecontroller/config_flow.py', 'r') as f:
            content = f.read()
        
        # Check for key classes and methods
        assert 'class ThermostatValveControllerConfigFlow' in content
        assert 'class ThermostatValveControllerOptionsFlow' in content
        assert 'async def async_step_user' in content
        assert 'async def async_step_manage_thermostats' in content
        assert 'async def async_step_thermostat_config' in content
        assert 'async def async_step_valve_position' in content
        assert 'async def async_step_thermostat_settings' in content
        assert 'async def async_step_presets' in content
        
        # Check for multiple thermostats support
        assert 'CONF_THERMOSTATS' in content
        assert 'CONF_THERMOSTAT_NAME' in content
        assert '_thermostats: list[dict[str, Any]] = []' in content
        
        # Check for proper flow management
        assert 'action == "add"' in content
        assert 'action == "edit"' in content
        assert 'action == "delete"' in content
        assert 'action == "finish"' in content
        
    except FileNotFoundError:
        assert False, "config_flow.py not found"


def test_climate_structure():
    """Test that climate module has proper structure."""
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
        assert 'for i, thermostat_config in enumerate(thermostats_config)' in content
        
        # Check for backward compatibility
        assert '# Legacy format - single thermostat from options' in content
        assert '_create_legacy_thermostat_entity' in content
        
        # Check unique ID generation
        assert 'unique_id = f"{config_entry.entry_id}_{thermostat_index}"' in content
        
    except FileNotFoundError:
        assert False, "climate.py not found"


def test_strings_structure():
    """Test that strings.json has proper structure."""
    import json
    
    try:
        with open('custom_components/thermostatvalvecontroller/strings.json', 'r') as f:
            strings = json.load(f)
        
        # Check config flow structure
        assert 'config' in strings
        assert 'step' in strings['config']
        assert 'user' in strings['config']['step']
        assert 'manage_thermostats' in strings['config']['step']
        assert 'thermostat_config' in strings['config']['step']
        assert 'valve_position' in strings['config']['step']
        assert 'thermostat_settings' in strings['config']['step']
        assert 'presets' in strings['config']['step']
        
        # Check options flow structure
        assert 'options' in strings
        assert 'step' in strings['options']
        
        # Check error messages
        assert 'error' in strings['config']
        assert 'no_thermostats' in strings['config']['error']
        
        # Verify specific translations
        assert strings['config']['step']['user']['title'] == 'Thermostat Valve Controller'
        assert strings['config']['step']['manage_thermostats']['title'] == 'Manage Thermostats'
        assert strings['config']['error']['no_thermostats'] == 'At least one thermostat must be configured'
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        assert False, f"strings.json error: {e}"


def test_manifest_structure():
    """Test that manifest.json is valid."""
    import json
    
    try:
        with open('custom_components/thermostatvalvecontroller/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert manifest['domain'] == 'thermostatvalvecontroller'
        assert manifest['config_flow'] is True
        assert 'name' in manifest
        assert 'version' in manifest
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        assert False, f"manifest.json error: {e}"


def test_backward_compatibility():
    """Test that backward compatibility is maintained."""
    with open('custom_components/thermostatvalvecontroller/climate.py', 'r') as f:
        content = f.read()
    
    # Check for legacy format handling
    assert 'thermostats_config = config_entry.data.get(CONF_THERMOSTATS)' in content
    assert 'if thermostats_config:' in content
    assert 'else:' in content
    assert '# Legacy format' in content
    assert '_create_legacy_thermostat_entity' in content
    
    # Check that options are still read for legacy format
    assert 'config_entry.options[CONF_VALVE_ENTITY_ID]' in content
    assert 'config_entry.options[CONF_TEMPERATURE_SENSOR_ENTITY_ID]' in content


if __name__ == "__main__":
    test_constants_file()
    test_config_flow_structure()
    test_climate_structure()
    test_strings_structure()
    test_manifest_structure()
    test_backward_compatibility()
    print("All tests passed!")