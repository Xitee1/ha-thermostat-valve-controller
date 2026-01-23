# Home Assistant Thermostat Valve Controller

Ever had the problem that your thermostat did not heat the way you wanted it to?<br>
It either did not open the valve enough or too much or had a high delay?<br>
A PID controller or other tools like `Better Thermostat` also didn't work?<br>
Having a thermostat like the `Eurotronic Comet` that allows you to manually control its valve?<br>
Then this integration is for you!<br>
Based on a temperature difference between current and target, you can define your own valve positions easily.<br>
It's like the `generic thermostat` but for valves, not on/off heaters, and has many additional [features](#features-list-incomplete).

This integration was originally based on my AppDaemon script, which is now archived: https://github.com/Xitee1/AD-ThermostatController
This project uses my Home Assistant custom components template with dev containers: https://github.com/Xitee1/home-assistant-custom-components-devcontainers-template

## Installation
### HACS
1. Open the custom repository dialog in HACS ([Instructions](https://www.hacs.xyz/docs/faq/custom_repositories/))
2. Enter this repository URL into the `Repository` field and select `Integration` as type.<br>`https://github.com/Xitee1/ha-thermostat-valve-controller`
3. Search for `Thermostat Valve Controller` in HACS and install the integration
4. Restart Home Assistant
5. Navigate to [Helpers in HA or click this link](https://my.home-assistant.io/redirect/helpers/)
6. Create a new helper and select `Thermostat Valve Controller`

## Todo
- When testing using input_numbers, the current temp will not load until it updates. Need more investigation for this in real world usage. According to the code it should update if it is available and on any state changes that are valid (not unavailable, ...) but that does not seem to happen in my testings

### Features (list is incomplete)

- Easy setup in GUI, no need to use YAML
- Multiple Valve Support: Control multiple valves/radiators in the same room with a single thermostat
- Allows manually defining valve positions based on temperature difference
- Configurable presets
- Emergency valve position: In case the temperature sensor fails, the valve will be set automatically to a specified position that keeps your room at an acceptable temperature
- Minimum cycle duration: Set a minimum duration between valve position updates

### Ideas

- Emergency valve position: Not only trigger this position if the values are unavailable but also if they haven't changed for a while (`calculate_valve_position()`)
