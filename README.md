# Home Assistant Thermostat Valve Controller

Ever had the problem that your thermostat did not heat the way you wanted it to?<br>
It either did not open the valve enough or too much or had a high delay?<br>
A PID controller or other tools like `Better Thermostat` also didn't work?<br>
Having a thermostat like the `Eurotronic Comet` that allows you to manually control its valve?<br>
Then this integration is for you!<br>
Based on a temperature difference between current and target, you can define your own valve positions easily.<br>
It's like the `generic thermostat` but for valves, not on/off heaters, and has many additional [features](#features).

This integration was originally based on my AppDaemon script, which is now archived: https://github.com/Xitee1/AD-ThermostatController
This project uses my Home Assistant custom components template with dev containers: https://github.com/Xitee1/home-assistant-custom-components-devcontainers-template

## Features

- Setup in the UI as a helper, no YAML needed. All settings can be changed later in the options of the helper.
- Works with any thermostat that exposes its valve position as a `number` or `input_number` entity.
- Uses any `sensor`, `number` or `input_number` entity as temperature source, for example a separate room sensor.
- Valve positions are defined by you, based on the difference between target and current temperature ([Valve position mapping](#valve-position-mapping)).
- Multiple valves: Control multiple valves/radiators in the same room with a single climate entity. All valves get the same position.
- HVAC modes `heat` and `off`: `off` sets all valves to the lowest position of the mapping. While the mode is `off`, manual changes of the valve position are kept.
- Presets `home`, `away`, `comfort`, `eco`, `sleep` and `activity`: Only presets with a temperature are shown. Switching back to no preset restores the previous target temperature.
- Emergency valve position: If the temperature sensor is unavailable, the valves are set to a position that keeps your room at an acceptable temperature.
- Minimum cycle duration: Sets a minimum time between valve position updates. A blocked update is executed when the time has passed.
- Minimum temperature change step: Updates the valve position only if the temperature has changed by a minimum amount since the last update.
- Target temperature, HVAC mode and preset are restored after a restart of Home Assistant.
- The climate entity is added to the device of the main valve entity.

## Installation
### Marketplace
Requires Home Assistant 2026.11 or newer.

[![Open your Home Assistant instance and open a repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=Xitee1&repository=ha-thermostat-valve-controller&category=integration)

1. Click the button above, or add the repository manually ([Instructions](https://www.home-assistant.io/integrations/marketplace/)):
   1. Go to **Settings** > **Marketplace** and select **Add from link** in the upper-right corner
   2. Enter this repository URL under **GitHub link** and select **Add**<br>`https://github.com/Xitee1/ha-thermostat-valve-controller`
2. Open `Thermostat Valve Controller` in the Marketplace and select **Install**
3. If Home Assistant asks for a restart (**Settings** > **System** > **Repairs**), restart Home Assistant
4. Navigate to [Helpers in HA or click this link](https://my.home-assistant.io/redirect/helpers/)
5. Create a new helper and select `Thermostat Valve Controller`

## Configuration

The setup has four steps. All settings can be changed later in the options of the helper.

### Valve

| Option | Default | Description |
| --- | --- | --- |
| Thermostat Name | | Name of the climate entity |
| Temperature sensor entity | | `sensor`, `number` or `input_number` entity with the current room temperature |
| Temperature sensor precision | `0.1` | Precision of the temperature sensor, usually `0.1` or `1`. Used to display the current temperature. |
| Thermostat valve entity | | `number` or `input_number` entity that sets the valve position |
| Additional valve entities | | Further `number` or `input_number` entities. They get the same position as the main valve. |
| Minimum cycle duration | | Minimum time the main valve keeps its position before the next update. Changes of HVAC mode, preset or target temperature are applied immediately. |
| Emergency valve position | `25` | Valve position while the temperature sensor is `unavailable` or `unknown`, removed, or reports a non-numeric value |
| Minimum temperature change step | `0` | Minimum temperature change since the last valve update before the valve position is updated again. `0` disables this check. Changes of HVAC mode, preset or target temperature are applied immediately. |

### Valve position mapping

The mapping assigns a valve position to the difference between target and current temperature (target − current, rounded to 0.1). Each key is a temperature difference, each value is a valve position. The position of a key applies if the difference is greater than the key.

Default mapping:

```yaml
"-0.2": 0
"-0.1": 15
"0.0": 25
"0.1": 35
"0.2": 50
"0.4": 80
"0.7": 90
"1.0": 100
"1.3": 120
"1.7": 150
"2.0": 180
```

Resulting valve positions:

| Target − current | Valve position |
| --- | --- |
| ≤ -0.1 | 0 |
| > -0.1 to 0.0 | 15 |
| > 0.0 to 0.1 | 25 |
| > 0.1 to 0.2 | 35 |
| > 0.2 to 0.4 | 50 |
| > 0.4 to 0.7 | 80 |
| > 0.7 to 1.0 | 90 |
| > 1.0 to 1.3 | 100 |
| > 1.3 to 1.7 | 120 |
| > 1.7 to < 2.0 | 150 |
| ≥ 2.0 | 180 |

Example: Target 21.0 °C, current 20.7 °C. The difference is 0.3, so the valve is set to 50.

- It's recommended to start with the default mapping and fine tune it later.
- The values are sent unchanged to the valve entities. They must be within the range of your valve entities. The default mapping uses values up to 180. If your valve entity uses for example 0–100, adjust the mapping.
- The lowest value of the mapping is used when the HVAC mode is set to `off`. The HVAC action is `heating` while any valve is above this value.

### Thermostat

| Option | Default | Description |
| --- | --- | --- |
| Minimum temperature | `7` | Lowest target temperature that can be set |
| Maximum temperature | `35` | Highest target temperature that can be set |
| Target temperature step | `0.5` | Step by which the target temperature can be changed |

### Presets

Target temperature for each preset. Presets without a temperature are not shown on the climate entity.

## Ideas and bugs

Ideas and bugs are tracked in the [issues](https://github.com/Xitee1/ha-thermostat-valve-controller/issues).
