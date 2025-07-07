# Home Assistant Thermostat Valve Controller (WIP)

Ever had the problem that your thermostat did not heat the way you wanted it to?<br>
It either did not open the valve enough or too much or had a high delay?<br>
A PID controller or other tools like `Better Thermostat` also didn't work?<br>
Having a thermostat like the `Eurotronic Comet` that allows you to manually control its valve?<br>
Then this integration is for you!<br>
Based on a temperature difference between current and target, you can define your own valve positions easily.<br>
It's like the `generic thermostat` but for valves, not on/off heaters, and has many additional [features](#features-list-incomplete).


## Installation
### HACS
1. Open the custom repository dialog in HACS ([Instructions](https://www.hacs.xyz/docs/faq/custom_repositories/))
2. Enter this repository URL into the `Repository` field and select `Integration` as type.<br>`https://github.com/Xitee1/ha-thermostat-valve-controller`
3. Search for `Thermostat Valve Controller` in HACS and install the integration
4. Restart Home Assistant
5. Navigate to [Helpers in HA or click this link](https://my.home-assistant.io/redirect/helpers/)
6. Create a new helper and select `Thermostat Valve Controller`

## Multiple Thermostats Support

Starting from this version, you can configure multiple thermostats within a single integration entry. This provides better organization and reduces clutter in your integrations list when managing multiple rooms or zones.

### How it works:
1. **Integration Entry**: Create one integration entry with a descriptive name (e.g., "House Thermostats")
2. **Add Thermostats**: Within that entry, add multiple thermostat configurations, each with:
   - Unique thermostat name (e.g., "Living Room", "Bedroom")
   - Individual temperature sensor
   - Individual valve entity
   - Independent valve position mappings
   - Separate thermostat settings and presets
3. **Entity Management**: Each thermostat becomes a separate climate entity with unique entity IDs

### Benefits:
- **Better Organization**: Group related thermostats under one integration entry
- **Individual Control**: Each thermostat operates independently with its own settings
- **Easier Management**: Add, edit, or remove thermostats through the options menu
- **Backward Compatibility**: Existing single-thermostat setups continue to work unchanged

## Project start

Based on: https://github.com/Xitee1/home-assistant-custom-components-devcontainers-template

Based on my AppDaemon script: https://github.com/Xitee1/AD-ThermostatController

Because I now have more thermostats and the appdaemon version requires you to misuse the generic_thermostat integration which just doesn't work good when used like this and all the manual work that is needed, I'm creating an integration for this.

Goal for this is:

- Configuring everything trough the GUI (temp sensor, valve, min/max, heating steps)
- Also being able to configure heating presets
- The integration creates a new climate entity (no need to use generic_thermostat and helpers) and links it to the existing device (better visibility and room linking? - need to find that out)

### Todo

- Need to check if device mapping does work (so that the thermostat entity of this integration gets linked to the existing valve device (if the valve integration provides a device))
- ~~Add support for multiple thermostats per config entry~~ ✅ **Completed**
- Add support for multiple valves per thermostat  
- Trigger valve position update after min cycle duration (if was skipped before beacuse of the delay)
- When testing using input_numbers, the current temp will not load until it updates. Need more investigation for this in real world usage. According to the code it should update if it is available and on any state changes that are valid (not unavailable, ...) but that does not seem to happen in my testings

### Features (list incomplete)

- Easy setup in GUI, no need to use YAML
- **Multiple thermostats per config entry**: Configure multiple thermostat entities within a single integration entry for better organization
- Allows manually defining valve positions based on temperature difference
- Configurable presets
- Emergency valve position: In case the temperature sensor fails, the valve will be set automatically to a specified position that keeps your room at an acceptable temperature
- Minimum cycle duration: Set a minimum duration between valve position updates
- **Backward compatibility**: Existing single-thermostat configurations continue to work without changes

### Ideas

- Emergency valve position: Not only trigger this position if the values are unavailable but also if they haven't changed for a while (`calculate_valve_position()`)
