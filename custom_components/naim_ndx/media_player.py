from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries, core
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    RepeatMode,
)
from homeassistant.const import CONF_NAME
from homeassistant.helpers import (
    config_validation as cv,
    entity_platform,
)
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, SERVICE_SEND_COMMAND, CONF_BROADLINK

_LOGGER = logging.getLogger(__name__)

COMMANDS = {
    "play": "JgAsAB0eHB4fHDk8OR8bPRwfOD07OhwAC4UbIBsfHCA3PTkfGz0bHzk9OTwbAA0FAAAAAAAAAAAAAAAA",
    "pause": "JgAyAAZkHSEYIhkgOTs5IB45GyE5IBogGx8bAAujGx8bIRkgOT06HRw9Gx84IBshGiIYAA0FAAAAAAAA",
    "stop": "JgAoAB4gODw5PDofGj4aIDg+Gx84AAujGyA4PTg9OR8bPRsgOTwbHzkADQU=",
    "next": "JgAwABwfHB4cHzg9OR8dOzkgGx8bIBsgGgALoxwgGx4cIDk7Oh4cPDkfGx8dHxsfGwANBQAAAAAAAAAA",
    "previous": "JgAsABwgOjs5PTgfHjs4IBsfHB4dOxwAC4UdHzg8OT04Hxw6PB4bIBogGj4dAA0FAAAAAAAAAAAAAAAA",
    "repeat": "JgAsABsfOT05PDkfGx8cPBwfGyA4PRsAC4YbHzo8OD05HxsfHDwcHxsfOT0bAA0FAAAAAAAAAAAAAAAA",
    "disp": "JgAwAB0eHB8cHzk9Oh4dHhwfHTs5PRwfHQALdRsfHB8cHzk8Oh8cIBsbID05PRsgGwANBQAAAAAAAAAA",
    "one": "JgAwAB4fOTw5PTkfHCAbHxwfHCAbIBw8GwALdh0eOT05PTkfGyAcHxsgHCAbIBs9GgANBQAAAAAAAAAA",
    "two": "JgAwAB4dHB8bIDk9OR8bIBwfGyAbIBs9OQALkxwfHSAbHjk9OSAcIBogGx8cHxw8OAANBQAAAAAAAAAA",
    "three": "JgAwAB0eOT03PzkfHCAcIBseGyEcPBwgGwALdRweOT05PTchHCAbHx0gGyAbPBweHAANBQAAAAAAAAAA",
    "four": "JgAsAB4eNj85PDkgGyAdHhseHT03IRwAC5McHzk9Nz83IRwfHB8dHhw8OCMaAA0FAAAAAAAAAAAAAAAA",
    "five": "JgAwAB0fHB8cHjk9NyIcIBseHCAcOzk9HAALdR0eHSAbIDVANiEcHx0eHCAcPDk8HAANBQAAAAAAAAAA",
    "six": "JgAsABwgOD05PTkfHCAcHhwfHTscHzkAC5QbIDk8OT05IBsgGyAbHxw9HB85AA0FAAAAAAAAAAAAAAAA",
    "seven": "JgAwABwfOT05PDogGiAbIBwgGT4cHxwfGwALdh0eOjw5PTkfHB8dHhwfHDwcHxwfHAANBQAAAAAAAAAA",
    "eight": "JgAwAB0eHB8dHjk9OR8dHhwfHD05HxsgGwALlBwfHB8bHzo9OR8cHxsgGz05Hx0eHAANBQAAAAAAAAAA",
    "nine": "JgAsABsgOTw5PTkfHCAbIBs7Ox8cOx0AC3YcHzk9OTw6HxsgGyAcPDkfHD0bAA0FAAAAAAAAAAAAAAAA",
    "zero": "JgA0ABsgHB8bIDo7OSAbIBsgGyAcHxweHB8cAAuTHR4cHxwfOT05Hx0fGx8cHxwfGyAbIBwADQUAAAAA",
}

SUPPORT_NDX = (
    MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PLAY_MEDIA
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.REPEAT_SET
)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
) -> None:
    async_add_entities(
        [
            NDXDevice(
                hass, config_entry.data[CONF_NAME], config_entry.data[CONF_BROADLINK]
            )
        ]
    )

    # Register entity services
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_SEND_COMMAND,
        {
            vol.Required("command"): cv.string,
        },
        NDXDevice.send_command.__name__,
    )


class NDXDevice(MediaPlayerEntity):
    # Representation of a Emotiva Processor

    def __init__(self, hass, name, broadlink_entity):
        self._hass = hass
        self._state = MediaPlayerState.IDLE
        self._entity_id = "media_player.naim_ndx"
        self._unique_id = "naim_ndx_" + name.replace(" ", "_").replace(
            "-", "_"
        ).replace(":", "_")
        self._device_class = "receiver"
        self._name = name
        self._broadlink_entity = broadlink_entity

    @property
    def should_poll(self):
        return False

    @property
    def icon(self):
        return "mdi:disc"

    @property
    def state(self) -> MediaPlayerState:
        return self._state

    @property
    def name(self):
        # return self._device.name
        return None

    @property
    def has_entity_name(self):
        return True

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self._unique_id)
            },
            name=self._name,
            manufacturer="Naim",
            model="NDX",
        )

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def entity_id(self):
        return self._entity_id

    @property
    def device_class(self):
        return self._device_class

    @entity_id.setter
    def entity_id(self, entity_id):
        self._entity_id = entity_id

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        return SUPPORT_NDX

    @property
    def repeat(self):
        return RepeatMode.ONE

    async def send_command(self, command):
        await self._send_broadlink_command(command)

    async def _send_broadlink_command(self, command):
        await self._hass.services.async_call(
            "remote",
            "send_command",
            {
                "entity_id": self._broadlink_entity,
                "num_repeats": "1",
                "delay_secs": "0.4",
                "command": f"b64:{COMMANDS[command]}",
            },
        )

    async def async_set_repeat(self, repeat: RepeatMode) -> None:
        """Set the repeat mode."""
        if repeat == RepeatMode.ONE:
            await self._send_broadlink_command("repeat")
            self.async_schedule_update_ha_state()

    async def async_media_stop(self) -> None:
        """Send stop command to media player."""
        await self._send_broadlink_command("stop")
        self._state = MediaPlayerState.IDLE
        self.async_schedule_update_ha_state()

    async def async_media_play(self) -> None:
        """Send play command to media player."""
        await self._send_broadlink_command("play")
        self._state = MediaPlayerState.PLAYING
        self.async_schedule_update_ha_state()

    async def async_media_pause(self) -> None:
        """Send pause command to media player."""
        await self._send_broadlink_command("pause")
        self._state = MediaPlayerState.PAUSED
        self.async_schedule_update_ha_state()

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self._send_broadlink_command("next")

    async def async_media_previous_track(self) -> None:
        """Send next track command."""
        await self._send_broadlink_command("previous")
