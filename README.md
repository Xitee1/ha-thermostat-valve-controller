# Home Assistant Thermostat Valve Controller
Based on: https://github.com/Xitee1/home-assistant-custom-components-devcontainers-template

Based on my AppDaemon script: https://github.com/Xitee1/AD-ThermostatController

Because I now have more thermostat and the appdaemon version requires you to misuse the generic_thermostat integration which just doesn't work good when used like this and all the manual work that is needed, I'm creating an integration for this.

Goal for this is:

- Configuring everything trough the GUI (temp sensor, valve, min/max, heating steps)
- Also being able to configure heating presets
- The integration creates a new climate entity (no need to use generic_thermostat and helpers) and links it to the existing device (better visibility and room linking? - need to find that out)
